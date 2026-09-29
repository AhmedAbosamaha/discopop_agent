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

            // Allocate temporary arrays to collect updates from frontier processing
            bool *temp_updating_graph_mask = (bool*)malloc(no_of_nodes * sizeof(bool));
            int *temp_cost = (int*)malloc(no_of_nodes * sizeof(int));
            memset(temp_updating_graph_mask, false, no_of_nodes * sizeof(bool));

            // Process frontier nodes: write updates to temporary arrays (no loop-carried dependence)
            for(int tid = 0; tid < no_of_nodes; tid++ )
            {
                if (h_graph_mask[tid] == true){
                    h_graph_mask[tid]=false;
                    for(int i=h_graph_nodes[tid].starting; i<(h_graph_nodes[tid].no_of_edges + h_graph_nodes[tid].starting); i++)
                    {
                        int id = h_graph_edges[i];
                        if(!h_graph_visited[id])
                        {
                            temp_cost[id]=h_cost[tid]+1;
                            temp_updating_graph_mask[id]=true;
                        }
                    }
                }
            }

            // Merge collected updates back to global arrays
            #pragma omp parallel for shared(temp_cost,temp_updating_graph_mask) 
            for(int id = 0; id < no_of_nodes; id++)
            {
                if(temp_updating_graph_mask[id])
                {
                    h_cost[id]=temp_cost[id];
                    h_updating_graph_mask[id]=true;
                }
            }

            free(temp_updating_graph_mask);
            free(temp_cost);

            bool *local_stop = (bool*)malloc(no_of_nodes * sizeof(bool));
            memset(local_stop, false, no_of_nodes * sizeof(bool));

            #pragma omp parallel for lastprivate(temp_updating_graph_mask) shared(local_stop) 
            for(int tid=0; tid< no_of_nodes ; tid++ )
            {
                if (h_updating_graph_mask[tid] == true){
                    h_graph_mask[tid]=true;
                    h_graph_visited[tid]=true;
                    local_stop[tid]=true;
                    h_updating_graph_mask[tid]=false;
                }
            }

            stop=false;
            for(int tid=0; tid< no_of_nodes ; tid++ )
            {
                if(local_stop[tid])
                {
                    stop=true;
                    break;
                }
            }
            free(local_stop);
            k++;
        }
	while(stop);
}

PB_MAIN(kernel_bfs)
