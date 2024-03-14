"""
For paired-end reads:
python3 sra_accessions.py accession_ids.txt /path/to/download_directory --paired

For single-end reads:
python3 sra_accessions.py accession_ids.txt /path/to/download_directory

"""

import subprocess
import argparse
import os

def download_sra_files(accession_file_path, download_directory):
    """
    Downloads SRA files to a specified directory.

    Parameters:
    - accession_file_path: Path to the file containing SRA accession IDs.
    - download_directory: Directory where SRA files will be downloaded.
    """
    with open(accession_file_path, 'r') as file:
        next(file)  # Skip the header line
        sra_numbers = [line.strip() for line in file if line.strip()]

    for sra_id in sra_numbers:
        print(f"Currently downloading: {sra_id}")
        prefetch_command = ['prefetch', '-O', download_directory, sra_id]
        subprocess.run(prefetch_command, check=True)
        print(f"Download completed for: {sra_id}")

    return sra_numbers

def generate_fastq_files(sra_numbers, download_directory, is_paired):
    """
    Converts downloaded SRA files to FASTQ format.

    Parameters:
    - sra_numbers: List of SRA accession IDs that have been downloaded.
    - download_directory: Directory where SRA files were downloaded and where FASTQ files will be stored.
    - is_paired: Boolean indicating if the sequencing data is paired-end.
    """
    for sra_id in sra_numbers:
        sra_file_path = os.path.join(download_directory, sra_id, f"{sra_id}.sra")
        if not os.path.exists(sra_file_path):
            print(f"File not found: {sra_file_path}, skipping.")
            continue

        print(f"Generating FASTQ for: {sra_id}")
        outdir = os.path.join(download_directory, "fastq")
        os.makedirs(outdir, exist_ok=True)
        
        fastq_dump_command = [
            'fastq-dump', '--outdir', outdir, '--gzip',
            '--skip-technical', '--readids', '--read-filter', 'pass',
            '--dumpbase', '--clip', sra_file_path
        ]
        
        if is_paired:
            fastq_dump_command.append('--split-files')
            print(f"Processing paired-end reads. Output will be split into separate files for each read.")
        else:
            print(f"Processing single-end reads.")
        
        subprocess.run(fastq_dump_command, check=True)
        print(f"FASTQ generation completed for: {sra_id}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Automates downloading SRA files and converting them into FASTQ format.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("accession_file_path", help="Path to the file containing SRA accession IDs")
    parser.add_argument("download_directory", help="Directory where SRA files will be downloaded and FASTQ files stored")
    parser.add_argument("--paired", action='store_true', help="Indicate if the reads are expected to be paired-end")

    args = parser.parse_args()

    sra_numbers = download_sra_files(args.accession_file_path, args.download_directory)
    generate_fastq_files(sra_numbers, args.download_directory, args.paired)

    print("All processes completed.")
