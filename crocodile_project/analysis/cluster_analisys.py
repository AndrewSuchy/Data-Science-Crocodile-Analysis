import pandas as pd
import numpy as np
from pathlib import Path

def analyze_clusters(clusters_file, output_file):

    df = pd.read_csv(clusters_file)

    with open(output_file, 'w') as f:

        f.write(f"Total Species Analyzed: {len(df)}\n")
        f.write(f"Number of Clusters: {df['Cluster_ID'].nunique()}\n")
        f.write(f"Date Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        total_critical = len(df[df['Conservation_Status'] == 'Critically Endangered'])
        total_endangered = len(df[df['Conservation_Status'] == 'Endangered'])
        total_vulnerable = len(df[df['Conservation_Status'] == 'Vulnerable'])
        
        f.write("Overall Conservation Status:\n")
        f.write(f"  Critically Endangered: {total_critical} species\n")
        f.write(f"  Endangered: {total_endangered} species\n")
        f.write(f"  Vulnerable: {total_vulnerable} species\n")
        f.write(f"  Total at-risk species: {total_critical + total_endangered + total_vulnerable}\n")
        f.write("\n")

        cluster_priorities = {}

        for cluster_id in sorted(df['Cluster_ID'].unique()):
            cluster_data = df[df['Cluster_ID'] == cluster_id]

            f.write(f"Number of Species: {len(cluster_data)}\n\n")

            f.write("Conservation Status Breakdown:\n")
            status_counts = cluster_data['Conservation_Status'].value_counts()
            for status, count in status_counts.items():
                percentage = (count / len(cluster_data)) * 100
                f.write(f"  {status:<30} {count:>3} ({percentage:>5.1f}%)\n")
            f.write("\n")

            f.write("Morphological Characteristics:\n")
            f.write(f"  Mean Normalized Length:       {cluster_data['Mean_Length_Norm'].mean():>7.3f}\n")
            f.write(f"  Mean Normalized Weight:       {cluster_data['Mean_Weight_Norm'].mean():>7.3f}\n")
            f.write(f"  Mean Normalized Body Ratio:          {cluster_data['Body_Ratio_Norm'].mean():>7.3f}\n")
            f.write(f"  Mean Sexual Dimorphism:       {cluster_data['Sexual_Dimorphism_Norm'].mean():>7.3f}\n")
            f.write("\n")

            f.write("Ecological Characteristics:\n")
            f.write(f"  Mean Habitat Diversity:       {cluster_data['Num_Habitats_Norm'].mean():>7.3f}\n")
            f.write(f"  Mean Geographic Range:        {cluster_data['Num_Countries_Norm'].mean():>7.3f}\n")
            f.write(f"  Mean Adult Ratio:             {cluster_data['Adult_Ratio_Norm'].mean():>7.3f}\n")
            f.write(f"  Mean Observation Count:       {cluster_data['Observation_Count'].mean():>7.1f}\n")
            f.write("\n")

            f.write("Species in this Cluster:\n")
            for i, species in enumerate(cluster_data['Scientific_Name'].values, 1):
                status = cluster_data[cluster_data['Scientific_Name'] == species]['Conservation_Status'].values[0]
                f.write(f"  {i:>2}. {species:<45} [{status}]\n")
                if i >= 15 and len(cluster_data) > 15:
                    f.write(f"      ... and {len(cluster_data) - 15} more species\n")
                    break
            f.write("\n")

            critically_endangered = len(cluster_data[cluster_data['Conservation_Status'] == 'Critically Endangered'])
            endangered = len(cluster_data[cluster_data['Conservation_Status'] == 'Endangered'])
            vulnerable = len(cluster_data[cluster_data['Conservation_Status'] == 'Vulnerable'])
            
            priority_score = (critically_endangered * 5) + (endangered * 3) + (vulnerable * 1)
            cluster_priorities[cluster_id] = priority_score
            
            f.write("Conservation Priority Assessment:\n")
            f.write(f"  Critically Endangered:        {critically_endangered:>3} species (x5 = {critically_endangered*5:>3} points)\n")
            f.write(f"  Endangered:                   {endangered:>3} species (x3 = {endangered*3:>3} points)\n")
            f.write(f"  Vulnerable:                   {vulnerable:>3} species (x1 = {vulnerable*1:>3} points)\n")
            f.write(f"  TOTAL PRIORITY SCORE:         {priority_score:>3} points\n\n")

            if priority_score >= 20:
                level = "CRITICAL"
            elif priority_score >= 10:
                level = "HIGH"
            elif priority_score >= 5:
                level = "MEDIUM"
            else:
                level = "LOW"
            
            f.write(f"  PRIORITY LEVEL: {level}\n\n")

            if level == "CRITICAL":
                f.write("Immediate action required\n")
                f.write("- Urgent habitat protection needed\n")
                f.write("- Implement breeding programs\n")
                f.write("- Increase monitoring efforts\n")
            elif level == "HIGH":
                f.write("Significant conservation needed\n")
                f.write("- Enhanced habitat monitoring\n")
                f.write("- Community engagement programs\n")
                f.write("- Regular population surveys\n")
            elif level == "MEDIUM":
                f.write("Continue monitoring\n")
                f.write("- Maintain current conservation efforts\n")
                f.write("- Monitor population trends\n")
            else:
                f.write("Slight monitoring\n")
                f.write("- Continue standard monitoring\n")
            f.write("\n\n")

        ranked_clusters = sorted(cluster_priorities.items(), key=lambda x: x[1], reverse=True)
        
        f.write("Clusters Ranked by Conservation Priority:\n")
        for rank, (cluster_id, score) in enumerate(ranked_clusters, 1):
            f.write(f"  {rank}. Cluster {cluster_id}: {score} points\n")
        f.write("\n")

        f.write("Habitat Diversity Comparison:\n")
        habitat_means = df.groupby('Cluster_ID')['Num_Habitats_Norm'].mean().sort_values()
        for cluster_id, value in habitat_means.items():
            f.write(f"  Cluster {cluster_id}: {value:>6.3f} (normalized)\n")
        f.write("\n")
        
        lowest_habitat = habitat_means.idxmin()
        f.write(f"Cluster {lowest_habitat} shows LOWEST habitat diversity\n")
        f.write("Consider habitat expansion initiatives for these species.\n\n")

        f.write("Geographic Range Comparison:\n")
        geo_means = df.groupby('Cluster_ID')['Num_Countries_Norm'].mean().sort_values()
        for cluster_id, value in geo_means.items():
            f.write(f"  Cluster {cluster_id}: {value:>6.3f} (normalized)\n")
        f.write("\n")
        
        lowest_geo = geo_means.idxmin()
        f.write(f"Cluster {lowest_geo} has MOST LIMITED geographic range\n")
        f.write("These species are vulnerable to localized threats.\n\n")

        highest_priority_cluster = ranked_clusters[0][0]
        
        f.write("1. Immediate priority actions: \n")
        f.write(f"   Focus: Cluster {highest_priority_cluster} (Highest Priority Score)\n\n")
        f.write("   Recommended Actions:\n")
        f.write("   - Establish protected areas in key habitats\n")
        f.write("   - Implement captive breeding programs for critically endangered species\n")
        f.write("   - Increase anti-poaching enforcement\n")
        f.write("   - Conduct population viability analyses\n")
        f.write("   - Engage local communities in conservation efforts\n\n")
        
        f.write("2. Habitat protection priorities\n")
        f.write(f"   Focus: Cluster {lowest_habitat} (Lowest Habitat Diversity)\n\n")
        f.write("   Recommended Actions:\n")
        f.write("   - Survey potential habitat expansion areas\n")
        f.write("   - Restore degraded habitats\n")
        f.write("   - Create wildlife corridors between existing habitats\n")
        f.write("   - Monitor habitat quality indicators\n\n")
        
        f.write("3. Geographic range expansion\n")
        f.write(f"   Focus: Cluster {lowest_geo} (Most Limited Range)\n\n")
        f.write("   Recommended Actions:\n")
        f.write("   - Assess reintroduction opportunities\n")
        f.write("   - Strengthen international cooperation agreements\n")
        f.write("   - Address cross-border conservation challenges\n")
        f.write("   - Identify suitable translocation sites\n\n")
        
        f.write("4. Research priorities\n")
        f.write("   - Conduct genetic diversity studies within high-priority clusters\n")
        f.write("   - Investigate population connectivity between habitats\n")
        f.write("   - Study climate change impacts on distribution\n")
        f.write("   - Monitor disease prevalence in vulnerable populations\n")
        f.write("   - Assess human-wildlife conflict patterns\n\n")
        
        f.write("5. Monitoring and evaluation\n")
        f.write("   - Establish standardized monitoring protocols\n")
        f.write("   - Conduct annual population surveys\n")
        f.write("   - Track conservation status changes\n")
        f.write("   - Evaluate intervention effectiveness\n")
        f.write("   - Update cluster analysis every 5 years\n\n")

        total_species = len(df)
        at_risk = len(df[df['Conservation_Status'].isin(['Critically Endangered', 'Endangered', 'Vulnerable'])])
        at_risk_pct = (at_risk / total_species) * 100
        
        f.write(f"- {at_risk_pct:.1f}% of analyzed species are at risk (CE, EN, or VU)\n")

        low_br_clusters = df.groupby('Cluster_ID')['Body_Ratio_Norm'].mean().sort_values()
        if low_br_clusters.iloc[0] < -0.5:
            f.write(f"- Cluster {low_br_clusters.index[0]} shows concerning low body condition index\n")

        high_dimorphism = df.groupby('Cluster_ID')['Sexual_Dimorphism_Norm'].mean()
        if (high_dimorphism > 1.0).any():
            cluster_high = high_dimorphism.idxmax()
            f.write(f"- Cluster {cluster_high} exhibits significant sexual dimorphism patterns\n")

        low_obs = df.groupby('Cluster_ID')['Observation_Count'].mean().sort_values()
        if low_obs.iloc[0] < 10:
            f.write(f"- Cluster {low_obs.index[0]} has limited observation data - more field surveys needed\n")
        f.write("\n")

    print(f"Analysis report saved to: {output_file}")
    
    print("Priority Ranking:")
    ranked_clusters = sorted(cluster_priorities.items(), key=lambda x: x[1], reverse=True)
    for rank, (cluster_id, score) in enumerate(ranked_clusters, 1):
        cluster_data = df[df['Cluster_ID'] == cluster_id]
        critical = len(cluster_data[cluster_data['Conservation_Status'] == 'Critically Endangered'])
        print(f"  {rank}. Cluster {cluster_id}: {score} points ({len(cluster_data)} species, {critical} critically endangered)")
    
    print()
    print(f"Highest Priority: Cluster {ranked_clusters[0][0]} - IMMEDIATE ACTION REQUIRED")

if __name__ == "__main__":
    try:
        project_root = "C:/Users/andre/OneDrive/DataSci/crocodile_project"
        output_dir = f"{project_root}/output"
        analyze_clusters(f"{output_dir}/final_clusters.csv", f"{output_dir}/cluster_analysis_report.txt")
    except FileNotFoundError:
        print("ERROR: final_clusters.csv not found!")
        print("Please run the K-Means clustering job first.")