import pandas as pd

df = pd.read_csv('top-1m.csv')
domains = [website for website in df['Website']]