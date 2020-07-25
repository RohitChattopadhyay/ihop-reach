import sys
import os
import csv
import threading
import json
from os.path import join, getsize
import logging
from collections import defaultdict
from pymongo import MongoClient


class Database:
    def __init__(self):
        self.mongo_url = os.getenv('MONGO_SRV', 'localhost')
        self.mongo_port = os.getenv('MONGO_PORT', 27017)

        try:
            mongo_client = MongoClient(
                connect=False, host=self.mongo_url, port=self.mongo_port)
            self.mongo_db = mongo_client["iHOP"]
        except Exception as e:
            logging.error(e.message, e.args)
            quit()

        try:
            pmc_thresh = os.environ['PMC_THRESHOLD']
            if pmc_thresh.startswith("PMC"):
                pmc_thresh = pmc_thresh[3:]
        except:
            pmc_thresh = 3930612

        self.pmc_thresh = int(pmc_thresh)

    def filterFiles(self, file_content):
        def _isPmcPresent(pmcid, filePath):
            pmcid = str(pmcid)
            if pmcid.startswith("PMC"):
                pmcid = pmcid[3:]

            if int(pmcid) < self.pmc_thresh:
                return

            destFile = '/src/reach/filterFiles.txt'
            mongo_col = self.mongo_db["articles"]
            count = mongo_col.find({"pmc_id": pmcid}).count()
            if count == 0:
                with open(destFile, "a") as myfile:
                    myfile.write(filePath)
            return

        for line in file_content:
            fileName = line.strip().split("/")[-1]
            fileComponents = fileName.split(".")
            fileExt = fileComponents[-1]
            if fileExt != "nxml" and fileExt != "NXML":
                continue
            pmcID = fileComponents[0]
            _isPmcPresent(pmcID, line)

    def import_metadata_csv(self, filepath, payloadLimit=1000, threadsLimit=10):
        def _sendToMongo(insertList):
            col = self.mongo_db["pubmed"]
            try:
                res = col.insert_many(insertList)
                print("Insered {} documents".format(len(res.inserted_ids)))
            except Exception as e:
                print("Insered {} documents".format(e["nInserted"]))

        fields = ['journal_title', 'year', 'doi', 'pmcid',
                  'pmid', 'article_type', 'mesh_headings']
        documents = []
        threads = [None] * threadsLimit
        count = 0
        threadsCount = 0
        with open(filepath) as dataFile:
            reader = csv.reader(dataFile)
            for row in reader:
                count += 1
                if count == 1:
                    # Ignore header of CSV
                    continue
                if len(row[3]) < 2:
                    # ignore rows with empty pmcid
                    count -= 1
                    continue
                document = {}
                i = 0
                for field in fields:
                    document[field] = row[i]
                    i += 1
                document[field] = document[field].split(' , ')
                documents.append(document)
                if count % payloadLimit == 0:
                    threads[threadsCount] = threading.Thread(
                        target=_sendToMongo, args=(documents,))
                    threads[threadsCount].start()
                    threadsCount += 1
                    documents = []
                if threadsCount == threadsLimit:
                    for x in threads:
                        x.join()
                    threadsCount = 0

            _sendToMongo(documents)

    def add_article_to_db(self, data):
        mongoCollection = self.mongo_db["articles"]  # Collection name
        try:
            # Getting number of documents in the collection
            prevCount = mongoCollection.count()
            mongoCollection.insert_many(data)  # Command to insert documents
        except:
            # Incase of any error from mongodb
            print("Documents insertion failed")
            quit()
        return (mongoCollection.count()-prevCount)

    def import_article_to_db(self, sourcePath):
        def check_article_exists(article):
            mongoCollection = self.mongo_db["articles"]
            return mongoCollection.findOne(article).size() == 0

        def verify_article_schema(jsonPath):
            with open(jsonPath) as jsonFile:
                try:
                    jsonData = json.load(jsonFile)
                    participant_b = jsonData["extracted_information"]["participant_b"]
                    del jsonData["extracted_information"]["participant_b"]
                    jsonData["extracted_information"]["participant_b"] = [
                        participant_b]
                    temp = []
                    if "participant_a" in jsonData["extracted_information"]:
                        participant_a = jsonData["extracted_information"]["participant_a"]
                        partA_type = type(participant_a)
                        if(partA_type is dict):
                            del jsonData["extracted_information"]["participant_a"]
                            temp = [participant_a]
                        elif(partA_type is list):
                            del jsonData["extracted_information"]["participant_a"]
                            temp.extend(participant_a)
                    jsonData["extracted_information"]["participant_a"] = temp
                    return jsonData
                except json.decoder.JSONDecodeError as e:
                    # if the file is not a proper json file
                    print("Decoding JSON has failed")
                    print(e)  # display the error message
                    print("in " + jsonPath)  # display the file location
            return None

        fileData = []
        fileCount = 0

        resultCount = 0
        chunkSize = 10000  # Size of smaller parts of the payload

        # r=root, d=directories, f = files
        for r, d, f in os.walk(sourcePath):
            for file in f:
                if ('.json' or '.JSON') in file:
                    fileCount += 1  # keeping count of json files
                    fromPath = os.path.join(r, file)
                    data = verify_article_schema(fromPath)
                    if data != None:
                        if check_article_exists(data):
                            continue
                        # delete processed file
                        os.remove(fromPath)
                        # append proper JSON data to array
                        fileData.append(data)
                        if(fileCount % chunkSize == 0):
                            # Call for insertion in database
                            # function call for insertion of array of JSON data
                            resultCount += self.add_article_to_db(fileData)
                            print("Inserted {} documents".format(
                                resultCount))  # print info message
                            print("Uploaded till "+fromPath)
                            fileData.clear()  # clear list for next set of documents

        if(len(fileData) > 0):
            # Call for insertion in database
            # function call for insertion of array of JSON data
            resultCount += self.add_article_to_db(fileData)
            print("Inserted {} documents".format(resultCount))
            print("Uploaded till " + fromPath)
        print("{} json files found, out of which {} json file(s) are invalid".format(
            fileCount, (fileCount-resultCount)))
        # execution result display
        if fileCount == 0:
            # No valid JSON file to insert
            print("No json file to insert")
        elif resultCount == 0:
            # No document inserted in MongoDB
            print("No json file inserted")
        elif resultCount < fileCount:
            # Partial success in inserting the documents
            print("Successfully inserted {} json files to database out of {} json files".format(
                resultCount, fileCount))
        elif resultCount == fileCount:
            # Successfull insertion
            print("Successfully inserted {} json files to database".format(resultCount))

    def generate_article_iden_map(self):
        mongoCollectionS = self.mongo_db["articles"]  # Collection name
        # Collection name
        mongoCollectionD = self.mongo_db["identifier_mapping"]
        mongoCollectionD.drop()
        mongoCollectionD.create_index([('iden', 1)], unique=True)

        def _add_mapping_to_db(data):
            if(len(data) == 0):
                return 0
            try:
                res = mongoCollectionD.insert_many(
                    data)  # Command to insert documents
            except:
                # Incase of any error from mongodb
                print("Documents insertion failed")
                logging.error("Mongo Ins Fail:\t{}\n".format(data))
            return (len(res.inserted_ids))

        identifiers = defaultdict(set)
        entType = defaultdict(str)
        documents = []
        logging.info("Fetching collection from database")
        articles = mongoCollectionS.find({}, {"_id": 0, "extracted_information.participant_b.identifier": 1, "extracted_information.participant_b.entity_text": 1, "extracted_information.participant_b.entity_type": 1,
                                              "extracted_information.participant_a.identifier": 1, "extracted_information.participant_a.entity_text": 1, "extracted_information.participant_a.entity_type": 1})

        logging.info("Reading documents")
        for article in articles:
            info = article["extracted_information"]

            for participant in info.get("participant_b", []):
                if "identifier" in participant:
                    identifiers[participant["identifier"]].add(
                        participant.get("entity_text", "").lower())
                    entType[participant["identifier"]] = (
                        participant.get("entity_type", ""))

            for participant in info.get("participant_a", []):
                if "identifier" in participant:
                    identifiers[participant["identifier"]].add(
                        participant.get("entity_text", "").lower())
                    entType[participant["identifier"]] = (
                        participant.get("entity_type", ""))

        logging.info("\nAdding {} identifiers".format(len(entType)))
        for iden in identifiers:
            if "uaz" in iden:
                continue
            obj = {
                "iden": iden,
                "syn": list(identifiers[iden]),
                "typ": entType[iden]
            }
            documents.append(obj)
            if(len(documents) == 10000):
                logging.info("\tAdded {} documents".format(
                    _add_mapping_to_db(documents)))
                documents = []
        _add_mapping_to_db(documents)
