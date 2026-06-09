# Jämförelse mellan MySQL och MongoDB vid hantering av tidsseriedata

## Om projektet

Detta repository innehåller källkod, testskript och resultat som använts i examensarbetet:

**"Jämförelse mellan MySQL och MongoDB vid hantering av tidsseriedata – Ett experimentellt arbete med fokus på AI-genererade data"**

Arbetet genomfördes vid Mittuniversitetet och syftar till att undersöka hur en relationsdatabas (MySQL) och en dokumentorienterad NoSQL-databas (MongoDB) presterar vid hantering av tidsseriedata.

Studien fokuserar på:

- Insättningsprestanda (INSERT)
- Sökprestanda (SELECT)
- Påverkan av indexering
- Sekventiell och parallell belastning
- Skillnader mellan AI-genererade och verkliga data
- Hur ökande datamängder påverkar prestandan

---

## Forskningsfrågor

Projektet utgår från följande forskningsfrågor:

1. Hur skiljer sig transaktionstid mellan MySQL och MongoDB vid olika datamängder och typer av insättningar?

2. Hur skiljer sig tiden för transaktion mellan MySQL och MongoDB vid sökningar baserade på userId och tidsintervall, samt hur påverkas den av användning av index?

3. Hur påverkas prestandan i MySQL och MongoDB av ökande datamängder?

---

## Projektstruktur

```text
.
├── kod/                # Python-skript för tester och analys
├── data/               # AI-genererade och verkliga testdata
├── results/            # Resultat från genomförda tester
├── drawio/             # Diagram och modeller
├── README.md
└── requirements.txt
```

---

## Källkod

### Databastester

| Fil | Beskrivning |
|------|-------------|
| test_mysql.py | Sekventiella tester för MySQL |
| test_mongo.py | Sekventiella tester för MongoDB |
| real_mysql_test.py | Tester med verkliga data i MySQL |
| real_mongo_test.py | Tester med verkliga data i MongoDB |
| index_mysql.py | Tester med index i MySQL |
| index_mongo.py | Tester med index i MongoDB |
| index_real_mysql.py | Indexerade tester med verkliga data i MySQL |
| index_real_mongo.py | Indexerade tester med verkliga data i MongoDB |
| db_mysql.py | Databasanslutning och hantering för MySQL |
| plot_data.py | Generering av diagram och visualiseringar |
| run_all.sh | Kör samtliga tester automatiskt |

---

## Testdata

Två typer av data används i studien:

### AI-genererad data

Syntetiskt genererade chattmeddelanden med:

- userId
- tidsstämpel
- meddelandetext

Syftet är att skapa kontrollerbara och reproducerbara testförhållanden.

### Verklig data

Anonymiserade chattloggar från en offentlig Kaggle-dataset.

Data har bearbetats för att minska identifierbar information innan testerna genomfördes.

---

## Genomförda tester

### Insättningstester

Datamängder:

- 100 000 poster
- 250 000 poster
- 500 000 poster
- 750 000 poster
- 1 000 000 poster

Mätvärde:

- Exekveringstid

---

### Söktester

Sökningar baserade på:

- userId
- tidsintervall

Mätvärde:

- Söktid

---

### Belastningstester

Två scenarier jämförs:

- Sekventiell körning
- Parallell körning med flera samtidiga trådar

---

### Indexering

Samtliga tester genomförs:

- Utan index
- Med index

för att analysera indexeringens påverkan på prestandan.

---

## Installation

### Klona projektet

```bash
git clone https://github.com/DITT_ANVÄNDARNAMN/mysql-vs-mongodb-prestanda.git
cd mysql-vs-mongodb-prestanda
```

### Installera beroenden

```bash
pip install -r requirements.txt
```

---

## Använda tekniker

- Python
- MySQL
- MongoDB
- Pandas
- NumPy
- Matplotlib
- PyMongo
- MySQL Connector

---

## Resultat

Resultaten visar att:

- MongoDB generellt presterar bättre vid insättningar.
- MySQL i vissa fall presterar bättre vid sökningar.
- Indexering påverkar sökprestandan men effekten varierar mellan testfall.
- AI-genererade data gav ofta lägre exekveringstider än verkliga data.
- Valet av testdata kan påverka resultatet av prestandamätningar.

För fullständig analys hänvisas till examensrapporten.

---

## Författare

Maria Nekzada

Kandidatexamensarbete i Datateknik (15 hp)

Mittuniversitetet

Vårterminen 2026

Detta repository innehåller källkod och experimentella resultat som använts i examensarbetet för att jämföra prestandan hos MySQL och MongoDB vid hantering av tidsseriedata.
