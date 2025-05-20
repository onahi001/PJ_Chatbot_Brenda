import json
import os

def merge_json_dicts(input_folder, output_file):
    merged_data = []
    
    # Iterate through all JSON files in the directory
    for file_name in os.listdir(input_folder):
        if file_name.endswith(".json"): #Processes only JSON files
            file_path = os.path.join(input_folder, file_name)
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    if isinstance(data, list): #Append lists
                        merged_data.extend(data)
                    else: #Append dictionaries as separate items
                        merged_data.append(data)
                except json.JSONDecodeError as e:
                    print(f'Error reading {file_name}: {e}')
    
    # write merged JSON to the output file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(merged_data, f, indent=4)



input_folder = "data/Parables of Jesus"
output_file = "data/Parables of Jesus/Parables of Jesus.json"
merge_json_dicts(input_folder, output_file)