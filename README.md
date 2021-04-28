# PowerBenchmarking

1. Start interactive session on Casper using execcasper. This will be "Terminal A",
   and will be used to run the jobs you want to benchmark power consumption for.

2. After interactive session starts in Terminal A, use "hostname" to get the name of your node

3. In another terminal, "Terminal B", connect to Casper and use "ssh <hostname>" to access the
    same resources as your interactive session. You'll use Terminal B to run the scripts.

4. The Energy/Power benchmarking scripts will not run or stop automatically (TO DO: workflow), so prepare to
   start and end them when your job begins/ends.

5. In Terminal B, navigate to this repository and modify the output file name (if necessary) in 
    either CPU_Energy or GPU_Power, depending on which you are using.

6. In Terminal A, prepare to run your job.  

7. Once you start your job in Terminal A, start the benchmarking scripts in Terminal B
     ex: "./GPU_Power" or "./CPU_Energy"

8. Once the job in Terminal A ends (or you are finished gathering benchmarking data), stop the benchmarking
   scripts in Terminal B using Ctrl-C

9. The benchmarking data is written to a .txt file. The .txt file can be parsed using the python scripts.
   Load the python module ("module load python"), then parse the output:
   ex: "python GPU_Power_Parse.py GPU_P.txt" or "python CPU_Energy_Parse.py CPU_E.txt"

10. The parsing script will create a .summary file and .csv file of the data
