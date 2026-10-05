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

            bool frontier[no_of_nodes];
            #pragma omp parallel for 
            for(int tid = 0; tid < no_of_nodes; tid++)
            {
                frontier[tid] = h_graph_mask[tid];
            }

            #pragma omp parallel for 
            for(int tid = 0; tid < no_of_nodes; tid++)
            {
                if (h_graph_mask[tid] == true)
                {
                    h_graph_mask[tid]=false;
                }
            }

            #pragma omp parallel for 
            for(int tid = 0; tid < no_of_nodes; tid++)
            {
                if (frontier[tid])
                {
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

            int num_updated = 0;
            #pragma omp parallel for reduction(+:num_updated) 
            for(int tid=0; tid< no_of_nodes ; tid++ )
            {
                if (h_updating_graph_mask[tid] == true){
                    h_graph_mask[tid]=true;
                    h_graph_visited[tid]=true;
                    num_updated++;
                    h_updating_graph_mask[tid]=false;
                }
            }
            stop = (num_updated > 0);
            k++;
        }
	while(stop);
}

PB_MAIN(kernel_bfs)
