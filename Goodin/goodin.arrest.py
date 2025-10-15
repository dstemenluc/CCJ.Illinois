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
                    actor_id = actor.get('ID')
                    actor_role = actor.get('Role')

                    identity = actor.find('Identity')
                    if identity is not None:
                        fullname = identity.get('FullName')
                        gender = identity.get('Gender')
                        ethnicity = identity.get('Ethnicity')
                        dob = identity.get('DateOfBirth')
                    else:
                        fullname = gender = ethnicity = dob = None

                    # Each ArrestData entry
                    litigant = actor.find('LitigantDetails')
                    if litigant is not None:
                        for arrest in litigant.findall('ArrestData'):
                            arrest_data = {
                                'arrest_date': arrest.get('ArrestDate'),
                                'arresting_officer': arrest.get('ArrestingOfficer'),
                                'violation_type': arrest.get('ViolationType'),
                                'action_type': arrest.get('ActionType'),
                                'comment': arrest.get('Comment'),
                                'bond_amount': arrest.get('BondAmount'),
                                'user_date': arrest.get('UserDate'),
                            }

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
