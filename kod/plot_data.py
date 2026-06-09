import matplotlib
matplotlib.use('Agg')

import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

# ==========================================
# 1. SÖKVÄGAR
# ==========================================
mysql_dir = "results/mysql"
mongo_dir = "results/mongo"
mysql_index_dir = "results/mysql_index"
mongo_index_dir = "results/mongo_index"

output_dir = "results"
os.makedirs(output_dir, exist_ok=True)

# ==========================================
# 2. LADDA DATA
# ==========================================
mysql_single = pd.read_csv(f"{mysql_dir}/single.csv")
mysql_multi = pd.read_csv(f"{mysql_dir}/multi.csv")
mongo_single = pd.read_csv(f"{mongo_dir}/single.csv")
mongo_multi = pd.read_csv(f"{mongo_dir}/multi.csv")

mysql_single_index = pd.read_csv(f"{mysql_index_dir}/single_index.csv")
mongo_single_index = pd.read_csv(f"{mongo_index_dir}/single_index.csv")

mysql_single_real = pd.read_csv(f"{mysql_dir}/single_real.csv")
mongo_single_real = pd.read_csv(f"{mongo_dir}/single_real.csv")

mysql_single_real_index = pd.read_csv(f"{mysql_index_dir}/single_real_index.csv")
mongo_single_real_index = pd.read_csv(f"{mongo_index_dir}/single_real_index.csv")

# ==========================================
# 3. FIXA KOLUMNNAMN
# ==========================================
for df in [mysql_single_real, mongo_single_real, mysql_single_real_index, mongo_single_real_index]:
    df.rename(columns={"target_rows": "size", "query_time": "query", "insert_time": "insert"}, inplace=True)

# ==========================================
# 4. MEDELVÄRDE PER DATAMÄNGD
# Medelvärde (mean) beräknar representativt värde per datamängd
# ==========================================
mysql_single_avg = mysql_single.groupby("size").mean()
mysql_multi_avg = mysql_multi.groupby("size").mean()
mongo_single_avg = mongo_single.groupby("size").mean()
mongo_multi_avg = mongo_multi.groupby("size").mean()

mysql_single_index_avg = mysql_single_index.groupby("size").mean()
mongo_single_index_avg = mongo_single_index.groupby("size").mean()

mysql_single_real_avg = mysql_single_real.groupby("size").mean()
mongo_single_real_avg = mongo_single_real.groupby("size").mean()

mysql_single_real_index_avg = mysql_single_real_index.groupby("size").mean()
mongo_single_real_index_avg = mongo_single_real_index.groupby("size").mean()

for df in [mysql_single_avg, mysql_multi_avg, mongo_single_avg, mongo_multi_avg,
           mysql_single_index_avg, mongo_single_index_avg,
           mysql_single_real_avg, mongo_single_real_avg,
           mysql_single_real_index_avg, mongo_single_real_index_avg]:
    df.index = df.index.astype(int)

# ==========================================
# 5. X-AXEL
# ==========================================
xticks = [100000, 250000, 500000, 750000, 1000000]
xlabels = ["100k", "250k", "500k", "750k", "1M"]

# ==========================================
# 6. DERIVATAFUNKTIONER
# ==========================================
# Millisekunder 
def derivative_milliseconds(series):
    x = series.index.to_numpy()
    y = series.to_numpy()

    deriv = np.gradient(y, x)

    return x, deriv * 100000 * 1000

# ==========================================
# FIGUR 6.1 - INSÄTTNING: MED VS UTAN INDEX
# ==========================================
plt.figure(figsize=(8, 5))

x, y = derivative_milliseconds(mysql_single_avg["insert"])
plt.plot(x, y, marker='o', color='#1f77b4', label="MySQL (utan index)")

x, y = derivative_milliseconds(mysql_single_index_avg["insert"])
plt.plot(x, y, marker='o', linestyle='--', color='#1f77b4', label="MySQL (med index)")

