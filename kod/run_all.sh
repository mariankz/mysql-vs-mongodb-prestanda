#!/bin/bash

echo "=== START ALLA TESTER ==="

# =========================
# AI DATA
# =========================
echo "1/12 MySQL AI utan index..."
python test_mysql.py

echo "2/12 MySQL AI med index..."
python index_mysql.py

echo "3/12 MongoDB AI utan index..."
python test_mongo.py

echo "4/12 MongoDB AI med index..."
python index_mongo.py


# =========================
# VERKLIG DATA
# =========================
echo "5/12 MySQL verklig utan index..."
python real_mysql_test.py

echo "6/12 MySQL verklig med index..."
python index_real_mysql.py

echo "7/12 MongoDB verklig utan index..."
python real_mongo_test.py

echo "8/12 MongoDB verklig med index..."
python index_real_mongo.py


# =========================
# PLOT
# =========================
echo "9/12 Skapar grafer..."
python plot_data.py

echo "=== ALLA TESTER KLARA ==="
