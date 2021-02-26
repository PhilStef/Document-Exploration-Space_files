# Interactions to Provenance Conditions (For Jeremy's Study)

I wanted to make this document to keep track of how I'm generating the provenance data in theis study
The history condition is easier so let's start there:

## History condition

This is really simple I wrote a bash script that takes an interaction log from the system (like ```output.json```) and purges all interactions accept highlight and search events. The resulting log is saved as mouseless-history.json and this get's loaded into the text exploration application.

To do this, navigate to the proper directory and run the following on the command line.
```sh
interactionHistories > $ ./removeMouseMoves.sh output.json
```
then look for ```mouseless-history.json``` in the same folder.

<hr>

## Coverage Condition

A bit more complex, but I'll explain.
We want to take the same interaction history (```output.json```), extract the key terms from the documents they interacted with, and compare that with the baseline key terms in the document dataset, to create a ratio.

This ratio (user interaction document terms / baseline occurance terms) is what the following dteps attempt to calculate.

### Calcualting baseline frequencies

First we need the baseline occurances of the dataset. So we start by extracting the document content from `documents_1.json`. We can use 
```sh
 data $ jq '[.[]| .contents]' documents_1.json > docs1-all-text.csv
 ```
 With the dataset document content extracted, I can use the `bagOwords.py` file to count word frequencies and remove common stop words. The stop words are the generic ones from `nltk.tokenize` in the `word_tokenize` python library.
```sh
$ python3 ./explorer/data/bagOwords.py docs1-all-text.csv
```
Running the above will export a file `vec-docs1-all-text.csv` and this is when things get funky: we need to use excel to sort the output by it's values. <small>I know I could probably find a way to do this alforithmicly, but it was removing words with identicle frequencies. that's no good </small>

Within **excel**, sort by the second column and copy the data into a blank file. - we're gonna use some fancy find and replace, and multi-cursor selection to make an array of tuples. Save this new file as a `.json` file. It should look like:
```json
[
["arms", 125],
["report", 123],
["us", 96],
["government", 93], ... ]
```
<hr> 

### Calculating key interaction history frequencies

In similar maner to the above steps, we'll do the same for the key interactions. 

First thing to extract are the key histories: (just like for the history condition)
```sh
interactionHistories > $ ./removeMouseMoves.sh output.json
```
The resulting output has refrences to element_id's that are one index below the index in the original dataset, so we'll use this fact to create associations with the data. this is where the `calcCoverage.py` script is helpful for joining the key interactions with the actual document data.

```sh
data > $ python3 calcCoverage.py interactionHistories/mouseless-history.json
```
Now we have a csv file with document content multiplied by the number of times it was interacted with. The more times there were highlights on a document the more frequently it appears in the the output file: `interactionJoinedDocs.csv`

Now we can repeat the bag of words algorithm we used before to get frequencies of tokenized words.
```sh
data > $ python3 bagOwords.py interactionJoinedDocs.csv
```
the output is  `vec-interactionJoinedDocs.csv` and we will need to sort this in **excel**, copy the sorted data into a new file and save it as a `.json` like we did for the baseline frequencies.

### Calculating a ratio

Now we just need to take these two lists of touples and do some division. That's what `ratioGenerator.py` is for.

```sh
$ python3 explorer/data/ratioGenerator.py interactionHistories/interactions-vectorized.json vectoriezed.json
```
This will export `coverage.json` as a list of touples with the word and it's ratio so a bar graph with a width can be generated in the system.