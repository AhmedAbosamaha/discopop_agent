/* Rodinia 3.1 bfs, from Rodinia's bfs.cpp (sha256 308ac84a8e6e; University of Virginia licence,
 * see benchmarks/rodinia_3.1/LICENSE). */
#include "rodinia_b1/bfs.h"

static void kernel_bfs(void)
{
	int k=0;
	bool stop;
	do
        {
            bool* temp_mask = (bool*)malloc(no_of_nodes * sizeof(bool));
            #pragma omp parallel for shared(temp_mask) 
            for(int tid = 0; tid < no_of_nodes; tid++)
            {
                temp_mask[tid] = h_graph_mask[tid];
            }

            #pragma omp parallel for shared(temp_mask) 
            for(int tid = 0; tid < no_of_nodes; tid++ )
            {
                if (temp_mask[tid] == true){
                    h_graph_mask[tid]=false;
                    for(int i=h_graph_nodes[tid].starting; i<(h_graph_nodes[tid].no_of_edges + h_graph_nodes[tid].starting); i++)
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

            free(temp_mask);

            int num_updated = 0;
            #pragma omp parallel for reduction(+:num_updated) 
            for(int tid=0; tid< no_of_nodes ; tid++ )
            {
                if (h_updating_graph_mask[tid] == true){
                    h_graph_mask[tid]=true;
                    h_graph_visited[tid]=true;
                    h_updating_graph_mask[tid]=false;
                    num_updated = num_updated + 1;
                }
            }
            stop = (num_updated > 0);
            k++;
        }
	while(stop);
}

PB_MAIN(kernel_bfs)
