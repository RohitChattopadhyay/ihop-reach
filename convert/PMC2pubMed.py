import pandas as pd
import sys

if(len(sys.argv)!=3):
    print("Less arguments provided")
    print("python <SCRIPT_NAME>.py <INPUT>.csv <OUTPUT>.csv")
    print("Closing Script")
    quit()
try:
    f=pd.read_csv(sys.argv[1], low_memory=False)
except:
    print("Failed to read input file")
    print("Closing Script")
    quit()
print("Completed Reading File")

# Extracting important information
keep_col = ['Journal Title','Year','DOI','PMCID','PMID']
new_f = f[keep_col]
# Saving in CSV file
new_f.to_csv(sys.argv[2], index=False, float_format="%.0f")
print("Completed Printing File")
print("Closing Script")