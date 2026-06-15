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
    df = pd.read_csv("compensation.csv")
    df = add_total_compensation(df)

    # ---- ШАПКА ----
    st.markdown("## HR Analytics – Аналіз компенсацій і пільг")
    st.write("Дашборд показує структуру компенсаційних пакетів співробітників: "
             "базову зарплату, бонуси та пільги. Є фільтри, ключові показники, графіки та аналіз ринку.")

    st.markdown("---")

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

    # ---- ГРАФІКИ ПО ВІДДІЛАХ ----
    dept_comp = filtered_df.groupby("department")[["base_salary", "bonus", "total_compensation"]].mean().reset_index()
    st.plotly_chart(px.bar(dept_comp, x="department", y=["base_salary", "bonus"], barmode="group",
                           title="Середня базова зарплата та бонус по відділах"), use_container_width=True)
    st.plotly_chart(px.bar(dept_comp, x="department", y="total_compensation",
                           title="Середній повний пакет по відділах"), use_container_width=True)

    # ---- BOXplot ----
    fig_box, ax = plt.subplots(figsize=(8, 4))
    sns.boxplot(data=filtered_df, x="department", y="base_salary", ax=ax)
    plt.xticks(rotation=30)
    st.pyplot(fig_box)

    st.markdown("---")

    # ---- ПІЛЬГИ ----
    benefits_count = {
        "Медстрахування": int(filtered_df["health_insurance"].sum()),
        "Спортзал": int(filtered_df["sport"].sum()),
        "Remote allowance": int(filtered_df["remote_allowance"].sum()),
    }
    benefits_df = pd.DataFrame(list(benefits_count.items()), columns=["Пільга", "Кількість"])
    st.plotly_chart(px.pie(benefits_df, names="Пільга", values="Кількість", title="Розподіл пільг"), use_container_width=True)
    st.dataframe(benefits_df)

    st.markdown("---")

    # ---- ТОП СПІВРОБІТНИКІВ ----
    st.markdown("### 🏆 ТОП співробітників за повним пакетом")
    top_n = st.slider("Кількість у ТОП‑списку:", min_value=3, max_value=min(50, len(filtered_df)), value=10)
    top_df = filtered_df.sort_values("total_compensation", ascending=False).head(top_n)
    st.dataframe(top_df[[
        "name","department","base_salary","bonus",
        "health_insurance","sport","remote_allowance","total_compensation","Role_ua","Role"
    ]])

    st.markdown("---")

    # ---- ЕКСПОРТ ----
    st.markdown("### 📤 Експорт відфільтрованих даних")
    csv_bytes = convert_df_to_csv(filtered_df)
    st.download_button(label="⬇️ Завантажити CSV", data=csv_bytes,
                       file_name="filtered_compensation.csv", mime="text/csv")

    st.markdown("---")

    # ---- Market Analysis ----
    st.markdown("### 🌍 Market Analysis")

    # вибір української назви посади
    role_ua = st.selectbox("Оберіть посаду (укр):", df["Role_ua"].unique())
    city = st.selectbox("Оберіть місто:", ["Київ","Львів","Полтава","Одеса"])

    # виклик парсера з українською назвою
    market_df = get_market_data(role_ua, city)

    if isinstance(market_df, pd.DataFrame) and "Salary" in market_df.columns:
        market_df["Salary"] = market_df["Salary"].replace(["Не вказано",""], "—")
        st.dataframe(market_df)

        valid_salaries = pd.to_numeric(market_df["Salary"].str.replace(" грн",""), errors="coerce").dropna()
        if not valid_salaries.empty:
            st.metric("Середня ринкова зарплата", f"{valid_salaries.mean():,.0f} грн")
        else:
            st.warning("Для цієї посади/міста немає вказаних зарплат.")
    else:
        st.warning("Парсер не повернув даних для цієї посади/міста.")

# === Запуск ===
if __name__ == "__main__":
    main()
