import sys
import pandas as pd

def mapper():

    df = pd.read_csv(sys.stdin)
    
    for _, row in df.iterrows():
        try:
            species = row['Scientific Name']
            length = row['Observed Length (m)']
            weight = row['Observed Weight (kg)']
            sex = row['Sex']
            age_class = row['Age Class']
            habitat = row['Habitat Type']
            country = row['Country/Region']
            status = row['Conservation Status']
            
            print(f"{species}\t{length},{weight},{sex},{habitat},{country},{status},{age_class}")
        except:
            continue

if __name__ == "__main__":
    mapper()