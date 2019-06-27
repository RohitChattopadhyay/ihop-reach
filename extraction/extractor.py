import os,gzip,time,sys
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
    pm_articles = tree.findall('./PubmedArticle')
    # TODO change to indra package function get_metadata
    for art_ix, pm_article in enumerate(pm_articles):
        medline_citation = pm_article.find('./MedlineCitation')
        pubmed = pm_article.find('./PubmedData')
        history_pub_date =  pubmed.find('./History/PubMedPubDate[@PubStatus="pubmed"]')
        year = parser._find_elem_text(history_pub_date, 'Year')
        month = parser._find_elem_text(history_pub_date, 'Month')
        day = parser._find_elem_text(history_pub_date, 'Day')

        # Add the Publication date from Journal info

        pub_date = {
            "year"  : None if (year  is None) else int(year),
            "month" : None if (month is None) else int(month),
            "day"   : None if (day   is None) else int(day)
        }
        # Get article info
        article_info = parser._get_article_info(medline_citation, pm_article.find('PubmedData'))
        # Get journal info
        journal_info = parser._get_journal_info(medline_citation, False)

        # Preparing results
        title   = journal_info["journal_abbrev"] or ""
        Year    = pub_date["year"]
        DOI     = article_info["doi"] or ""
        PMCID   = article_info["pmcid"] or ""
        PMID    = article_info["pmid"] or ""
        # storing in csv file 

        print('"{}",{},"{}",{},{}'.format(title,Year,DOI,PMCID,PMID),file=destCSV)
    # Closing file
    destCSV.close()


rootDir = sys.argv[1] or None
directory = os.fsencode(rootDir)
for file in os.listdir(directory):
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