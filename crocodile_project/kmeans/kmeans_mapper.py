import sys
import pandas as pd
import numpy as np

centroids = None

def load_centroids(centroid_file):
    global centroids
    centroids = pd.read_csv(centroid_file)
    print(f"Loaded {len(centroids)} centroids", file=sys.stderr)

def euclidean_distance(point, centroid):
    features = [
        'Mean_Length_Norm', 'Std_Length_Norm', 'Mean_Weight_Norm', 'Std_Weight_Norm',
        'Body_Ratio_Norm', 'Sexual_Dimorphism_Norm', 'Num_Habitats_Norm',
        'Num_Countries_Norm', 'Adult_Ratio_Norm'
    ]
    
    point_vec = np.array([point[f] for f in features])
    centroid_vec = np.array([centroid[f] for f in features])
    
    return np.linalg.norm(point_vec - centroid_vec)

def find_nearest_centroid(point):
    distances = [euclidean_distance(point, centroids.iloc[i]) for i in range(len(centroids))]
    return np.argmin(distances)

def mapper():
    df = pd.read_csv(sys.stdin)
    
    for _, row in df.iterrows():
        try:

            centroid_id = find_nearest_centroid(row)

            features = ','.join([str(row[col]) for col in row.index])
            print(f"{centroid_id}\t{features}")
            
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            continue

if __name__ == "__main__":
    if len(sys.argv) > 1:
        load_centroids(sys.argv[1])
    else:
        load_centroids('centroids.csv')
    
    mapper()