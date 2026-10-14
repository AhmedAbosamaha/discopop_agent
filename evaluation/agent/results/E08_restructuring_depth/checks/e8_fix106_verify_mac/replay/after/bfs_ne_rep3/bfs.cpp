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

            bool *was_frontier = (bool*)malloc(no_of_nodes * sizeof(bool));
            int *new_cost = (int*)malloc(no_of_nodes * sizeof(int));
            bool *new_updating_mask = (bool*)malloc(no_of_nodes * sizeof(bool));

            #pragma omp parallel for shared(new_cost,was_frontier,new_updating_mask) 
            for(int i = 0; i < no_of_nodes; i++) {
                was_frontier[i] = h_graph_mask[i];
                new_cost[i] = h_cost[i];
                new_updating_mask[i] = h_updating_graph_mask[i];
            }

            for(int tid = 0; tid < no_of_nodes; tid++ )
            {
                if (was_frontier[tid]){
                    h_graph_mask[tid]=false;
                    for(int i=h_graph_nodes[tid].starting; i<(h_graph_nodes[tid].no_of_edges + h_graph_nodes[tid].starting); i++)
                    {
                        int id = h_graph_edges[i];
                        if(!h_graph_visited[id])
                        {
                            new_cost[id]=h_cost[tid]+1;
                            new_updating_mask[id]=true;
                        }
                    }
                }
            }

            #pragma omp parallel for shared(new_cost,new_updating_mask) 
            for(int tid = 0; tid < no_of_nodes; tid++) {
                h_cost[tid] = new_cost[tid];
                h_updating_graph_mask[tid] = new_updating_mask[tid];
            }

            free(was_frontier);
            free(new_cost);
            free(new_updating_mask);

            int count_updated = 0;
            #pragma omp parallel for reduction(+:count_updated) 
            for(int tid=0; tid< no_of_nodes ; tid++ )
            {
                if (h_updating_graph_mask[tid] == true){
                    h_graph_mask[tid]=true;
                    h_graph_visited[tid]=true;
                    count_updated++;
                    h_updating_graph_mask[tid]=false;
                }
            }
            stop = (count_updated > 0);
            k++;
        }
	while(stop);
}

PB_MAIN(kernel_bfs)
