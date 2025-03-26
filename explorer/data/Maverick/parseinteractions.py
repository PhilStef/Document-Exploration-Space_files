import json
import os

main_file_path = '4_8e80b316_interactions.json'
file_name = os.path.basename(main_file_path)

print(file_name)
try:
    data = []
    # Try to open the file
    with open(main_file_path, 'r') as file:
        data = json.load(file)   
        print("File is opened successfully.")
except IOError:
    print("File is already opened or doesn't exist.")  

newData = [] 
##First checks if the next object is a mouse leave, if not, it will be added to the result
def timeInDoc(obj,i,data): 
    i = i+1
    if(data[i]["type"] != "mouseleave-doc"):
        return 1000
    print(f"{obj["doc_id"]} and {data[i]["doc_id"]}   is       {data[i]["timestamp"] - obj["timestamp"]}")
    ##Returns the time in the doc
    return data[i]["timestamp"] - obj["timestamp"]


##How many seconds in the doc needed to be included
time_limit = 0.75
skip = False
for i, current in enumerate(data):
    #If this is true, it does not add the mouse leave object 
    if(skip):
        skip = False
        continue
    if(current["type"] == "mouseenter-doc"): 
        #If the time is less than the limit, this will make skip true, not adding the leaving instant and also will not add the current enter object
        if (timeInDoc(current, i, data) < time_limit):
            skip = True
            continue
    print("adding " + current["type"] + " " + str(i)) 
    newData.append(current)
print(len(data))
print(len(newData))
print(newData) 

# Get the current directory
current_dir = os.getcwd()

# Define the file path as the current directory with your desired file name
file_path = os.path.join(current_dir, f'parsed{file_name}.json')

# Write JSON data to a file in the same folder
with open(file_path, 'w') as json_file:
    json.dump(newData, json_file, indent=4)
    