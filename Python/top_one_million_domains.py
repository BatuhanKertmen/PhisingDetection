import pandas as pd

df = pd.read_csv('top-1m.csv')
top_one_millions_domains = [website for website in df['Website']]
print(top_one_millions_domains)