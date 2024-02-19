"""
This script automates the process of performing quality control (QC) on BAM files using Samtools. 
It is designed to work through a directory structure, find all BAM files, and then run both 
'samtools flagstat' and 'samtools stats' on each found BAM file. The results of these QC checks 
are saved into separate text files corresponding to each BAM file, providing insights into 
the quality of the alignments. The output files are named after the original BAM files with 
the addition of '_flagstat.txt' or '_stats.txt' to distinguish the type of QC results they contain. 

This script is particularly useful for batch processing multiple BAM files, saving time and 
ensuring consistency in the QC process. It requires the path to the base directory where the 
BAM files are located as an input argument, making it flexible for use with different datasets 
or projects. Logging is used to provide feedback on the script's progress and to report any 
errors encountered during execution.

Usage:
    python bam_qc_samtools.py /path/to/bam_files_directory

Where '/path/to/bam_files_directory' is the directory containing the BAM files to be processed.
"""

import subprocess
import argparse
import os
import logging

def run_samtools_qc(bam_file, output_dir):
    # Construct the samtools flagstat command
    flagstat_command = ['samtools', 'flagstat', bam_file]

    # Run samtools flagstat
    logging.info(f"Running samtools flagstat on {bam_file}")
    flagstat_result = subprocess.run(flagstat_command, capture_output=True, text=True)
    if flagstat_result.returncode == 0:
        # Save the flagstat output to a file
        flagstat_output_path = os.path.join(output_dir, os.path.basename(bam_file) + '_flagstat.txt')
        with open(flagstat_output_path, 'w') as f:
            f.write(flagstat_result.stdout)
    else:
        logging.error(f"Failed to run samtools flagstat on {bam_file}")

    # Construct the samtools stats command
    stats_command = ['samtools', 'stats', bam_file]

    # Run samtools stats
    logging.info(f"Running samtools stats on {bam_file}")
    stats_result = subprocess.run(stats_command, capture_output=True, text=True)
    if stats_result.returncode == 0:
        # Save the stats output to a file
        stats_output_path = os.path.join(output_dir, os.path.basename(bam_file) + '_stats.txt')
        with open(stats_output_path, 'w') as f:
            f.write(stats_result.stdout)
    else:
        logging.error(f"Failed to run samtools stats on {bam_file}")

def main(output_dir_base):
    for root, dirs, files in os.walk(output_dir_base):
        for file in files:
            if file.endswith(".bam"):
                bam_file_path = os.path.join(root, file)
                run_samtools_qc(bam_file_path, root)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Run samtools QC on BAM files.")
    parser.add_argument("output_dir_base", help="Base directory for saving the alignment results and where BAM files are located.")
    args = parser.parse_args()
    
    main(args.output_dir_base)
