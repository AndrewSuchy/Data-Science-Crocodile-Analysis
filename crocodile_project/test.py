#!/usr/bin/env python3
"""
Performance Evaluation Script for Crocodilian Conservation Project
Measures execution times and provides statistical analysis of clustering results
"""
import pandas as pd
import numpy as np
import time
import subprocess
import os
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sb
from sklearn.metrics import silhouette_score
from scipy import stats

def measure_execution_times(project_root):
    """Measure execution time for each pipeline stage"""
    
    print("=" * 70)
    print("PERFORMANCE EVALUATION: EXECUTION TIMES")
    print("=" * 70)
    
    times = {}
    
    # Test Data Cleaning
    print("\n1. Testing Data Cleaning...")
    input_file = f"{project_root}/crocodile_dataset.csv"
    output_file = f"{project_root}/output/crocodile_dataset_cleaned.csv"
    
    start = time.time()
    subprocess.run(f'py "{project_root}/cleaning/clean_data.py"', shell=True)
    times['Data Cleaning'] = time.time() - start
    print(f"   Time: {times['Data Cleaning']:.2f} seconds")
    
    # Test Aggregation (Job 1)
    print("\n2. Testing Aggregation MapReduce...")
    start = time.time()
    subprocess.run(f'py "{project_root}/aggregation/aggregation_runner.py"', shell=True)
    times['Job 1: Aggregation'] = time.time() - start
    print(f"   Time: {times['Job 1: Aggregation']:.2f} seconds")
    
    # Test Normalization (Job 2)
    print("\n3. Testing Normalization MapReduce...")
    start = time.time()
    subprocess.run(f'py "{project_root}/normalization/normalization_runner.py"', shell=True)
    times['Job 2: Normalization'] = time.time() - start
    print(f"   Time: {times['Job 2: Normalization']:.2f} seconds")
    
    # Test K-Means (Job 3)
    print("\n4. Testing K-Means Clustering (10 iterations)...")
    start = time.time()
    subprocess.run(f'py "{project_root}/kmeans/kmeans_runner.py"', shell=True)
    times['Job 3: K-Means (10 iter)'] = time.time() - start
    print(f"   Time: {times['Job 3: K-Means (10 iter)']:.2f} seconds")
    
    # Test Analysis
    print("\n5. Testing Cluster Analysis...")
    start = time.time()
    subprocess.run(f'py "{project_root}/analysis/cluster_analisys.py"', shell=True)
    times['Cluster Analysis'] = time.time() - start
    print(f"   Time: {times['Cluster Analysis']:.2f} seconds")
    
    # Test Visualization
    print("\n6. Testing Visualization Generation...")
    start = time.time()
    subprocess.run(f'py "{project_root}/analysis/graphs.py"', shell=True)
    times['Visualization'] = time.time() - start
    print(f"   Time: {times['Visualization']:.2f} seconds")
    
    # Calculate total
    times['Total Pipeline'] = sum(times.values())
    
    return times


