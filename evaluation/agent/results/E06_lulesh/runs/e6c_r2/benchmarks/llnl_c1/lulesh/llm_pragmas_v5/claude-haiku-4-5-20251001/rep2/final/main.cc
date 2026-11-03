#include <sys/time.h>
#include <iostream>
#include "lulesh.h"
#include "llnl_c1/lulesh_harness.h"

void TimeIncrement(Domain& domain);
void LagrangeLeapFrog(Domain& domain);

int main(int argc, char *argv[])
{
   pb_lulesh_begin();
   Domain *locDom ;
   int numRanks ;
   int myRank ;
   struct cmdLineOpts opts;

   numRanks = 1;
   myRank = 0;

   opts.its = PB_ITS;
   opts.nx  = PB_NX;
   opts.numReg = 11;
   opts.numFiles = (int)(numRanks+10)/9;
   opts.showProg = 0;
   opts.quiet = 0;
   opts.viz = 0;
   opts.balance = 1;
   opts.cost = 1;

   if ((myRank == 0) && (opts.quiet == 0)) {
      std::cout << "Running problem size " << opts.nx << "^3 per domain until completion\n";
      std::cout << "Num processors: "      << numRanks << "\n";
      std::cout << "Total number of elements: " << ((Int8_t)numRanks*opts.nx*opts.nx*opts.nx) << " \n\n";
      std::cout << "To run other sizes, use -s <integer>.\n";
      std::cout << "To run a fixed number of iterations, use -i <integer>.\n";
      std::cout << "To run a more or less balanced region set, use -b <integer>.\n";
      std::cout << "To change the relative costs of regions, use -c <integer>.\n";
      std::cout << "To print out progress, use -p\n";
      std::cout << "To write an output file for VisIt, use -v\n";
      std::cout << "See help (-h) for more options\n\n";
   }

   Int_t col, row, plane, side;
   InitMeshDecomp(numRanks, myRank, &col, &row, &plane, &side);

   locDom = new Domain(numRanks, col, row, plane, opts.nx,
                       side, opts.numReg, opts.balance, opts.cost) ;
   pb_lulesh_perturb(*locDom, argc, argv);

   timeval start;
   pb_timer_start();
   gettimeofday(&start, NULL) ;
   while((locDom->time() < locDom->stoptime()) && (locDom->cycle() < opts.its)) {

      TimeIncrement(*locDom) ;
      LagrangeLeapFrog(*locDom) ;

      if ((opts.showProg != 0) && (opts.quiet == 0) && (myRank == 0)) {
         std::cout << "cycle = " << locDom->cycle()       << ", "
                   << std::scientific
                   << "time = " << double(locDom->time()) << ", "
                   << "dt="     << double(locDom->deltatime()) << "\n";
         std::cout.unsetf(std::ios_base::floatfield);
      }
   }

   double elapsed_time;
   timeval end;
   gettimeofday(&end, NULL) ;
   pb_timer_stop();
   elapsed_time = (double)(end.tv_sec - start.tv_sec) + ((double)(end.tv_usec - start.tv_usec))/1000000 ;
   double elapsed_timeG;
   elapsed_timeG = elapsed_time;

   if (opts.viz) {
      DumpToVisit(*locDom, opts.numFiles, myRank, numRanks) ;
   }

   if ((myRank == 0) && (opts.quiet == 0)) {
      VerifyAndWriteFinalOutput(elapsed_timeG, *locDom, opts.nx, numRanks);
   }

   pb_lulesh_finish(*locDom);
   delete locDom;

   return 0 ;
}
