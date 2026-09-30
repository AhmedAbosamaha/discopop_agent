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

            int* staging_cost = (int*)malloc(no_of_nodes * sizeof(int));
            bool* staging_mask = (bool*)malloc(no_of_nodes * sizeof(bool));

            memcpy(staging_cost, h_cost, no_of_nodes * sizeof(int));
            memset(staging_mask, false, no_of_nodes * sizeof(bool));

            for(int tid = 0; tid < no_of_nodes; tid++ )
            {
                if (h_graph_mask[tid] == true){
                    h_graph_mask[tid]=false;
                    for(int i=h_graph_nodes[tid].starting; i<(h_graph_nodes[tid].no_of_edges + h_graph_nodes[tid].starting); i++)
                    {
                        int id = h_graph_edges[i];
                        if(!h_graph_visited[id])
                        {
                            staging_cost[id]=h_cost[tid]+1;
                            staging_mask[id]=true;
                        }
                    }
                }
            }

            for(int tid = 0; tid < no_of_nodes; tid++)
            {
                if(staging_mask[tid])
                {
                    h_cost[tid]=staging_cost[tid];
                    h_updating_graph_mask[tid]=true;
                }
            }

            free(staging_cost);
            free(staging_mask);

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
                }
            }
            k++;
        }
	while(stop);
}

PB_MAIN(kernel_bfs)
