/* Rodinia 3.1 bfs, from Rodinia's bfs.cpp (sha256 308ac84a8e6e; University of Virginia licence,
 * see benchmarks/rodinia_3.1/LICENSE). */
#include "rodinia_b1/bfs.h"

static void kernel_bfs(void)
{
	int k=0;
	bool stop;

	// Allocate temporary buffers
	int* temp_cost = (int*)malloc(no_of_nodes * sizeof(int));
	bool* temp_mask = (bool*)malloc(no_of_nodes * sizeof(bool));
	bool* stop_updates = (bool*)malloc(no_of_nodes * sizeof(bool));

	do
        {
            stop=false;

            // Initialize temporary buffers
            #pragma omp parallel for shared(temp_mask,temp_cost) 
            for(int i = 0; i < no_of_nodes; i++)
            {
                temp_cost[i] = h_cost[i];
                temp_mask[i] = false;
            }

            // First loop: process nodes and accumulate updates in temp buffers
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
                            temp_mask[id]=true;
                        }
                    }
                }
            }

            // Apply updates from temporary buffers
            #pragma omp parallel for shared(temp_mask,temp_cost) 
            for(int id = 0; id < no_of_nodes; id++)
            {
                if (temp_mask[id])
                {
                    h_cost[id] = temp_cost[id];
                    h_updating_graph_mask[id] = true;
                }
            }

            // Second loop: update visited status and accumulate stop condition
            #pragma omp parallel for shared(stop_updates) 
            for(int tid=0; tid< no_of_nodes ; tid++ )
            {
                bool had_update = h_updating_graph_mask[tid];
                if (had_update){
                    h_graph_mask[tid]=true;
                    h_graph_visited[tid]=true;
                    h_updating_graph_mask[tid]=false;
                }
                stop_updates[tid] = had_update;
            }

            // Compute reduction: check if any updates occurred
            stop = false;
            for(int tid = 0; tid < no_of_nodes; tid++)
            {
                if (stop_updates[tid])
                {
                    stop = true;
                    break;
                }
            }

            k++;
        }
	while(stop);

	// Free temporary buffers
	free(temp_cost);
	free(temp_mask);
	free(stop_updates);
}

PB_MAIN(kernel_bfs)
