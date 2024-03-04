"""
This script facilitates the alignment of FASTQ reads to a reference genome using the STAR aligner. It is designed to handle
both compressed (gzip) and uncompressed FASTQ files, automatically decompressing them if necessary. The script processes each
pair of FASTQ files (assuming paired-end reads), aligns them to the specified genome using STAR, and outputs the results in a
structured directory format, with each set of results placed in a subdirectory named after the accession ID extracted from the
FASTQ file names.

The script takes four command-line arguments:
- The path to the STAR executable (--star-path).
- The path to the STAR genome index directory (--genomeDir).
- One or more paths to the input FASTQ files (--readFilesIn). These can be either compressed (with a .gz extension) or uncompressed.
- The base directory for saving the alignment results (--output-dir). The script creates this directory if it does not exist.

Each pair of FASTQ files is aligned in turn, and the output (including BAM files and any other specified STAR output) is saved
in a subdirectory of the output directory, named according to the accession ID derived from the first file of each pair. This
structure makes it easy to associate output files with their corresponding input files and simplifies downstream analysis.

The script employs logging to provide real-time feedback on its progress and to report any errors encountered during
decompression or alignment. This feedback can be useful for troubleshooting and ensuring that the alignment process completes
successfully.

Usage:
    python alignment.py --star-path /path/to/STAR \
                                    --genomeDir /path/to/genomeIndex \
                                    --readFilesIn /path/to/read1.fastq /path/to/read2.fastq ... \
                                    --output-dir /path/to/outputDirectory

Requirements:
- Python 3
- STAR aligner installed and accessible from the command line
- samtools (if working with compressed FASTQ files)
"""

import subprocess
import argparse
import os
import logging
import glob

def decompress_files(files):
    """Decompress .gz FASTQ files if necessary."""
    decompressed_files = []
    for file in files:
        if file.endswith('.gz'):
            decompressed_file = file[:-3]  # Remove '.gz' extension
            if not os.path.exists(decompressed_file):
                logging.info(f"Decompressing file: {file}")
                try:
                    subprocess.run(['gzip', '-d', file], check=True)
                    decompressed_files.append(decompressed_file)
                except subprocess.CalledProcessError as e:
                    logging.error(f"Failed to decompress file {file}: {e}")
            else:
                logging.info(f"File already decompressed: {decompressed_file}")
                decompressed_files.append(decompressed_file)
        else:
            decompressed_files.append(file)
    return decompressed_files

def find_bam_file(directory):
    """Find the first BAM file in the given directory."""
    bam_files = glob.glob(os.path.join(directory, '*.bam'))
    if bam_files:
        return bam_files[0]  # Return the first BAM file found
    else:
        return None

def write_bam_manifest(manifest_data, output_dir_base):
    """Append BAM file details to the manifest."""
    manifest_path = os.path.join(output_dir_base, 'bam_manifest.txt')
    with open(manifest_path, 'a') as manifest_file:
        for accession_id, bam_path in manifest_data:
            manifest_file.write(f"{accession_id}\t{bam_path}\n")
    logging.info("BAM manifest updated with new entries.")

def align_reads(star_path, genome_dir, read_files, output_dir_base):
    read_files = decompress_files(read_files)
    
    if not os.path.exists(output_dir_base):
        os.makedirs(output_dir_base)
       
    bam_manifest_data = []
    
    for i in range(0, len(read_files), 2):  # Assuming pairs of read files
        pair = read_files[i:i+2]
        accession_id = os.path.basename(pair[0]).split('_')[0]
        
        output_subdir = os.path.join(output_dir_base, accession_id)
        if not os.path.exists(output_subdir):
            os.makedirs(output_subdir)
        
        star_command = [
            star_path,
            '--runThreadN', '10',
            '--genomeDir', genome_dir,
            '--readFilesIn'
        ] + pair + [
            '--outFileNamePrefix', os.path.join(output_subdir, ''),
            '--outSAMtype', 'BAM', 'SortedByCoordinate'
        ]
        
        logging.info(f"Running STAR alignment for {accession_id} with command: {' '.join(star_command)}")
        try:
            subprocess.run(star_command, check=True)
            bam_file_path = find_bam_file(output_subdir)
            if bam_file_path:
                bam_manifest_data.append((accession_id, bam_file_path))
            else:
                logging.error(f"No BAM file found for {accession_id} in {output_subdir}")
        except subprocess.CalledProcessError as e:
            logging.error(f"STAR alignment for {accession_id} failed: {e}")
    
    write_bam_manifest(bam_manifest_data, output_dir_base)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    parser = argparse.ArgumentParser(description="Align FASTQ reads to the reference genome using STAR.")
    parser.add_argument("--star-path", required=True, help="Path to the STAR executable")
    parser.add_argument("--genomeDir", required=True, help="Path to the STAR genome index directory")
    parser.add_argument("--readFilesIn", nargs='+', required=True, help="Paths to input FASTQ files")
    parser.add_argument("--output-dir", required=True, help="Base directory for saving the alignment results")
    
    args = parser.parse_args()
    
    align_reads(args.star_path, args.genomeDir, args.readFilesIn, args.output_dir)
    
    logging.info("Alignment completed.")
