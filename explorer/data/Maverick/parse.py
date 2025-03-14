import json

def process_json(filename, func):
    with open(filename, "r") as file:
        data = json.load(file)  
    
    my_function(data)  

def my_function(data): 
    count = 0
    for i, item in enumerate(data, start=1):
        if("Mustard" in item["contents"] or item["title"] is "Mustard"):

            print(f"Document {count}")
            count = count +1

# Usage
process_json(r"C:\\Users\\stefa\\Research\Document-Exploration-Space_files\\explorer\\data\\Maverick\\MavOutput.json", my_function)
