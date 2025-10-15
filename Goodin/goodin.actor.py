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
                    for count in actor.findall('.//Count'):
                        for charge in count.findall('Charge'):
                            offense_type = charge.get('OffenseType')
                            charge_number = charge.get('Number')
                            description = charge.get('Description')
                            description = charge.get('Description')

                for actor in case.findall('Actor'):
                    for count in actor.findall('.//Count'):
                        for charge in count.findall('Charge'):
                            for disposition in charge.findall('CriminalDisposition'):
                            disposition_description = disposition.get('Description')

                            # Handle Sentences (can be multiple)
                            sentences = disposition.findall('Sentence'):
                            for sentence in sentences:
                                sentence_description = sentence.attrib.get('Description')

                                # Get sentence length if it exists
                                length_elem = sentence.find('SentenceLength')
                                if length_elem is not None:
                                    years = length_elem.attrib.get('Years', '0')
                                    months = length_elem.attrib.get('Months', '0')
                                    days = length_elem.attrib.get('Days', '0')
                                    hours = length_elem.attrib.get('Hours', '0')

                                    length_str = f"{years}y {months}m {days}d {hours}h"
                                else:
                                    length_str = sentence.attrib.get('LengthText', '')

                            # Add basic case/actor info
                            record = {
                                'county': court_name,
                                'court_ncic': court_ncic,
                                'case_number': case_number,
                                'case_last_update': case_last_update,
                                'actor_id': actor_id,
                                'actor_role': actor_role,
                                'fullname': fullname,
                                'gender': gender,
                                'ethnicity': ethnicity,
                                'dob': dob,
                                **arrest_data
                            }
                            records.append(record)

        except Exception as e:
            print(f"⚠️ Error parsing {xml_path}: {e}")

    # Save per-county CSV
    if records:
        df = pd.DataFrame(records)
        output_csv = os.path.join(parent_dir, f"{folder_name}.actor.csv")
        df.to_csv(output_csv, index=False)
        print(f"✅ Saved CSV for '{folder_name}' with {len(records)} records.")
    else:
        print(f"⚠️ No data found in '{folder_name}'.")

# --- Combine all CSVs into one master file ---
all_data = []
for file in os.listdir(parent_dir):
    if file.endswith('actor.csv') and not file.startswith('actor_all_counties'):
        csv_path = os.path.join(parent_dir, file)
        try:
            df = pd.read_csv(csv_path)
            all_data.append(df)
            print(f"✅ Loaded {file} ({len(df)} rows)")
        except Exception as e:
            print(f"⚠️ Skipped {file}: {e}")

if all_data:
    master_df = pd.concat(all_data, ignore_index=True)
    master_csv = os.path.join(parent_dir, "actor_all_counties.csv")
    master_df.to_csv(master_csv, index=False)
    print(f"\n🎉 Master CSV saved: {master_csv} ({len(master_df)} total records)")
else:
    print("🚫 No data found in any CSV files. Master CSV not created.")
