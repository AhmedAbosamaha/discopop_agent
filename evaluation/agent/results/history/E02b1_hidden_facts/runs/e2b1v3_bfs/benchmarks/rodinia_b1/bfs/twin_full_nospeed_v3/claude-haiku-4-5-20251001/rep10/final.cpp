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

            // Cache costs of all nodes before processing to eliminate read-before-write ordering dependencies
            int* cached_cost = (int*)malloc(no_of_nodes * sizeof(int));
            #pragma omp parallel for shared(cached_cost) 
            for(int tid = 0; tid < no_of_nodes; tid++) {
                cached_cost[tid] = h_cost[tid];
            }

            #pragma omp parallel for shared(cached_cost) 
            for(int tid = 0; tid < no_of_nodes; tid++ )
            {
                if (h_graph_mask[tid] == true){
                    h_graph_mask[tid]=false;
                    int my_cost = cached_cost[tid];
                    for(int i=h_graph_nodes[tid].starting; i<(h_graph_nodes[tid].no_of_edges + h_graph_nodes[tid].starting); i++)
                    {
                        int id = h_graph_edges[i];
                        if(!h_graph_visited[id])
                        {
                            h_cost[id]=my_cost+1;
                            h_updating_graph_mask[id]=true;
                        }
                    }
                }
            }

            free(cached_cost);

            #pragma omp parallel for lastprivate(stop) 
            for(int tid=0; tid< no_of_nodes ; tid++ )
            {
                if (h_updating_graph_mask[tid] == true){
                    h_graph_mask[tid]=true;
                    h_graph_visited[tid]=true;
                    stop=true;
                    h_updating_graph_mask[tid]=false;
                }
            }
            k++;
        }
	while(stop);
}

PB_MAIN(kernel_bfs)
