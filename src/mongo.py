import sys,os

from os.path import join, getsize

from pymongo import MongoClient
try:
#    mongo_ip = os.environ['MONGOIP']
    mongo_client = MongoClient(connect=False, host = os.environ.get('API_IP') ,port=27017)
    # mongo_client = MongoClient(connect=False)
    mongo_col = mongo_client["iHOP"]["articles"]         # SET DB DETAILS HERE
except Exception as e:
    print(e.message, e.args)
    quit()
    
try:
    pmc_thresh = os.environ['PMC_THRESHOLD']
    if pmc_thresh.startswith("PMC"):
        pmc_thresh = pmc_thresh[3:]
except:
    pmc_thresh = 3930612

deleted = 0

def isPmcPresent(pmcid,filePath):
    pmcid = str(pmcid)
    if pmcid.startswith("PMC"):
        pmcid = pmcid[3:]

    if int(pmcid) < int(pmc_thresh):
        return

    count = int(mongo_col.find({"pmc_id" : pmcid}).count())
    if count==0:
        with open(destFile, "a") as myfile:
            myfile.write(filePath)
    return  

sourceFile  = '/src/reach/inputFiles.txt'
global destFile
destFile = '/src/reach/filterFiles.txt'

with open(sourceFile) as f:
    content = f.readlines()
    for line in content:
        fileName = line.strip().split("/")[-1]
        fileComponents = fileName.split(".")
        fileExt = fileComponents[-1]
        if fileExt != "nxml" and fileExt != "NXML":
            continue
        pmcID = fileComponents[0]
        isPmcPresent(pmcID,line)
