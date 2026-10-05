/* Rodinia 3.1 bfs, from Rodinia's bfs.cpp (sha256 308ac84a8e6e; University of Virginia licence,
 * see benchmarks/rodinia_3.1/LICENSE). */
#include "rodinia_b1/bfs.h"

static void kernel_bfs(void)
{
	int k=0;
	bool stop;
	bool* local_stop = (bool*)malloc(no_of_nodes * sizeof(bool));
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
                            h_cost[id]=h_cost[tid]+1;
                            h_updating_graph_mask[id]=true;
                        }
                    }
                }
            }

            #pragma omp parallel for shared(local_stop) 
            for(int tid=0; tid< no_of_nodes ; tid++ )
            {
                local_stop[tid] = false;
                if (h_updating_graph_mask[tid] == true){
                    h_graph_mask[tid]=true;
                    h_graph_visited[tid]=true;
                    local_stop[tid]=true;
                    h_updating_graph_mask[tid]=false;
                }
            }

            for(int tid=0; tid< no_of_nodes ; tid++ )
            {
                if (local_stop[tid] == true){
                    stop=true;
                }
            }
            k++;
        }
	while(stop);
	free(local_stop);
}

PB_MAIN(kernel_bfs)
