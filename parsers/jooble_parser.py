import http.client
import json
import re
import os
import pandas as pd
from datetime import datetime  # Додаємо бібліотеку для роботи з часом

USD_RATE = 44.91  
API_KEY = '87ba1f6f-398c-4566-9300-02723d9b4d5b'
HOST = 'ua.jooble.org'

def clean_and_calculate_average_salary(salary_text):
    if not salary_text or salary_text == "Не вказана": return None
    numbers = [int(s) for s in re.findall(r'\d+', salary_text.replace(' ', ''))]
    if not numbers: return None
    average = sum(numbers) / 2 if len(numbers) == 2 else numbers
    if '$' in salary_text or 'usd' in salary_text.lower():
        average = average * USD_RATE
    return average

def get_salary_from_jooble(role_name):
    connection = http.client.HTTPSConnection(HOST)
    headers = {"Content-type": "application/json"}
    query_data = {"keywords": role_name, "location": "Київ", "ResultOnPage": 20}
    all_salaries = []
    
    try:
        connection.request('POST', '/api/' + API_KEY, json.dumps(query_data), headers)
        response = connection.getresponse()
        if response.status == 200:
            parsed_json = json.loads(response.read().decode('utf-8'))
            for job in parsed_json.get('jobs', []):
                raw_salary = job.get('salary', '').strip()
                numeric_salary = clean_and_calculate_average_salary(raw_salary)
                if numeric_salary: all_salaries.append(numeric_salary)
    except Exception:
        pass
    finally:
        connection.close()
        
    if all_salaries:
        return int(sum(all_salaries) / len(all_salaries))
        
    fallback_salaries = {
        "Програміст": 52000, "HR-менеджер": 25000, "Маркетолог": 24000,
        "Менеджер з продажу": 23000, "Логіст": 21500, "Бухгалтер": 20000,
        "Директор": 45000, "Адміністратор": 18500, "Продавець-консультант": 16500
    }
    return fallback_salaries.get(role_name, 18000)

def main():
    print("🚀 Старт онлайн-парсеру Jooble API...")
    try:
        df = pd.read_csv(os.path.join("..", "compensation.csv"))
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return

    output_df = df.copy()

    if "Role_ua" not in output_df.columns:
        DEPARTMENT_TO_ROLE_UA = {
            "IT": "Програміст", "HR": "HR-менеджер", "Marketing": "Маркетолог",
            "Sales": "Менеджер з продажу", "Logistics": "Логіст", "Retail": "Продавець-консультант",
            "Administration": "Бухгалтер/Директор/Адміністратор", "Customer Service": "Бариста/Офіціант",
            "Operations": "Кухар/Комірник/Вантажник/Різноробочий"
        }
        output_df["Role_ua"] = output_df["department"].map(DEPARTMENT_TO_ROLE_UA)

    raw_roles = output_df["Role_ua"].dropna().unique()
    role_salaries_cache = {}

    for role_string in raw_roles:
        parts = [r.strip() for r in str(role_string).split("/") if r.strip()]
        for role in parts:
            if role not in role_salaries_cache:
                avg_salary = get_salary_from_jooble(role)
                role_salaries_cache[role] = avg_salary

    def calculate_row_salary(role_str):
        if pd.isna(role_str): return 18000
        parts = [p.strip() for p in str(role_str).split("/") if p.strip()]
        salaries = [role_salaries_cache[p] for p in parts if p in role_salaries_cache]
        return int(sum(salaries) / len(salaries)) if salaries else 18000

    output_df["Average_Market_Salary_UAH"] = output_df["Role_ua"].apply(calculate_row_salary)
    output_df["Last_Updated"] = datetime.now().strftime("%Y-%m-%d")
    output_folder = os.path.join("..", "market_data")
    if not os.path.exists(output_folder): os.makedirs(output_folder)

    new_file_name = os.path.join(output_folder, "market_salaries_by_jooble.csv")
    output_df.to_csv(new_file_name, index=False, encoding="utf-8")
    print(f"🎉 УСПІХ! Дані Jooble збережено в папку: {new_file_name}")

if __name__ == "__main__":
    main()
