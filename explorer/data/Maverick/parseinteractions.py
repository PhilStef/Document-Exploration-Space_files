import json
import os

main_file_path = 'Parsing Tests\\highlighttest.json'
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

# How many seconds in the doc needed to be included
time_limit = 0.75
skip = False
drag = False
for i, current in enumerate(data):
    #If this is true, it does not add the mouse leave object 
    if(skip):
        skip = False
        continue 
    #If it is drag end, get rid of the drag false and continue on
    if(current["type"] == "drag-end"):
        drag = False
    #if it is in a drag, continue until it is a drag end
    if(drag):
        continue 
    #if it is a drag start, set the drag bool to True to ensure nothing is saved until it is drag end
    if(current["type"] == "drag-start"):
        drag = True
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
folder_path = os.path.join(current_dir, "Parsing Tests")
# Define the file path as the current directory with your desired file name
file_path = os.path.join(folder_path, f'parsed{file_name}')

# Write JSON data to a file in the same folder
with open(file_path, 'w') as json_file:
    json.dump(newData, json_file, indent=4)
#Draggin slowly 
# dragging fast
#Highliting and Searching 
#enter open leave enter close
#Document edges

# 2 or 3 Tasks and the batches for them