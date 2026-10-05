/* Rodinia 3.1 bfs, from Rodinia's bfs.cpp (sha256 308ac84a8e6e; University of Virginia licence,
 * see benchmarks/rodinia_3.1/LICENSE). */
#include "rodinia_b1/bfs.h"

static void kernel_bfs(void)
{
	int k=0;
	bool stop;
	int* h_cost_new = (int*)malloc(no_of_nodes * sizeof(int));
	do
        {
            stop=false;

            for(int tid = 0; tid < no_of_nodes; tid++ )
            {
                if (h_graph_mask[tid] == true){
                    h_graph_mask[tid]=false;
                    for(int i=h_graph_nodes[tid].starting; i<(h_graph_nodes[tid].no_of_edges + h_graph_nodes[tid].starting); i++)
                    {
                        int id = h_graph_edges[i];
                        if(!h_graph_visited[id])
                        {
                            h_cost_new[id]=h_cost[tid]+1;
                            h_updating_graph_mask[id]=true;
                        }
                    }
                }
            }

            #pragma omp parallel for shared(h_cost_new) 
            for(int id = 0; id < no_of_nodes; id++)
            {
                if (h_updating_graph_mask[id] == true){
                    h_cost[id] = h_cost_new[id];
                }
            }

            bool* stop_flags = (bool*)malloc(no_of_nodes * sizeof(bool));
            #pragma omp parallel for shared(stop_flags) 
            for(int tid=0; tid< no_of_nodes ; tid++ )
            {
                stop_flags[tid] = false;
                if (h_updating_graph_mask[tid] == true){
                    h_graph_mask[tid]=true;
                    h_graph_visited[tid]=true;
                    stop_flags[tid]=true;
                    h_updating_graph_mask[tid]=false;
                }
            }
            stop = false;
            for(int tid=0; tid< no_of_nodes ; tid++ )
            {
                if (stop_flags[tid]){
                    stop = true;
                    break;
                }
            }
            free(stop_flags);
            k++;
        }
	while(stop);
	free(h_cost_new);
}

PB_MAIN(kernel_bfs)
