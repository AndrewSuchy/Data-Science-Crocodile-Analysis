#!/usr/bin/env python3
"""
Mapper for Normalization using pandas
"""
import sys
import pandas as pd

def mapper():
    """Extract numeric features for normalization"""
    
    # Read aggregated data from stdin
    df = pd.read_csv(sys.stdin)
    
    # Define numeric features to normalize
    numeric_features = [
        'Mean_Length', 'Std_Length', 'Mean_Weight', 'Std_Weight',
        'Body_Ratio', 'Sexual_Dimorphism', 'Num_Habitats', 'Num_Countries', 'Adult_Ratio'
    ]
    
    # Output each feature value with its name
    for _, row in df.iterrows():
        for feature in numeric_features:
            if feature in row:
                print(f"{feature}\t{row[feature]}")

if __name__ == "__main__":
    mapper()