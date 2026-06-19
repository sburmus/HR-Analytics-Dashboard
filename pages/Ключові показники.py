import streamlit as st
import numpy as np
import pandas as pd
from pathlib import Path
import importlib.util
import sys
st.set_page_config(layout="wide")

# Імпорт функцій з головного app.py
module_path = Path(__file__).parent.parent / "app.py"
spec = importlib.util.spec_from_file_location("app", str(module_path))
app = importlib.util.module_from_spec(spec)
sys.modules["app"] = app
spec.loader.exec_module(app)

add_total_compensation = app.add_total_compensation

def main():
    df = pd.read_csv("compensation.csv")
    df = add_total_compensation(df)

    st.title("📊 Ключові показники")
    st.markdown("""
    Ця сторінка показує основні HR‑метрики компанії: зарплати, бонуси, пільги та
    додаткові показники. Вона допомагає швидко оцінити рівень компенсацій та
    виявити ключові тенденції.
    """)

    # --- Основні показники ---
    st.subheader("Основні показники")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Кількість співробітників", len(df))
    c2.metric("Середня базова зарплата", f"{df['base_salary'].mean():,.0f} грн")
    c3.metric("Медіанна базова зарплата", f"{np.median(df['base_salary']):,.0f} грн")
    c4.metric("Станд. відхилення окладу", f"{np.std(df['base_salary']):,.0f} грн")
    c5.metric("Середній бонус", f"{df['bonus'].mean():,.0f} грн")
    c6.metric("Середній повний пакет", f"{df['total_compensation'].mean():,.0f} грн")

    st.markdown("**Висновок:** середня зарплата та бонуси показують загальний рівень компенсацій, а стандартне відхилення демонструє різницю між співробітниками.")

    st.markdown("---")

    st.subheader("Додаткові показники")
    c7, c8, c9, c10 = st.columns([2, 2, 3, 3])  # ширші колонки
    c7.metric("Мін. базова зарплата", f"{df['base_salary'].min():,.0f} грн")
    c8.metric("Макс. базова зарплата", f"{df['base_salary'].max():,.0f} грн")
    c9.metric("Загальний бюджет компенсацій", f"{df['total_compensation'].sum():,.0f} грн")
    coef_var = (df['base_salary'].std() / df['base_salary'].mean() * 100) if df['base_salary'].mean() else 0
    c10.metric("Коефіцієнт варіації окладу", f"{coef_var:.1f}%")


    # --- Нові показники з CSV ---
    st.subheader("Додаткові HR‑метрики")
    if "performance_score" in df.columns:
        st.metric("Середній performance score", f"{df['performance_score'].mean():.1f}")
        st.markdown("**Висновок:** середній бал продуктивності допомагає оцінити ефективність персоналу.")

    if "market_median" in df.columns:
        compa_ratio = (df["base_salary"].mean() / df["market_median"].mean()) * 100
        st.metric("Compa Ratio (до ринку)", f"{compa_ratio:.1f}%")
        st.markdown("**Висновок:** Compa Ratio показує, наскільки внутрішні зарплати відповідають ринковим.")

    if "gender" in df.columns:
        gender_counts = df["gender"].value_counts()
        st.metric("Кількість жінок", gender_counts.get("Жінка", 0))
        st.metric("Кількість чоловіків", gender_counts.get("Чоловік", 0))
        st.markdown("**Висновок:** гендерний розподіл дозволяє оцінити баланс у компанії.")

    st.markdown("---")
    st.subheader("Повні дані")
    st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main()
