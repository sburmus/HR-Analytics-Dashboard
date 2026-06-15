import requests
from bs4 import BeautifulSoup
import pandas as pd

# --- Work.ua ---
def parse_workua(role: str, pages: int = 1) -> pd.DataFrame:
    results = []
    for page in range(1, pages+1):
        url = f"https://www.work.ua/jobs-{role}/?page={page}"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")

        jobs = soup.select("div.job-link")
        for job in jobs:
            title = job.select_one("h2 a").text.strip()
            salary_tag = job.select_one("div.add-top-xs span")
            salary = salary_tag.text.strip() if salary_tag else "Не вказано"
            results.append({"Role": role, "Salary": salary, "Source": "Work.ua"})
    return pd.DataFrame(results)

# --- Rabota.ua ---
def parse_rabotaua(role: str, pages: int = 1) -> pd.DataFrame:
    results = []
    for page in range(1, pages+1):
        url = f"https://rabota.ua/zapros/{role}/pg{page}"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")

        jobs = soup.select("div.card-body")
        for job in jobs:
            title = job.select_one("h2 a").text.strip()
            salary_tag = job.select_one("p.salary")
            salary = salary_tag.text.strip() if salary_tag else "Не вказано"
            results.append({"Role": role, "Salary": salary, "Source": "Rabota.ua"})
    return pd.DataFrame(results)

# --- Djinni.co ---
def parse_djinni(role: str, pages: int = 1) -> pd.DataFrame:
    results = []
    for page in range(1, pages+1):
        url = f"https://djinni.co/jobs/?keywords={role}&page={page}"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")

        jobs = soup.select("div.list-jobs__item")
        for job in jobs:
            title = job.select_one("div.list-jobs__title a").text.strip()
            salary_tag = job.select_one("span.public-salary-item")
            salary = salary_tag.text.strip() if salary_tag else "Не вказано"
            results.append({"Role": role, "Salary": salary, "Source": "Djinni"})
    return pd.DataFrame(results)

# --- LinkedIn Jobs (спрощено через пошук) ---
def parse_linkedin(role: str) -> pd.DataFrame:
    # LinkedIn має захист, тому тут краще використовувати API або Selenium
    # Для прикладу зробимо "заглушку"
    results = [
        {"Role": role, "Salary": "Не вказано", "Source": "LinkedIn Jobs"}
    ]
    return pd.DataFrame(results)

# --- Об’єднання всіх джерел ---
def get_market_data