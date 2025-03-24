import json
import os

file_path = '4_8e80b316_interactions.json'
file_name = os.path.basename(file_path)

print(file_name)
try:
    data = []
    # Try to open the file
    with open(file_path, 'r') as file:
        data = json.load(file)   
        print("File is opened successfully.")
except IOError:
    print("File is already opened or doesn't exist.")  
newData = [] 
def timeInDoc(obj,i,data): 
    i = i+1
    if(data[i]["type"] != "mouseleave-doc"):
        return 1000
    print(f"{obj["doc_id"]} and {data[i]["doc_id"]}   is       {data[i]["timestamp"] - obj["timestamp"]}")
    return data[i]["timestamp"] - obj["timestamp"]




skip = False
for i, current in enumerate(data): 
    if(skip):
        skip = False
        continue
    if(current["type"] == "mouseenter-doc"):
        if (timeInDoc(current, i, data) < 0.75 ):
            skip = True
            continue
    print("adding " + current["type"]) 
    newData.append(current) 
    print(f"adding {current["timestamp"]}") 
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
    