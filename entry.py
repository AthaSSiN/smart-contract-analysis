import csv
import subprocess
import sys
import os

import csv
import subprocess
import sys
import os

filename = sys.argv[2]
 
# initializing the titles and rows list

if sys.argv[1] == "-d":
    fields = []
    rows = []
    
    if filename[-3:] != "csv":
        rows = [["_", filename]]

    else:
        # reading csv file
        with open(filename, 'r') as csvfile:
            # creating a csv reader object
            csvreader = csv.reader(csvfile)
        
            # extracting field names through first row
            _ = next(csvreader)
            fields = next(csvreader)
    
            # extracting each data row one by one
            for row in csvreader:
                rows.append(row)

    for i in range(len(rows)):
        
        print("Running for address", rows[i][1])
        c = f"python3 run.py -d {rows[i][1]} 3600".split()
        subprocess.run(c)
        print("---------------------\n")

else :
    rows = os.listdir(filename)

    for i in range(len(rows)):
        if rows[i][-3:] == "sol":
            print("Running for file", filename + '/' + rows[i])
            c = f"python3 run.py -f {filename}/{rows[i]} 3600".split()
            subprocess.run(c)
            print("---------------------\n")

