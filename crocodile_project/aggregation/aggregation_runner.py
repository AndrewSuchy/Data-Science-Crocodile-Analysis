#!/usr/bin/env python3
"""
Runner for Job 1: Species Aggregation MapReduce
"""
import os
import subprocess
import sys

def run_aggregation():
    """Run the aggregation MapReduce job"""
    
    print("=" * 50)
    print("JOB 1: SPECIES AGGREGATION")
    print("=" * 50)
    
    # Define paths
    PROJECT_ROOT = "C:/Users/andre/OneDrive/DataSci/crocodile_project"
    OUTPUT_DIR = f"{PROJECT_ROOT}/output"
    AGGREGATION_DIR = f"{PROJECT_ROOT}/aggregation"
    
    # HDFS paths
    HDFS_INPUT = "/user/hadoop/crocodile_cleaned.csv"
    HDFS_OUTPUT = "/user/hadoop/aggregated"
    
    # Local files
    MAPPER = f"{AGGREGATION_DIR}/aggregation_mapper.py"
    REDUCER = f"{AGGREGATION_DIR}/aggregation_reducer.py"
    INPUT_FILE = f"{OUTPUT_DIR}/crocodile_dataset_cleaned.csv"
    OUTPUT_FILE = f"{OUTPUT_DIR}/species_features.csv"
    
    # Check if input exists
    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: Input file not found: {INPUT_FILE}")
        print("Please run clean_data.py first!")
        sys.exit(1)
    
    # Remove previous HDFS output
    print("\nCleaning previous output...")
    subprocess.run(f'hdfs dfs -rm -r {HDFS_OUTPUT}', 
                   stderr=subprocess.DEVNULL, shell=True)
    
    # Upload cleaned data to HDFS
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
    
    # Run MapReduce job - FIXED: Use "py" instead of "python"
    print("\nRunning MapReduce aggregation job...")
    cmd = f'hadoop jar "{streaming_jar}" -input {HDFS_INPUT} -output {HDFS_OUTPUT} -mapper "py {MAPPER}" -reducer "py {REDUCER}" -file "{MAPPER}" -file "{REDUCER}"'
    result = subprocess.run(cmd, shell=True)
    
    if result.returncode != 0:
        print("ERROR: MapReduce job failed")
        sys.exit(1)
    
    # Download results from HDFS
    print("\nDownloading results from HDFS...")
    temp_output = f"{AGGREGATION_DIR}/species_aggregated_output.csv"
    result = subprocess.run(f'hdfs dfs -get {HDFS_OUTPUT}/part-00000 "{temp_output}"', shell=True)
    
    if result.returncode != 0:
        print("ERROR: Failed to download results from HDFS")
        sys.exit(1)
    
    # Add CSV header and save to output directory
    print(f"\nSaving results to: {OUTPUT_FILE}")
    header = "Scientific_Name,Mean_Length,Std_Length,Mean_Weight,Std_Weight,Body_Ratio,Sexual_Dimorphism,Num_Habitats,Num_Countries,Conservation_Status,Adult_Ratio,Observation_Count\n"
    with open(OUTPUT_FILE, 'w') as outfile:
        outfile.write(header)
        with open(temp_output, 'r') as infile:
            outfile.write(infile.read())
    
    # Clean up temp file
    os.remove(temp_output)
    
    print(f"\n{'=' * 50}")
    print("Job 1 complete!")
    print(f"Output: {OUTPUT_FILE}")
    print(f"{'=' * 50}\n")

if __name__ == "__main__":
    run_aggregation()