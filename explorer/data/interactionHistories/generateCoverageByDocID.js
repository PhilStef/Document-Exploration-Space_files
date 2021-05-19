/**
 * @param interactedDocs - Array of document ids to match to the dataset.
 * @param fullDataset - json file with all the dataset documents and their assocaited countries in a list (country_list)
 * Takes a set of documents that were interacted with duing a session (interactedDocs) and attributes them to the appropriate country.
 * The goal is to automate the creation of coverage from a set of docuemtents.
 */

'use strict';

const fs = require('fs');

// todo create interactedDocs using the node-jq package so I don't have to create a list of interacted docs manually (https://www.npmjs.com/package/node-jq)
// $ cat AnalystA-log.json | jq -c 'map(select(.type == "open-doc")|.doc_id) | unique'
let interactedDocs = ["ArmsDealing10", "ArmsDealing103", "ArmsDealing17", "ArmsDealing23", "ArmsDealing25", "ArmsDealing26", "ArmsDealing31", "ArmsDealing67", "ArmsDealing68", "ArmsDealing69", "ArmsDealing72", "ArmsDealing73", "ArmsDealing80", "ArmsDealing81", "ArmsDealing96"] // ["ArmsDealing10","ArmsDealing103","ArmsDealing17","ArmsDealing25","ArmsDealing26","ArmsDealing31","ArmsDealing67","ArmsDealing72","ArmsDealing73","ArmsDealing80","ArmsDealing81","ArmsDealing96"]
// *** Exchange this array ^ with the list of documents a anaylst interacted with to generate a fresh coverage file. 
// the list should not contain repeats.

let fullDataset = './../ArmsDealing-documents-test.json' //Original Documents as json.
let colOfInterest = 'country_list'
let rawdata = fs.readFileSync(fullDataset);
let d = JSON.parse(rawdata);

let fullCoverage = []; //output collection
let allCountryList = []; // list of country names so we know which countries we've seen already.
let largest = 0; // Most number of documents associated with any country regardless of being interacted with
let mostSeen = 0; //a value for the country with the most overlap with interacted docs. - largest frequency for any country (max length for a coverage bar.)

for (let document in d) {
    let re = /,\s?/ //Split on commas or comma+spaces
    let countryList = d[document][colOfInterest].split(re);
    // do the following for each country mentioned in this document
    for (let country in countryList) {
        //have we seen this country name yet?
        let countryIdx = allCountryList.indexOf(countryList[country])
        //if this is a new country then we need to create a new object
        if (countryIdx == -1) {
            let coverageObj = {}; //the object we will be adding to the coverage file
            if (interactedDocs.includes(d[document].id)) {
                coverageObj = {
                    "country": countryList[country],
                    "affCount": 1,
                    "proportion": 1,
                    "total": 1,
                    "affiliated": d[document].id,
                    "unaffiliated": ""

                }
            } else {
                coverageObj = {
                    "country": countryList[country],
                    "affCount": 0,
                    "proportion": 0,
                    "total": 1,
                    "affiliated": "",
                    "unaffiliated": d[document].id
                }
            }
            fullCoverage.push(coverageObj) //add this new object to the output file.
            allCountryList.push(countryList[country]) //add this country to the list of seen countries
        } else {
            if (interactedDocs.includes(d[document].id)) {
                fullCoverage[countryIdx].affiliated += "," + d[document].id;
                fullCoverage[countryIdx].total++;
                fullCoverage[countryIdx].affCount++;
                fullCoverage[countryIdx].proportion = fullCoverage[countryIdx].affCount / fullCoverage[countryIdx].total
            } else {
                fullCoverage[countryIdx].unaffiliated += "," + d[document].id;
                fullCoverage[countryIdx].total++;
                fullCoverage[countryIdx].proportion = fullCoverage[countryIdx].affCount / fullCoverage[countryIdx].total
            }
            //update the max memory values
            (fullCoverage[countryIdx].affCount > mostSeen) ? mostSeen = fullCoverage[countryIdx].affCount: mostSeen = mostSeen;
            (fullCoverage[countryIdx].total > largest) ? largest = fullCoverage[countryIdx].total: largest = largest
        }
    }
}

// sort by alphabetical country name
fullCoverage.sort((a, b) => a.country.localeCompare(b.country));
// sort by total documents
// fullCoverage.sort((a, b) => b.total - a.total);
// sort by Proportion
fullCoverage.sort((a, b) => b.proportion - a.proportion);

// Add a control node at the front of the array so I can make all the bars the right length
fullCoverage.unshift({
    "mostDoc": largest,
    "mostAff": mostSeen,
    "country": "setUp",
    "affCount": mostSeen,
    "proportion": mostSeen / largest,
    "total": largest,
    "affiliated": "",
    "unaffiliated": ""
})

// Declare a buffer and write the
// data in the buffer
let buffer = new Buffer.from(JSON.stringify(fullCoverage));
   
// The fs.open() method takes a "flag"
// as the second argument. If the file
// does not exist, an empty file is
// created. 'w' stands for write mode
// which means that if the program is
// run multiple time data will be
// overwritten to the output file.
fs.open('generatedCoverage.json', 'w', function(err, fd) {
    if(err) {
        console.log('Cant open file');
    }else {
        fs.write(fd, buffer, 0, buffer.length, 
                null, function(err,writtenbytes) {
            if(err) {
                console.log('Cant write to file');
            }else {
                console.log(writtenbytes +
                    ' characters written to file');
            }
        })
    }
})