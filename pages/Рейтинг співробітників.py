import streamlit as st
import pandas as pd
import numpy as np

from app import add_total_compensation, page_top

# Завантаження даних
df = pd.read_csv("compensation.csv")
df.columns = df.columns.str.strip()

if "performance_score" not in df.columns:
    df["performance_score"] = np.random.randint(1, 11, size=len(df))

if "market_median" not in df.columns and "base_salary" in df.columns:
    df["market_median"] = (df["base_salary"] * np.random.uniform(0.85, 1.2, size=len(df))).astype(int)

if "employee_id" not in df.columns and "id" in df.columns:
    df["employee_id"] = df["id"]

df = add_total_compensation(df)

# Виклик функції для ТОП співробітників
page_top(df)
