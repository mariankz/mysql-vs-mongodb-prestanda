import datetime
import json
import requests
import random

TOTAL_BATCHES = 20
MESSAGES_PER_BATCH = 20

data = []

current_time = datetime.datetime.now() - datetime.timedelta(days=1)

for b in range(TOTAL_BATCHES):
    print(f"Genererar batch {b+1}/{TOTAL_BATCHES}...")

    prompt = f"""
    Generate a JSON array containing EXACTLY {MESSAGES_PER_BATCH} unique, realistic chat messages.
    Each item in the array should just be a string representing the message text.
    Make the messages look like a real public chatroom (casual conversation, tech talk, greetings, questions).
    Return ONLY the raw JSON array. No markdown, no explanations.
    Each item must be a plain string, not an object.
    Do NOT return objects with keys like msg or text.
    """

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.1:8b",
                "prompt": prompt,
                "stream": False,
                "temperature": 0.7,
            },
        )

        result = response.json()["response"]

        # Extrahera JSON-arrayen
        start = result.find("[")
        end = result.rfind("]") + 1

        if start == -1 or end == 0:
            print(f"Felaktigt JSON-format i batch {b+1}")
            continue

        clean = result[start:end]

        messages_list = json.loads(clean)

        for msg in messages_list:

            if isinstance(msg, dict):
                if "msg" in msg:
                    msg = msg["msg"]
                elif "text" in msg:
                    msg = msg["text"]
                else:
                    continue 

            current_time += datetime.timedelta(
                seconds=random.randint(5, 30),
                milliseconds=random.randint(0, 999)
            )

            obj = {
                "userId": random.randint(1, 1000),
                "timestamp": current_time.isoformat() + "Z",
                "message": msg,
            }

            data.append(obj)

    except Exception as e:
        print(f"Fel vid batch {b+1}: {e}")
        continue


with open("ai_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Klart! Totalt genererades {len(data)} tidsserie-rader.")