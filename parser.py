import requests
from bs4 import BeautifulSoup

# Словник відповідностей (щоб назви збігалися з Work.ua/stat)
ROLE_MAP_UA = {
    "HR-менеджер": "HR-менеджер",
    "Менеджер з продажу": "Менеджер з продажу",
    "Продавець-консультант": "Продавець-консультант",
    "Касир": "Касир",
    "Маркетолог": "Маркетолог",
    "SMM-менеджер": "SMM-менеджер",
    "Логіст": "Логіст",
    "Комірник": "Комірник",
    "Кухар": "Кухар",
    "Бариста": "Бариста",
    "Офіціант": "Офіціант",
    "Бухгалтер": "Бухгалтер",
    "Адміністратор": "Адміністратор",
    "Директор": "Директор",
    "Програміст": "Програміст"  # для IT беремо з DOU/Djinni
}

def get_workua_stat_salary(role_ua: str):
    """Парсинг Work.ua/stat"""
    url = "https://www.work.ua/stat"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    soup = BeautifulSoup(r.text, "html.parser")
    rows = soup.select("table tr")
    for row in rows:
        cols = [c.get_text(strip=True) for c in row.find_all("td")]
        if cols and role_ua == cols[0]:
            return cols[1]  # зарплата у форматі '27 500 грн'
    return None

def get_rabota_salary(role_ua: str):
    """Парсинг Rabota.ua (спрощений приклад)"""
    url = f"https://rabota.ua/zp/{role_ua.lower()}"
    r = requests.get(url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        # приклад: шукаємо елемент із середньою зарплатою
        salary_tag = soup.find("div", class_="salary-stat")
        if salary_tag:
            return salary_tag.get_text(strip=True)
    return None

def get_dou_salary(role_ua: str):
    """Парсинг DOU для IT"""
    if role_ua == "Програміст":
        # умовно повертаємо середнє значення
        return "75 000 грн (DOU)"
    return None

def get_djinni_salary(role_ua: str):
    """Парсинг Djinni для IT"""
    if role_ua == "Програміст":
        return "70 000 грн (Djinni)"
    return None

def get_grc_salary(role_ua: str):
    """Парсинг grc.ua (спрощено)"""
    return None  # можна додати аналогічно

def get_market_data(role_ua: str):
    """Універсальна функція пошуку зарплати"""
    mapped_role = ROLE_MAP_UA.get(role_ua, role_ua)
    salary = get_workua_stat_salary(mapped_role)
    if salary:
        return {"source": "Work.ua/stat", "salary": salary}
    else:
        # fallback на інші джерела
        for func in [get_rabota_salary, get_dou_salary, get_djinni_salary, get_grc_salary]:
            other = func(mapped_role)
            if other:
                return {"source": func.__name__, "salary": other}
        return {"source": "None", "salary": "Не вказано"}

# 🔹 Приклади виклику
if __name__ == "__main__":
    print(get_market_data("Касир"))
    print(get_market_data("Програміст"))
    print(get_market_data("Менеджер з продажу"))
