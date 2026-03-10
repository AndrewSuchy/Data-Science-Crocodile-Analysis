import sys
import pandas as pd
import numpy as np

def reducer():
    data = []
    for line in sys.stdin:
        try:
            feature, value = line.strip().split('\t')
            data.append({'feature': feature, 'value': float(value)})
        except:
            continue
    
    if not data:
        return
    
    df = pd.DataFrame(data)

    for feature, group in df.groupby('feature'):
        mean = group['value'].mean()
        std = group['value'].std()

        if std == 0 or pd.isna(std):
            std = 1.0
        
        print(f"{feature}\t{mean:.6f}\t{std:.6f}")

if __name__ == "__main__":
    reducer()