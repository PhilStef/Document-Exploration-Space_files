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


#Some notes for extracting document ids from the full dataset
## Export the ids that have to do with a specific country
# jq '[ .[] | select( .country_origin == "Kenya") | .id ]' ArmsDealing-documents.json

## lists all the countries and the documents associated with them (as well as the number of documents.)
# jq ' map({country: .country_origin, id: .id}) | group_by(.country) | map({country: map(.country)|unique, unaffiliated: map(.id), total: length})' ArmsDealing-documents.json
## take the .json output and paste it into the http://convertcsv.com/json-to-csv.htm (select "still not happy" in the output options) then you need to add 2 columns: "affiliated", "proportion"
## you can remove the extra rows you don't care about (Switzerland, USA etc.) then you'll want to apply the following formula to the proportion column: =if(D2="",0,len(D2)-len(SUBSTITUTE(D2,",",""))+1)/C2
## Sort by Proportion, then take the new coverage spreadsheet and convert to json using: http://convertcsv.com/csv-to-json.htm

#todo Find a way to make JQ make the csv or at least the json because you had to convert all the lists into json arrays instead of just text.
#todo orrrrr I could just make the function split the text by commas and not worry about this...I'll try that first