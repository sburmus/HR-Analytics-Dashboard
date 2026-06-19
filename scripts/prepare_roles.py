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
}

DEPARTMENT_TO_ROLE_EN = {
    "IT": "Python Developer",
    "HR": "HR Manager",
    "Marketing": "Marketing Specialist",
    "Sales": "Sales Manager",
    "Logistics": "Logistics Specialist",
    "Retail": "Retail Specialist",
}

# Додаємо нові колонки
df["Role_ua"] = df["department"].map(DEPARTMENT_TO_ROLE_UA)
df["Role"] = df["department"].map(DEPARTMENT_TO_ROLE_EN)

# Зберігаємо назад
df.to_csv("compensation.csv", index=False)

print("✅ Файл compensation.csv оновлено: додано Role_ua та Role")
