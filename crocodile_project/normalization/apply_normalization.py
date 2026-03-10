#!/usr/bin/env python3
"""
Apply z-score normalization using pandas
"""
import pandas as pd
import numpy as np
import sys

def apply_normalization(species_file, stats_file, output_file):
    """Apply z-score normalization: z = (x - mean) / std"""
    
    # Read normalization statistics from reducer output
    stats_df = pd.read_csv(stats_file, sep='\t', header=None, names=['feature', 'mean', 'std'])
    stats = stats_df.set_index('feature').to_dict('index')
    
    print(f"Loaded statistics for {len(stats)} features")
    
    # Read species aggregated data
    df = pd.read_csv(species_file)
    
    # Map original columns to normalized column names
    feature_mapping = {
        'Mean_Length': 'Mean_Length_Norm',
        'Std_Length': 'Std_Length_Norm',
        'Mean_Weight': 'Mean_Weight_Norm',
        'Std_Weight': 'Std_Weight_Norm',
        'Body_Ratio': 'Body_Ratio_Norm',  # CHANGED FROM BCI
        'Sexual_Dimorphism': 'Sexual_Dimorphism_Norm',
        'Num_Habitats': 'Num_Habitats_Norm',
        'Num_Countries': 'Num_Countries_Norm',
        'Adult_Ratio': 'Adult_Ratio_Norm'
    }
    
    # Calculate normalized values using z-score formula
    for original_col, norm_col in feature_mapping.items():
        if original_col in df.columns and original_col in stats:
            mean = stats[original_col]['mean']
            std = stats[original_col]['std']
            df[norm_col] = (df[original_col] - mean) / std
        else:
            print(f"Warning: {original_col} not found")
    
    # Select columns for output
    output_cols = [
        'Scientific_Name',
        'Mean_Length_Norm',
        'Std_Length_Norm',
        'Mean_Weight_Norm',
        'Std_Weight_Norm',
        'Body_Ratio_Norm',  # CHANGED FROM BCI_Norm
        'Sexual_Dimorphism_Norm',
        'Num_Habitats_Norm',
        'Num_Countries_Norm',
        'Conservation_Status',
        'Adult_Ratio_Norm',
        'Observation_Count'
    ]
    
    df_normalized = df[output_cols]
    
    # Save normalized data to output file
    df_normalized.to_csv(output_file, index=False)
    
    print(f"Normalized data written to: {output_file}")
    print(f"Shape: {df_normalized.shape}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 apply_normalization.py <species_features.csv> <normalization_stats.txt> <output.csv>")
        sys.exit(1)
    
    apply_normalization(sys.argv[1], sys.argv[2], sys.argv[3])