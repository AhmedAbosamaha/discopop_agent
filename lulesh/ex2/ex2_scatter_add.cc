/**
 * LULESH Example 2: Scatter-Add via elemToNode Indirection
 * Source: lulesh.cc - IntegrateStressForElems (scatter phase)
 *
 * Dependency profile for DiscoPoP agent:
 *   - OUTER loop (over elements) has a SCATTER pattern:
 *       domain.fx[elemToNode[lnode]] += fx_local[lnode]
 *     Multiple elements may share nodes → WAW race condition.
 *   - This is the classic "irregular reduction" or "scatter" pattern.
 *   - DiscoPoP will detect RAW/WAW dependencies on fx/fy/fz through the
 *     indirection array elemToNode[].
 *
 * LLM restructuring candidates:
 *   Option A — Temporaries + second DOALL gather pass (as LULESH 2.0 does
 *              with fx_elem[] when OpenMP is active):
 *       Loop 1 (DOALL): for each elem k, write fx_elem[k*8+lnode]
 *       Loop 2 (DOALL): for each node g, sum contributions from cornerList
 *   Option B — atomic updates (simple but may serialize heavily)
 *   Option C — graph coloring so non-adjacent elements run in parallel
 *
 * This file isolates the scalar-force contribution pattern without the full
 * shape-function math, so DiscoPoP can profile the dependency structure cleanly.
 */

#include <cstdlib>
#include <cstdio>
#include <vector>
#include <cmath>

typedef double Real_t;
typedef int    Index_t;

// ---------------------------------------------------------------------------
// Minimal mesh structure
// ---------------------------------------------------------------------------
struct Mesh {
    Index_t numElem;
    Index_t numNode;

    // nodelist[k*8 .. k*8+7]: 8 node indices for element k
    std::vector<Index_t> nodelist;

    // Node force accumulators
    std::vector<Real_t> fx, fy, fz;

    // Element stress (simplified: one scalar per element per direction)
    std::vector<Real_t> sigxx, sigyy, sigzz;

    // Per-node list of (elem, local_corner) pairs for the gather pass
    std::vector<Index_t> nodeElemCount;
    std::vector<std::vector<Index_t>> nodeElemCornerList;
};

// ---------------------------------------------------------------------------
// Simulate shape-function output as a trivial stand-in
// (In real LULESH this is CalcElemShapeFunctionDerivatives + normal sums)
// ---------------------------------------------------------------------------
static void MockElemForces(Index_t /*k*/, Real_t sigx, Real_t /*sigy*/,
                           Real_t /*sigz*/, Real_t fx_local[8],
                           Real_t fy_local[8], Real_t fz_local[8])
{
    for (int i = 0; i < 8; ++i) {
        fx_local[i] = sigx * 0.125;   // equal weight to each corner
        fy_local[i] = sigx * 0.125;
        fz_local[i] = sigx * 0.125;
    }
}

// ---------------------------------------------------------------------------
// Kernel (serial / race-prone version) — what DiscoPoP will analyze:
//   The WAW dependency on fx[gnode] is the key pattern.
// ---------------------------------------------------------------------------
void IntegrateStressForElems_Serial(Mesh& mesh)
{
    Index_t numElem8 = mesh.numElem * 8;
    std::vector<Real_t> fx_elem(numElem8, 0.0);
    std::vector<Real_t> fy_elem(numElem8, 0.0);
    std::vector<Real_t> fz_elem(numElem8, 0.0);

    for (Index_t k = 0; k < mesh.numElem; ++k) {
        Real_t fx_local[8], fy_local[8], fz_local[8];
        MockElemForces(k, mesh.sigxx[k], mesh.sigyy[k], mesh.sigzz[k],
                       fx_local, fy_local, fz_local);
        for (Index_t lnode = 0; lnode < 8; ++lnode) {
            fx_elem[k * 8 + lnode] = fx_local[lnode];
            fy_elem[k * 8 + lnode] = fy_local[lnode];
            fz_elem[k * 8 + lnode] = fz_local[lnode];
        }
    }

    std::fill(mesh.fx.begin(), mesh.fx.end(), 0.0);
    std::fill(mesh.fy.begin(), mesh.fy.end(), 0.0);
    std::fill(mesh.fz.begin(), mesh.fz.end(), 0.0);

    for (Index_t gnode = 0; gnode < mesh.numNode; ++gnode) {
        Index_t count = mesh.nodeElemCount[gnode];
        for (Index_t i = 0; i < count; ++i) {
            Index_t corner = mesh.nodeElemCornerList[gnode][i];
            mesh.fx[gnode] += fx_elem[corner];
            mesh.fy[gnode] += fy_elem[corner];
            mesh.fz[gnode] += fz_elem[corner];
        }
    }
}

