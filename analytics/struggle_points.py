import pandas as pd

df = pd.read_csv("logs/user_events.csv")
struggles = df[df["error"].notnull()]
print("Top struggle points:")
print(struggles.groupby("page")["error"].count().sort_values(ascending=False))
