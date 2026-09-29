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

            bool* discovered = (bool*) malloc(sizeof(bool) * no_of_nodes);
            int* discovered_cost = (int*) malloc(sizeof(int) * no_of_nodes);

            for (int i = 0; i < no_of_nodes; i++) {
                discovered[i] = false;
                discovered_cost[i] = h_cost[i];
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
                            discovered_cost[id]=h_cost[tid]+1;
                            discovered[id]=true;
                        }
                    }
                }
            }

            for(int i = 0; i < no_of_nodes; i++)
            {
                if (discovered[i]) {
                    h_cost[i] = discovered_cost[i];
                    h_updating_graph_mask[i] = true;
                }
            }

            for(int tid=0; tid< no_of_nodes ; tid++ )
            {
                if (h_updating_graph_mask[tid] == true){
                    h_graph_mask[tid]=true;
                    h_graph_visited[tid]=true;
                    h_updating_graph_mask[tid]=false;
                    stop=true;
                }
            }

            free(discovered);
            free(discovered_cost);
            k++;
        }
	while(stop);
}

PB_MAIN(kernel_bfs)
