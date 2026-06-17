import json
import os
from datetime import datetime, timedelta

MARKET_FILE = "market_salaries.json"

# 🔹 Словник зарплат одразу як числа
DEFAULT_SALARIES = {
    "Продавець-консультант": 23500,
    "Менеджер з продажу": 37500,
    "Комірник": 28500,
    "Кухар": 31500,
    "Водій": 37500,
    "Касир": 22500,
    "Бариста": 24000,
    "HR-менеджер": 32000,
    "Маркетолог": 35000,
    "SMM-менеджер": 30000,
    "Бухгалтер": 33000,
    "Директор": 60000,
    "Програміст": 75000
    # ... решта посад
}

def update_market_salaries():
    with open(MARKET_FILE, "w", encoding="utf-8") as f:
        json.dump({"updated": datetime.now().isoformat(), "data": DEFAULT_SALARIES},
                  f, ensure_ascii=False, indent=2)

def load_market_salaries():
    if not os.path.exists(MARKET_FILE):
        update_market_salaries()
    with open(MARKET_FILE, "r", encoding="utf-8") as f:
        content = json.load(f)

    updated = datetime.fromisoformat(content["updated"])
    if datetime.now() - updated > timedelta(days=30):
        update_market_salaries()
        with open(MARKET_FILE, "r", encoding="utf-8") as f:
            content = json.load(f)

    return content["data"], content["updated"]

def get_market_data(role_ua: str):
    salaries, updated = load_market_salaries()
    if role_ua in salaries:
        return {"source": "Work.ua/stat", "salary": int(salaries[role_ua]), "updated": updated}
    else:
        return {"source": "None", "salary": "Не вказано", "updated": updated}
