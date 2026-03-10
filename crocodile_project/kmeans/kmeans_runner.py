#!/usr/bin/env python3
"""
Runner for Job 3: K-Means Clustering MapReduce
"""
import os
import subprocess
import sys

def run_kmeans(k=4, max_iter=10):
    """Run the K-Means clustering MapReduce job"""
    
    print("=" * 50)
    print("JOB 3: K-MEANS CLUSTERING")
    print("=" * 50)
    
    # Define paths
    PROJECT_ROOT = "C:/Users/andre/OneDrive/DataSci/crocodile_project"
    OUTPUT_DIR = f"{PROJECT_ROOT}/output"
    KMEANS_DIR = f"{PROJECT_ROOT}/kmeans"
    
    # HDFS paths
    HDFS_DATA = "/user/hadoop/species_normalized.csv"
    HDFS_CENTROIDS = "/user/hadoop/centroids.csv"
    HDFS_OUTPUT = "/user/hadoop/kmeans_output"
    
    # Local files
    MAPPER = f"{KMEANS_DIR}/kmeans_mapper.py"
    REDUCER = f"{KMEANS_DIR}/kmeans_reducer.py"
    INIT_CENTROIDS = f"{KMEANS_DIR}/centroid_initialization.py"
    ASSIGN_CLUSTERS = f"{KMEANS_DIR}/assign_clusters.py"
    
    INPUT_FILE = f"{OUTPUT_DIR}/species_normalized.csv"
    CENTROIDS_FILE = f"{OUTPUT_DIR}/centroids.csv"
    OUTPUT_FILE = f"{OUTPUT_DIR}/final_clusters.csv"
    
    # Check if input exists
    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: Input file not found: {INPUT_FILE}")
        print("Please run normalization_runner.py first!")
        sys.exit(1)
    
    # Initialize centroids - FIXED: Use "py" instead of "python"
    print(f"\nInitializing {k} random centroids...")
    result = subprocess.run(f'py "{INIT_CENTROIDS}" "{INPUT_FILE}" {k} "{CENTROIDS_FILE}"', shell=True)
    
    if result.returncode != 0:
        print("ERROR: Centroid initialization failed")
        sys.exit(1)
    
    # Get Hadoop home
    hadoop_home = os.environ.get('HADOOP_HOME')
    if not hadoop_home:
        print("ERROR: HADOOP_HOME not set")
        sys.exit(1)
    
    streaming_jar = f"{hadoop_home}/share/hadoop/tools/lib/hadoop-streaming-3.3.6.jar"
    
    # Run K-Means iterations
    for iteration in range(1, max_iter + 1):
        print(f"\nIteration {iteration}/{max_iter}...")
        
        # Remove previous output
        subprocess.run(f'hdfs dfs -rm -r {HDFS_OUTPUT}', 
                       stderr=subprocess.DEVNULL, shell=True)
        
        # Upload data and centroids to HDFS
        subprocess.run(f'hdfs dfs -put -f "{INPUT_FILE}" {HDFS_DATA}', shell=True)
        subprocess.run(f'hdfs dfs -put -f "{CENTROIDS_FILE}" {HDFS_CENTROIDS}', shell=True)
        
        # Run MapReduce job - FIXED: Use "py" instead of "python"
        cmd = f'hadoop jar "{streaming_jar}" -input {HDFS_DATA} -output {HDFS_OUTPUT} -mapper "py {MAPPER}" -reducer "py {REDUCER}" -file "{MAPPER}" -file "{REDUCER}" -cacheFile {HDFS_CENTROIDS}#centroids.csv'
        result = subprocess.run(cmd, shell=True)
        
        if result.returncode != 0:
            print(f"ERROR: K-Means iteration {iteration} failed")
            sys.exit(1)
        
        # Download new centroids
        temp_centroids = f"{KMEANS_DIR}/new_centroids_temp.csv"
        result = subprocess.run(f'hdfs dfs -get {HDFS_OUTPUT}/part-00000 "{temp_centroids}"', shell=True)
        
        if result.returncode != 0:
            print("ERROR: Failed to download new centroids")
            sys.exit(1)
        
        # Add header to new centroids
        header = "Scientific_Name,Mean_Length_Norm,Std_Length_Norm,Mean_Weight_Norm,Std_Weight_Norm,Body_Ratio_Norm,Sexual_Dimorphism_Norm,Num_Habitats_Norm,Num_Countries_Norm,Conservation_Status,Adult_Ratio_Norm,Observation_Count\n"
        
        with open(CENTROIDS_FILE, 'w') as outfile:
            outfile.write(header)
            with open(temp_centroids, 'r') as infile:
                outfile.write(infile.read())
        
        # Clean up temp file
        os.remove(temp_centroids)
    
    # Final cluster assignment - FIXED: Use "py" instead of "python"
    print("\nAssigning final clusters...")
    result = subprocess.run(f'py "{ASSIGN_CLUSTERS}" "{INPUT_FILE}" "{CENTROIDS_FILE}" "{OUTPUT_FILE}"', shell=True)
    
    if result.returncode != 0:
        print("ERROR: Final cluster assignment failed")
        sys.exit(1)
    
    print(f"\n{'=' * 50}")
    print("Job 3 complete!")
    print(f"Output: {OUTPUT_FILE}")
    print(f"{'=' * 50}\n")

if __name__ == "__main__":
    # You can change K and iterations here
    K = 4
    MAX_ITER = 10
    
    run_kmeans(k=K, max_iter=MAX_ITER)