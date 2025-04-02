import json
import os

def timeInDoc(obj, i, data): 
    """Calculate time spent in a document"""
    i = i+1
    if(i >= len(data) or data[i]["type"] != "mouseleave-doc"):
        return 1000
    print(f"{obj['doc_id']} and {data[i]['doc_id']}   is       {data[i]['timestamp'] - obj['timestamp']}")
    return data[i]["timestamp"] - obj["timestamp"]

def parse_json_file(input_file_path, time_limit=0.75):
    """
    Parse a JSON file to filter data based on specific conditions
    
    Args:
        input_file_path (str): Path to the input JSON file
        time_limit (float): Time limit in seconds for document interactions
        
    Returns:
        list: Filtered data
        str: Path to the output file
    """
    file_name = os.path.basename(input_file_path)
    print(f"Processing file: {file_name}")
    
    # Load the data
    try:
        with open(input_file_path, 'r') as file:
            data = json.load(file)   
            print("File is opened successfully.")
    except IOError as e:
        print(f"Error opening file: {e}")
        return [], ""
    
    newData = [] 
    skip = False
    drag = False
    
    for i, current in enumerate(data):
        if skip:
            skip = False
            continue 
        
        if current["type"] == "drag-end":
            drag = False
            
        if drag:
            continue 
            
        if current["type"] == "drag-start":
            drag = True
            
        if current["type"] == "mouseenter-doc": 
            if timeInDoc(current, i, data) < time_limit:
                skip = True
                continue
                
        print(f"adding {current['type']} {i}") 
        newData.append(current)
    
    print(f"Original data length: {len(data)}")
    print(f"New data length: {len(newData)}")
    
    # Create output path
    current_dir = os.getcwd()
    folder_path = os.path.join(current_dir, "PreparedInteractionLogs", "01-cleaned")
    
    # Create the directory if it doesn't exist
    os.makedirs(folder_path, exist_ok=True)
    
    output_file_path = os.path.join(folder_path, f'parsed_{file_name}')
    
    # Write filtered data to output file
    with open(output_file_path, 'w') as json_file:
        json.dump(newData, json_file, indent=4)
    
    return newData, output_file_path

def main():
    """Main function if you want to run the script directly"""
    logToParse = '4_ac11c30b_interactions.json'
    print(os.getcwd())
    main_file_path = os.path.join('participantLogs',logToParse) 
    results, output_path = parse_json_file(main_file_path)
    print(f"Results saved to: {output_path}")

if __name__ == "__main__":
    main()

#Draggin slowly 
# dragging fast
#Highliting and Searching 
#enter open leave enter close
#Document edges

# 2 or 3 Tasks and the batches for them 



## onlydrag fast was just dragging fast: only the drag was kept
# chs was clicking highlighting and selecting:  nothing changed 
#Scrolled to one doc on edge, stopped and then stopped study: Only kept the one doc I stopped on