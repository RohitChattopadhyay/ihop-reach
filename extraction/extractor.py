import os,gzip,time,sys,csv
import indra.literature.pubmed_client as parser
import xml.etree.ElementTree as ET
start_time = time.time()

if(len(sys.argv)!=2):
    print("Less arguments provided")
    print("python <SCRIPT_NAME>.py <Source Path>")
    print("Closing Script")
    quit()

def extractFromXML(fileContent):
    destFileName = "output.csv"
    if(os.path.isfile(destFileName)):
        destCSV = open(destFileName, 'a')
    else:
        destCSV = open(destFileName, 'w')
        print("Journal Title,Year,DOI,PMCID,PMID", file=destCSV)
    tree = ET.fromstring(fileContent)
    try:
        results = parser.get_metadata_from_xml_tree(tree)
    except Exception as e:
        print(e)
        return
    
    # preparing for print
    writer = csv.writer(destCSV, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for key,value in results.items():
        title   = value["journal_abbrev"]
        year    = None if value["publication_date"]["year"] is None else value["publication_date"]["year"]
        doi     = value["doi"]
        pmcid   = value["pmcid"]
        pmid    = value["pmid"]
        writer.writerow([title,year,doi,pmcid,pmid])
    # Closing file
    destCSV.close()


rootDir = sys.argv[1] or None
directory = os.fsencode(rootDir)
dirlist = os.listdir(directory)
dirlist.sort()
print("Total files found: ", len(dirlist))
for file in dirlist:
     filename = os.fsdecode(file)
     if filename.endswith(".gz"): 
         filePath = os.path.join(rootDir,filename)
         print("Processing ",filename)
         with gzip.open(filePath, 'r') as f:
            fileContent = f.read()
            extractFromXML(fileContent)
     else:
         continue

print("--- %s seconds ---" % (time.time() - start_time))
quit()