/* Rodinia 3.1 bfs, from Rodinia's bfs.cpp (sha256 308ac84a8e6e; University of Virginia licence,
 * see benchmarks/rodinia_3.1/LICENSE). */
#include <atomic>
#include "rodinia_b1/bfs.h"

static void kernel_bfs(void)
{
	int k=0;
	bool stop;
	do
        {
            stop=false;

            std::atomic<int>* cost_atomic = (std::atomic<int>*)h_cost;
            std::atomic<bool>* mask_atomic = (std::atomic<bool>*)h_updating_graph_mask;

            #pragma omp parallel for shared(cost_atomic,mask_atomic) 
            for(int tid = 0; tid < no_of_nodes; tid++ )
            {
                if (h_graph_mask[tid] == true){
                    h_graph_mask[tid]=false;
                    for(int i=h_graph_nodes[tid].starting; i<(h_graph_nodes[tid].no_of_edges + h_graph_nodes[tid].starting); i++)
                    {
                        int id = h_graph_edges[i];
                        if(!h_graph_visited[id])
                        {
                            cost_atomic[id].store(h_cost[tid]+1, std::memory_order_relaxed);
                            mask_atomic[id].store(true, std::memory_order_relaxed);
                        }
                    }
                }
            }

            #pragma omp parallel for 
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
