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

		for(int tid = 0; tid < no_of_nodes; tid++ )
		{
			if (h_graph_mask[tid] == true){
				h_graph_mask[tid]=false;
				int frontier_cost = h_cost[tid] + 1;
				for(int i=h_graph_nodes[tid].starting; i<(h_graph_nodes[tid].no_of_edges + h_graph_nodes[tid].starting); i++)
				{
					int id = h_graph_edges[i];
					if(!h_graph_visited[id])
					{
						h_cost[id]=frontier_cost;
						h_updating_graph_mask[id]=true;
					}
				}
			}
		}

		bool any_updated = false;
		#pragma omp parallel for lastprivate(any_updated) 
		for(int tid=0; tid< no_of_nodes ; tid++ )
		{
			if (h_updating_graph_mask[tid] == true){
				h_graph_mask[tid]=true;
				h_graph_visited[tid]=true;
				h_updating_graph_mask[tid]=false;
				any_updated = true;
			}
		}
		stop = any_updated;
		k++;
	}
	while(stop);
}

PB_MAIN(kernel_bfs)
