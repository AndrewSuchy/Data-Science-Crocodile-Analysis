import pandas as pd
import numpy as np
import sys

def centroid_initialization(input_file, k, output_file):

    df = pd.read_csv(input_file)

    np.random.seed(42)
    centroids = df.sample(n=k, random_state=42)
    
    centroids.to_csv(output_file, index=False)
    
    print(f"Initialized {k} centroids:")
    for i, row in centroids.iterrows():
        print(f"  Centroid {i}: {row['Scientific_Name']}")
    
    print(f"\nCentroids saved to: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 centroid_initialization.py <normalized_data.csv> <k> <output.csv>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    k = int(sys.argv[2])
    output_file = sys.argv[3]
    
    centroid_initialization(input_file, k, output_file)