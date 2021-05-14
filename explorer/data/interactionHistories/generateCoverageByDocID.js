/**
 * @param interactedDocs - Array of document ids to match
 * @param fullDataset - json file to have it's affiliated and propotion values overwritten
 * Takes a set of documents that were interacted with duing a session (interactedDocs) and attributes them to the appropriate country.
 * The goal is to automate the creation of coverage from a set of docuemtents.
 */

'use strict';

const fs = require('fs');

// todo create interactedDocs using the node-jq package so I don't have to do this manually https://www.npmjs.com/package/node-jq
let interactedDocs = ["ArmsDealing24","ArmsDealing25","ArmsDealing28","ArmsDealing30","ArmsDealing56","ArmsDealing64","ArmsDealing65","ArmsDealing67","ArmsDealing80","ArmsDealing81","ArmsDealing85","ArmsDealing86","ArmsDealing96"]
let fullDataset = './manually-generated-coverage-sorted.json'

let rawdata = fs.readFileSync(fullDataset);
let d = JSON.parse(rawdata);


function clearAffiliated(object){
    object.affiliated = "";
}
//clear out any of the affiliated ones
for (let country in d){
    clearAffiliated(d[country])
}

for (let idx in d){
    for(let i =0; i < interactedDocs.length; i++){
        if(d[idx].unaffiliated.includes(interactedDocs[i])){
            if (d[idx].affiliated == "") {
                d[idx]["affiliated"] = interactedDocs[i]
                d[idx]["proportion"] = 1 / d[idx]["total"]
            } else {
                d[idx]["affiliated"] += "," + interactedDocs[i];
                d[idx]["proportion"] = (Math.round(d[idx]["proportion"] * d[idx]["total"]) + 1) / d[idx]["total"]
            } 
        }
    }
}

//todo write to file. for now it just prints to console.
console.log(d);