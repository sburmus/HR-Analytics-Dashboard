import pandas as pd

# приклад словника з вартостями пільг
BENEFIT_COSTS = {
    "health_insurance": 5000,   # страхування
    "sport": 2000,              # спортзал
    "remote_allowance": 3000    # компенсація за віддалену роботу
}

def add_total_compensation(df):
    df["total_compensation"] = (
        df["base_salary"] +
        df["bonus"] +
        df["health_insurance"] * BENEFIT_COSTS["health_insurance"] +
        df["sport"] * BENEFIT_COSTS["sport"] +
        df["remote_allowance"] * BENEFIT_COSTS["remote_allowance"]
    )
    return df

# приклад завантаження CSV
df = pd.read_csv("employees.csv")
df = add_total_compensation(df)

print(df[["name", "department", "total_compensation"]])
