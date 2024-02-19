"""
This script automates the process of downloading sequence read archive (SRA) files based on a list of accession IDs and
converting them into FASTQ format. It is designed to facilitate large-scale data retrieval and conversion for bioinformatics
analyses, streamlining the initial steps of data preparation.

The script operates in two main stages:
1. Downloading SRA files: It reads a list of SRA accession IDs from a specified file (skipping the header line), and uses the
   `prefetch` command from the SRA Toolkit to download each SRA file into a designated download directory.
2. Generating FASTQ files: For each downloaded SRA file, the script then uses the `fastq-dump` command, also from the SRA
   Toolkit, to convert SRA files into compressed FASTQ files. It supports splitting paired-end reads into separate files and
   applies several other options to optimize the output for subsequent analysis.

Requirements:
- A file containing SRA accession IDs, one per line with a header line.
- The SRA Toolkit installed and available in the system's PATH. This includes both `prefetch` and `fastq-dump` utilities.

Usage:
    python this_script.py <accession_file_path> <download_directory>

Where:
- `<accession_file_path>` is the path to the text file containing SRA accession IDs to download. The file should contain one
  ID per line, with the first line being a header that will be skipped by the script.
- `<download_directory>` is the path to the directory where SRA files will be downloaded and where the FASTQ files will be
  stored after conversion. The script organizes FASTQ files in a subdirectory within this directory.

Example Command:
    python this_script.py accession_ids.txt /path/to/download_directory

The script prints messages to the console to inform the user of its progress, including the accession ID currently being
processed and the specific commands being executed.

Note: Ensure sufficient disk space is available in the specified download directory, as SRA and FASTQ files can be large.
"""

import subprocess
import argparse
import os

def download_sra_files(accession_file_path, download_directory):
    with open(accession_file_path, 'r') as file:
        next(file)  # Skip the header line
        sra_numbers = [line.strip() for line in file if line.strip()]

    for sra_id in sra_numbers:
        print(f"Currently downloading: {sra_id}")
        prefetch_command = ['prefetch', '-O', download_directory, sra_id]
        print(f"The command used was: {' '.join(prefetch_command)}")
        subprocess.run(prefetch_command, check=True)

    return sra_numbers

def generate_fastq_files(sra_numbers, download_directory):
    for sra_id in sra_numbers:
        sra_file_path = f"{download_directory}/{sra_id}/{sra_id}.sra"
        if not os.path.exists(sra_file_path):
            print(f"File not found: {sra_file_path}")
            continue  # Skip this file and go to the next iteration
        print(f"Generating fastq for: {sra_id}")
        fastq_dump_command = [
            'fastq-dump', '--outdir', f"{download_directory}/fastq", '--gzip',
            '--skip-technical', '--readids', '--read-filter', 'pass', '--dumpbase',
            '--split-files', '--clip', sra_file_path  # Use '--split-files' to split paired reads into separate files
        ]
        print(f"The command used was: {' '.join(fastq_dump_command)}")
        subprocess.run(fastq_dump_command, check=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download SRA files and convert them to FASTQ format.")
    parser.add_argument("accession_file_path", help="Path to the CSV file containing the accession IDs")
    parser.add_argument("download_directory", help="Directory where SRA files will be downloaded and processed")

    args = parser.parse_args()

    sra_numbers = download_sra_files(args.accession_file_path, args.download_directory)
    generate_fastq_files(sra_numbers, args.download_directory)

    print("Process completed.")
