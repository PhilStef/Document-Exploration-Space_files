# this tool will:
# 1. take the reduced (key) interactions
# 2. join the id's with their appropriate documents 
# 3. Export a txt file that is all the documents (repeated) by the number of references.
# This will then be used in the vectorization tool to determine the terms with more coverage by an analyst.
# We can compare the output form the analyst to the vector produced from the default document list to see where there are more coverage.  

import sys
import json
import csv 

# load data
folder = './explorer/data/'
analystLog = folder + sys.argv[1] #'interactionHistories/mouseless-history.json'
interactions = json.load(open(analystLog, 'r'))
corpus = json.load(open(folder+'documents_1.json', 'r'))
# print(corpus)

# translate the interacted elements to match the ids of the documents.json
keyDocumentIds = []
for interaction in interactions:
    if not interaction['element_id'] == 'unknown':
        keyDocumentIds.append("ArmsDealing"+str(int(interaction['element_id'].replace('dialog',''))+1)) # translate the element_id to match the document id.

#joining the documents and getting content out.
joinedTextContent = []
for keydoc in keyDocumentIds:
    for doc in corpus:
        if(doc["id"] == keydoc):
            joinedTextContent.append(doc["contents"])

# todo remove other stop words like <br> 

#export to file.
with open(folder+'interactionJoinedDocs.csv', 'w') as f:
    write = csv.writer(f) 
    write.writerow(joinedTextContent)