import pandas as pd
import re
import os
from bs4 import BeautifulSoup
from datetime import datetime  # Додаємо бібліотеку для роботи з часом

def clean_and_calculate_average_salary(salary_text):
    if not salary_text or salary_text == "Не вказана":
        return None
    numbers = [int(s) for s in re.findall(r'\d+', salary_text.replace(' ', ''))]
    if not numbers:
        return None
    return sum(numbers) / 2 if len(numbers) == 2 else numbers

def main():
    print("🚀 Старт локального парсера Work.ua...")
    
    # Крок 1. Читаємо вхідний файл, який лежить на один рівень вище (в головній папці)
    try:
        df = pd.read_csv(os.path.join("..", "compensation.csv"))
        print("✅ Початковий файл compensation.csv зчитано.")
    except Exception as e:
        print(f"❌ Помилка: Помістіть compensation.csv в головну папку: {e}")
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

    # Крок 2. Парсимо HTML-файл з Робочого столу
    html_path = r"C:\Users\svitl\OneDrive\Робочий стіл\ПРоект\scripts\Середня зарплата в Україні — Work.ua_files"
    html_salaries_cache = {}
    
    try:
        with open(html_path, encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
        print("✅ HTML-файл статистики Work.ua успішно зчитано.")
        
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows[1:]:
                cols = row.find_all("td")
                if len(cols) >= 2:
                    role_name = cols[0].get_text(strip=True).lower()
                    salary_val = cols[1].get_text(strip=True)
                    html_salaries_cache[role_name] = salary_val
    except Exception as e:
        print(f"⚠️ Не вдалося знайти файл на Робочому столі: {e}. Працюють резервні константи.")

    raw_roles = output_df["Role_ua"].dropna().unique()
    role_salaries_cache = {}

    # Крок 3. Збір та очищення
    for role_string in raw_roles:
        parts = [r.strip() for r in str(role_string).split("/") if r.strip()]
        for role in parts:
            if role not in role_salaries_cache:
                raw_salary = html_salaries_cache.get(role.lower(), "")
                avg_salary = clean_and_calculate_average_salary(raw_salary)
                
                if avg_salary:
                    role_salaries_cache[role] = int(avg_salary)
                else:
                    fallback_salaries = {
                        "Програміст": 52000, "HR-менеджер": 25000, "Маркетолог": 24000,
                        "Менеджер з продажу": 23000, "Логіст": 21500, "Бухгалтер": 20000,
                        "Директор": 45000, "Адміністратор": 18500, "Продавець-консультант": 16500,
                        "Фахівець роздрібної торгівлі": 17000, "Бариста": 15500, "Офіціант": 15000,
                        "Кухар": 18000, "Комірник": 17500, "Вантажник": 16000, "Різноробочий": 14500
                    }
                    role_salaries_cache[role] = fallback_salaries.get(role, 18000)

    def calculate_row_salary(role_str):
        if pd.isna(role_str): return 18000
        parts = [p.strip() for p in str(role_str).split("/") if p.strip()]
        salaries = [role_salaries_cache[p] for p in parts if p in role_salaries_cache]
        return int(sum(salaries) / len(salaries)) if salaries else 18000

    output_df["Average_Market_Salary_UAH"] = output_df["Role_ua"].apply(calculate_row_salary)
    output_df["Last_Updated"] = datetime.now().strftime("%Y-%m-%d")
    # Крок 4. Збереження результату в папку market_data (на рівень вище)
    output_folder = os.path.join("..", "market_data")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    new_file_name = os.path.join(output_folder, "market_salaries_by_work.csv")
    output_df.to_csv(new_file_name, index=False, encoding="utf-8")
    print(f"🎉 УСПІХ! Дані Work.ua збережено в папку: {new_file_name}")

if __name__ == "__main__":
    main()
