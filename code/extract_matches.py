import json
import glob
import csv

output = []

# Adjust this if your JSON files are not in the current directory
for file in glob.glob("/Users/saral/Documents/cricket/cricsheet/all_json/nepal/*.json"):
    try:
        with open(file, "r") as f:
            data = json.load(f)
            print(f"Processing {file}...")
            # Ensure it's a list or make it iterable
            records = data if isinstance(data, list) else [data]

            for record in records:
                mt = record.get("match_type")
                if mt in ["ODM", "ODI"]:
                    match_type_number = record.get("match_type_type_number")
                    output.append({
                        "filename": file,
                        "match_type": mt,
                        "match_type_number": match_type_number
                    })

    except Exception as e:
        print(f"Error processing {file}: {e}")

# Write to CSV
with open("match_type_output.csv", "w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["filename", "match_type", "match_type_number"])
    writer.writeheader()
    writer.writerows(output)