def statistical_analysis(clusters_file, output_dir):
    """Perform statistical analysis on clustering results"""
    
    print("\n" + "=" * 70)
    print("STATISTICAL ANALYSIS OF CLUSTERING RESULTS")
    print("=" * 70)
    
    df = pd.read_csv(clusters_file)
    
    # Prepare feature matrix for clustering metrics
    feature_cols = [
        'Mean_Length_Norm', 'Std_Length_Norm', 'Mean_Weight_Norm', 
        'Std_Weight_Norm', 'Body_Ratio_Norm', 'Sexual_Dimorphism_Norm',
        'Num_Habitats_Norm', 'Num_Countries_Norm', 'Adult_Ratio_Norm'
    ]
    
    X = df[feature_cols].values
    labels = df['Cluster_ID'].values
    
    # Calculate clustering quality metrics
    print("\n1. Clustering Quality Metrics:")
    print("-" * 50)
    
    # Silhouette Score (range: -1 to 1, higher is better)
    silhouette = silhouette_score(X, labels)
    print(f"   Silhouette Score: {silhouette:.4f}")
    if silhouette > 0.5:
        print("   -> Strong clustering structure")
    elif silhouette > 0.3:
        print("   -> Reasonable clustering structure")
    else:
        print("   -> Weak clustering structure")
    
    # Cluster size distribution
    print("\n2. Cluster Size Distribution:")
    print("-" * 50)
    cluster_sizes = df['Cluster_ID'].value_counts().sort_index()
    for cluster_id, size in cluster_sizes.items():
        percentage = (size / len(df)) * 100
        print(f"   Cluster {cluster_id}: {size} species ({percentage:.1f}%)")
    
    # Statistical tests for feature differences across clusters
    print("\n3. ANOVA: Feature Differences Across Clusters")
    print("-" * 50)
    
    feature_names = {
        'Mean_Length_Norm': 'Mean Length',
        'Mean_Weight_Norm': 'Mean Weight',
        'Body_Ratio_Norm': 'Body Ratio',
        'Num_Countries_Norm': 'Geographic Range',
        'Num_Habitats_Norm': 'Habitat Diversity',
        'Sexual_Dimorphism_Norm': 'Sexual Dimorphism'
    }
    
    anova_results = []
    for col, name in feature_names.items():
        groups = [df[df['Cluster_ID'] == i][col].values for i in sorted(df['Cluster_ID'].unique())]
        f_stat, p_value = stats.f_oneway(*groups)
        anova_results.append({
            'Feature': name,
            'F-statistic': f_stat,
            'p-value': p_value,
            'Significant': 'Yes' if p_value < 0.05 else 'No'
        })
        
        sig = "✓ Significant" if p_value < 0.001 else ("✓ Significant" if p_value < 0.05 else "✗ Not significant")
        print(f"   {name}: F={f_stat:.2f}, p={p_value:.4f} {sig}")
    
    # Overall at-risk percentage
    at_risk = df['Conservation_Status'].isin(['Critically Endangered', 'Endangered', 'Vulnerable']).sum()
    at_risk_pct = (at_risk / len(df)) * 100
    print(f"\n   Overall: {at_risk}/{len(df)} species at risk ({at_risk_pct:.1f}%)")
    
    return {
        'silhouette': silhouette,
        'cluster_sizes': cluster_sizes,
        'anova_results': anova_results
    }


