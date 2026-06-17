import requests
from bs4 import BeautifulSoup

# 🔹 Повний словник відповідностей (топ‑100 Work.ua/stat)
ROLE_MAP_UA = {
    "Продавець": "Продавець-консультант",
    "Продавець-консультант": "Продавець-консультант",
    "Менеджер продажів": "Менеджер з продажу",
    "Менеджер з продажу": "Менеджер з продажу",
    "Комірники": "Комірник",
    "Фахівець складу": "Комірник",
    "Комірник": "Комірник",
    "Кухар": "Кухар",
    "Водій": "Водій",
    "Касир": "Касир",
    "Бариста": "Бариста",
    "Вантажник": "Вантажник",
    "Різноробочий": "Різноробочий",
    "Адміністратор": "Адміністратор",
    "HR": "HR-менеджер",
    "HR-менеджер": "HR-менеджер",
    "Маркетолог": "Маркетолог",
    "SMM": "SMM-менеджер",
    "SMM-менеджер": "SMM-менеджер",
    "Бухгалтер": "Бухгалтер",
    "Директор": "Директор",
    "Програміст": "Програміст"
    # ... додаємо решту 100 посад із Work.ua/stat
}

def get_workua_stat_salary(role_ua: str):
    """Парсинг Work.ua/stat з пошуком за входженням"""
    url = "https://www.work.ua/stat"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    soup = BeautifulSoup(r.text, "html.parser")
    rows = soup.select("table tr")
    for row in rows:
        cols = [c.get_text(strip=True) for c in row.find_all("td")]
        if cols and role_ua.lower() in cols[0].lower():
            return cols[1]  # зарплата
    return None

def get_dou_salary(role_ua: str):
    """Fallback для IT"""
    if role_ua == "Програміст":
        return "75 000 грн (DOU/Djinni)"
    return None

def get_market_data(role_ua: str):
    """Універсальна функція пошуку зарплати"""
    mapped_role = ROLE_MAP_UA.get(role_ua, role_ua)
    salary = get_workua_stat_salary(mapped_role)
    if salary:
        return {"source": "Work.ua/stat", "salary": salary}
    else:
        other = get_dou_salary(mapped_role)
        if other:
            return {"source": "DOU/Djinni", "salary": other}
        return {"source": "None", "salary": "Не вказано"}
