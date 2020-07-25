import os
import sys
import csv
import glob
import indra.literature.pubmed_client as parser
import xml.etree.ElementTree as ET


def generate_metadata_csv(path, destFileName):
    def extractFromXML(fileContent):
        if(os.path.isfile(destFileName)):
            destCSV = open(destFileName, 'a')
        else:
            destCSV = open(destFileName, 'w')
            print("Journal Title,Year,DOI,PMCID,PMID,Article Type,Topics", file=destCSV)
        writer = csv.writer(destCSV, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        tree = ET.fromstring(fileContent)
        pm_articles = tree.findall('./PubmedArticle')
        for art_ix, pm_article in enumerate(pm_articles):
            medline_citation = pm_article.find('./MedlineCitation')
            pubmed = pm_article.find('./PubmedData')
            try:
                history_pub_date = pubmed.find(
                    './History/PubMedPubDate[@PubStatus="pubmed"]')
                year = parser._find_elem_text(history_pub_date, 'Year')
                PublicationTypeList = medline_citation.find(
                    './Article/PublicationTypeList')
                pubType = parser._find_elem_text(
                    PublicationTypeList, 'PublicationType')
                topics = []
                for topic in medline_citation.findall('./MeshHeadingList/MeshHeading'):
                    topics.append(topic.find('DescriptorName').text)
                topics_string = ' , '.join(topics)
            except Exception as err:
                print(err)
                continue

            pub_year = None if (year is None) else int(year)
            article_info = parser._get_article_info(
                medline_citation, pm_article.find('PubmedData'))
            journal_info = parser._get_journal_info(medline_citation, False)

            # Preparing results
            title = journal_info["journal_abbrev"] or ""
            Year = pub_year
            DOI = article_info["doi"] or ""
            PMCID = article_info["pmcid"] or ""
            PMID = article_info["pmid"] or ""
            article_type = pubType or ""
            article_topics = topics_string or ""
            # storing in csv file
            writer.writerow([title, Year, DOI, PMCID, PMID,
                             article_type, article_topics])
        # Closing file
        destCSV.close()

    for filename in glob.iglob(path + '**/*.nxml', recursive=True):
        with open(filename) as file:
            extractFromXML(file.read())
