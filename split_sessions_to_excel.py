import pandas as pd
import json
import os

# Read the user activity log
with open("user_activity_log.jsonl") as f:
    events = [json.loads(line) for line in f]

df = pd.DataFrame(events)

# Check that "session" exists
if "session" not in df.columns:
    raise ValueError("No 'session' column found! Make sure your logging JS includes session IDs.")

# Create a folder for session excels
os.makedirs("sessions_excels", exist_ok=True)

# Split by session and save each to Excel
for session_id, session_df in df.groupby("session"):
    # Optional: sort by timestamp
    session_df = session_df.sort_values("timestamp")
    # Save each session to its own Excel file
    out_path = f"sessions_excels/session_{session_id}.xlsx"
    session_df.to_excel(out_path, index=False)
    print(f"Wrote {out_path}")

print("\nDone! Each session is in its own Excel file in the 'sessions_excels' folder.") 