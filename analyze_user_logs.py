import pandas as pd
import json

# Read the log file
with open("user_activity_log.jsonl") as f:
    events = [json.loads(line) for line in f]

df = pd.DataFrame(events)

# Example: Show first events
print(df.head())

# Example: Count page views
page_views = df[df["type"] == "page_view"]["details"].apply(lambda d: d["path"]).value_counts()
print("\nMost visited pages:\n", page_views)

# Example: Most clicked buttons
button_clicks = df[df["type"] == "button_click"]["details"].apply(lambda d: d["button_text"].strip()).value_counts()
print("\nMost clicked buttons:\n", button_clicks)

# Example: Timeline of events
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp")
print("\nEvents over time:\n", df[["type", "details", "timestamp"]])
