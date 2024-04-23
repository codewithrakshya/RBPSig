"""
Script to filter pairwise Fisher results and allPS data based on dynamic group comparisons.

To run this script from the command line, use:
python filter_data.py --output-prefix "/path/to/your/output"

Where '/path/to/your/output' is the base path that will be used to generate the names of the input and output files.
"""

import pandas as pd
import argparse

def filter_data(input_file, manifest_file, output_file):
    manifest = pd.read_csv(manifest_file, sep='\t', header=None, names=['ID', 'Path', 'RBP', 'Type'])
    id_to_type = dict(zip(manifest['ID'], manifest['Type']))

    df = pd.read_csv(input_file, sep='\t')

    def is_valid_comparison(col):
        if "_" not in col:
            return False
        id1, id2 = col.split('_')
        return id_to_type.get(id1) != id_to_type.get(id2)  # Compare different groups

    valid_columns = [col for col in df.columns if is_valid_comparison(col)]
    valid_columns.insert(0, 'clusterID')  # Ensure clusterID is included

    filtered_df = df[valid_columns]

    # filtering condition for values less than 0.05
    condition = (filtered_df.loc[:, filtered_df.columns != 'clusterID'] < 0.05).all(axis=1)
    final_df = filtered_df[condition]

    final_df.to_csv(output_file, sep='\t', index=False)
    print(f'Filtered data saved to {output_file}')

    return final_df['clusterID'].tolist()

def filter_allPS(input_file, significant_clusters, output_file):
    df = pd.read_csv(input_file, sep='\t')

    filtered_df = df[df['cluster'].isin(significant_clusters)]

    filtered_df.to_csv(output_file, sep='\t', index=False)
    print(f'Filtered _allPS data saved to {output_file}')

def main(output_prefix):
    input_file = f"{output_prefix}_pairwiseFisherResults.tsv"
    manifest_file = f"{output_prefix}_manifest.txt"
    output_file = f"{output_prefix}_filteredResults.tsv"
    allPS_file = f"{output_prefix}_allPS.tsv"
    allPS_output_file = f"{output_prefix}_filteredAllPS.tsv"

    significant_clusters = filter_data(input_file, manifest_file, output_file)
    filter_allPS(allPS_file, significant_clusters, allPS_output_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter pairwise Fisher results based on dynamic group comparisons.")
    parser.add_argument("--output-prefix", required=True, help="Base path for input/output files")
    
    args = parser.parse_args()
    main(args.output_prefix)
