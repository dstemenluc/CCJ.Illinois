import os
import xml.etree.ElementTree as ET
import pandas as pd

# Set parent directory containing county folders
parent_dir = '/Users/donstemen/Desktop/LoyolaPreTrial_20250917-1040'

# Loop through county folders
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

            # Get provider and court info
            court = root.find('Court')
            if court is None:
                continue

            court_name = court.get('Name', '')

            # Iterate through cases
            for case in court.findall('Case'):
                case_number = case.get('Number', '')

                for actor in case.findall('Actor'):
                    litigant_details = actor.find('LitigantDetails')
                    if litigant_details is None:
                        continue

                    # Iterate through all counts
                    for count in litigant_details.findall('Count'):
                        charge_count = count.get('Number', '')
                        charge_offense_date = count.get('OffenseDate', '')

                        # Iterate through all charges within each count
                        for charge in count.findall('Charge'):
                            record = {
                                'case_number': case_number,
                                'county': court_name,
                                'charge_count': charge_count,
                                'charge_offense_date': charge_offense_date,
                                'chargeType': charge.get('Type', ''),
                                'chargeOffenseType': charge.get('OffenseType', ''),
                                'chargeNumber': charge.get('Number', ''),
                                'chargeStatus': charge.get('Status', ''),
                                'chargeCode': charge.get('Code', ''),
                                'chargeDescription': charge.get('Description', ''),
                                'chargeQualifier': charge.get('Qualifier', ''),
                                'chargeStatuteReference': charge.get('StatuteReference', ''),
                                'chargeClass': charge.get('Class', ''),
                            }
                            records.append(record)

        except Exception as e:
            print(f"⚠️ Error parsing {xml_path}: {e}")

    # Save per-county CSV
    if records:
        df = pd.DataFrame(records)
        output_csv = os.path.join(parent_dir, f"{folder_name}.charge.csv")
        df.to_csv(output_csv, index=False)
        print(f"✅ Saved CSV for '{folder_name}' with {len(records)} records.")
    else:
        print(f"⚠️ No data found in '{folder_name}'.")

# --- Combine all CSVs into one master file ---
all_data = []
for file in os.listdir(parent_dir):
    if file.endswith('charge.csv') and not file.startswith('charge_all_counties'):
        csv_path = os.path.join(parent_dir, file)
        try:
            df = pd.read_csv(csv_path)
            all_data.append(df)
            print(f"✅ Loaded {file} ({len(df)} rows)")
        except Exception as e:
            print(f"⚠️ Skipped {file}: {e}")

if all_data:
    master_df = pd.concat(all_data, ignore_index=True)
    master_csv = os.path.join(parent_dir, "charge_all_counties.csv")
    master_df.to_csv(master_csv, index=False)
    print(f"\n🎉 Master CSV saved: {master_csv} ({len(master_df)} total records)")
else:
    print("🚫 No data found in any CSV files. Master CSV not created.")