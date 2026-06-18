import streamlit as st
import pandas as pd
from app import add_total_compensation, show_top

# Завантаження даних
df = pd.read_csv("compensation.csv")
df.columns = df.columns.str.strip()
df = add_total_compensation(df)

# Виклик функції для ТОП співробітників
show_top(df)
