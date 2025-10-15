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
                            charge_code = charge.get('Code')
                            charge_description = charge.get('Description')

                            for disposition in charge.findall('CriminalDisposition'):
                                dispo_code = disposition.get('Code')
                                dispo_description = disposition.get('Description')

                                for sentence in disposition.findall('Sentence'):
                                    sentence_number = sentence.get('Number')
                                    sentence_description = sentence.get('Description')
                                    sentence_code = sentence.get('Code')
                                    sentence_status_code = sentence.get('StatusCode')
                                    sentence_status_desc = sentence.get('StatusDescription')

                                    length = sentence.find('SentenceLength')
                                    sentence_years = length.get('Years') if length is not None else ''
                                    sentence_months = length.get('Months') if length is not None else ''
                                    sentence_days = length.get('Days') if length is not None else ''

                                    record = {
                                        'county': court_name,
                                        'court_ncic': court_ncic,
                                        'case_number': case_number,
                                        'case_last_update': case_last_update,
                                        'charge_count': charge_count,
                                        'offense_date': offense_date,
                                        'charge_code': charge_code,
                                        'charge_description': charge_description,
                                        'disposition_code': dispo_code,
                                        'disposition_description': dispo_description,
                                        'sentence_number': sentence_number,
                                        'sentence_description': sentence_description,
                                        'sentence_code': sentence_code,
                                        'sentence_status_code': sentence_status_code,
                                        'sentence_status_desc': sentence_status_desc,
                                        'sentence_length_years': sentence_years,
                                        'sentence_length_months': sentence_months,
                                        'sentence_length_days': sentence_days
                                    }

                                    records.append(record)

        except Exception as e:
            print(f"⚠️ Error parsing {xml_path}: {e}")

    # Save per-county CSV
    if records:
        df = pd.DataFrame(records)
        output_csv = os.path.join(parent_dir, f"{folder_name}.sentences.csv")
        df.to_csv(output_csv, index=False)
        print(f"✅ Saved sentence CSV for '{folder_name}' with {len(records)} records.")
    else:
        print(f"⚠️ No sentence data found in '{folder_name}'.")

# --- Combine all sentence CSVs into one master file ---
all_data = []
for file in os.listdir(parent_dir):
    if file.endswith('.sentences.csv') and not file.startswith('sentences_all_counties'):
        csv_path = os.path.join(parent_dir, file)
        try:
            df = pd.read_csv(csv_path)
            all_data.append(df)
            print(f"✅ Loaded {file} ({len(df)} rows)")
        except Exception as e:
            print(f"⚠️ Skipped {file}: {e}")

if all_data:
    master_df = pd.concat(all_data, ignore_index=True)
    master_csv = os.path.join(parent_dir, "sentences_all_counties.csv")
    master_df.to_csv(master_csv, index=False)
    print(f"\n🎉 Master sentence CSV saved: {master_csv} ({len(master_df)} total records)")
else:
    print("🚫 No sentence data found in any CSV files. Master CSV not created.")
