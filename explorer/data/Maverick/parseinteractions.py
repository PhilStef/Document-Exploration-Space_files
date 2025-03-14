import json
try:
    data = []
    # Try to open the file
    with open('explorer\\data\\Maverick\\1_e2c0a69a_interactions.json', 'r') as file:
        data = json.load(file)   
        print("File is opened successfully.")
except IOError:
    print("File is already opened or doesn't exist.")  
newData = [] 
def timeInDoc(obj, i, data): 
    # if next["type"] == "mouseenter-doc" and data[i+1]["type"] =="mouseleave-doc":
    #     return next["timestamp"] - data[i+1]["timestamp"] 
    # i = i+1 
    i = i+1 

    print(f"{obj["doc_id"]} and {data[i]["doc_id"]}   is       {data[i]["timestamp"] - obj["timestamp"]}")
    return data[i]["timestamp"] - obj["timestamp"]




skip = False
for i, current in enumerate(data):
    if(skip):
        skip = False
        print(f"skipping {current["timestamp"]}")
        continue  
    if(current["type"] == "mouseenter-doc"):
        if (timeInDoc(current, i, data) < 0.9 ):
            skip = True
            continue
    newData.append(current) 
    print(f"adding {current["timestamp"]}")
print(newData)

    