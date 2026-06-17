import requests
import pandas as pd
from bs4 import BeautifulSoup

ROLE_MAP = {
    "HR-менеджер": "HR Manager",
    "Фахівець роздрібної торгівлі": "Retail Specialist",
    "Менеджер з продажу": "Sales Manager",
    "Програміст": "Developer",
    "Маркетолог": "Marketing Specialist",
    "Логіст": "Logistics Specialist",
}

# ---- Work.ua ----
def get_workua_salary(role_ua):
    try:
        r = requests.get("https://www.work.ua/stat/", timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        tables = soup.find_all("table")

        for table in tables:
            rows = table.find_all("tr")
            for row in rows[1:]:
                cols = [c.get_text(strip=True) for c in row.find_all("td")]
                if len(cols) >= 2:
                    job_title, salary = cols[0], cols[1]
                    if role_ua.lower() in job_title.lower():
                        return pd.DataFrame([{"Role": role_ua, "Salary": salary, "Source": "Work.ua"}])

        return pd.DataFrame([{"Role": role_ua, "Salary": "Не вказано", "Source": "Work.ua"}])
    except Exception:
        return pd.DataFrame([{"Role": role_ua, "Salary": "Не вказано", "Source": "Work.ua"}])

# ---- Rabota.ua ----
def get_rabota_salary(role_ua):
    try:
        url = f"https://rabota.ua/zapros/{role_ua}"
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        salaries = [s.get_text(strip=True) for s in soup.select(".card-salary") if s.get_text(strip=True)]

        if salaries:
            return pd.DataFrame([{"Role": role_ua, "Salary": "; ".join(salaries), "Source": "Rabota.ua"}])
        else:
            return pd.DataFrame([{"Role": role_ua, "Salary": "Не вказано", "Source": "Rabota.ua"}])
    except Exception:
        return pd.DataFrame([{"Role": role_ua, "Salary": "Не вказано", "Source": "Rabota.ua"}])

# ---- Djinni ----
def get_djinni_salary(role_ua):
    try:
        url = f"https://djinni.co/jobs/?keywords={role_ua}"
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        salaries = [s.get_text(strip=True) for s in soup.select(".public-salary") if s.get_text(strip=True)]

        if salaries:
            return pd.DataFrame([{"Role": role_ua, "Salary": "; ".join(salaries), "Source": "Djinni"}])
        else:
            return pd.DataFrame([{"Role": role_ua, "Salary": "Не вказано", "Source": "Djinni"}])
    except Exception:
        return pd.DataFrame([{"Role": role_ua, "Salary": "Не вказано", "Source": "Djinni"}])

# ---- grc.ua ----
def get_grc_salary(role_ua):
    try:
        url = f"https://grc.ua/search/vacancy?text={role_ua}"
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        salaries = [s.get_text(strip=True) for s in soup.select(".vacancy-serp-item__compensation") if s.get_text(strip=True)]

        if salaries:
            return pd.DataFrame([{"Role": role_ua, "Salary": "; ".join(salaries), "Source": "grc.ua"}])
        else:
            return pd.DataFrame([{"Role": role_ua, "Salary": "Не вказано", "Source": "grc.ua"}])
    except Exception:
        return pd.DataFrame([{"Role": role_ua, "Salary": "Не вказано", "Source": "grc.ua"}])

# ---- DOU ----
def get_dou_salary(role_en):
    try:
        url = f"https://jobs.dou.ua/salaries/{role_en.lower().replace(' ', '-')}/"
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        salary = soup.select_one(".average-salary")
        if salary:
            return pd.DataFrame([{"Role": role_en, "Salary": salary.get_text(strip=True), "Source": "DOU"}])
        else:
            return pd.DataFrame([{"Role": role_en, "Salary": "Не вказано", "Source": "DOU"}])
    except Exception:
        return pd.DataFrame([{"Role": role_en, "Salary": "Не вказано", "Source": "DOU"}])

# ---- World Bank ----
def get_worldbank_salary(role_en):
    return pd.DataFrame([{"Role": role_en, "Salary": "Не вказано", "Source": "World Bank"}])

# ---- Об’єднання ----
def get_market_data(role_ua):
    role_en = ROLE_MAP.get(role_ua, role_ua)  # переклад у англійську

    dfs = [
        get_workua_salary(role_ua),
        get_rabota_salary(role_ua),
        get_djinni_salary(role_ua),
        get_grc_salary(role_ua),
        get_dou_salary(role_en),
        get_worldbank_salary(role_en)
    ]
    result = pd.concat([df for df in dfs if not df.empty], ignore_index=True)
    return result
