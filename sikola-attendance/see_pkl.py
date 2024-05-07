import pandas as pd

currentDate = "2024-05-06-ALL"
type_data = "dosen"

df = pd.read_pickle(f'log/{currentDate}_attendance_{type_data}_raw.pkl')

print(df)
