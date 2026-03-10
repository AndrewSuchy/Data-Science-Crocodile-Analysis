#!/usr/bin/env python3
"""
Complete Crocodile Conservation K-Means Pipeline
Runs all jobs in sequence: Clean → Aggregate → Normalize → Cluster → Analyze
"""
import os
import subprocess
import sys
from pathlib import Path

def run_pipeline():
    """Run the complete MapReduce pipeline"""
    
    print("=" * 60)
    print("CROCODILE CONSERVATION K-MEANS PIPELINE")
    print("=" * 60)
    
    # Define project paths
    PROJECT_ROOT = "C:/Users/andre/OneDrive/DataSci/crocodile_project"
    CLEANING_DIR = f"{PROJECT_ROOT}/cleaning"
    AGGREGATION_DIR = f"{PROJECT_ROOT}/aggregation"
    NORMALIZATION_DIR = f"{PROJECT_ROOT}/normalization"
    KMEANS_DIR = f"{PROJECT_ROOT}/kmeans"
    ANALYSIS_DIR = f"{PROJECT_ROOT}/analysis"
    OUTPUT_DIR = f"{PROJECT_ROOT}/output"
    
    # Create output directory if it doesn't exist
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    
    # Step 0: Clean Data
    print("\n" + "=" * 60)
    print("[Step 0] Cleaning data...")
    print("=" * 60)
    
    clean_script = f"{CLEANING_DIR}/clean_data.py"
    result = subprocess.run(["python", clean_script])
    if result.returncode != 0:
        print("ERROR: Data cleaning failed")
        sys.exit(1)
    
    # Step 1: Aggregation
    print("\n" + "=" * 60)
    print("[Step 1] Running species aggregation...")
    print("=" * 60)
    
    aggregation_runner = f"{AGGREGATION_DIR}/aggregation_runner.py"
    result = subprocess.run(["python", aggregation_runner])
    if result.returncode != 0:
        print("ERROR: Aggregation job failed")
        sys.exit(1)
    
    # Step 2: Normalization
    print("\n" + "=" * 60)
    print("[Step 2] Running normalization...")
    print("=" * 60)
    
    normalization_runner = f"{NORMALIZATION_DIR}/normalization_runner.py"
    result = subprocess.run(["python", normalization_runner])
    if result.returncode != 0:
        print("ERROR: Normalization job failed")
        sys.exit(1)
    
    # Step 3: K-Means Clustering
    print("\n" + "=" * 60)
    print("[Step 3] Running K-Means clustering...")
    print("=" * 60)
    
    kmeans_runner = f"{KMEANS_DIR}/kmeans_runner.py"
    result = subprocess.run(["python", kmeans_runner])
    if result.returncode != 0:
        print("ERROR: K-Means clustering failed")
        sys.exit(1)
    
    # Step 4: Analysis and Visualization
    print("\n" + "=" * 60)
    print("[Step 4] Generating analysis and visualizations...")
    print("=" * 60)
    
    # FIXED: Use correct filename (cluster_analisys.py)
    cluster_analysis = f"{ANALYSIS_DIR}/cluster_analisys.py"
    result = subprocess.run(["python", cluster_analysis])
    if result.returncode != 0:
        print("WARNING: Cluster analysis failed (continuing...)")
    
    graphs_script = f"{ANALYSIS_DIR}/graphs.py"
    result = subprocess.run(["python", graphs_script])
    if result.returncode != 0:
        print("WARNING: Graph generation failed (continuing...)")
    
    # Pipeline complete
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE!")
    print("=" * 60)
    print("\nOutput files:")
    print(f"  - {OUTPUT_DIR}/crocodile_dataset_cleaned.csv (cleaned data)")
    print(f"  - {OUTPUT_DIR}/species_features.csv (aggregated features)")
    print(f"  - {OUTPUT_DIR}/species_normalized.csv (normalized data)")
    print(f"  - {OUTPUT_DIR}/final_clusters.csv (cluster assignments)")
    print(f"  - {OUTPUT_DIR}/cluster_analysis_report.txt (analysis report)")
    print(f"  - {OUTPUT_DIR}/figures/ (visualizations)")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    run_pipeline()