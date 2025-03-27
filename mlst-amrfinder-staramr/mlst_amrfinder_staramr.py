import json
import csv
import sys

def generate_csv_from_json(json_data):
    """
    Parse the JSON and generate CSV files based on the analysis_software_name Abricate, AMRfinder plus and STARamr.
    Additionally, extract and process the 'mlst_file' content into its own CSV.
    """
    for entry in json_data:
        analysis_software = entry.get("analysis_software_name", "unknown")
        results = entry.get("results", [])

        if results:
            csv_file = f"{analysis_software}_output.csv"
            extracted_data = []
            headers = []

            for result in results:
                if result.get("name") == "mlst_file":
                    mlst_file_path = "mlst.csv"
                    mlst_content = result.get("content", [])
                    mlst_headers = ["Isolate ID", "Scheme", "Sequence Type", "Locus"]

                    # Write the MLST CSV file
                    if mlst_content:
                        with open(mlst_file_path, "w", newline="", encoding="utf-8") as f:
                            writer = csv.DictWriter(f, fieldnames=mlst_headers)
                            writer.writeheader()
                            for row in mlst_content:
                                writer.writerow({
                                    "Isolate ID": row.get("Isolate ID", ""),
                                    "Scheme": row.get("Scheme", ""),
                                    "Sequence Type": row.get("Sequence Type", ""),
                                    "Locus": "; ".join(row.get("Locus", []))
                                })

                        print(f"MLST CSV file successfully generated: {mlst_file_path}")

                if "content" in result and isinstance(result["content"], list):
                    for content_item in result["content"]:
                        extracted_data.append(content_item)
                        for key in content_item.keys():
                            if key not in headers:
                                headers.append(key)  # Maintain the original order of the JSON keys

            # Write the CSV file if there is data
            if extracted_data:
                with open(csv_file, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=headers)
                    writer.writeheader()
                    for row in extracted_data:
                        writer.writerow({key: row.get(key, "") for key in headers})

                print(f"CSV file successfully generated: {csv_file}")
            else:
                print(f"No content found for {analysis_software}.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py input.json")
        sys.exit(1)

    input_json_file = sys.argv[1]

    try:
        with open(input_json_file, "r", encoding="utf-8") as file:
            json_data = json.load(file)
        generate_csv_from_json(json_data)
        sys.exit(0)
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)
