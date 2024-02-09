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
            '--split-3', '--clip', sra_file_path
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