// ---------------------------------------------------------------------------
// Restructured version (two-pass: elem-private storage → gather)
// This is what the LLM Code Modification Layer would produce to
// eliminate the scatter WAW dependency.
// ---------------------------------------------------------------------------
void IntegrateStressForElems_TwoPass(Mesh& mesh)
{
    Index_t numElem8 = mesh.numElem * 8;
    std::vector<Real_t> fx_elem(numElem8, 0.0);
    std::vector<Real_t> fy_elem(numElem8, 0.0);
    std::vector<Real_t> fz_elem(numElem8, 0.0);

    // Pass 1: DOALL — each element writes to private corner slots
    // No shared writes → fully parallel
    for (Index_t k = 0; k < mesh.numElem; ++k) {
        Real_t fx_local[8], fy_local[8], fz_local[8];
        MockElemForces(k, mesh.sigxx[k], mesh.sigyy[k], mesh.sigzz[k],
                       fx_local, fy_local, fz_local);

        for (Index_t lnode = 0; lnode < 8; ++lnode) {
            fx_elem[k * 8 + lnode] = fx_local[lnode];
            fy_elem[k * 8 + lnode] = fy_local[lnode];
            fz_elem[k * 8 + lnode] = fz_local[lnode];
        }
    }

    // Pass 2: DOALL — each node gathers its contributions from its element list
    // Each node index is unique to one thread → no write conflict
    for (Index_t gnode = 0; gnode < mesh.numNode; ++gnode) {
        Real_t fx_tmp = 0.0, fy_tmp = 0.0, fz_tmp = 0.0;
        Index_t count = mesh.nodeElemCount[gnode];
        for (Index_t i = 0; i < count; ++i) {
            Index_t corner = mesh.nodeElemCornerList[gnode][i];
            fx_tmp += fx_elem[corner];
            fy_tmp += fy_elem[corner];
            fz_tmp += fz_elem[corner];
        }
        mesh.fx[gnode] = fx_tmp;
        mesh.fy[gnode] = fy_tmp;
        mesh.fz[gnode] = fz_tmp;
    }
}

// ---------------------------------------------------------------------------
// Driver: build a simple 2x2x2 structured hex mesh (8 elems, 27 nodes)
// ---------------------------------------------------------------------------
static void BuildMesh2x2x2(Mesh& m)
{
    // 3x3x3 node grid → 27 nodes, 2x2x2 element grid → 8 elements
    m.numNode = 27;
    m.numElem = 8;
    m.fx.assign(27, 0.0); m.fy.assign(27, 0.0); m.fz.assign(27, 0.0);
    m.sigxx.assign(8, 1.0); m.sigyy.assign(8, 1.0); m.sigzz.assign(8, 1.0);
    m.nodelist.resize(8 * 8);
    m.nodeElemCount.assign(27, 0);
    m.nodeElemCornerList.resize(27);

    for (int eidx = 0; eidx < 8; ++eidx) {
        int ez = eidx / 4;
        int ey = (eidx / 2) % 2;
        int ex = eidx % 2;
        // 8 corners of hex element (i,j,k) in a 3x3x3 node grid
        int base = ez*9 + ey*3 + ex;
        int ns[8] = {
            base,     base+1,   base+4,   base+3,
            base+9,   base+10,  base+13,  base+12
        };
        for (int ln = 0; ln < 8; ++ln) {
            m.nodelist[eidx*8 + ln] = ns[ln];
            // Build corner list for gather pass
            Index_t corner = eidx * 8 + ln;
            m.nodeElemCornerList[ns[ln]].push_back(corner);
            m.nodeElemCount[ns[ln]]++;
        }
    }
}

int main()
{
    Mesh m;
    BuildMesh2x2x2(m);

    IntegrateStressForElems_Serial(m);
    printf("Serial:   fx[13]=%.6f (center node)\n", m.fx[13]);

    std::fill(m.fx.begin(), m.fx.end(), 0.0);
    std::fill(m.fy.begin(), m.fy.end(), 0.0);
    std::fill(m.fz.begin(), m.fz.end(), 0.0);

    IntegrateStressForElems_TwoPass(m);
    printf("TwoPass:  fx[13]=%.6f (center node, should match)\n", m.fx[13]);

    return 0;
}
