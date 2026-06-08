import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    return pd.read_csv("compensation.csv")

def main():
    st.set_page_config(...)

    st.sidebar.title("Фільтри")

    if st.sidebar.button("🔄 Оновити дані з файлу"):
        st.cache_data.clear()

    df = load_data()




@st.cache_data
def load_data():
    df = pd.read_csv("compensation.csv")
    return df

def add_total_compensation(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # перетворимо 0/1 у bool для зручності
    for col in ["health_insurance", "sport", "remote_allowance"]:
        df[col] = df[col].astype(int)

    df["benefits_value"] = (
        df["health_insurance"] * BENEFIT_COSTS["health_insurance"]
        + df["sport"] * BENEFIT_COSTS["sport"]
        + df["remote_allowance"] * BENEFIT_COSTS["remote_allowance"]
    )

    df["total_compensation"] = df["base_salary"] + df["bonus"] + df["benefits_value"]
    return df

def main():
    st.set_page_config(
        page_title="HR Analytics – Adidas (умовні дані)",
        page_icon="📊",
        layout="wide"
    )

    st.title("HR Analytics – Аналіз компенсацій і пільг")
    st.subheader("Умовна компанія Adidas Ukraine (200 співробітників)")

    df = load_data()
    df = add_total_compensation(df)

    # Бокова панель з фільтрами
    st.sidebar.header("Фільтри")

    departments = ["Усі"] + sorted(df["department"].unique().tolist())
    selected_dept = st.sidebar.selectbox("Відділ", departments)

    min_salary = int(df["base_salary"].min())
    max_salary = int(df["base_salary"].max())
    salary_range = st.sidebar.slider(
        "Діапазон базової зарплати",
        min_salary, max_salary, (min_salary, max_salary), step=1000
    )

    # фільтри по пільгах
    only_health = st.sidebar.checkbox("Тільки з медстрахуванням")
    only_sport = st.sidebar.checkbox("Тільки зі спортом")
    only_remote = st.sidebar.checkbox("Тільки з remote allowance")

    # застосування фільтрів
    filtered = df.copy()

    # фільтр по відділу
    if selected_dept != "Усі":
        filtered = filtered[filtered["department"] == selected_dept]

    # фільтр по зарплаті
    filtered = filtered[
        (filtered["base_salary"] >= salary_range[0]) &
        (filtered["base_salary"] <= salary_range[1])
    ]

    # фільтри по пільгах
    if only_health:
        filtered = filtered[filtered["health_insurance"] == 1]
    if only_sport:
        filtered = filtered[filtered["sport"] == 1]
    if only_remote:
        filtered = filtered[filtered["remote_allowance"] == 1]

    st.markdown("### Загальна статистика (з урахуванням фільтрів)")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Кількість співробітників", len(filtered))
    with col2:
        st.metric("Середня базова зарплата", f"{filtered['base_salary'].mean():.0f} грн")
    with col3:
        st.metric("Середній бонус", f"{filtered['bonus'].mean():.0f} грн")
    with col4:
        st.metric("Середній повний пакет", f"{filtered['total_compensation'].mean():.0f} грн")

    st.markdown("---")

    # 1. Графік: середня компенсація по відділах
    st.markdown("### Середня компенсація по відділах")

    dept_stats = (
        filtered
        .groupby("department")[["base_salary", "bonus", "benefits_value", "total_compensation"]]
        .mean()
        .reset_index()
    )

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.bar_chart(
            dept_stats.set_index("department")[["base_salary", "bonus"]],
            height=350
        )
        st.caption("Середня базова зарплата та бонус по відділах")

    with col_chart2:
        st.bar_chart(
            dept_stats.set_index("department")[["total_compensation"]],
            height=350
        )
        st.caption("Середній повний компенсаційний пакет по відділах")

    st.markdown("---")

    # 2. Графік: розподіл пільг
    st.markdown("### Розподіл пільг серед співробітників")

    benefit_counts = pd.DataFrame({
        "benefit": ["health_insurance", "sport", "remote_allowance"],
        "count": [
            filtered["health_insurance"].sum(),
            filtered["sport"].sum(),
            filtered["remote_allowance"].sum(),
        ]
    })

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.bar_chart(benefit_counts.set_index("benefit")["count"], height=350)
        st.caption("Скільки людей має кожну пільгу")

    with col_b2:
        st.write("Таблиця по пільгах")
        st.dataframe(benefit_counts, use_container_width=True)

    st.markdown("---")

    # 3. Топ-N співробітників за повним пакетом
    st.markdown("### Топ співробітників за вартістю компенсаційного пакету")

    top_n = st.slider("Скільки показати (Top N)", 3, 50, 10)
    top_employees = (
        filtered.sort_values("total_compensation", ascending=False)
        .head(top_n)
        [["id", "name", "department", "base_salary", "bonus", "benefits_value", "total_compensation"]]
    )

    st.dataframe(top_employees, use_container_width=True)

    st.markdown("---")

    # 4. Детальна таблиця співробітників (з фільтрами)
    st.markdown("### Детальна таблиця співробітників (з урахуванням фільтрів)")
    st.dataframe(
        filtered[
            ["id", "name", "department", "base_salary", "bonus",
             "health_insurance", "sport", "remote_allowance", "total_compensation"]
        ].sort_values("id"),
        use_container_width=True
    )

    st.markdown(
        "<br><small>Проєкт: Аналіз компенсацій і пільг в умовній компанії Adidas Ukraine. Дані згенеровані для навчальних цілей.</small>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
    
