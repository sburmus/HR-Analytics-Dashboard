import pandas as pd
import numpy as np
import json
from datetime import datetime

# === Функція для отримання ринкових зарплат із JSON (Work.ua/DOU) ===
def get_market_data(role_ua: str):
    try:
        with open("market_salaries.json", "r", encoding="utf-8") as f:
            content = json.load(f)
        salaries = content.get("data", {})
        updated = content.get("updated", datetime.now().strftime("%Y-%m-%d"))
        if role_ua in salaries:
            return {
                "source": "Work.ua/DOU",
                "salary": int(salaries[role_ua]),
                "updated": updated
            }
        else:
            return {
                "source": "Work.ua/DOU",
                "salary": "Не вказано",
                "updated": updated
            }
    except Exception as e:
        return {
            "source": "Error",
            "salary": "Не вказано",
            "updated": datetime.now().strftime("%Y-%m-%d"),
            "error": str(e)
        }

# === Функція для генерації випадкових власних досліджень ринку ===
def generate_random_market_research():
    roles = [
        "Програміст", "HR-менеджер", "Маркетолог",
        "Касир", "Бариста", "Бухгалтер", "Менеджер з продажу",
        "Адміністратор", "Директор"
    ]
    data = []
    for role in roles:
        salary = np.random.randint(20000, 80000)  # випадкова зарплата
        data.append({
            "Role": role,
            "Market_Salary": salary,
            "Source": "Власне дослідження",
            "Date": datetime.now().strftime("%Y-%m-%d")
        })
    return pd.DataFrame(data)
