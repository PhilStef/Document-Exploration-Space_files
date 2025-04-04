import pandas as pd
import json
import openpyxl 
def excel_to_json(input_file, output_file):
    # Read the Excel file
    df = pd.read_excel(input_file)
    # Create an empty list to store the JSON data
    json_data = []
    prev = (1,0) 
    total = 0 
    weapons = [49,67,68,117,131,132,139,155]
    # Process each row in the DataFrame
    for i, row in df.iterrows(): 
        if i<1 or i > 181:
            continue 
        if((int(row.iloc[0])) not in [2,7,8,13,14,15] and (int(row.iloc[1]) not in (weapons))):
            continue
        # if(int(row.iloc[0]) != prev[0]):
        #     print(f"batch {prev[0]} has {row.iloc[1]- prev[1]} docs") 
        #     prev = (int(row.iloc[0]), row.iloc[1])
        json_entry = {
            "id": str(int(row.iloc[1])),
            "title": row.iloc[4],
            "date": f"{row.iloc[2]} {row.iloc[3]}",
            #180/20 columns
            "column": f"set{2*(total // 15)}",
            "contents": row.iloc[7], 
            "batch" : str(int(row.iloc[0]))
        }
        json_data.append(json_entry)
        print(total//15) 
        total = total + 1
        
    # print(f"batch {prev[0]} has {182- prev[1]} docs") 
   # Write the JSON data to a file
    with open(output_file, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)

# Example usage
input_file = r"C:\\Users\\stefa\\Research\Document-Exploration-Space_files\\explorer\\data\\Maverick\\MData.xlsx"  # Replace with your actual input file path
output_file = "MavOutputWW2.json"  # Replace with your desired output file path
excel_to_json(input_file, output_file)