def create_performance_visualizations(times, stats_results, output_dir):
    """Create visualizations for performance evaluation"""
    
    print("\n" + "=" * 70)
    print("GENERATING PERFORMANCE VISUALIZATIONS")
    print("=" * 70)
    
    figures_dir = Path(output_dir) / "performance_figures"
    figures_dir.mkdir(exist_ok=True)
    
    # 1. Execution Time Bar Chart
    print("\n1. Creating execution time chart...")
    plt.figure(figsize=(12, 6))
    
    stages = list(times.keys())[:-1]  # Exclude 'Total Pipeline'
    durations = [times[stage] for stage in stages]
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
    
    bars = plt.bar(range(len(stages)), durations, color=colors, edgecolor='black', linewidth=1.5)
    plt.xlabel('Pipeline Stage', fontsize=12, fontweight='bold')
    plt.ylabel('Execution Time (seconds)', fontsize=12, fontweight='bold')
    plt.title('Pipeline Execution Time by Stage', fontsize=14, fontweight='bold')
    plt.xticks(range(len(stages)), stages, rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels on bars
    for i, (bar, duration) in enumerate(zip(bars, durations)):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, 
                f'{duration:.1f}s', ha='center', fontsize=10, fontweight='bold')
    
    # Add total time annotation
    total_time = times['Total Pipeline']
    plt.text(0.95, 0.95, f'Total Pipeline: {total_time:.1f}s', 
             transform=plt.gca().transAxes, fontsize=12, fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
             verticalalignment='top', horizontalalignment='right')
    
    plt.tight_layout()
    plt.savefig(figures_dir / 'execution_times.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   Saved: {figures_dir}/execution_times.png")
    
    # 2. Clustering Quality Metrics - Just Silhouette Score
    print("\n2. Creating clustering quality metric chart...")
    plt.figure(figsize=(8, 6))
    
    # Silhouette Score
    silhouette = stats_results['silhouette']
    bar = plt.bar(['Silhouette Score'], [silhouette], color='#2ecc71', 
                  edgecolor='black', linewidth=2, width=0.5)
    plt.axhline(y=0.5, color='red', linestyle='--', linewidth=2, label='Good threshold (0.5)')
    plt.axhline(y=0.3, color='orange', linestyle='--', linewidth=2, label='Fair threshold (0.3)')
    plt.ylim(0, 1)
    plt.ylabel('Score', fontsize=12, fontweight='bold')
    plt.title('Clustering Quality: Silhouette Score\n(Higher is Better)', 
              fontsize=14, fontweight='bold', pad=20)
    plt.legend(fontsize=10, loc='upper right')
    plt.text(0, silhouette + 0.05, f'{silhouette:.3f}', ha='center', 
             fontsize=14, fontweight='bold')
    
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    plt.savefig(figures_dir / 'clustering_quality.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   Saved: {figures_dir}/clustering_quality.png")
    
    # 3. Cluster Size Distribution Pie Chart
    print("\n3. Creating cluster size distribution chart...")
    plt.figure(figsize=(10, 8))
    
    sizes = stats_results['cluster_sizes'].values
    labels = [f"Cluster {i}\n({size} species)" for i, size in enumerate(stats_results['cluster_sizes'].values)]
    colors_pie = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
    
    plt.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.1f%%', 
            startangle=90, textprops={'fontsize': 12, 'fontweight': 'bold'},
            explode=[0.05] * len(sizes), shadow=True)
    plt.title('Species Distribution Across Clusters', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(figures_dir / 'cluster_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   Saved: {figures_dir}/cluster_distribution.png")
    
    print("\n" + "=" * 70)
    print("PERFORMANCE EVALUATION COMPLETE")
    print("=" * 70)


def save_performance_report(times, stats_results, output_dir):
    """Save detailed performance report to text file"""
    
    report_file = Path(output_dir) / "performance_evaluation_report.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("PERFORMANCE EVALUATION REPORT\n")
        f.write("Crocodilian Conservation Project\n")
        f.write("=" * 70 + "\n\n")
        
        # Execution Times
        f.write("1. EXECUTION TIMES\n")
        f.write("-" * 70 + "\n")
        for stage, duration in times.items():
            if stage == 'Total Pipeline':
                f.write("\n")
            f.write(f"{stage:<30} {duration:>10.2f} seconds\n")
        
        # Clustering Quality
        f.write("\n2. CLUSTERING QUALITY METRICS\n")
        f.write("-" * 70 + "\n")
        f.write(f"Silhouette Score: {stats_results['silhouette']:.4f}\n")
        f.write("  (Range: -1 to 1, higher is better)\n")
        if stats_results['silhouette'] > 0.5:
            f.write("  -> Strong clustering structure\n")
        elif stats_results['silhouette'] > 0.3:
            f.write("  -> Reasonable clustering structure\n")
        else:
            f.write("  -> Weak clustering structure\n")
        
        # Cluster Sizes
        f.write("\n3. CLUSTER SIZE DISTRIBUTION\n")
        f.write("-" * 70 + "\n")
        for cluster_id, size in stats_results['cluster_sizes'].items():
            percentage = (size / stats_results['cluster_sizes'].sum()) * 100
            f.write(f"Cluster {cluster_id}: {size:>3} species ({percentage:>5.1f}%)\n")
        
        # ANOVA Results
        f.write("\n4. ANOVA RESULTS (Feature Significance)\n")
        f.write("-" * 70 + "\n")
        f.write(f"{'Feature':<25} {'F-statistic':<15} {'p-value':<12} {'Significant'}\n")
        f.write("-" * 70 + "\n")
        for result in stats_results['anova_results']:
            f.write(f"{result['Feature']:<25} {result['F-statistic']:<15.2f} "
                   f"{result['p-value']:<12.4f} {result['Significant']}\n")
    
    print(f"\nPerformance report saved to: {report_file}")


if __name__ == "__main__":
    # Set project root
    project_root = "C:/Users/andre/OneDrive/DataSci/crocodile_project"
    output_dir = f"{project_root}/output"
    clusters_file = f"{output_dir}/final_clusters.csv"
    
    print("Starting Performance Evaluation...\n")
    
    # Check if final_clusters.csv exists
    if not os.path.exists(clusters_file):
        print("ERROR: final_clusters.csv not found!")
        print("Please run the full pipeline first.")
        exit(1)
    
    # Measure execution times (comment out if you don't want to re-run pipeline)
    print("NOTE: This will re-run the entire pipeline to measure execution times.")
    response = input("Proceed? (y/n): ")
    
    if response.lower() == 'y':
        times = measure_execution_times(project_root)
    else:
        # Use sample times if not re-running
        times = {
            'Data Cleaning': 2.3,
            'Job 1: Aggregation': 45.0,
            'Job 2: Normalization': 38.0,
            'Job 3: K-Means (10 iter)': 402.0,
            'Cluster Analysis': 1.8,
            'Visualization': 12.4,
            'Total Pipeline': 501.5
        }
        print("\nUsing sample execution times (pipeline not re-run).")
    
    # Perform statistical analysis
    stats_results = statistical_analysis(clusters_file, output_dir)
    
    # Create visualizations
    create_performance_visualizations(times, stats_results, output_dir)
    
    # Save report
    save_performance_report(times, stats_results, output_dir)
    
    print("\n✓ Performance evaluation complete!")
    print(f"Results saved to: {output_dir}/performance_figures/")
    print(f"Report saved to: {output_dir}/performance_evaluation_report.txt")