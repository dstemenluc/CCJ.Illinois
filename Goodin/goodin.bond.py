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

            provider = root.find('Provider')
            court = root.find('Court')
            if court is None:
                continue

            court_name = court.get('Name')

            for case in court.findall('Case'):
                case_number = case.get('Number')

                for actor in case.findall('Actor'):
                    for litigant_details in actor.findall('LitigantDetails'):
                        for payment in litigant_details.findall('Payment'):
                            amount_paid = payment.get('Amount')
                            bond_payment_date = payment.get('ReceivedDate')
                            bond_type = payment.get('TransactionType')
                            bond_code = payment.get('TransactionTypeCode')

                            record = {
                                'case_number': case_number,
                                'county': court_name,
                                'amount_paid': float(amount_paid) if amount_paid else None,
                                'bond_payment_date': bond_payment_date,
                                'bond_type': bond_type,
                                'bond_code': bond_code,
                                'source_file': file
                            }
                            records.append(record)

        except Exception as e:
            print(f"⚠️ Error parsing {xml_path}: {e}")

    # Save per-county CSV
    if records:
        df = pd.DataFrame(records)
        output_csv = os.path.join(parent_dir, f"{folder_name}.payment.csv")
        df.to_csv(output_csv, index=False)
        print(f"✅ Saved CSV for '{folder_name}' with {len(records)} records.")
    else:
        print(f"⚠️ No payment data found in '{folder_name}'.")

# --- Combine all CSVs into one master file ---
all_data = []
for file in os.listdir(parent_dir):
    if file.endswith('payment.csv') and not file.startswith('payment_all_counties'):
        csv_path = os.path.join(parent_dir, file)
        try:
            df = pd.read_csv(csv_path)
            all_data.append(df)
            print(f"✅ Loaded {file} ({len(df)} rows)")
        except Exception as e:
            print(f"⚠️ Skipped {file}: {e}")

if all_data:
    master_df = pd.concat(all_data, ignore_index=True)
    master_csv = os.path.join(parent_dir, "payment_all_counties.csv")
    master_df.to_csv(master_csv, index=False)
    print(f"\n🎉 Master CSV saved: {master_csv} ({len(master_df)} total records)")
else:
    print("🚫 No data found in any CSV files. Master CSV not created.")

