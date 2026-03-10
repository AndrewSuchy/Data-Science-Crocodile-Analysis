import pandas as pd
import numpy as np

def clean_data(input_file, output_file):

    df = pd.read_csv(input_file)

    essential_columns = [
        'Observation ID',
        'Common Name',
        'Scientific Name',
        'Genus',
        'Observed Length (m)',
        'Observed Weight (kg)',
        'Age Class',
        'Sex',
        'Country/Region',
        'Habitat Type',
        'Conservation Status'
    ]
    
    df = df[essential_columns]

    df = df.dropna(subset=['Scientific Name'])

    df['Observed Length (m)'] = df.groupby('Scientific Name')['Observed Length (m)'].transform(
        lambda x: x.fillna(x.mean())
    )

    df['Observed Weight (kg)'] = df.groupby('Scientific Name')['Observed Weight (kg)'].transform(
        lambda x: x.fillna(x.mean())
    )

    def get_age_from_length(row):
        if pd.isna(row['Age Class']) or row['Age Class'] == 'Unknown':
            length = row['Observed Length (m)']
            species = row['Scientific Name']

            species_data = df[df['Scientific Name'] == species]['Observed Length (m)']
            
            if len(species_data) > 3:
                q25 = species_data.quantile(0.25)
                q50 = species_data.quantile(0.50)
                q75 = species_data.quantile(0.75)
                
                if length < q25:
                    return 'Hatchling'
                elif length < q50:
                    return 'Juvenile'
                elif length < q75:
                    return 'Subadult'
                else:
                    return 'Adult'
            else:
                return row['Age Class'] if not pd.isna(row['Age Class']) else 'Adult'
        
        return row['Age Class']
    
    df['Age Class'] = df.apply(get_age_from_length, axis=1)

    df['Sex'] = df['Sex'].fillna('Unknown')

    df['Country/Region'] = df['Country/Region'].fillna('Unknown')

    df['Habitat Type'] = df.groupby('Scientific Name')['Habitat Type'].transform(
        lambda x: x.fillna(x.mode()[0] if len(x.mode()) > 0 else 'Unknown')
    )
    df['Habitat Type'] = df['Habitat Type'].fillna('Unknown')

    df['Conservation Status'] = df.groupby('Scientific Name')['Conservation Status'].transform(
        lambda x: x.fillna(x.mode()[0] if len(x.mode()) > 0 else 'Data Deficient')
    )
    df['Conservation Status'] = df['Conservation Status'].fillna('Data Deficient')

    df = df.sort_values(['Scientific Name', 'Observation ID']).reset_index(drop=True)

    df.to_csv(output_file, index=False)
    return df

if __name__ == "__main__":
    project_root = "C:/Users/andre/OneDrive/DataSci/crocodile_project"
    input_file = f"{project_root}/crocodile_dataset.csv"
    output_file = f"{project_root}/output/crocodile_dataset_cleaned.csv"
    
    df_cleaned = clean_data(input_file, output_file)
    
    print(f"\nCleaned data saved to: {output_file}")