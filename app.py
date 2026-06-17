import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from parser import get_market_data

# === КОНСТАНТИ ===
BENEFIT_COSTS = {
    "health_insurance": 5000,
    "sport": 2000,
    "remote_allowance": 3000,
}

# === ДОПОМІЖНІ ФУНКЦІЇ ===
def add_total_compensation(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in ["health_insurance", "sport", "remote_allowance"]:
        df[col] = df[col].fillna(0).astype(float)
    df["total_compensation"] = (
        df["base_salary"]
        + df["bonus"]
        + df["health_insurance"] * BENEFIT_COSTS["health_insurance"]
        + df["sport"] * BENEFIT_COSTS["sport"]
        + df["remote_allowance"] * BENEFIT_COSTS["remote_allowance"]
    )
    return df

def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")

# === ГОЛОВНА ФУНКЦІЯ ===
def main():
    st.set_page_config(page_title="HR Analytics – Compensation & Benefits", layout="wide")

    # ---- Завантаження даних ----
    df = pd.read_csv("compensation.csv", sep=",")
    df.columns = df.columns.str.strip()
    df = add_total_compensation(df)

    st.write("Колонки у CSV:", df.columns.tolist())  # для перевірки

    # ---- ШАПКА ----
    st.markdown("## HR Analytics – Аналіз компенсацій і пільг")

    # ---- SIDEBAR: ФІЛЬТРИ ----
    st.sidebar.title("🔎 Панель фільтрів")
    departments = st.sidebar.multiselect("Відділи:", options=sorted(df["department"].unique()))
    salary_min, salary_max = int(df["base_salary"].min()), int(df["base_salary"].max())
    salary_range = st.sidebar.slider("Діапазон базової зарплати:", min_value=salary_min, max_value=salary_max,
                                     value=(salary_min, salary_max), step=1000)
    only_health = st.sidebar.checkbox("Тільки з медстрахуванням")
    only_sport = st.sidebar.checkbox("Тільки зі спортивною пільгою")
    only_remote = st.sidebar.checkbox("Тільки з remote allowance")

    # ---- ЗАСТОСУВАННЯ ФІЛЬТРІВ ----
    filtered_df = df.copy()
    if departments:
        filtered_df = filtered_df[filtered_df["department"].isin(departments)]
    filtered_df = filtered_df[(filtered_df["base_salary"] >= salary_range[0]) &
                              (filtered_df["base_salary"] <= salary_range[1])]
    if only_health:
        filtered_df = filtered_df[filtered_df["health_insurance"] == 1]
    if only_sport:
        filtered_df = filtered_df[filtered_df["sport"] == 1]
    if only_remote:
        filtered_df = filtered_df[filtered_df["remote_allowance"] == 1]

    if filtered_df.empty:
        st.warning("За обраними фільтрами немає жодного співробітника.")
        return

    # ---- КЛЮЧОВІ ПОКАЗНИКИ ----
    st.markdown("### 📊 Ключові показники")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Кількість співробітників", len(filtered_df))
    col2.metric("Середня базова зарплата", f"{filtered_df['base_salary'].mean():,.0f} грн")
    col3.metric("Медіанна базова зарплата", f"{np.median(filtered_df['base_salary']):,.0f} грн")
    col4.metric("Станд. відхилення окладу", f"{np.std(filtered_df['base_salary']):,.0f} грн")
    col5.metric("Середній бонус", f"{filtered_df['bonus'].mean():,.0f} грн")
    col6.metric("Середній повний пакет", f"{filtered_df['total_compensation'].mean():,.0f} грн")

    st.markdown("---")

    # ---- ГРАФІКИ ----
    dept_comp = filtered_df.groupby("department")[["base_salary", "bonus", "total_compensation"]].mean().reset_index()
    st.plotly_chart(px.bar(dept_comp, x="department", y=["base_salary", "bonus"], barmode="group",
                           title="Середня базова зарплата та бонус по відділах"), width="stretch")
    st.plotly_chart(px.bar(dept_comp, x="department", y="total_compensation",
                           title="Середній повний пакет по відділах"), width="stretch")

    fig_box, ax = plt.subplots(figsize=(8, 4))
    sns.boxplot(data=filtered_df, x="department", y="base_salary", ax=ax)
    plt.xticks(rotation=30)
    st.pyplot(fig_box, width="stretch")

    st.markdown("---")

    # ---- ТОП СПІВРОБІТНИКІВ ----
    st.markdown("### 🏆 ТОП співробітників за повним пакетом")
    top_n = st.slider("Кількість у ТОП‑списку:", min_value=3, max_value=min(50, len(filtered_df)), value=10)
    top_df = filtered_df.sort_values("total_compensation", ascending=False).head(top_n)
    st.dataframe(top_df[[
        "name","department","base_salary","bonus",
        "health_insurance","sport","remote_allowance","total_compensation","Role_ua","Role"
    ]], width="stretch")

    st.markdown("---")

    # ---- ЕКСПОРТ ----
    st.markdown("### 📤 Експорт відфільтрованих даних")
    csv_bytes = convert_df_to_csv(filtered_df)
    st.download_button(label="⬇️ Завантажити CSV", data=csv_bytes,
                       file_name="filtered_compensation.csv", mime="text/csv")

    st.markdown("---")

    #import streamlit as st
from parser import get_market_data

st.title("Market Analysis")
st.subheader("Оберіть посаду (укр)")

# список посад для вибору
roles = [
    "Касир", "Продавець-консультант", "Менеджер з продажу",
    "HR-менеджер", "Маркетолог", "SMM-менеджер",
    "Логіст", "Комірник", "Кухар", "Бариста",
    "Офіціант", "Бухгалтер", "Адміністратор", "Директор",
    "Програміст"
]

selected_role = st.selectbox("Посада:", roles)

if selected_role:
    data = get_market_data(selected_role)
    st.write("### Результат пошуку")
    st.table({
        "Role": [selected_role],
        "Salary": [data["salary"]],
        "Source": [data["source"]]
    })


# === Запуск ===
if __name__ == "__main__":
    main()

