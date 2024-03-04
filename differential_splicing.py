import argparse
import subprocess

def parse_arguments():
    parser = argparse.ArgumentParser(description='Process files for genomic analysis.')
    parser.add_argument('-g', '--genome', required=True, help='Path to the genome file')
    parser.add_argument('-m', '--manifest', required=True, help='Path to the manifest file')
    parser.add_argument('-a', '--annotations', required=True, help='Path to the annotations file')
    parser.add_argument('-o', '--output_prefix', required=True, help='Output prefix for files')
    return parser.parse_args()

def bam_to_junc_bed(genome, manifest, annotations, output_prefix):
    command = f"mesa bam_to_junc_bed -m '{manifest}' -a '{annotations}' -g '{genome}' -o '{output_prefix}' -n 10"
    print("Running bam_to_junc_bed command:", command)
    try:
        subprocess.run(command, shell=True, check=True)
        print("bam_to_junc_bed command executed successfully.")
    except subprocess.CalledProcessError as e:
        print("Failed to execute bam_to_junc_bed command:", e)
        raise

def quant(output_prefix):

    command = f"mesa quant -i '{output_prefix}.txt' -o '{output_prefix}_quant_output'"
    print("Running quant command:", command)
    try:
        subprocess.run(command, shell=True, check=True)
        print("Quant command executed successfully.")
    except subprocess.CalledProcessError as e:
        print("Failed to execute quant command:", e)
        raise

def main():
    args = parse_arguments()
    try:
        bam_to_junc_bed(args.genome, args.manifest, args.annotations, args.output_prefix)
        quant(args.output_prefix)
    except Exception as e:
        print(f"An error occurred during processing: {e}")

if __name__ == "__main__":
    main()
