#Looks like this file was just used to clean up a folder called "unclean/***.json and print out all the keys used in the file? - not sure, but it doesn't look like this script has already served it's purpose."
import json


original_file = "production_allll.json"

infile = open(original_file)

counts = {}
outfiles = {}
all_types = {}

whitelist = ["P22","P3","P4","P5","P6","P7"]

for line in infile:
    parsed = json.loads(line)
    if "participant_tag" in parsed:
        print (parsed)
        ptag = parsed["participant_tag"]
        if ptag in counts:
            counts[ptag] += 1
        else:
            counts[ptag] = 1
            if ptag in whitelist:
                outfiles[ptag] = open("unclean/"+ptag+".json","w")
        if ptag in whitelist:
            all_types[parsed["type"]] = 1
            outfiles[ptag].write(line)

for ptag in outfiles.keys():
    outfiles[ptag].close()

print ("done",json.dumps(counts,indent=2))
print (json.dumps(all_types.keys()))






