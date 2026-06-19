import csv
import random

# Відділи та орієнтовні діапазони зарплат для "умовної Adidas Ukraine"
DEPARTMENTS = {
    "Sales":      (35000, 60000),
    "Marketing":  (38000, 65000),
    "Retail":     (28000, 40000),
    "HR":         (35000, 55000),
    "IT":         (50000, 90000),
    "Logistics":  (35000, 55000),
}

FIRST_NAMES = [
    "Oleksii", "Anna", "Maksym", "Olha", "Andrii", "Iryna", "Denys", "Kateryna",
    "Serhii", "Natalia", "Volodymyr", "Lesia", "Mykhailo", "Yuliia", "Andriana",
    "Oleksa", "Olena", "Stepan", "Svitlana", "Inna", "Petro", "Igor", "Bohdan",
    "Mariana", "Oleksandr", "Halyna", "Taras", "Oksana", "Viktor", "Lidiia",
]

LAST_NAMES = [
    "Kovalenko", "Petrenko", "Shevchuk", "Sydorenko", "Melnyk", "Koval",
    "Romaniuk", "Bondar", "Danyliuk", "Tkachenko", "Horbenko", "Polishchuk",
    "Ivanov", "Kravets", "Oliinyk", "Marchenko", "Chernenko", "Levchenko",
    "Rudenko", "Shapoval", "Holub", "Moroz", "Lysenko", "Zhuk", "Savchenko",
    "Dmytrenko", "Pavlenko", "Klymenko", "Karpov", "Mazur", "Hrytsenko",
    "Kushnir", "Fedorchuk", "Vasylenko", "Sobol", "Kutsenko", "Boyko"
]


def random_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def random_employee(emp_id):
    # випадковий відділ
    department = random.choice(list(DEPARTMENTS.keys()))
    base_min, base_max = DEPARTMENTS[department]
    base_salary = random.randrange(base_min, base_max + 1, 1000)

    # бонус: від 5% до 30% від бази
    bonus = int(base_salary * random.uniform(0.05, 0.30))

    # пільги: ймовірності різні
    health_insurance = 1 if random.random() < 0.7 else 0
    sport = 1 if random.random() < 0.5 else 0
    if department in ("IT", "Marketing", "HR"):
        remote_allowance = 1 if random.random() < 0.6 else 0
    else:
        remote_allowance = 1 if random.random() < 0.2 else 0

    return {
        "id": emp_id,
        "name": random_name(),
        "department": department,
        "base_salary": base_salary,
        "bonus": bonus,
        "health_insurance": health_insurance,
        "sport": sport,
        "remote_allowance": remote_allowance,
    }


def generate_csv(filename="compensation.csv", n=200):
    random.seed(42)  # щоб результат можна було відтворити
    fieldnames = [
        "id", "name", "department", "base_salary", "bonus",
        "health_insurance", "sport", "remote_allowance"
    ]

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(1, n + 1):
            emp = random_employee(i)
            writer.writerow(emp)

    print(f"Файл {filename} згенеровано, кількість записів: {n}")


if __name__ == "__main__":
    generate_csv("compensation.csv", n=200)
