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

            bool *local_updating_mask = (bool *)malloc(no_of_nodes * sizeof(bool));
            int *local_cost = (int *)malloc(no_of_nodes * sizeof(int));
            memset(local_updating_mask, 0, no_of_nodes * sizeof(bool));

            for(int tid = 0; tid < no_of_nodes; tid++ )
            {
                if (h_graph_mask[tid] == true){
                    h_graph_mask[tid]=false;
                    for(int i=h_graph_nodes[tid].starting; i<(h_graph_nodes[tid].no_of_edges + h_graph_nodes[tid].starting); i++)
                    {
                        int id = h_graph_edges[i];
                        if(!h_graph_visited[id])
                        {
                            local_cost[id]=h_cost[tid]+1;
                            local_updating_mask[id]=true;
                        }
                    }
                }
            }

            #pragma omp parallel for shared(local_cost,local_updating_mask) 
            for(int id = 0; id < no_of_nodes; id++)
            {
                if(local_updating_mask[id])
                {
                    h_updating_graph_mask[id] = true;
                    h_cost[id] = local_cost[id];
                }
            }

            free(local_updating_mask);
            free(local_cost);

            #pragma omp parallel for 
            for(int tid=0; tid< no_of_nodes ; tid++ )
            {
                if (h_updating_graph_mask[tid] == true){
                    h_graph_mask[tid]=true;
                    h_graph_visited[tid]=true;
                    h_updating_graph_mask[tid]=false;
                }
            }

            for(int tid=0; tid< no_of_nodes ; tid++ )
            {
                if (h_graph_mask[tid] == true){
                    stop=true;
                    break;
                }
            }

            k++;
        }
	while(stop);
}

PB_MAIN(kernel_bfs)
