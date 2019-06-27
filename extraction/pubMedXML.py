import indra.literature.pubmed_client as parser
import xml.etree.ElementTree as ET
import os.path
import time
start_time = time.time()
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

def _convert_month_abbv_to_int(month_abbrv):
    int_month = None
    try:
        int_month = int(month_abbrv)
    except ValueError:
        months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        int_month =  months.index(month_abbrv.lower()) + 1
    finally:
        return int_month

# Getting articles from the XML file
pm_articles = tree.findall('./PubmedArticle')
for art_ix, pm_article in enumerate(pm_articles):
    medline_citation = pm_article.find('./MedlineCitation')

    journal = medline_citation.find('Article/Journal')
    # Add the Publication date from Journal info
    journal_pub_date = journal.find('JournalIssue/PubDate')
    year = parser._find_elem_text(journal_pub_date, 'Year')
    month = parser._find_elem_text(journal_pub_date, 'Month')
    day = parser._find_elem_text(journal_pub_date, 'Day')

    pub_date = {
        "year"  : None if (year  is None) else int(year),
        "month" : None if (month is None) else _convert_month_abbv_to_int(month),
        "day"   : None if (day   is None) else int(day),
        "medline_date" : parser._find_elem_text(journal_pub_date, 'MedlineDate')
    }
    # Get article info
    article_info = parser._get_article_info(medline_citation, pm_article.find('PubmedData'))
    # Get journal info
    journal_info = parser._get_journal_info(medline_citation, False)

    # Preparing results
    title   = journal_info["journal_abbrev"] or ""
    Year    = pub_date["year"] or pub_date["medline_date"]
    DOI     = article_info["doi"] or ""
    PMCID   = article_info["pmcid"] or ""
    PMID    = article_info["pmid"] or ""

    # storing in csv file 
    print(title,Year,DOI,PMCID,PMID,sep=",",file=destCSV)

print("--- %s seconds ---" % (time.time() - start_time))
quit()