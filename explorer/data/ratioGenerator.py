import sys
import json

# load files to join
folder = './explorer/data/'
analystFile = folder + sys.argv[1] #'tok-key-interactions.json'
baselineFile = folder + sys.argv[2] #'tok-docs1-all-text.json'
analyst = json.load(open(analystFile, 'r'))
baseline = json.load(open(baselineFile, 'r'))

# Join the two touple sets and calculate ratios. 
# Also track the max ratio for normalization later.
tokenRatios = []
maxRatio = 0 
for token in analyst:
    for j in baseline:
        if (token[0] == j[0]):
            ratio = token[1] / j[1]
            if(ratio > maxRatio):
                maxRatio = ratio
            tokenRatios.append([token[0], ratio])

# Normalize the ratios to (0,1]
for token in tokenRatios:
    token[1] = token[1]/maxRatio

# Write to file
with open(folder+'coverage.json', 'w') as outfile:
    json.dump(tokenRatios, outfile)