x, y = derivative_milliseconds(mongo_single_avg["insert"])
plt.plot(x, y, marker='s', color="#ff0e0e", label="MongoDB (utan index)")

x, y = derivative_milliseconds(mongo_single_index_avg["insert"])
plt.plot(x, y, marker='s', linestyle='--', color="#ff0e0e", label="MongoDB (med index)")

plt.xticks(xticks, xlabels)
plt.xlabel("Antal dataposter")
plt.ylabel("Snitt per post (ms)")
plt.title("Insättningstid med vs utan index (AI-data)")
plt.legend()
plt.grid(True, linestyle=":", alpha=0.6)

plt.savefig(f"{output_dir}/fig_6_1.png", dpi=300, bbox_inches="tight")
plt.close()


# ==========================================
# FIGUR 6.2 - INSÄTTNING: SEKVENTIELL VS PARALLELL
# ==========================================
plt.figure(figsize=(8, 5))

x, y = derivative_milliseconds(mysql_single_avg["insert"])
plt.plot(x, y, marker='o', color='#1f77b4', label="MySQL (sekventiell)")

x, y = derivative_milliseconds(mysql_multi_avg["insert"])
plt.plot(x, y, marker='o', linestyle='--', color='#1f77b4', label="MySQL (parallell)")

x, y = derivative_milliseconds(mongo_single_avg["insert"])
plt.plot(x, y, marker='s', color="#ff0e0e", label="MongoDB (sekventiell)")

x, y = derivative_milliseconds(mongo_multi_avg["insert"])
plt.plot(x, y, marker='s', linestyle='--', color="#ff0e0e", label="MongoDB (parallell)")

plt.xticks(xticks, xlabels)
plt.xlabel("Antal dataposter")
plt.ylabel("Snitt per post (ms)")
plt.title("Insättningstid vid sekventiell och parallell körning (AI-data)")
plt.legend()
plt.grid(True, linestyle=":", alpha=0.6)

plt.savefig(f"{output_dir}/fig_6_2.png", dpi=300, bbox_inches="tight")
plt.close()


# ==========================================
# FIGUR 6.3 - SÖK: MED VS UTAN INDEX
# ==========================================
plt.figure(figsize=(8, 5))

x, y = derivative_milliseconds(mysql_single_avg["query"])
plt.plot(x, y, marker='o', color='#1f77b4', label="MySQL (utan index)")

x, y = derivative_milliseconds(mysql_single_index_avg["query"])
plt.plot(x, y, marker='o', linestyle='--', color='#1f77b4', label="MySQL (med index)")

x, y = derivative_milliseconds(mongo_single_avg["query"])
plt.plot(x, y, marker='s', color="#ff0e0e", label="MongoDB (utan index)")

x, y = derivative_milliseconds(mongo_single_index_avg["query"])
plt.plot(x, y, marker='s', linestyle='--', color="#ff0e0e", label="MongoDB (med index)")

plt.xticks(xticks, xlabels)
plt.xlabel("Antal dataposter")
plt.ylabel("Snitt per post (ms)")
plt.title("Söktid med vs utan index (AI-data)")
plt.legend()
plt.grid(True, linestyle=":", alpha=0.6)

plt.savefig(f"{output_dir}/fig_6_3.png", dpi=300, bbox_inches="tight")
plt.close()


# ==========================================
# FIGUR 6.4 - SÖK: SEKVENTIELL VS PARALLELL
# ==========================================
plt.figure(figsize=(8, 5))

x, y = derivative_milliseconds(mysql_single_avg["query"])
plt.plot(x, y, marker='o', color='#1f77b4', label="MySQL (sekventiell)")

x, y = derivative_milliseconds(mysql_multi_avg["query"])
plt.plot(x, y, marker='o', linestyle='--', color='#1f77b4', label="MySQL (parallell)")

x, y = derivative_milliseconds(mongo_single_avg["query"])
plt.plot(x, y, marker='s', color="#ff0e0e", label="MongoDB (sekventiell)")

