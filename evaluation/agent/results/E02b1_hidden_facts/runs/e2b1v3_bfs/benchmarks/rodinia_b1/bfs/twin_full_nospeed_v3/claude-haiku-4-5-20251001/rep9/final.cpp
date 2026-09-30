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

            int* h_cost_updates = (int*)malloc(sizeof(int) * no_of_nodes);
            bool* cost_updated = (bool*)malloc(sizeof(bool) * no_of_nodes);
            memset(cost_updated, false, sizeof(bool) * no_of_nodes);

            for(int tid = 0; tid < no_of_nodes; tid++ )
            {
                if (h_graph_mask[tid] == true){
                    h_graph_mask[tid]=false;
                    for(int i=h_graph_nodes[tid].starting; i<(h_graph_nodes[tid].no_of_edges + h_graph_nodes[tid].starting); i++)
                    {
                        int id = h_graph_edges[i];
                        if(!h_graph_visited[id])
                        {
                            h_cost_updates[id]=h_cost[tid]+1;
                            cost_updated[id]=true;
                            h_updating_graph_mask[id]=true;
                        }
                    }
                }
            }

            #pragma omp parallel for shared(h_cost_updates,cost_updated) 
            for(int i = 0; i < no_of_nodes; i++)
            {
                if(cost_updated[i])
                {
                    h_cost[i] = h_cost_updates[i];
                }
            }
            free(h_cost_updates);
            free(cost_updated);

            #pragma omp parallel for lastprivate(stop) 
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
}

PB_MAIN(kernel_bfs)
