import time
import requests
import csv



LATENCY_LOG = []

def measure_latency(url):
    try:
        start = time.time()
        r = requests.get(url)
        duration = time.time() - start
        size = len(r.text)
        print(f"[GET] {url} | Status: {r.status_code}, Time: {duration:.3f}s, Size: {size} bytes")
        LATENCY_LOG.append({
            "url": url,
            "status": r.status_code,
            "response_time": round(duration, 3),
            "size_bytes": size
        })
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        LATENCY_LOG.append({
            "url": url,
            "status": "ERROR",
            "response_time": None,
            "size_bytes": 0
        })

def export_latency_to_csv():
    with open("latency_report.csv", "w", newline="") as csvfile:
        fieldnames = ["url", "status", "response_time", "size_bytes"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for entry in LATENCY_LOG:
            writer.writerow(entry)
    print("Latency report saved to latency_report.csv")