import streamlit as st
import pandas as pd
import plotly.express as px

# === Константи ===
BENEFIT_COSTS = {
    "health_insurance": 5000,
    "sport": 2000,
    "remote_allowance": 3000
}

# === Функції ===
def add_total_compensation(df):
    df["total_compensation"] = (
        df["base_salary"] +
        df["bonus"] +
        df["health_insurance"] * BENEFIT_COSTS["health_insurance"] +
        df["sport"] * BENEFIT_COSTS["sport"] +
        df["remote_allowance"] * BENEFIT_COSTS["remote_allowance"]
    )
    return df

def convert_df_to_csv(df):
    return df.to_csv(index=False).encode("utf-8")

# === Основна логіка ===
def main():
    st.title("💼 HR Analytics – Аналіз компенсацій і пільг")

    # Завантаження даних
    df = pd.read_csv("compensation.csv")   # ✅ замінено на твій файл
    df = add_total_compensation(df)

    # === Фільтри ===
    st.sidebar.header("🔎 Фільтри")
    departments = st.sidebar.multiselect("Виберіть відділи:", df["department"].unique())
    salary_range = st.sidebar.slider("Діапазон базової зарплати:", 
                                     int(df["base_salary"].min()), 
                                     int(df["base_salary"].max()), 
                                     (int(df["base_salary"].min()), int(df["base_salary"].max())))
    only_health = st.sidebar.checkbox("Тільки з медстрахуванням")
    only_sport = st.sidebar.checkbox("Тільки зі спортом")
    only_remote = st.sidebar.checkbox("Тільки з remote allowance")

    # Фільтрація даних
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

    # === Метрики ===
    st.subheader("📊 Загальні показники")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Кількість співробітників", len(filtered_df))
    col2.metric("Середня базова зарплата", f"{filtered_df['base_salary'].mean():,.0f} грн")
    col3.metric("Середній бонус", f"{filtered_df['bonus'].mean():,.0f} грн")
    col4.metric("Середній повний пакет", f"{filtered_df['total_compensation'].mean():,.0f} грн")

    # === Графіки ===
    st.subheader("🏢 Середня компенсація по відділах")
    dept_comp = filtered_df.groupby("department")[["base_salary","bonus","total_compensation"]].mean().reset_index()
    fig1 = px.bar(dept_comp, x="department", y=["base_salary","bonus"], 
                  title="Середня зарплата та бонуси")
    st.plotly_chart(fig1)

    st.subheader("🎁 Розподіл пільг серед співробітників")
    benefits = filtered_df.groupby("department")["total_compensation"].mean().reset_index()
    fig2 = px.bar(benefits, x="department", y="total_compensation", 
                  title="Середній повний пакет по відділах")
    st.plotly_chart(fig2)

    st.subheader("🥧 Відсоток співробітників із пільгами")
    benefits_count = {
        "Медстрахування": filtered_df["health_insurance"].sum(),
        "Спортзал": filtered_df["sport"].sum(),
        "Remote allowance": filtered_df["remote_allowance"].sum()
    }
    benefits_df = pd.DataFrame(list(benefits_count.items()), columns=["Пільга","Кількість"])
    fig3 = px.pie(benefits_df, names="Пільга", values="Кількість", title="Розподіл пільг")
    st.plotly_chart(fig3)

    # === Таблиця ===
    st.subheader("📋 Деталі по співробітниках")
    st.dataframe(filtered_df[["name","department","base_salary","bonus","health_insurance","sport","remote_allowance","total_compensation"]])

    # === Експорт ===
    st.subheader("📤 Експорт даних")
    csv = convert_df_to_csv(filtered_df)
    st.download_button("⬇️ Завантажити CSV", csv, "filtered_compensation.csv", "text/csv")

if __name__ == "__main__":
    main()
