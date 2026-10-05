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

            for(int tid = 0; tid < no_of_nodes; tid++ )
            {
                bool in_frontier = h_graph_mask[tid];
                h_graph_mask[tid]=false;
                if (in_frontier){
                    int edge_start = h_graph_nodes[tid].starting;
                    int edge_end = edge_start + h_graph_nodes[tid].no_of_edges;
                    for(int i = edge_start; i < edge_end; i++)
                    {
                        int id = h_graph_edges[i];
                        if(!h_graph_visited[id])
                        {
                            h_cost[id]=h_cost[tid]+1;
                            h_updating_graph_mask[id]=true;
                        }
                    }
                }
            }

            #pragma omp parallel for 
            for(int tid=0; tid< no_of_nodes ; tid++ )
            {
                if (h_updating_graph_mask[tid] == true){
                    h_graph_mask[tid]=true;
                    h_graph_visited[tid]=true;
                    h_updating_graph_mask[tid]=false;
                }
            }

            #pragma omp parallel for lastprivate(stop) 
            for(int tid=0; tid< no_of_nodes ; tid++ )
            {
                if (h_graph_mask[tid] == true){
                    stop=true;
                }
            }
            k++;
        }
	while(stop);
}

PB_MAIN(kernel_bfs)
