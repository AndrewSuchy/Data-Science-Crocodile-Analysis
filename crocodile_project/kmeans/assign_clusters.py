import pandas as pd
import numpy as np
import sys

def euclidean_distance(point, centroid):

    features = [
        'Mean_Length_Norm', 'Std_Length_Norm', 'Mean_Weight_Norm', 'Std_Weight_Norm',
        'Body_Ratio_Norm', 'Sexual_Dimorphism_Norm', 'Num_Habitats_Norm',
        'Num_Countries_Norm', 'Adult_Ratio_Norm'
    ]
    
    point_vec = np.array([point[f] for f in features])
    centroid_vec = np.array([centroid[f] for f in features])
    
    return np.linalg.norm(point_vec - centroid_vec)

def assign_clusters(data_file, centroid_file, output_file):

    df = pd.read_csv(data_file)
    centroids = pd.read_csv(centroid_file)
    
    print(f"Loaded {len(centroids)} centroids")
    print(f"Assigning {len(df)} species to clusters...")

    cluster_ids = []
    distances = []
    
    for _, row in df.iterrows():
        dists = [euclidean_distance(row, centroids.iloc[i]) for i in range(len(centroids))]
        nearest_cluster = np.argmin(dists)
        min_distance = dists[nearest_cluster]
        
        cluster_ids.append(nearest_cluster)
        distances.append(min_distance)

    df['Cluster_ID'] = cluster_ids
    df['Distance_to_Centroid'] = distances

    df.to_csv(output_file, index=False)
    
    print(f"Cluster assignments saved to: {output_file}")

    print("\nCluster Summary:")
    cluster_summary = df.groupby('Cluster_ID').size()
    for cluster_id, count in cluster_summary.items():
        print(f"  Cluster {cluster_id}: {count} species")

    print("\nConservation Status by Cluster:")
    for cluster_id in sorted(df['Cluster_ID'].unique()):
        cluster_data = df[df['Cluster_ID'] == cluster_id]
        print(f"\n  Cluster {cluster_id}:")
        status_counts = cluster_data['Conservation_Status'].value_counts()
        for status, count in status_counts.items():
            print(f"    {status}: {count}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 assign_clusters.py <normalized_data.csv> <final_centroids.csv> <output.csv>")
        sys.exit(1)
    
    assign_clusters(sys.argv[1], sys.argv[2], sys.argv[3])