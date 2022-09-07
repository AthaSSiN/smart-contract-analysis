import csv
import subprocess

filename = "export-verified-contractaddress-opensource-license.csv"
 
# initializing the titles and rows list
fields = []
rows = []
 
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

for i in range(10):
    
    print("Running for address", rows[i][1])
    c = f"python3 run.py -d {rows[i][1]} 1 30".split()
    subprocess.run(c)
    print("---------------------\n")
