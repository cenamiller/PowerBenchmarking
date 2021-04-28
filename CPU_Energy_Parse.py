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

def extractEnergy(line):
    #print(line)
    result = re.findall("\d+$", line)
    #print("extract energy: " + str(result[0]))
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

TimeMatches = re.findall("Time:.*", text)
sock0Matches = re.findall("Socket0.*", text)
sock1Matches = re.findall("Socket1.*", text)
dram0Matches = re.findall("DRAM0.*", text)
dram1Matches = re.findall("DRAM1.*", text)

# Get a list of the times (calling map returns a map)
sock0 = list(map(extractEnergy, sock0Matches))
sock1 = list(map(extractEnergy, sock1Matches))
dram0 = list(map(extractEnergy, dram0Matches))
dram1 = list(map(extractEnergy, dram1Matches))
Times = list(map(extractTime, TimeMatches))

i = 1
dtTimes = list()
elapTimes = list()
sock0_p = list()
sock1_p = list()
dram0_p = list()
dram1_p = list()
tot_p = list()
dtTimes.append(0) 
elapTimes.append(0)
sock0_p.append(0)
sock1_p.append(0)
dram0_p.append(0)
dram1_p.append(0)
tot_p.append(0)

f_csv.write('Step;Time Stamp;Elap Time (sec);dt (sec);Power Draw (W);Socket0 (W);Socket1 (W);DRAM0 (W);DRAM1 (W);Socket0 (uj);Socket1 (uj)\n')
while(i < (len(Times)-1)):
    dtTimes.append(getTime(Times[i-1],Times[i]))
    elapTimes.append(dtTimes[i]+elapTimes[i-1])
    sock0_p.append(getPower(dtTimes[i],sock0[i]-sock0[i-1]))
    sock1_p.append(getPower(dtTimes[i],sock1[i]-sock1[i-1]))
    dram0_p.append(getPower(dtTimes[i],dram0[i]-dram0[i-1]))
    dram1_p.append(getPower(dtTimes[i],dram1[i]-dram1[i-1]))
    tot_p.append(sock0_p[i]+sock1_p[i]+dram0_p[i]+dram1_p[i])
    f_csv.write('%d;%s;%f;%f;%f;%f;%f;%f;%f;%d;%d\n' %(i, Times[i], elapTimes[i],dtTimes[i],tot_p[i],sock0_p[i], sock1_p[i],dram0_p[i],dram1_p[i],sock0[i],sock1[i]))
    i = i+1

aver = mean(tot_p)
SDev = stdev(aver, tot_p)

aver0 = mean(sock0_p)
SDev0 = stdev(aver0, sock0_p)

aver1 = mean(sock1_p)
SDev1 = stdev(aver1, sock1_p)

averd0 = mean(dram0_p)
SDevd0 = stdev(averd0, dram0_p)

averd1 = mean(dram1_p)
SDevd1 = stdev(averd1, dram1_p)

print("\n---------------------")
print("Simulation Summary")
print("---------------------")

print("\n\tMeasured over " + str(elapTimes[-1]) + " secs\n")

print("\tAvg power (watts): " + str(aver))
print("\tStd Dev: " + str(SDev))

print("\n\tAvg power Socket0 (watts): " + str(aver0))
print("\tStd Dev: " + str(SDev0))

print("\n\tAvg power Socket1 (watts): " + str(aver1))
print("\tStd Dev: " + str(SDev1))

print("\n\tAvg power DRAM0 (watts): " + str(averd0))
print("\tStd Dev: " + str(SDevd0))

print("\n\tAvg power DRAM1 (watts): " + str(averd1))
print("\tStd Dev: " + str(SDevd1))

f.close()
f_csv.close()
f_summary.close()

