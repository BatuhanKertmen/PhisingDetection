import pandas as pd
# import random

df = pd.read_csv('top-1m.csv')
domains = [website for website in df['Website']]
# random.shuffle(domains)