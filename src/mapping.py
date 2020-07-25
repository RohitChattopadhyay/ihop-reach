from pymongo import MongoClient
from collections import defaultdict 

def addToDatabase(data):
    if(len(data)==0):
        return 0
    #returns number of inserted documents in the collection
    try:  
        res = mongoCollectionD.insert_many(data)           #Command to insert documents
    except:
        print("Documents insertion failed")         #Incase of any error from mongodb
        errLog.write("Mongo Ins Fail:\t{}\n".format(data))
    return (len(res.inserted_ids))


    mongoCollectionS = mongoConnection["iHOP"]["articles"] #Collection name
    mongoCollectionD = mongoConnection["iHOP"]["identifier_mapping"] #Collection name
    mongoCollectionD.drop()

    identifiers = defaultdict(set)
    entType = defaultdict(str)
    documents = []
    errLog = open("errorLog.csv", "a")
    #function to add json in MongoDB
    print("Fetching collection from database")
    #articles = mongoCollectionS.find({})
    articles = mongoCollectionS.find({})
    i = 1
    missA = 0
    print("Reading documents")
    for article in articles:
        info = article["extracted_information"]
        for participant in info["participant_b"]:
            try:
                identifiers[participant["identifier"]].add(participant["entity_text"].lower())
                entType[participant["identifier"]] = (participant["entity_type"])
            except:
                print(participant)
        for participant in info["participant_a"]:
            try:
                identifiers[participant["identifier"]].add(participant["entity_text"].lower())
                entType[participant["identifier"]] = (participant["entity_type"])
            except:
                print(participant)
        print(i, end=" ")
        i += 1
    i = 0
    print("\nAdding {} identifiers".format(len(entType)))
    for iden in identifiers:
        if "uaz" in iden:
            continue
        i += 1    
        obj = {
            "iden" : iden,
            "syn": list(identifiers[iden]),
            "typ": entType[iden]
        }
        documents.append(obj)
        if(len(documents) == 10000):
            print("\tAdded {} documents".format(addToDatabase(documents)))
            documents = []
        print(i,"\t", iden)
    addToDatabase(documents)    

    #Script termination message
    print("\nClosing mapping script")
    exit()
