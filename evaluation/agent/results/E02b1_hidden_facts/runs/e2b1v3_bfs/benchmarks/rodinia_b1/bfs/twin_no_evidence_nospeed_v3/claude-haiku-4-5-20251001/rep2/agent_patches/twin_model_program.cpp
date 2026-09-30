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

            int *temp_cost = (int *)malloc(no_of_nodes * sizeof(int));
            bool *temp_updating_graph_mask = (bool *)malloc(no_of_nodes * sizeof(bool));
            for(int i = 0; i < no_of_nodes; i++) {
                temp_cost[i] = h_cost[i];
                temp_updating_graph_mask[i] = false;
            }

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

            for(int tid=0; tid< no_of_nodes ; tid++ )
            {
                if (temp_updating_graph_mask[tid] == true){
                    h_cost[tid] = temp_cost[tid];
                    h_updating_graph_mask[tid] = true;
                }
            }

            free(temp_cost);
            free(temp_updating_graph_mask);

            for(int tid=0; tid< no_of_nodes ; tid++ )
            {
                if (h_updating_graph_mask[tid] == true){
                    stop=true;
                }
            }

            for(int tid=0; tid< no_of_nodes ; tid++ )
            {
                if (h_updating_graph_mask[tid] == true){
                    h_graph_mask[tid]=true;
                    h_graph_visited[tid]=true;
                    h_updating_graph_mask[tid]=false;
                }
            }
            k++;
        }
	while(stop);
}

PB_MAIN(kernel_bfs)
