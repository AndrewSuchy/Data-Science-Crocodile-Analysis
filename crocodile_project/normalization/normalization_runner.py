#!/usr/bin/env python3
"""
Runner for Job 2: Normalization MapReduce
"""
import os
import subprocess
import sys

def run_normalization():
    """Run the normalization MapReduce job"""
    
    print("=" * 50)
    print("JOB 2: NORMALIZATION")
    print("=" * 50)
    
    # Define paths
    PROJECT_ROOT = "C:/Users/andre/OneDrive/DataSci/crocodile_project"
    OUTPUT_DIR = f"{PROJECT_ROOT}/output"
    NORMALIZATION_DIR = f"{PROJECT_ROOT}/normalization"
    
    # HDFS paths
    HDFS_INPUT = "/user/hadoop/species_features.csv"
    HDFS_OUTPUT = "/user/hadoop/normalized_stats"
    
    # Local files
    MAPPER = f"{NORMALIZATION_DIR}/normalization_mapper.py"
    REDUCER = f"{NORMALIZATION_DIR}/normalization_reducer.py"
    APPLY_NORM = f"{NORMALIZATION_DIR}/apply_normalization.py"
    INPUT_FILE = f"{OUTPUT_DIR}/species_features.csv"
    OUTPUT_FILE = f"{OUTPUT_DIR}/species_normalized.csv"
    
    # Check if input exists
    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: Input file not found: {INPUT_FILE}")
        print("Please run aggregation_runner.py first!")
        sys.exit(1)
    
    # Remove previous HDFS output
    print("\nCleaning previous output...")
    subprocess.run(f'hdfs dfs -rm -r {HDFS_OUTPUT}', 
                   stderr=subprocess.DEVNULL, shell=True)
    
    # Upload species features to HDFS
    print(f"\nUploading data to HDFS: {HDFS_INPUT}")
    result = subprocess.run(f'hdfs dfs -put -f "{INPUT_FILE}" {HDFS_INPUT}', shell=True)
    if result.returncode != 0:
        print("ERROR: Failed to upload data to HDFS")
        sys.exit(1)
    
    # Get Hadoop home
    hadoop_home = os.environ.get('HADOOP_HOME')
    if not hadoop_home:
        print("ERROR: HADOOP_HOME not set")
        sys.exit(1)
    
    streaming_jar = f"{hadoop_home}/share/hadoop/tools/lib/hadoop-streaming-3.3.6.jar"
    
    # Run MapReduce job to compute statistics - FIXED: Use "py" instead of "python"
    print("\nComputing normalization statistics...")
    cmd = f'hadoop jar "{streaming_jar}" -input {HDFS_INPUT} -output {HDFS_OUTPUT} -mapper "py {MAPPER}" -reducer "py {REDUCER}" -file "{MAPPER}" -file "{REDUCER}"'
    result = subprocess.run(cmd, shell=True)
    
    if result.returncode != 0:
        print("ERROR: MapReduce job failed")
        sys.exit(1)
    
    # Download statistics from HDFS
    print("\nDownloading normalization statistics...")
    stats_file = f"{NORMALIZATION_DIR}/normalization_stats.txt"
    result = subprocess.run(f'hdfs dfs -get {HDFS_OUTPUT}/part-00000 "{stats_file}"', shell=True)
    
    if result.returncode != 0:
        print("ERROR: Failed to download statistics from HDFS")
        sys.exit(1)
    
    # Apply normalization locally - FIXED: Use "py" instead of "python"
    print("\nApplying z-score normalization...")
    result = subprocess.run(f'py "{APPLY_NORM}" "{INPUT_FILE}" "{stats_file}" "{OUTPUT_FILE}"', shell=True)
    
    if result.returncode != 0:
        print("ERROR: Normalization application failed")
        sys.exit(1)
    
    # Clean up temp file
    os.remove(stats_file)
    
    print(f"\n{'=' * 50}")
    print("Job 2 complete!")
    print(f"Output: {OUTPUT_FILE}")
    print(f"{'=' * 50}\n")

if __name__ == "__main__":
    run_normalization()