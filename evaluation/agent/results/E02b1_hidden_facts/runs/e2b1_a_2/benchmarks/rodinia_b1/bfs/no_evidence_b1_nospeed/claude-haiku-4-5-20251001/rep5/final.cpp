/* Rodinia 3.1 bfs, from Rodinia's bfs.cpp (sha256 308ac84a8e6e; University of Virginia licence,
 * see benchmarks/rodinia_3.1/LICENSE). */
#include "rodinia_b1/bfs.h"

static void kernel_bfs(void)
{
	int k=0;
	bool stop;
	int* new_cost = (int*)malloc(no_of_nodes * sizeof(int));
	bool* new_updating_mask = (bool*)malloc(no_of_nodes * sizeof(bool));

	do
        {
            stop=false;

            #pragma omp parallel for shared(new_cost,new_updating_mask) 
            for(int tid = 0; tid < no_of_nodes; tid++)
            {
                new_cost[tid] = h_cost[tid];
                new_updating_mask[tid] = false;
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
                            new_cost[id]=h_cost[tid]+1;
                            new_updating_mask[id]=true;
                        }
                    }
                }
            }

            #pragma omp parallel for shared(new_cost,new_updating_mask) 
            for(int tid = 0; tid < no_of_nodes; tid++)
            {
                h_cost[tid] = new_cost[tid];
                h_updating_graph_mask[tid] = new_updating_mask[tid];
            }

            bool updated_any = false;
            for(int tid=0; tid< no_of_nodes ; tid++ )
            {
                bool updated_this = false;
                if (h_updating_graph_mask[tid] == true){
                    h_graph_mask[tid]=true;
                    h_graph_visited[tid]=true;
                    updated_this = true;
                    h_updating_graph_mask[tid]=false;
                }
                updated_any = updated_any || updated_this;
            }
            stop = updated_any;
            k++;
        }
	while(stop);

	free(new_cost);
	free(new_updating_mask);
}

PB_MAIN(kernel_bfs)
