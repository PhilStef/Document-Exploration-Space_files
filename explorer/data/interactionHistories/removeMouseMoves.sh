#!/bin/bash
#this is a parser for json logs from the document exploritory analysis tool. 
#this will extract any highlights, and search interactions and savethem to a file called "mouseless-history.json"
# Run this from within the same directory with the following Command:
# $ ./removeMouseMoves.sh [fileName (should be .json)]
PARSEME=$1 
jq '[ .[] |
     select ( .type == "search" ), 
     select ( .type == "highlightText" ) | 
     {element_id,type,message,timestamp} ]' $PARSEME > "mouseless-history.json"

#Saving this for later:
# returns a list of the unique interactions captured this log.
#jq 'unique_by(.type)| .[].type ' output-5.json 
## > "collapse-document"
## > "createNote"
## > "enddrag-document"
## > "highlightText"
## > "mouseenter-document"
## > "mouseenter-document-minimized"
## > "mouseexit-document"
## > "mouseexit-document-minimized"
## > "newConnection"
## > "open-document"
## > "restore-from-scrunch"
## > "scrunch-highlight-view"
## > "search"
## > "startdrag-document"
## > "unhighlight"