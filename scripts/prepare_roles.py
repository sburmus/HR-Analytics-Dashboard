import pandas as pd

# Завантажуємо дані
df = pd.read_csv("compensation.csv")

# Словники для відділів
DEPARTMENT_TO_ROLE_UA = {
    "IT": "Програміст",
    "HR": "HR-менеджер",
    "Marketing": "Маркетолог",
    "Sales": "Менеджер з продажу",
    "Logistics": "Логіст",
    "Retail": "Фахівець роздрібної торгівлі",
    "Administration": "Бухгалтер/Директор/Адміністратор",
    "Customer Service": "Бариста/Офіціант",
    "Operations": "Кухар/Комірник/Вантажник/Різноробочий"
}

DEPARTMENT_TO_ROLE_EN = {
    "IT": "Developer",
    "HR": "HR Manager",
    "Marketing": "Marketing Specialist",
    "Sales": "Sales Manager",
    "Logistics": "Logistics Specialist",
    "Retail": "Retail Specialist",
    "Administration": "Accountant/Director/Administrator",
    "Customer Service": "Barista/Waiter",
    "Operations": "Cook/Storekeeper/Loader/General Worker"
}

# Оновлюємо або додаємо колонки
df["Role_ua"] = df["department"].map(DEPARTMENT_TO_ROLE_UA).fillna(df.get("Role_ua"))
df["Role"] = df["department"].map(DEPARTMENT_TO_ROLE_EN).fillna(df.get("Role"))

# Зберігаємо назад
df.to_csv("compensation.csv", index=False)

print("✅ Файл compensation.csv оновлено: Role_ua та Role синхронізовано з відділами")
