import sys
import pandas as pd
import numpy as np

def reducer():
    data = []
    for line in sys.stdin:
        try:
            centroid_id, features = line.strip().split('\t')
            data.append({
                'centroid_id': int(centroid_id),
                'features': features
            })
        except:
            continue
    
    if not data:
        return
    
    df = pd.DataFrame(data)

    first_features = df.iloc[0]['features'].split(',')
    col_names = [
        'Scientific_Name', 'Mean_Length_Norm', 'Std_Length_Norm',
        'Mean_Weight_Norm', 'Std_Weight_Norm', 'Body_Ratio_Norm',
        'Sexual_Dimorphism_Norm', 'Num_Habitats_Norm', 'Num_Countries_Norm',
        'Conservation_Status', 'Adult_Ratio_Norm', 'Observation_Count'
    ]

    features_list = []
    for _, row in df.iterrows():
        feature_values = row['features'].split(',')
        feature_dict = {col_names[i]: feature_values[i] for i in range(len(col_names))}
        feature_dict['centroid_id'] = row['centroid_id']
        features_list.append(feature_dict)
    
    df_features = pd.DataFrame(features_list)

    numeric_cols = [
        'Mean_Length_Norm', 'Std_Length_Norm', 'Mean_Weight_Norm', 'Std_Weight_Norm',
        'Body_Ratio_Norm', 'Sexual_Dimorphism_Norm', 'Num_Habitats_Norm',
        'Num_Countries_Norm', 'Adult_Ratio_Norm', 'Observation_Count'
    ]
    
    for col in numeric_cols:
        df_features[col] = pd.to_numeric(df_features[col])

    for centroid_id, group in df_features.groupby('centroid_id'):
        means = group[numeric_cols].mean()

        most_common_status = group['Conservation_Status'].mode()[0] if len(group) > 0 else "Unknown"

        print(f"Centroid_{centroid_id},"
              f"{means['Mean_Length_Norm']:.6f},"
              f"{means['Std_Length_Norm']:.6f},"
              f"{means['Mean_Weight_Norm']:.6f},"
              f"{means['Std_Weight_Norm']:.6f},"
              f"{means['Body_Ratio_Norm']:.6f},"
              f"{means['Sexual_Dimorphism_Norm']:.6f},"
              f"{means['Num_Habitats_Norm']:.6f},"
              f"{means['Num_Countries_Norm']:.6f},"
              f"{most_common_status},"
              f"{means['Adult_Ratio_Norm']:.6f},"
              f"{means['Observation_Count']:.1f}")

if __name__ == "__main__":
    reducer()