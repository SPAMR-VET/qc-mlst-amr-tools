import json
import csv
import sys
import os

def extract_software_data(json_data, software_name):
    """
    Extract QUAST data from JSON and create a CSV with assembly metrics.
    For "quast", include specific columns and calculate a Filter_N50 based on "N50".
    """
    # Ensure json_data is a dictionary
    if isinstance(json_data, list):
        json_data = next((entry for entry in json_data if "analysis_software_name" in entry and entry["analysis_software_name"] == software_name), None)
    
    if not isinstance(json_data, dict):
        print(f"Invalid JSON format for {software_name} extraction.")
        return
    
    results = json_data.get("results", [])
    extracted_data = []
    headers = [
        "Assembly",
        "contigs_(>=_0_bp)",
        "contigs_(>=_1000_bp)",
        "Total_length_(>=_0_bp)",
        "Total_length_(>=_1000_bp)",
        "contigs",
        "Largest_contig",
        "Total_length",
        "GC",
        "N50",
        "Filter_N50",
        "N90",
        "auN",
        "L50",
        "L90",
        "total_reads",
        "left",
        "right",
        "Mapped",
        "Properly_paired",
        "Avg._coverage_depth",
        "Coverage_>=_1x",
        "N's_per_100_kbp"
    ]
    output_csv_file = f"{software_name}_output.csv"

    for entry in results:
        if "content" in entry and isinstance(entry["content"], list):
            for content_item in entry["content"]:
                n50 = content_item.get("N50", "")
                try:
                    n50_value = float(n50) if n50 else 0
                    filter_n50 = "pass" if n50_value > 20000 else "fail"
                except ValueError:
                    filter_n50 = "fail"  # If the value is non-numeric, consider it as "fail"

                extracted_data.append({
                    "Assembly": content_item.get("Assembly", ""),
                    "contigs_(>=_0_bp)": content_item.get("contigs_(>=_0_bp)", ""),
                    "contigs_(>=_1000_bp)": content_item.get("contigs_(>=_1000_bp)", ""),
                    "Total_length_(>=_0_bp)": content_item.get("Total_length_(>=_0_bp)", ""),
                    "Total_length_(>=_1000_bp)": content_item.get("Total_length_(>=_1000_bp)", ""),
                    "contigs": content_item.get("contigs", ""),
                    "Largest_contig": content_item.get("Largest_contig", ""),
                    "Total_length": content_item.get("Total_length", ""),
                    "GC": content_item.get("GC", ""),
                    "N50": content_item.get("N50", ""),
                    "Filter_N50": filter_n50,
                    "N90": content_item.get("N90", ""),
                    "auN": content_item.get("auN", ""),
                    "L50": content_item.get("L50", ""),
                    "L90": content_item.get("L90", ""),
                    "total_reads": content_item.get("total_reads", ""),
                    "left": content_item.get("left", ""),
                    "right": content_item.get("right", ""),
                    "Mapped": content_item.get("Mapped", ""),
                    "Properly_paired": content_item.get("Properly_paired", ""),
                    "Avg._coverage_depth": content_item.get("Avg._coverage_depth", ""),
                    "Coverage_>=_1x": content_item.get("Coverage_>=_1x", ""),
                    "N's_per_100_kbp": content_item.get("N's_per_100_kbp", "")
                })
    
    with open(output_csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(extracted_data)
    
    print(f"CSV file successfully generated: {output_csv_file}")

def extract_contigs_to_fasta(json_data):
    """
    Extract contigs information from "shovill" and save it as a FASTA file.
    """
    if isinstance(json_data, list):
        json_data = next((entry for entry in json_data if "analysis_software_name" in entry and entry["analysis_software_name"] == "shovill"), None)

    if not isinstance(json_data, dict):
        print("Invalid JSON format for shovill extraction.")
        return

    results = json_data.get("results", [])
    output_fasta_file = "shovill_contigs.fasta"

    with open(output_fasta_file, "w", encoding="utf-8") as f:
        for entry in results:
            if "content" in entry and isinstance(entry["content"], list):
                for content_item in entry["content"]:
                    name = content_item.get("name", "unknown")
                    length = content_item.get("length", "unknown")
                    coverage = content_item.get("coverage", "unknown")
                    sequence = content_item.get("sequence", "")

                    header = f">{name}_{length}_{coverage}"
                    f.write(f"{header}\n{sequence}\n")

    print(f"FASTA file successfully generated: {output_fasta_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py input.json")
        sys.exit(1)

    input_json_file = sys.argv[1]

    try:
        with open(input_json_file, "r", encoding="utf-8") as file:
            json_data = json.load(file)
        extract_software_data(json_data, "quast")
        extract_contigs_to_fasta(json_data)
        sys.exit(0)
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)
