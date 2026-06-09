import time
import csv
import threading
import json
import random
from datetime import datetime
from pymongo import MongoClient
import os

output_dir = "results/mongo"
os.makedirs(output_dir, exist_ok=True)


# ===== CONNECT =====
def connect():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["ai_db"]
    return db


# ===== LADDA AI DATA =====
def load_ai_data():
    file_path = os.path.join(os.path.dirname(__file__), "ai_data.json")

    with open(file_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    data = []
    for item in raw:
        data.append({
            "userId": item["userId"],
            "timestamp": datetime.fromisoformat(item["timestamp"].replace("Z", "")),
            "message": item["message"]
        })
    return data


# ===== DATA =====
AI_DATA = load_ai_data() * 10000


# ===== INSERT (BATCH) =====
def test_insert(size, batch_size=1000):
    db = connect()
    start = time.time()

    batch = []

    for _ in range(size):
        item = random.choice(AI_DATA)

        doc = {
            "userId": item["userId"],
            "timestamp": item["timestamp"],
            "message": item["message"]
        }

        batch.append(doc)

        if len(batch) == batch_size:
            db.messages.insert_many(batch)
            batch = []

    if batch:
        db.messages.insert_many(batch)

    return time.time() - start


# ===== QUERY =====
def test_query():
    db = connect()
    start = time.time()

    list(db.messages.find({
        "userId": {"$gte": 1, "$lte": 50},
        "timestamp": {
            "$gte": datetime(2026, 1, 1),
            "$lte": datetime(2026, 12, 31)
        }
    }))

    return time.time() - start


# ===== PARALLELL WORKER (BATCH) =====
def worker(size, batch_size=1000):
    db = connect()
    batch = []

    for _ in range(size):
        item = random.choice(AI_DATA)

        doc = {
            "userId": item["userId"],
            "timestamp": item["timestamp"],
            "message": item["message"]
        }

        batch.append(doc)

        if len(batch) == batch_size:
            db.messages.insert_many(batch)
            batch = []

    if batch:
        db.messages.insert_many(batch)


def run_parallel_test(size, users=5):
    db = connect()
    db.messages.delete_many({})

    per_user = size // users
    threads = []

    start_insert = time.time()

    for _ in range(users):
        t = threading.Thread(target=worker, args=(per_user, 1000))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    insert_time = time.time() - start_insert

    query_time = test_query()

    return insert_time, query_time

# Rensa databas innan testerna startar
db = connect()
db.messages.delete_many({})
print("Databas rensad")


# ===== SEKVENTIELLT TEST =====
sizes = [100000, 250000, 500000, 750000, 1000000]

with open(f"{output_dir}/single.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["size", "run", "insert", "query"])

    for size in sizes:
        print(f"\nTesting {size} rows (single user)...")

        for run in range(1, 6):
            print(f"  Run {run}/5")

            db = connect()
            db.messages.delete_many({})

            insert_time = test_insert(size)
            query_time = test_query()

            print(f"    Insert: {insert_time:.4f}s | Query: {query_time:.6f}s")
            writer.writerow([size, run, insert_time, query_time])


# ===== PARALLELLT TEST =====
with open(f"{output_dir}/multi.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["size", "run", "insert", "query"])

    print("\n=== PARALLEL TEST (5 USERS) ===")

    for size in sizes:
        print(f"\nTesting {size} rows with 5 users...")

        for run in range(1, 6):
            print(f"  Run {run}/5")

            insert_time, query_time = run_parallel_test(size, users=5)

            print(f"    Insert: {insert_time:.4f}s | Query: {query_time:.6f}s")
            writer.writerow([size, run, insert_time, query_time])

print("\nDONE")