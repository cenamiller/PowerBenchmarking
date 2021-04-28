## Script to parse a role00 dynamics output file and create a text file with
##  this format for each timestep: 1;2010-10-23_00:00:00;0.335;FL
## Also prints summary to console
## 
## Example use: python DynamicsSteps.py -nnodes 72 log.atmosphere.role00.0000.out
## 
## Based on time parsing script written by Dylan Dickerson (UWYO)
## Modified by Suzanne Piver and Henry O'Meara (UWYO), and Cena Miller (NCAR) 

import re
import argparse
import sys
import datetime
import numpy as np

parser = argparse.ArgumentParser(description="Evaluate integration times from a dynamics output file")
parser.add_argument('-n', '--nnodes',default=1, help='number of resources (nodes) job ran on', type=int)
parser.add_argument('fileName', nargs=1, help="Filename of the output file. Example: log.atmosphere.role00.0000.out")
# For debugging
args = parser.parse_args()

# Parsing regular expressions

def extractTime(line):
    #print(line)
    result = re.findall("\d+\.\d+\.\d+\.\d+\.\d+\.\d+\.\d+", line)
    #print("extract time: " + str(result[0]))
    return str(result[0])

def extractPower(line):
    #print(line)
    result = re.findall("\d+\.\d+", line)
    #print("extract energy: " + str(result[0]))
    return float(result[0])

def extractNumGPUs(line):
    result = re.findall("\d+$", line)
    return float(result[0])


## Statistics functions
def mean(arr):
    sum = 0;
    for num in arr:
        sum += num
    return sum / len(arr)

def stdev(avg, arr):
    vari = 0;
    for num in arr:
        vari += ((num - avg) ** 2)
    sdev = (vari/len(arr)) ** 0.5
    return sdev
#Returns job time in minutes
def getTime(start,end):
    stime = datetime.datetime.strptime(start, '%Y.%m.%d.%H.%M.%S.%f')
    etime = datetime.datetime.strptime(end, '%Y.%m.%d.%H.%M.%S.%f')
    jtime = etime-stime
    return (jtime.total_seconds())

def getPower(elapT, eDelta):
    return (eDelta/(elapT*1000000))
    

# Write Summary to console and file simultaneously 
class Tee(object):
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush() # If you want the output to be visible immediately
    def flush(self) :
        for f in self.files:
            f.flush()

# Open the output file


f = open(args.fileName[0],"r")
summFile = args.fileName[0].strip(".txt")

f_csv = open(summFile+'.csv', 'a')
f_summary = open(summFile+'.summary', 'w')
sys.stdout = Tee(sys.stdout, f_summary)
nodes = args.nnodes
text = f.read()

# Extract the lines we care about. matches is a list of strings like:
#   Timing for integration step: 1.05685 s

TimeMatches = re.findall("Time: .*", text)
numGPUMatches = re.findall("Attached GPUs .*", text) 
PowerMatches = re.findall("Power Draw .*", text)

# Get a list of the times (calling map returns a map)
allpowers = list(map(extractPower, PowerMatches))
numGPUs = list(map(extractNumGPUs, numGPUMatches))
Times = list(map(extractTime, TimeMatches))
numGPU = int(numGPUs[0])
print("numGPU: " + str(numGPU))

powers = np.reshape(allpowers,(-1,numGPU))

i = 1
skip = 3  #Number of initial time steps to skip
elapTimes = list()
elapTimes.append(0) 



f_csv.write('Step;Time Stamp; Elap Time (sec);')
for j in range(numGPU):
    f_csv.write('GPU ' + str(j) + ' (W);')
f_csv.write('\n') 

while(i < (len(Times)-1)):
    elapTimes.append(getTime(Times[i],Times[i+1]))
    #print("i: " + str(i))
    #print("Time: " + str(Times[i]))
    #print("Time+1: " + str(Times[i+1]))
    #print("Elap time: " + str(getTime(Times[i],Times[i+1])))
    #print("sock0: " + str(sock0[i]))
    #print("sock1: " + str(sock1[i]))
    f_csv.write('%d;%s;%f;' %(i, Times[i], elapTimes[i]))
 
    for j in range(numGPU):
        f_csv.write('%f;' %(powers[i,j]))
    f_csv.write('\n')
    i = i+1


print("\n---------------------")
print("Simulation Summary")
print("---------------------")

for j in range(numGPU):
    aver = mean(powers[:,j])
    SDev = stdev(aver, powers[:,j])

    print("\tAvg power GPU " + str(j) + " (watts): " + str(aver))
    print("\tStd Dev: " + str(SDev))

f.close()
f_csv.close()
f_summary.close()

