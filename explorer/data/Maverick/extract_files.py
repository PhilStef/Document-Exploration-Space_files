import pandas as pd
import json
import openpyxl 
def excel_to_json(input_file, output_file):
    # Read the Excel file
    df = pd.read_excel(input_file)
    print(df.head)
    # Create an empty list to store the JSON data
    json_data = []

    # Process each row in the DataFrame
    # for i, row in df.iterrows():
    #     json_entry = {
    #         "id": str(i + 1),
    #         "title": row[0],
    #         "date": f"{row[2]} {row[3]}",
    #         "column": row[4],
    #         "contents": row[7]
    #     }
    #     json_data.append(json_entry)

    # # Write the JSON data to a file
    # with open(output_file, 'w') as json_file:
    #     json.dump(json_data, json_file, indent=4)

# Example usage
input_file = "explorer\data\Maverick\MData.xlsx"  # Replace with your actual input file path
output_file = "MavOutput.json"  # Replace with your desired output file path
excel_to_json(input_file, output_file)