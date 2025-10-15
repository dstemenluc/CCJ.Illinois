import os
import xml.etree.ElementTree as ET
import pandas as pd

# Set the parent directory containing county folders
parent_dir = '/Users/donstemen/Desktop/LoyolaPreTrial_20250917-1040'

# Loop through each county folder
for folder_name in os.listdir(parent_dir):
    folder_path = os.path.join(parent_dir, folder_name)
    if not os.path.isdir(folder_path):
        continue

    records = []

    for file in os.listdir(folder_path):
        if not file.endswith('.xml'):
            continue

        xml_path = os.path.join(folder_path, file)

        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            court = root.find('Court')
            if court is None:
                continue

            court_name = court.get('Name')
            court_ncic = court.get('NCIC')

            for case in court.findall('Case'):
                case_number = case.get('Number')

                for entry in case.findall('Entry'):
                    entry_date = entry.get('Date')
                    entry_text = entry.get('Text')

                    records.append({
                        'county': court_name,
                        'court_ncic': court_ncic,
                        'case_number': case_number,
                        'entry_date': entry_date,
                        'entry_text': entry_text
                    })

        except Exception as e:
            print(f"⚠️ Error parsing {xml_path}: {e}")

    # Save per-county CSV
    if records:
        df = pd.DataFrame(records)
        output_csv = os.path.join(parent_dir, f"{folder_name}.entries.csv")
        df.to_csv(output_csv, index=False)
        print(f"✅ Saved entry CSV for '{folder_name}' with {len(records)} records.")
    else:
        print(f"⚠️ No entry data found in '{folder_name}'.")

# --- Combine all entry CSVs into one master file ---
all_data = []
for file in os.listdir(parent_dir):
    if file.endswith('.entries.csv') and not file.startswith('entries_all_counties'):
        csv_path = os.path.join(parent_dir, file)
        try:
            df = pd.read_csv(csv_path)
            all_data.append(df)
            print(f"✅ Loaded {file} ({len(df)} rows)")
        except Exception as e:
            print(f"⚠️ Skipped {file}: {e}")

if all_data:
    master_df = pd.concat(all_data, ignore_index=True)
    master_csv = os.path.join(parent_dir, "entries_all_counties.csv")
    master_df.to_csv(master_csv, index=False)
    print(f"\n🎉 Master entry CSV saved: {master_csv} ({len(master_df)} total records)")
else:
    print("🚫 No entry data found in any CSV files. Master CSV not created.")
