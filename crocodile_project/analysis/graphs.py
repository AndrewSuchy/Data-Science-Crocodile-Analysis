import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sb
from pathlib import Path

def visualize_results(clusters_file, output_dir):

    df = pd.read_csv(clusters_file)

    # FIXED: Standardize column names (handle both 'Scientific Name' and 'Scientific_Name')
    if 'Scientific Name' in df.columns:
        df.rename(columns={'Scientific Name': 'Scientific_Name'}, inplace=True)

    figures_dir = Path(output_dir) / "figures"
    figures_dir.mkdir(exist_ok=True)

    sb.set_style("whitegrid")
    sb.set_context("paper", font_scale=1.2)
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.family'] = 'sans-serif'
    print()

    print("Creating conservation status breakdown...")
    plt.figure(figsize=(14, 7))
    
    conservation_counts = df.groupby(['Cluster_ID', 'Conservation_Status']).size().unstack(fill_value=0)
    
    ax = conservation_counts.plot(
        kind='bar',
        stacked=True,
        colormap='Set3',
        width=0.7,
        edgecolor='black',
        linewidth=0.5
    )
    
    plt.xlabel('Cluster ID', fontsize=14, fontweight='bold')
    plt.ylabel('Number of Species', fontsize=14, fontweight='bold')
    plt.title('Conservation Status Distribution by Cluster', 
              fontsize=16, fontweight='bold', pad=20)
    plt.legend(
        title='Conservation Status',
        bbox_to_anchor=(1.05, 1),
        loc='upper left',
        fontsize=11,
        title_fontsize=12,
        frameon=True,
        shadow=True
    )
    plt.xticks(rotation=0, fontsize=12)
    plt.yticks(fontsize=12)

    for container in ax.containers:
        ax.bar_label(container, label_type='center', fontsize=9, fmt='%.0f')
    
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    plt.savefig(figures_dir / 'conservation_breakdown.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {figures_dir}/conservation_breakdown.png")

    print("Creating cluster characteristics heatmap...")
    plt.figure(figsize=(12, 8))
    
    cluster_means = df.groupby('Cluster_ID')[[
        'Mean_Length_Norm',
        'Mean_Weight_Norm',
        'Body_Ratio_Norm',
        'Sexual_Dimorphism_Norm',
        'Num_Habitats_Norm',
        'Num_Countries_Norm',
        'Adult_Ratio_Norm'
    ]].mean()

    cluster_means.columns = [
        'Mean Length',
        'Mean Weight',
        'Body Condition',
        'Sexual Dimorphism',
        'Habitat Diversity',
        'Geographic Range',
        'Adult Ratio'
    ]
    
    sb.heatmap(
        cluster_means.T,
        annot=True,
        fmt='.2f',
        cmap='RdYlGn',
        center=0,
        cbar_kws={'label': 'Normalized Value'},
        linewidths=0.5,
        linecolor='gray',
        square=False
    )
    
    plt.xlabel('Cluster ID', fontsize=14, fontweight='bold')
    plt.ylabel('Feature', fontsize=14, fontweight='bold')
    plt.title('Cluster Characteristics Heatmap\n(Normalized Feature Values)', 
              fontsize=16, fontweight='bold', pad=20)
    plt.xticks(rotation=0, fontsize=12)
    plt.yticks(rotation=0, fontsize=12)
    plt.tight_layout()
    plt.savefig(figures_dir / 'cluster_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {figures_dir}/cluster_heatmap.png")

    print("Creating high-risk habitats analysis...")
    
    cleaned_data = pd.read_csv(Path(output_dir) / "crocodile_dataset_cleaned.csv")
    
    # FIXED: Standardize column names in cleaned_data too
    if 'Scientific Name' in cleaned_data.columns:
        cleaned_data.rename(columns={'Scientific Name': 'Scientific_Name'}, inplace=True)
    
    habitat_risk = cleaned_data.merge(
        df[['Scientific_Name', 'Cluster_ID', 'Conservation_Status']], 
        on='Scientific_Name', 
        how='left'
    )
    
    at_risk_statuses = ['Critically Endangered', 'Endangered', 'Vulnerable']
    habitat_risk['At_Risk'] = habitat_risk['Conservation_Status'].isin(at_risk_statuses)
    
    habitat_summary = habitat_risk.groupby(['Habitat Type', 'At_Risk']).size().unstack(fill_value=0)
    habitat_summary['Total'] = habitat_summary.sum(axis=1)
    habitat_summary['Risk_Percentage'] = (habitat_summary.get(True, 0) / habitat_summary['Total'] * 100)
    habitat_summary = habitat_summary.sort_values('Risk_Percentage', ascending=False)
    
    plt.figure(figsize=(14, 8))
    x = np.arange(len(habitat_summary))
    width = 0.35
    
    plt.bar(x - width/2, habitat_summary.get(False, 0), width, label='Not At Risk', color='lightgreen', edgecolor='black')
    plt.bar(x + width/2, habitat_summary.get(True, 0), width, label='At Risk (CE/EN/VU)', color='crimson', edgecolor='black')
    
    plt.xlabel('Habitat Type', fontsize=14, fontweight='bold')
    plt.ylabel('Number of Species', fontsize=14, fontweight='bold')
    plt.title('High-Risk Habitats: Species Conservation Status by Habitat\n(Which habitats need protection?)', 
              fontsize=16, fontweight='bold', pad=20)
    plt.xticks(x, habitat_summary.index, rotation=45, ha='right', fontsize=11)
    plt.legend(fontsize=12, loc='upper right')
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    
    for i, (idx, row) in enumerate(habitat_summary.iterrows()):
        total = row['Total']
        risk_pct = row['Risk_Percentage']
        plt.text(i, total + 5, f'{risk_pct:.1f}%', ha='center', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(figures_dir / 'high_risk_habitats.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {figures_dir}/high_risk_habitats.png")

    print("Creating species at-risk by location...")
    
    location_risk = habitat_risk.groupby(['Country/Region', 'At_Risk']).size().unstack(fill_value=0)
    location_risk['Total'] = location_risk.sum(axis=1)
    location_risk['Risk_Percentage'] = (location_risk.get(True, 0) / location_risk['Total'] * 100)
    
    top_locations = location_risk.nlargest(15, 'Total')
    
    plt.figure(figsize=(14, 8))
    x = np.arange(len(top_locations))
    width = 0.35
    
    plt.bar(x - width/2, top_locations.get(False, 0), width, label='Not At Risk', color='skyblue', edgecolor='black')
    plt.bar(x + width/2, top_locations.get(True, 0), width, label='At Risk (CE/EN/VU)', color='darkorange', edgecolor='black')
    
    plt.xlabel('Country/Region', fontsize=14, fontweight='bold')
    plt.ylabel('Number of Species', fontsize=14, fontweight='bold')
    plt.title('Species At-Risk by Location (Top 15 Countries)\n(Which regions need urgent conservation attention?)', 
              fontsize=16, fontweight='bold', pad=20)
    plt.xticks(x, top_locations.index, rotation=45, ha='right', fontsize=11)
    plt.legend(fontsize=12, loc='upper right')
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    
    for i, (idx, row) in enumerate(top_locations.iterrows()):
        total = row['Total']
        risk_pct = row['Risk_Percentage']
        plt.text(i, total + 5, f'{risk_pct:.1f}%', ha='center', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(figures_dir / 'species_risk_by_location.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {figures_dir}/species_risk_by_location.png")

    print("Creating morphological vulnerability patterns...")
    
    risk_colors = {
        'Critically Endangered': 'darkred',
        'Endangered': 'red',
        'Vulnerable': 'orange',
        'Near Threatened': 'gold',
        'Least Concern': 'green',
        'Data Deficient': 'gray'
    }
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    for status in df['Conservation_Status'].unique():
        status_data = df[df['Conservation_Status'] == status]
        axes[0, 0].scatter(status_data['Mean_Length_Norm'], 
                          [status] * len(status_data),
                          c=risk_colors.get(status, 'gray'),
                          s=100, alpha=0.6, label=status)
    axes[0, 0].set_xlabel('Normalized Mean Length', fontsize=12, fontweight='bold')
    axes[0, 0].set_ylabel('Conservation Status', fontsize=12, fontweight='bold')
    axes[0, 0].set_title('Body Length vs Conservation Risk', fontsize=13, fontweight='bold')
    axes[0, 0].grid(True, alpha=0.3)
    
    for status in df['Conservation_Status'].unique():
        status_data = df[df['Conservation_Status'] == status]
        axes[0, 1].scatter(status_data['Mean_Weight_Norm'], 
                          [status] * len(status_data),
                          c=risk_colors.get(status, 'gray'),
                          s=100, alpha=0.6)
    axes[0, 1].set_xlabel('Normalized Mean Weight', fontsize=12, fontweight='bold')
    axes[0, 1].set_ylabel('Conservation Status', fontsize=12, fontweight='bold')
    axes[0, 1].set_title('Body Weight vs Conservation Risk', fontsize=13, fontweight='bold')
    axes[0, 1].grid(True, alpha=0.3)
    
    for status in df['Conservation_Status'].unique():
        status_data = df[df['Conservation_Status'] == status]
        axes[1, 0].scatter(status_data['Body_Ratio_Norm'], 
                          [status] * len(status_data),
                          c=risk_colors.get(status, 'gray'),
                          s=100, alpha=0.6)
    axes[1, 0].set_xlabel('Normalized Body Ratio', fontsize=12, fontweight='bold')
    axes[1, 0].set_ylabel('Conservation Status', fontsize=12, fontweight='bold')
    axes[1, 0].set_title('Body Condition vs Conservation Risk', fontsize=13, fontweight='bold')
    axes[1, 0].grid(True, alpha=0.3)
    
    for status in df['Conservation_Status'].unique():
        status_data = df[df['Conservation_Status'] == status]
        axes[1, 1].scatter(status_data['Sexual_Dimorphism_Norm'], 
                          [status] * len(status_data),
                          c=risk_colors.get(status, 'gray'),
                          s=100, alpha=0.6)
    axes[1, 1].set_xlabel('Normalized Sexual Dimorphism', fontsize=12, fontweight='bold')
    axes[1, 1].set_ylabel('Conservation Status', fontsize=12, fontweight='bold')
    axes[1, 1].set_title('Sexual Dimorphism vs Conservation Risk', fontsize=13, fontweight='bold')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.suptitle('Morphological Vulnerability Patterns\n(Do certain body types correlate with higher extinction risk?)', 
                 fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.savefig(figures_dir / 'morphological_vulnerability.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {figures_dir}/morphological_vulnerability.png")

    print("Creating cluster priority ranking...")
    
    priority_data = []
    for cluster_id in sorted(df['Cluster_ID'].unique()):
        cluster_data = df[df['Cluster_ID'] == cluster_id]
        
        critical = len(cluster_data[cluster_data['Conservation_Status'] == 'Critically Endangered'])
        endangered = len(cluster_data[cluster_data['Conservation_Status'] == 'Endangered'])
        vulnerable = len(cluster_data[cluster_data['Conservation_Status'] == 'Vulnerable'])
        
        priority_score = (critical * 5) + (endangered * 3) + (vulnerable * 1)
        total_species = len(cluster_data)
        
        priority_data.append({
            'Cluster': f'Cluster {cluster_id}',
            'Priority_Score': priority_score,
            'Critical': critical,
            'Endangered': endangered,
            'Vulnerable': vulnerable,
            'Total_Species': total_species
        })
    
    priority_df = pd.DataFrame(priority_data).sort_values('Priority_Score', ascending=False)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    
    colors_map = {0: 'lightcoral', 1: 'gold', 2: 'lightblue', 3: 'lightgreen'}
    bar_colors = [colors_map[int(c.split()[1])] for c in priority_df['Cluster']]
    
    bars = ax1.barh(priority_df['Cluster'], priority_df['Priority_Score'], 
                    color=bar_colors, edgecolor='black', linewidth=1.5)
    ax1.set_xlabel('Priority Score', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Cluster ID', fontsize=14, fontweight='bold')
    ax1.set_title('Conservation Priority Ranking by Cluster\n(Higher score = More urgent)', 
                  fontsize=14, fontweight='bold')
    ax1.grid(axis='x', alpha=0.3, linestyle='--')
    
    for i, (idx, row) in enumerate(priority_df.iterrows()):
        ax1.text(row['Priority_Score'] + 0.5, i, f"{row['Priority_Score']:.0f}", 
                va='center', fontsize=11, fontweight='bold')
    
    x = np.arange(len(priority_df))
    width = 0.6
    
    p1 = ax2.barh(x, priority_df['Critical'], width, label='Critically Endangered (×5)', color='darkred')
    p2 = ax2.barh(x, priority_df['Endangered'], width, left=priority_df['Critical'], 
                  label='Endangered (×3)', color='red')
    p3 = ax2.barh(x, priority_df['Vulnerable'], width, 
                  left=priority_df['Critical'] + priority_df['Endangered'],
                  label='Vulnerable (×1)', color='orange')
    
    ax2.set_xlabel('Number of Species', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Cluster ID', fontsize=14, fontweight='bold')
    ax2.set_title('At-Risk Species Breakdown by Cluster', fontsize=14, fontweight='bold')
    ax2.set_yticks(x)
    ax2.set_yticklabels(priority_df['Cluster'])
    ax2.legend(loc='lower right', fontsize=10)
    ax2.grid(axis='x', alpha=0.3, linestyle='--')
    
    plt.suptitle('Cluster Priority Assessment for Conservation Action', 
                 fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig(figures_dir / 'cluster_priority_ranking.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {figures_dir}/cluster_priority_ranking.png")
    
    print("\n" + "="*60)
    print("ALL VISUALIZATIONS COMPLETE!")
    print("="*60)

if __name__ == "__main__":
    try:
        project_root = "C:/Users/andre/OneDrive/DataSci/crocodile_project"
        output_dir = f"{project_root}/output"
        visualize_results(f"{output_dir}/final_clusters.csv", output_dir)
    except FileNotFoundError:
        print("ERROR: final_clusters.csv not found!")
        print("Please run the K-Means clustering job first.")
    except ImportError as e:
        print(f"ERROR: Missing required package: {e}")
        print("Install with: pip install matplotlib seaborn")