x, y = derivative_milliseconds(mongo_multi_avg["query"])
plt.plot(x, y, marker='s', linestyle='--', color="#ff0e0e", label="MongoDB (parallell)")

plt.xticks(xticks, xlabels)
plt.xlabel("Antal dataposter")
plt.ylabel("Snitt per post (ms)")
plt.title("Söktid vid sekventiell och parallell körning (AI-data)")
plt.legend()
plt.grid(True, linestyle=":", alpha=0.6)

plt.savefig(f"{output_dir}/fig_6_4.png", dpi=300, bbox_inches="tight")
plt.close()

# ==========================================
# 7. FYRFALTARE
# ==========================================
def rita_fyrfaltare(data_matrix, titel, filnamn, col):
    fig, ax = plt.subplots(figsize=(7, 6.5))
    
    farg_matrix = np.array([
        [[0.12, 0.47, 0.71], [0.94, 0.33, 0.31]],
        [[0.17, 0.63, 0.17], [0.98, 0.80, 0.18]]
    ])
    
    ax.imshow(farg_matrix, aspect='equal')

    for i in range(2):
        for j in range(2):
            val = data_matrix[i, j]
            text_color = '#0f172a' if (i == 1 and j == 1) else 'white'
            if col.lower() == "insert":
                text = f"{val:.0f}"
            else:
                text = f"{val:.2f}"

            ax.text(j, i, text, ha="center", va="center",
                    fontsize=24, fontweight='bold', color=text_color)

    ax.set_xticks([0, 1])
    ax.set_xticklabels(['MySQL', 'MongoDB'], fontsize=14, fontweight='bold', color='#1e293b')

    ax.set_yticks([0, 1])
    ax.set_yticklabels(['Verklig data', 'AI-data'], fontsize=14, fontweight='bold', color='#1e293b')

    ax.spines[:].set_visible(False)

    ax.set_xticks(np.arange(2.5) - 0.5, minor=True)
    ax.set_yticks(np.arange(2.5) - 0.5, minor=True)

    ax.grid(which="minor", color="white", linestyle='-', linewidth=6)

    ax.tick_params(which="minor", bottom=False, left=False)
    ax.tick_params(axis='both', which='both', length=0, pad=12)

    fig.text(0.5, 0.95, titel, ha='center',
             fontsize=14, fontweight='bold', color='#0f172a')

    plt.savefig(f"{output_dir}/{filnamn}.png", bbox_inches='tight', dpi=300)
    plt.close()

# ==========================================
# DELTA BERÄKNING
# ==========================================
def kolla_delta(df, kolumn):
    delta = df.loc[1000000, kolumn] - df.loc[100000, kolumn]
    antal_steg = (1000000 - 100000) / 100000
    return (delta / antal_steg) * 1000
# ==========================================
# FIGURER
# ==========================================
for titel, filnamn, col, use_index in [
    ("Medel soktid utan index (ms)", "fig_6_5a_query_utan", "query", False),
    ("Medel soktid med index (ms)", "fig_6_5b_query_med", "query", True),
    ("Medel insattningstid utan index (ms)", "fig_6_5c_insert_utan", "insert", False),
    ("Medel insattningstid med index (ms)", "fig_6_5d_insert_med", "insert", True),
]:
    mysql_real = mysql_single_real_index_avg if use_index else mysql_single_real_avg
    mongo_real = mongo_single_real_index_avg if use_index else mongo_single_real_avg
    mysql_ai = mysql_single_index_avg if use_index else mysql_single_avg
    mongo_ai = mongo_single_index_avg if use_index else mongo_single_avg

    matris = np.array([
        [kolla_delta(mysql_real, col), kolla_delta(mongo_real, col)],
        [kolla_delta(mysql_ai, col), kolla_delta(mongo_ai, col)]
    ])
    rita_fyrfaltare(matris, titel, filnamn, col)

print("Klart! Alla grafer har skapats.")
