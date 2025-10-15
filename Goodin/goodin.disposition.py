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

            # Basic provider + court info
            provider = root.find('Provider')
            court = root.find('Court')
            if court is None:
                continue

            court_name = court.get('Name')
            court_ncic = court.get('NCIC')

            for case in court.findall('Case'):
                case_number = case.get('Number')
                case_last_update = case.get('LastUpdateDate')

                for actor in case.findall('Actor'):
                    litigant_details = actor.find('LitigantDetails')
                    if litigant_details is None:
                        continue

                    for count in litigant_details.findall('Count'):
                        charge_count = count.get('Number')
                        offense_date = count.get('OffenseDate')
                        for charge in count.findall('Charge'):
                            offense_type = charge.get('OffenseType')
                            charge_class = charge.get('Class')
                            charge_code = charge.get('Code')
                            charge_number = charge.get('Number')
                            charge_description = charge.get('Description')
                            charge_qualifier = charge.get('Qualifier')
                            charge_status = charge.get('Status')
                            charge_statute = charge.get('StatuteReference')
                            charge_type = charge.get('Type')  
                            
                            
                            # fixed name charge_type = charge.get('Type')
                            for disposition in charge.findall('CriminalDisposition'):
                                dispo_code = disposition.get('Code')
                                dispo_description = disposition.get('Description')
                                dispo_number = disposition.get('Number')
                                dispo_date = disposition.get('Qualifier')

            record = {
                'county': court_name,
                'court_ncic': court_ncic,
                'case_number': case_number,
                'case_last_update': case_last_update,
                'charge_count': charge_count,
                'offense_date': offense_date,
                'offense_type': offense_type,
                'charge_class': charge_class,
                'charge_code': charge_code,
                'charge_number': charge_number,
                'charge_description': charge_description,
                'charge_qualifier': charge_qualifier,
                'charge_status': charge_status,
                'charge_statute': charge_statute,
                'charge_type': charge_type,
                'dispo_code': dispo_code,
                'dispo_description': dispo_description,
                'dispo_number': dispo_number,
                'dispo_date': dispo_date
            }
            records.append(record)


        except Exception as e:
            print(f"⚠️ Error parsing {xml_path}: {e}")

    # Save per-county CSV
    if records:
        df = pd.DataFrame(records)
        output_csv = os.path.join(parent_dir, f"{folder_name}.dispo.csv")
        df.to_csv(output_csv, index=False)
        print(f"✅ Saved CSV for '{folder_name}' with {len(records)} records.")
    else:
        print(f"⚠️ No data found in '{folder_name}'.")

# --- Combine all CSVs into one master file ---
all_data = []
for file in os.listdir(parent_dir):
    if file.endswith('dispo.csv') and not file.startswith('dispo_all_counties'):
        csv_path = os.path.join(parent_dir, file)
        try:
            df = pd.read_csv(csv_path)
            all_data.append(df)
            print(f"✅ Loaded {file} ({len(df)} rows)")
        except Exception as e:
            print(f"⚠️ Skipped {file}: {e}")

if all_data:
    master_df = pd.concat(all_data, ignore_index=True)
    master_csv = os.path.join(parent_dir, "dispo_all_counties.csv")
    master_df.to_csv(master_csv, index=False)
    print(f"\n🎉 Master CSV saved: {master_csv} ({len(master_df)} total records)")
else:
    print("🚫 No data found in any CSV files. Master CSV not created.")
