/* Rodinia 3.1 bfs, from Rodinia's bfs.cpp (sha256 308ac84a8e6e; University of Virginia licence,
 * see benchmarks/rodinia_3.1/LICENSE). */
#include "rodinia_b1/bfs.h"

static void kernel_bfs(void)
{
	int k=0;
	bool stop;
	bool* new_updating_graph_mask = (bool*)malloc(sizeof(bool) * no_of_nodes);
	int* new_cost = (int*)malloc(sizeof(int) * no_of_nodes);
	do
        {
            stop=false;

            memset(new_updating_graph_mask, false, sizeof(bool) * no_of_nodes);
            memcpy(new_cost, h_cost, sizeof(int) * no_of_nodes);

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
                            new_updating_graph_mask[id]=true;
                        }
                    }
                }
            }

            memcpy(h_cost, new_cost, sizeof(int) * no_of_nodes);
            memcpy(h_updating_graph_mask, new_updating_graph_mask, sizeof(bool) * no_of_nodes);

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
	free(new_updating_graph_mask);
	free(new_cost);
}

PB_MAIN(kernel_bfs)
