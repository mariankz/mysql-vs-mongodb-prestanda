import os
import json
import time
import random
import csv
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from pymongo import MongoClient

# ===== CONNECT =====
def connect():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["ai_db"]
    collection = db["messages"]
    return collection

# ===== LOAD REAL DATA =====
file_path = os.path.join(os.path.dirname(__file__), "real_data.json")
with open(file_path, "r", encoding="utf-8") as f:
    real_data = json.load(f)

def format_timestamp(ts_str):
    dt = datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    return dt

# ===== GENERATE DATA =====
def generate_data(batch_size):
    batch = []

    while len(batch) < batch_size:
        item = random.choice(real_data)
        msg = item["message"]

        if msg.startswith("~"):
            continue

        batch.append({
            "userId": item["userId"],
            "timestamp": format_timestamp(item["timestamp"]),
            "message": msg
        })

    return batch

# ===== INSERT TEST =====
def test_insert(collection, total_rows, batch_size=1000):
    start_time = time.time()
    inserted = 0

    while inserted < total_rows:
        remaining = total_rows - inserted
        current_batch_size = min(batch_size, remaining)

        batch = generate_data(current_batch_size)
        collection.insert_many(batch)

        inserted += current_batch_size

    return time.time() - start_time

# ===== QUERY TEST =====
def test_query(collection):
    start_time = time.time()

    list(collection.find({
        "userId": {"$gte": 1, "$lte": 50},
        "timestamp": {
            "$gte": datetime(2024, 1, 1),
            "$lte": datetime(2024, 12, 31)
        }
    }))

    return time.time() - start_time

# ===== WORKER =====
def worker_task(total_rows_per_thread):
    collection = connect()

    ins_t = test_insert(collection, total_rows_per_thread)
    qry_t = test_query(collection)

    return ins_t, qry_t

# ===== SINGLE USER =====
def run_single_user_tests():
    collection = connect()

    results_dir = "results/mongo"
    os.makedirs(results_dir, exist_ok=True)

    csv_path = os.path.join(results_dir, "single_real.csv")

    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["size", "run", "insert", "query"])

        for rows in [100000, 250000, 500000, 750000, 1000000]:
            print(f"[Mongo Real] Single-user: {rows}")

            for run in range(1, 6):
                collection.delete_many({})

                ins_t = test_insert(collection, rows)
                qry_t = test_query(collection)

                writer.writerow([rows, run, ins_t, qry_t])
                f.flush()

# ===== MULTI USER =====
def run_multi_user_tests():
    collection = connect()

    results_dir = "results/mongo"
    csv_path = os.path.join(results_dir, "multi_real.csv")

    num_threads = 5

    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["size", "run", "insert", "query"])

        for rows in [100000, 250000, 500000, 750000, 1000000]:
            print(f"[Mongo Real] Multi-user: {rows}")

            rows_per_thread = rows // num_threads

            for run in range(1, 6):
                collection.delete_many({})

                with ThreadPoolExecutor(max_workers=num_threads) as executor:
                    futures = [
                        executor.submit(worker_task, rows_per_thread)
                        for _ in range(num_threads)
                    ]
                    thread_results = [f.result() for f in futures]

                avg_ins = sum(r[0] for r in thread_results) / num_threads
                avg_qry = sum(r[1] for r in thread_results) / num_threads

                writer.writerow([rows, run, avg_ins, avg_qry])
                f.flush()

# ===== MAIN =====
if __name__ == "__main__":
    print("=== START REAL DATA TESTS (MONGO) ===")

    run_single_user_tests()

    print("-" * 50)

    run_multi_user_tests()

    print("=== DONE ===")
