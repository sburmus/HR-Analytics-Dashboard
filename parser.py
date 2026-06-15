import requests
import pandas as pd
from bs4 import BeautifulSoup

# === Словник посад з похідними назвами ===
ROLE_SYNONYMS = {
    "Маркетолог": ["Маркетолог", "Маркетинг-менеджер", "Менеджер з маркетингу"],
    "Менеджер з продажу": ["Менеджер з продажу", "Sales Manager", "Торговий представник"],
    "Логіст": ["Логіст", "Менеджер з логістики", "Logistics Specialist"],
    "HR-менеджер": ["HR-менеджер", "Менеджер з персоналу", "Кадровик", "HR Specialist"],
    "Програміст": ["Програміст", "Розробник", "Software Engineer", "Developer"],
    "Бухгалтер": ["Бухгалтер", "Accountant", "Фінансовий спеціаліст"],
    "Аналітик": ["Аналітик", "Data Analyst", "Business Analyst"],
    "Дизайнер": ["Дизайнер", "UI/UX Designer", "Графічний дизайнер"],
    "Тестувальник": ["Тестувальник", "QA Engineer", "Quality Assurance"],
}

# === Словник міст та областей ===
CITY_SYNONYMS = {
    "Київ": ["Київ", "м. Київ", "Київська область"],
    "Львів": ["Львів", "м. Львів", "Львівська область"],
    "Полтава": ["Полтава", "м. Полтава", "Полтавська область"],
    "Одеса": ["Одеса", "м. Одеса", "Одеська область"],
    "Харків": ["Харків", "м. Харків", "Харківська область"],
    "Дніпро": ["Дніпро", "м. Дніпро", "Дніпропетровська область"],
    "Запоріжжя": ["Запоріжжя", "м. Запоріжжя", "Запорізька область"],
    "Чернігів": ["Чернігів", "м. Чернігів", "Чернігівська область"],
    "Черкаси": ["Черкаси", "м. Черкаси", "Черкаська область"],
    "Вінниця": ["Вінниця", "м. Вінниця", "Вінницька область"],
    "Житомир": ["Житомир", "м. Житомир", "Житомирська область"],
    "Миколаїв": ["Миколаїв", "м. Миколаїв", "Миколаївська область"],
    "Херсон": ["Херсон", "м. Херсон", "Херсонська область"],
    "Суми": ["Суми", "м. Суми", "Сумська область"],
    "Рівне": ["Рівне", "м. Рівне", "Рівненська область"],
    "Тернопіль": ["Тернопіль", "м. Тернопіль", "Тернопільська область"],
    "Івано-Франківськ": ["Івано-Франківськ", "м. Івано-Франківськ", "Івано-Франківська область"],
    "Ужгород": ["Ужгород", "м. Ужгород", "Закарпатська область"],
    "Луцьк": ["Луцьк", "м. Луцьк", "Волинська область"],
    "Чернівці": ["Чернівці", "м. Чернівці", "Чернівецька область"],
    "Кропивницький": ["Кропивницький", "м. Кропивницький", "Кіровоградська область"],
}

# === Основна функція парсера ===
def get_market_data(role_ua: str, city: str = None) -> pd.DataFrame:
    """
    Отримує ринкові дані по зарплатах з Work.ua/stat.
    role_ua: назва посади українською
    city: місто або область
    """

    synonyms = ROLE_SYNONYMS.get(role_ua, [role_ua])
    city_variants = CITY_SYNONYMS.get(city, [city]) if city else [None]

    data = []

    try:
        url = "https://work.ua/stat/"
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows[1:]:
                cols = [c.get_text(strip=True) for c in row.find_all("td")]
                if len(cols) >= 2:
                    city_name, salary = cols[0], cols[1]
                    # перевіряємо всі варіанти міста/області
                    if any(city_name.lower() == variant.lower() for variant in city_variants if variant):
                        for synonym in synonyms:
                            data.append({
                                "Role_ua": synonym,
                                "City": city_name,
                                "Salary": salary if salary else "Не вказано",
                                "Source": "Work.ua"
                            })
    except Exception:
        data.append({
            "Role_ua": role_ua,
            "City": city if city else "—",
            "Salary": "Не вказано",
            "Source": "Work.ua (error)"
        })

    return pd.DataFrame(data, columns=["Role_ua", "City", "Salary", "Source"])
