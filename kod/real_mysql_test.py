import os
import json
import time
import random
import csv
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from db_mysql import connect 

# ===== LOAD REAL DATA =====
file_path = os.path.join(os.path.dirname(__file__), "real_data.json")
with open(file_path, "r", encoding="utf-8") as f:
    real_data = json.load(f)

def format_timestamp(ts_str):
    dt = datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    return dt.strftime("%Y-%m-%d %H:%M:%S")

# ===== GENERATE DATA =====
def generate_data(batch_size):
    batch = []

    while len(batch) < batch_size:
        item = random.choice(real_data)
        msg = item["message"]

        if msg.startswith("~"):
            continue

        formatted_time = format_timestamp(item["timestamp"])
        batch.append((item["userId"], formatted_time, msg))

    return batch

# ===== INSERT TEST =====
def test_insert(cursor, conn, total_rows, batch_size=1000):
    start_time = time.time()
    inserted = 0

    while inserted < total_rows:
        remaining = total_rows - inserted
        current_batch_size = min(batch_size, remaining) 

        batch = generate_data(current_batch_size)

        cursor.executemany(
            "INSERT INTO messages (userId, timestamp, message) VALUES (%s, %s, %s)", 
            batch
        )
        conn.commit()

        inserted += current_batch_size

    return time.time() - start_time

# ===== QUERY TEST =====
def test_query(cursor):
    start_time = time.time()

    cursor.execute("""
        SELECT * FROM messages 
        WHERE userId BETWEEN 1 AND 50
        AND timestamp BETWEEN '2024-01-01 00:00:00' AND '2024-12-31 23:59:59'
    """)
    cursor.fetchall()

    return time.time() - start_time

# ===== WORKER (MULTI USER) =====
def worker_task(total_rows_per_thread):
    worker_conn, worker_cursor = connect()

    ins_t = test_insert(worker_cursor, worker_conn, total_rows_per_thread)
    qry_t = test_query(worker_cursor)

    worker_cursor.close()
    worker_conn.close()

    return ins_t, qry_t

# ===== SINGLE USER TEST =====
def run_single_user_tests():
    conn, cursor = connect()

    results_dir = "results/mysql"
    os.makedirs(results_dir, exist_ok=True)

    csv_path = os.path.join(results_dir, "single_real.csv")

    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["size", "run", "insert", "query"])

        for rows in [100000, 250000, 500000, 750000, 1000000]:
            print(f"[MySQL Real] Single-user test: {rows} rows")

            for run in range(1, 6):
                cursor.execute("TRUNCATE TABLE messages")
                conn.commit()

                ins_t = test_insert(cursor, conn, rows)
                qry_t = test_query(cursor)

                writer.writerow([rows, run, ins_t, qry_t])
                f.flush()

    cursor.close()
    conn.close()

# ===== MULTI USER TEST =====
def run_multi_user_tests():
    conn, cursor = connect()

    results_dir = "results/mysql"
    csv_path = os.path.join(results_dir, "multi_real.csv")

    num_threads = 5

    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["size", "run", "insert", "query"])

        for rows in [100000, 250000, 500000, 750000, 1000000]:
            print(f"[MySQL Real] Multi-user test (5 threads): {rows} rows")

            rows_per_thread = rows // num_threads

            for run in range(1, 6):
                cursor.execute("TRUNCATE TABLE messages")
                conn.commit()

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

    cursor.close()
    conn.close()

# ===== MAIN =====
if __name__ == "__main__":
    print("=== START REAL DATA TESTS (MYSQL) ===")

    run_single_user_tests()

    print("-" * 50)

    run_multi_user_tests()

    print("=== DONE! RESULTS SAVED ===")
