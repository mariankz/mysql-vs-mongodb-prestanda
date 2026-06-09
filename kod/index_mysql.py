import os
import time
import csv
import threading
import json
import random
from db_mysql import connect
from datetime import datetime


def format_timestamp(ts):
    ts = ts.replace("Z", "")
    if "." in ts:
        ts = ts.split(".")[0]
    dt = datetime.fromisoformat(ts)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


# ===== LADDA AI DATA =====
file_path = os.path.join(os.path.dirname(__file__), "ai_data.json")

with open(file_path, "r") as f:
    ai_data = json.load(f)


def generate_data(batch_size):
    batch = []
    for _ in range(batch_size):
        item = random.choice(ai_data)
        batch.append((
            int(item["userId"]),
            format_timestamp(item["timestamp"]),
            item["message"]
        ))
    return batch


# ===== OUTPUT =====
output_dir = "results/mysql_index"
os.makedirs(output_dir, exist_ok=True)

# 🔥 Rensa databasen innan alla tester
conn, cursor = connect()
cursor.execute("TRUNCATE TABLE messages")
conn.commit()
conn.close()
print("Databas rensad")


# ===== SETUP INDEX =====
def setup_index():
    conn, cursor = connect()

    cursor.execute("""
        SELECT COUNT(*) FROM information_schema.statistics
        WHERE table_schema = DATABASE()
        AND table_name = 'messages'
        AND index_name = 'idx_userId_timestamp'
    """)

    if cursor.fetchone()[0] > 0:
        cursor.execute("DROP INDEX idx_userId_timestamp ON messages")

    cursor.execute("CREATE INDEX idx_userId_timestamp ON messages (userId, timestamp)")
    conn.commit()
    conn.close()

    print("Index skapat: userId + timestamp")


setup_index()

# ===== INSERT =====
def test_insert(size, batch_size=1000):
    conn, cursor = connect()
    start = time.time()

    for i in range(0, size, batch_size):
        batch = generate_data(batch_size)

        cursor.executemany(
            "INSERT INTO messages (userId, timestamp, message) VALUES (%s, %s, %s)",
            batch
        )
        conn.commit()

    conn.close()
    return time.time() - start


# ===== SELECT =====
def test_query():
    conn, cursor = connect()
    start = time.time()

    cursor.execute("""
        SELECT * FROM messages 
        WHERE userId BETWEEN 1 AND 50
        AND timestamp BETWEEN '2026-01-01 00:00:00' 
        AND '2026-12-31 23:59:59'
    """)

    cursor.fetchall()
    conn.close()
    return time.time() - start


# ===== SEKVENTIELLT TEST =====
sizes = [100000, 250000, 500000, 750000, 1000000]

with open(f"{output_dir}/single_index.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow(["size", "run", "insert", "query"])

    for size in sizes:
        print(f"\nTesting {size} rows (single user)...")

        for run in range(1, 6):
            print(f"  Run {run}/5")

            # Rensa data (index kvar!)
            conn, cursor = connect()
            cursor.execute("TRUNCATE TABLE messages")
            conn.commit()
            conn.close()

            insert_time = test_insert(size)
            query_time = test_query()

            print(f"    Insert: {insert_time:.4f}s | Query: {query_time:.6f}s")
            writer.writerow([size, run, insert_time, query_time])


# ===== PARALLELL WORKER =====
def worker(size):
    conn, cursor = connect()
    batch_size = 1000

    for i in range(0, size, batch_size):
        batch = generate_data(batch_size)

        cursor.executemany(
            "INSERT INTO messages (userId, timestamp, message) VALUES (%s, %s, %s)",
            batch
        )
        conn.commit()

    conn.close()


def run_parallel_test(size, users=5):
    conn, cursor = connect()
    cursor.execute("TRUNCATE TABLE messages")
    conn.commit()
    conn.close()

    per_user = size // users
    threads = []

    start_insert = time.time()

    for _ in range(users):
        t = threading.Thread(target=worker, args=(per_user,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    insert_time = time.time() - start_insert
    query_time = test_query()

    return insert_time, query_time


# ===== PARALLELLT TEST =====
with open(f"{output_dir}/multi_index.csv", "w") as f:
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