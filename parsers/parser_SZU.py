import requests
import pandas as pd
import io
import os
from datetime import datetime  # Додаємо бібліотеку для роботи з часом

# Словник для точного пошуку в державній базі даних
DEPARTMENT_TO_SEARCH_KEYWORDS = {
    "IT": ["програміст", "системний адміністратор"],
    "HR": ["інспектор з кадрів", "менеджер з персоналу"],
    "Marketing": ["маркетолог"],
    "Sales": ["менеджер з продажу", "продавець"],
    "Logistics": ["логіст", "диспетчер"],
    "Retail": ["товарознавець", "касир"],
    "Administration": ["бухгалтер", "директор", "адміністратор"],
    "Customer Service": ["бариста", "офіціант"],
    "Operations": ["кухар", "комірник", "вантажник", "різноробочий"]
}

def main():
    print("🚀 Старт державного парсера Служби зайнятості (ДСЗ)...")
    print("1. Підключення до сервера відкритих даних...")
    
    # Офіційне пряме посилання на щоденний реєстр вакансій ДСЗ
    url = "https://dcz.gov.ua"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=60)
        
        if response.status_code != 200:
            print(f"❌ Не вдалося отримати файл від ДСЗ. Код сервера: {response.status_code}")
            return
            
        print("✅ 2. Державну базу вакансій успішно завантажено в пам'ять.")
        
        # Читаємо Excel через буфер пам'яті
        excel_buffer = io.BytesIO(response.content)
        df_state = pd.read_excel(excel_buffer)
        
        # Приводимо назви колонок до малого регістру
        df_state.columns = [str(col).strip().lower() for col in df_state.columns]
        
        posada_col = next((c for c in df_state.columns if 'посад' in c or 'назв' in c), None)
        salary_col = next((c for c in df_state.columns if 'зарп' in c or 'зп' in c or 'оклад' in c), None)
        
        if not posada_col or not salary_col:
            print("❌ Помилка: Структура файлу ДСЗ змінилася. Не знайдено колонки з посадами або ЗП.")
            return
            
        # 3. Читаємо вхідний файл, який лежить на рівень вище (в головній папці)
        try:
            df_user = pd.read_csv(os.path.join("..", "compensation.csv"))
            print("✅ 3. Початковий файл compensation.csv успішно зчитано.")
        except Exception as e:
            print(f"❌ Помилка: Помістіть compensation.csv в головну папку: {e}")
            return
            
        output_df = df_user.copy()
        
        # Створюємо стовпчик Role_ua, якщо його немає
        if "Role_ua" not in output_df.columns:
            DEPARTMENT_TO_ROLE_UA = {
                "IT": "Програміст", "HR": "HR-менеджер", "Marketing": "Маркетолог",
                "Sales": "Менеджер з продажу", "Logistics": "Логіст", "Retail": "Фахівець роздрібної торгівлі",
                "Administration": "Бухгалтер/Директор/Адміністратор", "Customer Service": "Бариста/Офіціант",
                "Operations": "Кухар/Комірник/Вантажник/Різноробочий"
            }
            output_df["Role_ua"] = output_df["department"].map(DEPARTMENT_TO_ROLE_UA)
            
        role_salaries_cache = {}
        print("🔍 4. Розрахунок середніх офіційних окладів Державної служби...")
        
        for dept, keywords in DEPARTMENT_TO_SEARCH_KEYWORDS.items():
            dept_salaries = []
            
            for keyword in keywords:
                state_filtered = df_state[df_state[posada_col].astype(str).str.lower().str.contains(keyword)]
                
                for _, row in state_filtered.iterrows():
                    try:
                        salary_val = int(float(str(row[salary_col]).replace(' ', '')))
                        if salary_val > 5000:  # Відсікаємо порожні або застарілі дані
                            dept_salaries.append(salary_val)
                    except:
                        continue
            
            # Визначаємо середній оклад для професії
            if dept_salaries:
                avg_salary = int(sum(dept_salaries) / len(dept_salaries))
            else:
                avg_salary = 18000  # Державна підстраховка
                
            for keyword in keywords:
                role_salaries_cache[keyword.capitalize()] = avg_salary
                
        def assign_salary(role_str):
            if pd.isna(role_str):
                return 18000
            parts = [p.strip().capitalize() for p in str(role_str).split("/") if p.strip()]
            salaries = [role_salaries_cache.get(p, 18000) for p in parts]
            return int(sum(salaries) / len(salaries)) if salaries else 18000
            
        output_df["Average_Market_Salary_UAH"] = output_df["Role_ua"].apply(assign_salary)
        output_df["Last_Updated"] = datetime.now().strftime("%Y-%m-%d")
        # 5. Збереження результату в папку market_data (на рівень вище)
        output_folder = os.path.join("..", "market_data")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            
        new_file_name = os.path.join(output_folder, "market_salaries_by_SZU.csv")
        output_df.to_csv(new_file_name, index=False, encoding="utf-8")
        
        print(f"\n🎉 ПАРСИНГ ДЕРЖАВНОГО РЕЄСТРУ ЗАВЕРШЕНО!")
        print(f"Результати Служби зайнятості успішно збережено у: {new_file_name}")
        
    except Exception as e:
        print(f"❌ Критична помилка під час обробки державного реєстру: {e}")

if __name__ == "__main__":
    main()

