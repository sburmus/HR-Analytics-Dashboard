import streamlit as st
import pandas as pd
import plotly.express as px
import io

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
        df[col] = df[col].astype(float)
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

def convert_df_to_excel(df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Compensation")
        worksheet = writer.sheets["Compensation"]
        for i, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, max_len)
    return output.getvalue()

# === ГОЛОВНА ФУНКЦІЯ ===
def main():
    st.set_page_config(page_title="HR Analytics – Compensation & Benefits", page_icon="💼", layout="wide")

    # ---- ШАПКА ----
    st.title("💼 HR Analytics – Аналіз компенсацій і пільг")
    st.markdown("**Умовна компанія:** Adidas Ukraine • змодельована база співробітників")
    st.markdown("### 📖 Опис проєкту")
    st.write("Дашборд показує структуру компенсаційних пакетів співробітників: базову заробітну плату, бонуси та пільги (медичне страхування, спортзал, компенсацію віддаленої роботи). Користувач може фільтрувати дані за відділами, діапазоном окладів і наявністю пільг, отримуючи агреговані показники, графіки та детальні таблиці.")
    st.markdown("---")

    # ---- ЗАВАНТАЖЕННЯ ДАНИХ ----
    df = pd.read_csv("compensation.csv")
    df = add_total_compensation(df)

    # ---- SIDEBAR: ФІЛЬТРИ ----
    st.sidebar.title("🔎 Панель фільтрів")
    departments = st.sidebar.multiselect("Відділи:", options=sorted(df["department"].unique()))
    salary_range = st.sidebar.slider("Діапазон базової зарплати:", int(df["base_salary"].min()), int(df["base_salary"].max()), (int(df["base_salary"].min()), int(df["base_salary"].max())), step=1000)
    only_health = st.sidebar.checkbox("Тільки з медстрахуванням")
    only_sport = st.sidebar.checkbox("Тільки зі спортивною пільгою")
    only_remote = st.sidebar.checkbox("Тільки з remote allowance")

    # ---- СИМУЛЯЦІЯ БОНУСІВ ----
    st.sidebar.markdown("**Симуляція:**")
    bonus_increase = st.sidebar.slider("Збільшити бонуси на %:", min_value=0, max_value=50, value=0, step=5)

    # ---- ФІЛЬТРАЦІЯ ----
    filtered_df = df.copy()
    if departments:
        filtered_df = filtered_df[filtered_df["department"].isin(departments)]
    filtered_df = filtered_df[(filtered_df["base_salary"] >= salary_range[0]) & (filtered_df["base_salary"] <= salary_range[1])]
    if only_health:
        filtered_df = filtered_df[filtered_df["health_insurance"] == 1]
    if only_sport:
        filtered_df = filtered_df[filtered_df["sport"] == 1]
    if only_remote:
        filtered_df = filtered_df[filtered_df["remote_allowance"] == 1]

    if filtered_df.empty:
        st.warning("За обраними фільтрами немає жодного співробітника.")
        return

    # ---- СИМУЛЯЦІЯ ----
    sim_df = filtered_df.copy()
    sim_df["bonus_simulated"] = sim_df["bonus"] * (1 + bonus_increase / 100)
    sim_df["total_compensation_simulated"] = (
        sim_df["base_salary"]
        + sim_df["bonus_simulated"]
        + sim_df["health_insurance"] * BENEFIT_COSTS["health_insurance"]
        + sim_df["sport"] * BENEFIT_COSTS["sport"]
        + sim_df["remote_allowance"] * BENEFIT_COSTS["remote_allowance"]
    )
    st.sidebar.write(f"📈 Середній пакет після симуляції: {sim_df['total_compensation_simulated'].mean():,.0f} грн")

    # ---- КЛЮЧОВІ ПОКАЗНИКИ ----
    st.markdown("### 📊 Ключові показники")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Кількість співробітників", len(filtered_df))
    col2.metric("Середня базова зарплата", f"{filtered_df['base_salary'].mean():,.0f} грн")
    col3.metric("Середній бонус", f"{filtered_df['bonus'].mean():,.0f} грн")
    col4.metric("Середній повний пакет", f"{filtered_df['total_compensation'].mean():,.0f} грн")
    st.markdown("---")

    # ---- ГРАФІКИ ----
    dept_comp = filtered_df.groupby("department")[["base_salary", "bonus", "total_compensation"]].mean().reset_index()
    st.markdown("### 🏢 Середня компенсація по відділах")

    fig_salary_bonus = px.bar(
        dept_comp,
        x="department",
        y=["base_salary", "bonus"],
        barmode="group",
        title="Середня зарплата та бонуси",
        labels={"department": "Відділ", "value": "Сума, грн", "variable": "Компонент"}
    )
    st.plotly_chart(fig_salary_bonus, width="stretch")

    fig_total = px.bar(
        dept_comp,
        x="department",
        y="total_compensation",
        title="Середній повний компенсаційний пакет по відділах",
        labels={"department": "Відділ", "total_compensation": "Сума, грн"}
    )
    st.plotly_chart(fig_total, width="stretch")

    st.markdown("### 🎁 Розподіл пільг")
    benefits_count = {"Медстрахування": int(filtered_df["health_insurance"].sum()), "Спортзал": int(filtered_df["sport"].sum()), "Remote allowance": int(filtered_df["remote_allowance"].sum())}
    benefits_df = pd.DataFrame(list(benefits_count.items()), columns=["Пільга","Кількість"])
    st.plotly_chart(px.pie(benefits_df, names="Пільга", values="Кількість", title="Частка співробітників із пільгами"), width="stretch")
    st.dataframe(benefits_df, width="stretch")

    # ---- ТОП СПІВРОБІТНИКІВ ----
    st.markdown("### 🏆 ТОП співробітників")
    top_n = st.slider("Кількість у ТОП‑списку:", min_value=3, max_value=min(50, len(filtered_df)), value=10)
    top_df = filtered_df.sort_values("total_compensation", ascending=False).head(top_n)[["name","department","base_salary","bonus","total_compensation"]]
    st.dataframe(top_df, width="stretch")

    # ---- ГІСТОГРАМА ЗАРПЛАТ ----
    st.markdown("### 📈 Розподіл базових зарплат")
    fig_hist = px.histogram(
        filtered_df,
        x="base_salary",
        nbins=20,
        title="Гістограма розподілу базових зарплат",
        labels={"base_salary": "Базова зарплата, грн"}
    )
    st.plotly_chart(fig_hist, width="stretch")

    # ---- ДЕТАЛЬНА ТАБЛИЦЯ ----
    st.markdown("### 📋 Детальна таблиця")
    details_df = filtered_df[["name","department","base_salary","bonus","health_insurance","sport","remote_allowance","total_compensation"]].sort_values("name")


    st.dataframe(details_df, width="stretch")
    # ---- ЕКСПОРТ ----
    st.markdown("### 📤 Експорт")

    csv_bytes = convert_df_to_csv(filtered_df)
    st.download_button(
        label="⬇️ Завантажити CSV (Excel-friendly)",
        data=csv_bytes,
        file_name="filtered_compensation.csv",
        mime="text/csv",
        key="download_csv"
    )

    excel_bytes = convert_df_to_excel(filtered_df)
    st.download_button(
        label="⬇️ Завантажити Excel",
        data=excel_bytes,
        file_name="filtered_compensation.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="download_excel"
    )

    # ---- ФУТЕР ----
    st.markdown(
        "<br><hr><small>Проєкт: аналіз компенсацій і пільг співробітників "
        "в умовній компанії Adidas Ukraine. Усі дані є змодельованими для навчальних цілей.</small>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

