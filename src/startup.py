import os
import tarfile

from database import Database
from export import generate_metadata_csv

import logging
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

ram_limit = os.getenv('MEMORY_LIMIT', 12)
file_limit = os.getenv('FILE_LIMIT', None)
file_start = os.getenv('FILE_START', None)

def main():
    file_names = [
        "non_comm_use.A-B", 
        "non_comm_use.O-Z", 
        "non_comm_use.C-H", 
        "non_comm_use.I-N", 
        "comm_use.A-B", 
        "comm_use.C-H", 
        "comm_use.I-N", 
        "comm_use.O-Z"
    ]

    if file_limit:
        file_names = file_names[:file_limit]   
    if file_start:
        file_names = file_names[file_start:]   

    logging.info("Processing files: {}".format(", ".join(file_names)))

    if not os.path.isfile("/src/reach.jar"):
        logging.error("REACH JAR file not found")
        exit(1)

    db = Database()
    logging.info("Starting REACH Server")
    os.system("java -cp reach.jar org.clulab.processors.server.ProcessorServer &")
    for file_name in file_names:
        logging.info(f"Processing {file_name}")
        download_link = f"ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk/${file_name}.xml.tar.gz"
        os.system(f'curl -o /src/reach/source.tar.gz "{download_link}"')
        os.system("mkdir -p /src/reach/papers")
        
        with tarfile.open("/src/reach/source.tar.gz", "r:gz") as tar_file:         
            db.filterFiles(tar_file.getmembers())
        
        os.system("tar -xzf /src/reach/source.tar.gz -C /src/reach/papers/ -T /src/reach/filterFiles.txt")
        os.system("rm /src/reach/source.tar.gz")
        
        logging.info("Starting REACH NLP")
        os.system(f"java -jar -Xmx{ram_limit}g reach.jar")
        logging.info("REACH NLP Complete")
        os.system("rm -rf /src/reach/papers")

        logging.info("Starting Mongo Import")
        logging.info("Generate PUBMED collection")
        generate_metadata_csv("/src/reach/papers/", "/src/reach/output.csv")
        db.import_metadata_csv("/src/reach/papers/")

        logging.info("Import to articles collection")
        db.import_article_to_db("/src/reach/output/")
        
        logging.info("Mapping articles")
        db.generate_article_iden_map()
        
        logging.info(f"Processing {file_name} Complete")