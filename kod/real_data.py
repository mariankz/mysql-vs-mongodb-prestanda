import json
import random
from datetime import datetime

whatsapp_file = "WhatsApp Chat with Kaggle_Community Discussions.txt"
output_json_file = "real_data.json"

real_data = []

print("Kör en konvertering utan krånglig textmatchning...")

try:
    with open(whatsapp_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if " - " in line:
                time_part, content_part = line.split(" - ", 1)
                if ":" in content_part:
                    author, message_text = content_part.split(":", 1)
                    message_text = message_text.strip()
                else:
                    message_text = content_part.strip()
                
                if not message_text or "encrypted" in message_text or "created group" in message_text:
                    continue
                
                fake_hour = random.randint(0, 23)
                fake_minute = random.randint(0, 59)
                fake_second = random.randint(0, 59)
                fake_day = random.randint(1, 28)
                
                timestamp_iso = f"2024-05-{fake_day:02d}T{fake_hour:02d}:{fake_minute:02d}:{fake_second:02d}.000000Z"
                
                real_data.append({
                    "userId": random.randint(1, 1000),
                    "timestamp": timestamp_iso,
                    "message": message_text
                })

    with open(output_json_file, "w", encoding="utf-8") as f:
        json.dump(real_data, f, indent=2, ensure_ascii=False)

    print(f"\nLyckades rädda och konvertera {len(real_data)} rader!")
    print(f"Filen '{output_json_file}' har skapats i din mapp.")

except FileNotFoundError:
    print(f"Fel: Kunde inte hitta filen '{whatsapp_file}'.")
