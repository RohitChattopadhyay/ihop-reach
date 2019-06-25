import indra.literature.pubmed_client as parser
import xml.etree.ElementTree as ET
import os.path

# Read from file
tree = ET.parse('source/pubmed19n0654.xml')
# root = tree.getroot()

# Set Destination file name
destFileName = "output.csv"

# Opening destination file
if(os.path.isfile(destFileName)):
    destCSV = open(destFileName, 'a')
else:
    destCSV = open(destFileName, 'w')
    print("Journal Title,Year,DOI,PMCID,PMID", file=destCSV)

# Getting articles from the XML file
pm_articles = tree.findall('./PubmedArticle')
for art_ix, pm_article in enumerate(pm_articles):
    medline_citation = pm_article.find('./MedlineCitation')
    pubDate = medline_citation.find('Article/Journal/JournalIssue/PubDate')

    # Get article info
    article_info = parser._get_article_info(medline_citation, pm_article.find('PubmedData'))
    # Get journal info
    journal_info = parser._get_journal_info(medline_citation, False)

    # Preparing results
    title   = journal_info["journal_abbrev"] or ""
    Year    = parser._find_elem_text(pubDate, 'Year') or ""
    DOI     = article_info["doi"] or ""
    PMCID   = article_info["pmcid"] or ""
    PMID    = article_info["pmid"] or ""

    # storing in csv file 
    print(title,Year,DOI,PMCID,PMID,sep=",",file=destCSV)
