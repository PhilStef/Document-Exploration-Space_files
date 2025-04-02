import json
import os
from datetime import datetime

def augment_data(input_file_path, lookup_file_path="explorer/data/Maverick/augmentedMavOutput_04-01_23-53-38.json"):
    """
    Augment JSON data with additional information from a lookup file
    
    Args:
        input_file_path (str): Path to the input JSON file (cleaned data)
        lookup_file_path (str): Path to the lookup JSON file
        
    Returns:
        list: Augmented data
        str: Path to the output file
    """
    file_name = os.path.basename(input_file_path)
    print(f"Augmenting file: {file_name}")
    
    # Load the main data
    try:
        with open(input_file_path, 'r') as file:
            data = json.load(file)
            print("Input file opened successfully.")
    except IOError as e:
        print(f"Error opening input file: {e}")
        return [], ""
    
    # Load the lookup data
    try:
        with open(lookup_file_path, 'r') as file:
            lookup_data = json.load(file)
            print("Lookup file opened successfully.")
    except IOError as e:
        print(f"Error opening lookup file: {e}")
        return [], ""
    
    # Create a dictionary for faster lookup
    lookup_dict = {item["id"]: item for item in lookup_data}
    # print(lookup_dict)
    
    # Augment the data
    augmented_data = []
    for event in data:
        # print(event["doc_id"])
        # print(type(event["doc_id"])==True)
        # todo check that this is actually working for search events.
        if (type(event["doc_id"])!=list) and "doc_id" in event and event["doc_id"] in lookup_dict:
            # Merge the lookup data into the event
            lookup_info = lookup_dict[event["doc_id"]]
            for key, value in lookup_info.items():
                if key != "id":  # Skip id to avoid duplication
                    event[key] = value
            print(f"Augmented event with ID: {event['doc_id']}")
        
        augmented_data.append(event)
    
    # Create output path
    current_dir = os.getcwd()
    folder_path = os.path.join(current_dir, "PreparedInteractionLogs", "02-augmented")

    # Create the directory if it doesn't exist
    os.makedirs(folder_path, exist_ok=True)
    timestamp = datetime.now().strftime('%m-%d_%H-%M-%S')
    output_file_path = os.path.join(folder_path, f'augmented_{file_name}_{timestamp}.json')
    
    # Write augmented data to output file
    with open(output_file_path, 'w') as json_file:
        json.dump(augmented_data, json_file, indent=4)
    
    return augmented_data, output_file_path

def main():
    """Main function if you want to run the script directly"""
    logToAugment = 'parsed_4_ac11c30b_interactions.json'
    main_file_path = os.path.join("PreparedInteractionLogs", "01-cleaned",logToAugment) 
    results, output_path = augment_data(main_file_path)
    print(f"Results saved to: {output_path}")

if __name__ == "__main__":
    main()