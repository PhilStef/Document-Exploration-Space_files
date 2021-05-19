#!/bin/bash
#this is a parser for json logs from the document exploritory analysis tool. 
#this will take a raw interaction log and remove the frequant/noisy interactions.
# Removes mouseenter-doc, mouseleave-dog, drag-start, drag-end and saves the remaining interactions to a file called "key-interactions.json"

# Run this from within the same directory with the following Command:
# $ ./prepForHistory.sh [fileName (should be .json)]
PARSEME=$1
cat $PARSEME  | jq 'map(select(.type != "mouseenter-doc" and .type != "mouseleave-doc" and .type != "drag-start" and .type != "drag-end"))' > "key-interactions.json"

# echo "These documents were opened in this interaction log\n ------"
#  cat $PARSEME | jq -c 'map(select(.type == "open-doc")|.doc_id) | unique' 
