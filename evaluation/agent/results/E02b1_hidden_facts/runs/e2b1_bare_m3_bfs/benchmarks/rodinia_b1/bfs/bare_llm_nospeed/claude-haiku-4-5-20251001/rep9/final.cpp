/* Rodinia 3.1 bfs, from Rodinia's bfs.cpp (sha256 308ac84a8e6e; University of Virginia licence,
 * see benchmarks/rodinia_3.1/LICENSE). */
#include "rodinia_b1/bfs.h"

static void kernel_bfs(void)
{
	int k=0;
	bool stop;
	do
        {
            stop=false;

            // First loop: each thread processes one node at the current level and updates
            // its unvisited neighbors. Multiple threads may write the same values to
            // h_cost[id] and h_updating_graph_mask[id] if neighbors are shared; atomic
            // writes prevent races while preserving idempotent correctness.
            #pragma omp parallel for default(none) shared(h_graph_mask, h_graph_nodes, h_graph_edges, h_graph_visited, h_cost, h_updating_graph_mask, no_of_nodes)
            for(int tid = 0; tid < no_of_nodes; tid++ )
            {
                if (h_graph_mask[tid] == true){
                    h_graph_mask[tid]=false;
                    for(int i=h_graph_nodes[tid].starting; i<(h_graph_nodes[tid].no_of_edges + h_graph_nodes[tid].starting); i++)
                    {
                        int id = h_graph_edges[i];
                        if(!h_graph_visited[id])
                        {
                            #pragma omp atomic write
                            h_cost[id]=h_cost[tid]+1;
                            #pragma omp atomic write
                            h_updating_graph_mask[id]=true;
                        }
                    }
                }
            }

            // Second loop: each thread updates one node's status for the next level.
            // Threads write to unique indices, so no races on array elements. The stop
            // variable is combined using logical OR reduction (idempotent: true OR anything = true).
            #pragma omp parallel for default(none) shared(h_updating_graph_mask, h_graph_mask, h_graph_visited, no_of_nodes) reduction(||:stop)
            for(int tid=0; tid< no_of_nodes ; tid++ )
            {
                if (h_updating_graph_mask[tid] == true){
                    h_graph_mask[tid]=true;
                    h_graph_visited[tid]=true;
                    stop = stop || true;
                    h_updating_graph_mask[tid]=false;
                }
            }
            k++;
        }
	while(stop);
}

PB_MAIN(kernel_bfs)
