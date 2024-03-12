import subprocess
import argparse

def run_mesa_bam_to_junc_bed(manifest, annotations, genome, output_prefix, n_threads):
    """Executes the mesa bam_to_junc_bed command with specified arguments."""
    command = [
        'mesa', 'bam_to_junc_bed',
        '-m', manifest,
        '-a', annotations,
        '-g', genome,
        '-o', output_prefix,
        '-n', str(n_threads)
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Command executed successfully. Output files are prefixed with: {output_prefix}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute command: {e}")

def run_mesa_quant(manifest, output_prefix):
    """Executes the mesa quant command with the specified manifest file."""
    command = [
        'mesa', 'quant',
        '-m', manifest,
        '-o', output_prefix
    ]

    try:
        subprocess.run(command, check=True)
        print(f"mesa quant command executed successfully. Output files are prefixed with: {output_prefix}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute mesa quant command: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run mesa bam_to_junc_bed and quant directly from command line arguments.")
    parser.add_argument("--genome", required=True, help="Path to the genome FASTA file")
    parser.add_argument("--manifest", required=True, help="Path to the manifest file")
    parser.add_argument("--annotations", required=True, help="Path to the annotations GTF file")
    parser.add_argument("--output-prefix", required=True, help="Output prefix for the .bed files")
    parser.add_argument("--n-threads", type=int, default=10, help="Number of threads")

    args = parser.parse_args()

    # Always run bam_to_junc_bed
    run_mesa_bam_to_junc_bed(args.manifest, args.annotations, args.genome, args.output_prefix, args.n_threads)


    quant_manifest = f"{args.output_prefix}_manifest.txt"
    run_mesa_quant(quant_manifest, args.output_prefix)
