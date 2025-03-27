import json
import csv
import sys
import os

def extract_software_data(json_data, software_name):
    """
    Extract data for a specific software from the JSON input
    
    For "bracken", add a "contamination" column where the value is "pass"
    if fraction_total_reads > 0.6, otherwise "fail".
    
    For "fastp", include only specific columns.
    """
    # Ensure json_data is a dictionary
    if isinstance(json_data, list):
        json_data = next((entry for entry in json_data if "analysis_software_name" in entry and entry["analysis_software_name"] == software_name), None)
    
    if not isinstance(json_data, dict):
        print(f"Invalid JSON format for {software_name} extraction.")
        return
    
    results = json_data.get("results", [])
    extracted_data = []
    headers = []  # Use list to collect headers to maintain order
    output_csv_file = f"{software_name}_output.csv"

    # Define specific columns for "fastp"
    fastp_columns = [
        "summary_sequencing",
        "summary_before_filtering_total_reads",
        "summary_before_filtering_total_bases",
        "summary_before_filtering_q20_bases",
        "summary_before_filtering_q30_bases",
        "summary_before_filtering_q20_rate",
        "summary_before_filtering_q30_rate",
        "summary_before_filtering_read1_mean_length",
        "summary_before_filtering_read2_mean_length",
        "summary_before_filtering_gc_content",
        "summary_after_filtering_total_reads",
        "summary_after_filtering_total_bases",
        "summary_after_filtering_q20_bases",
        "summary_after_filtering_q30_bases",
        "summary_after_filtering_q20_rate",
        "summary_after_filtering_q30_rate",
        "summary_after_filtering_read1_mean_length",
        "summary_after_filtering_read2_mean_length",
        "summary_after_filtering_gc_content",
        "filtering_result_passed_filter_reads",
        "filtering_result_low_quality_reads",
        "filtering_result_too_many_N_reads",
        "filtering_result_too_short_reads",
        "filtering_result_too_long_reads",
        "duplication_rate",
        "insert_size_peak",
    ]

    for entry in results:
        if "content" in entry and isinstance(entry["content"], list):
            for content_item in entry["content"]:
                row_data = {}
                if software_name == "fastp":
                    for key, value in content_item.items():
                        if isinstance(value, dict):
                            for sub_key, sub_value in value.items():
                                if isinstance(sub_value, dict):
                                    for sub_sub_key, sub_sub_value in sub_value.items():
                                        column_name = f"{key}_{sub_key}_{sub_sub_key}"
                                        if column_name in fastp_columns:
                                            row_data[column_name] = sub_sub_value
                                            if column_name not in headers:
                                                headers.append(column_name)
                                else:
                                    column_name = f"{key}_{sub_key}"
                                    if column_name in fastp_columns:
                                        row_data[column_name] = sub_value
                                        if column_name not in headers:
                                            headers.append(column_name)
                        else:
                            if key in fastp_columns:
                                row_data[key] = value
                                if key not in headers:
                                    headers.append(key)
                elif software_name == "bracken":
                    for key, value in content_item.items():
                        if isinstance(value, dict):
                            for sub_key, sub_value in value.items():
                                column_name = f"{key}_{sub_key}"
                                row_data[column_name] = sub_value
                                if column_name not in headers:
                                    headers.append(column_name)
                        else:
                            row_data[key] = value
                            if key not in headers:
                                headers.append(key)

                    # Add contamination column for "bracken"
                    fraction_total_reads = row_data.get("fraction_total_reads", 0)
                    row_data["contamination"] = "pass" if float(fraction_total_reads) > 0.6 else "fail"
                    if "contamination" not in headers:
                        headers.append("contamination")

                extracted_data.append(row_data)
    
    if not extracted_data:
        print(f"No data extracted for {software_name}")
        # Create empty file to prevent Galaxy error
        with open(output_csv_file, "w", newline="", encoding="utf-8") as f:
            f.write("No data available\n")
        return
    
    with open(output_csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(extracted_data)
    
    print(f"CSV file successfully generated: {output_csv_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_software_data.py input.json")
        sys.exit(1)
    
    input_json_file = sys.argv[1]
    
    try:
        with open(input_json_file, "r", encoding="utf-8") as file:
            json_data = json.load(file)
        extract_software_data(json_data, "fastp")
        extract_software_data(json_data, "bracken")
        sys.exit(0)
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)
