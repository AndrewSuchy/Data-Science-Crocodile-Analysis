import sys
import pandas as pd
import numpy as np

def reducer():

    data = []
    for line in sys.stdin:
        try:
            species, values = line.strip().split('\t')
            length, weight, sex, habitat, country, status, age_class = values.split(',')
            data.append({
                'species': species,
                'length': float(length),
                'weight': float(weight),
                'sex': sex,
                'habitat': habitat,
                'country': country,
                'status': status,
                'age_class': age_class
            })
        except:
            continue
    
    if not data:
        return
    
    df = pd.DataFrame(data)
    
    results = []
    
    for species, group in df.groupby('species'):

        mean_length = group['length'].mean()
        std_length = group['length'].std()
        mean_weight = group['weight'].mean()
        std_weight = group['weight'].std()

        body_ratio = mean_weight / mean_length if mean_length > 0 else 0

        male_lengths = group[group['sex'] == 'Male']['length']
        female_lengths = group[group['sex'] == 'Female']['length']
        
        if len(male_lengths) > 0 and len(female_lengths) > 0:
            sexual_dimorphism = male_lengths.mean() / female_lengths.mean()
        else:
            sexual_dimorphism = 1.0

        num_habitats = group['habitat'].nunique()
        num_countries = group['country'].nunique()

        most_common_status = group['status'].mode()[0] if len(group['status'].mode()) > 0 else "Data Deficient"

        adult_count = (group['age_class'] == 'Adult').sum()
        adult_ratio = adult_count / len(group)

        observation_count = len(group)

        print(f"{species},{mean_length:.4f},{std_length:.4f},{mean_weight:.4f},{std_weight:.4f},"
              f"{body_ratio:.4f},{sexual_dimorphism:.4f},{num_habitats},{num_countries},"
              f"{most_common_status},{adult_ratio:.4f},{observation_count}")

if __name__ == "__main__":
    reducer()