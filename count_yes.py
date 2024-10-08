import json
import argparse

# Function to count "Yes", "No", and print other unexpected values in assessments
def count_assessments(file_path):
    print(f"Processing file: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Data loaded: {len(data)} entries")  # Print the number of entries

    yes_count = 0
    no_count = 0
    other_values = []
    
    for entry in data:
        if 'assessment' in entry:
            if entry['assessment'] == 'Yes':
                yes_count += 1
            elif entry['assessment'] == 'No':
                no_count += 1
            else:
                #no_count += 1  # Collect entries with unexpected values
                pass
        else:
            print(f"Missing 'assessment' field in entry: {entry}")
    
    print(f"Yes count: {yes_count}")
    print(f"No count: {no_count}")
    print(f"Entries with unexpected values: {len(other_values)}")
    if other_values:
        print("Entries with unexpected values:")
        for other_entry in other_values:
            print(other_entry)

# Command line argument parsing
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Count Yes and No in assessment fields of a JSON file, print unexpected values.")
    parser.add_argument('file_path', type=str, help="Path to the JSON file")
    
    args = parser.parse_args()
    count_assessments(args.file_path)
