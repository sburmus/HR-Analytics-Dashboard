import csv

# Вартість пільг (умовні значення, грн/міс)
BENEFIT_COSTS = {
    "health_insurance": 3000,     # медстрахування
    "sport": 1500,                # спортзал
    "remote_allowance": 2000,     # компенсація за віддалену роботу
}

def load_compensation(filename):
    """
    Завантажує дані з CSV у список словників.
    Кожен рядок = один співробітник.
    """
    employees = []
    with open(filename, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # перетворюємо текстові значення в числа / логічні значення
            row["base_salary"] = float(row["base_salary"])
            row["bonus"] = float(row["bonus"])
            row["health_insurance"] = row["health_insurance"] == "1"
            row["sport"] = row["sport"] == "1"
            row["remote_allowance"] = row["remote_allowance"] == "1"
            employees.append(row)
    return employees

def total_compensation_for_employee(e):
    """
    Розраховує загальну вартість пакету для одного співробітника:
    базова + бонус + вартість усіх його пільг.
    """
    total = e["base_salary"] + e["bonus"]
    for benefit, cost in BENEFIT_COSTS.items():
        if e[benefit]:
            total += cost
    return total

def total_compensation_all(employees):
    """Загальні витрати на компенсації по всій компанії."""
    return sum(total_compensation_for_employee(e) for e in employees)

def average_base_and_total(employees):
    """Середня базова зарплата та середній повний пакет."""
    if not employees:
        return 0, 0
    base_sum = sum(e["base_salary"] for e in employees)
    total_sum = sum(total_compensation_for_employee(e) for e in employees)
    n = len(employees)
    return base_sum / n, total_sum / n

def compensation_by_department(employees):
    """
    Рахує середні компенсації по відділах.
    Повертає словник: {відділ: {avg_base: ..., avg_total: ...}}
    """
    stats = {}
    for e in employees:
        dept = e["department"]
        if dept not in stats:
            stats[dept] = {"base_sum": 0, "total_sum": 0, "count": 0}
        stats[dept]["base_sum"] += e["base_salary"]
        stats[dept]["total_sum"] += total_compensation_for_employee(e)
        stats[dept]["count"] += 1

    result = {}
    for dept, data in stats.items():
        result[dept] = {
            "avg_base": data["base_sum"] / data["count"],
            "avg_total": data["total_sum"] / data["count"],
        }
    return result

def benefit_stats(employees):
    """
    Повертає, скільки людей має кожну пільгу.
    Напр.: {'health_insurance': 7, 'sport': 5, ...}
    """
    counts = {b: 0 for b in BENEFIT_COSTS.keys()}
    for e in employees:
        for b in BENEFIT_COSTS.keys():
            if e[b]:
                counts[b] += 1
    return counts

def top_n_by_total_package(employees, n=3):
    """Повертає топ-N співробітників за вартістю пакету."""
    sorted_emps = sorted(
        employees,
        key=lambda e: total_compensation_for_employee(e),
        reverse=True
    )
    return sorted_emps[:n]

def find_employee(employees, name_part):
    """Пошук співробітників за частиною імені (без урахування регістру)."""
    name_part = name_part.lower()
    return [e for e in employees if name_part in e["name"].lower()]

def print_employee(e):
    """Гарний вивід інформації про співробітника."""
    total = total_compensation_for_employee(e)
    print(f"{e['id']} | {e['name']} | {e['department']}")
    print(f"  Базова зарплата: {e['base_salary']}")
    print(f"  Бонус: {e['bonus']}")
    print("  Пільги:")
    has_any_benefit = False
    for b, cost in BENEFIT_COSTS.items():
        if e[b]:
            has_any_benefit = True
            print(f"    - {b} (+{cost})")
    if not has_any_benefit:
        print("    (немає)")
    print(f"  Загальний пакет: {total}")
    print("-" * 40)

def main():
    # 1. Завантажуємо дані з CSV
    employees = load_compensation("compensation.csv")

    # 2. Цикл меню
    while True:
        print("\nАналіз компенсацій і пільг")
        print("1. Показати загальні витрати на компенсації")
        print("2. Показати середню базову зарплату і загальний пакет")
        print("3. Показати статистику компенсацій по відділах")
        print("4. Показати статистику за видами пільг")
        print("5. Показати топ-N співробітників за вартістю пакету")
        print("6. Знайти співробітника і показати його пакет")
        print("7. Вийти")

        choice = input("Оберіть пункт меню: ")

        if choice == "1":
            total = total_compensation_all(employees)
            print("Загальні щомісячні витрати на компенсації:", round(total, 2))

        elif choice == "2":
            avg_base, avg_total = average_base_and_total(employees)
            print("Середня базова зарплата:", round(avg_base, 2))
            print("Середній загальний пакет:", round(avg_total, 2))

        elif choice == "3":
            stats = compensation_by_department(employees)
            for dept, data in stats.items():
                print(f"\nВідділ: {dept}")
                print("  Середня базова:", round(data["avg_base"], 2))
                print("  Середній пакет:", round(data["avg_total"], 2))

        elif choice == "4":
            stats = benefit_stats(employees)
            print("Кількість співробітників з пільгами:")
            for b, cnt in stats.items():
                print(f"  {b}: {cnt}")

        elif choice == "5":
            try:
                n = int(input("Введіть N: "))
            except ValueError:
                print("Потрібно ввести ціле число.")
                continue
            top = top_n_by_total_package(employees, n)
            print(f"Топ-{n} співробітників за вартістю пакету:")
            for e in top:
                print_employee(e)

        elif choice == "6":
            name_part = input("Введіть частину імені: ")
            found = find_employee(employees, name_part)
            if not found:
                print("Нічого не знайдено")
            else:
                for e in found:
                    print_employee(e)

        elif choice == "7":
            print("Вихід...")
            break

        else:
            print("Невірний вибір, спробуйте ще раз")

if __name__ == "__main__":
    main()
