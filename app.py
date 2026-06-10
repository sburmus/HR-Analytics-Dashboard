import streamlit as st
import pandas as pd
import plotly.express as px

# === КОНСТАНТИ ===
BENEFIT_COSTS = {
    "health_insurance": 5000,
    "sport": 2000,
    "remote_allowance": 3000,
}


# === ДОПОМІЖНІ ФУНКЦІЇ ===
def add_total_compensation(df: pd.DataFrame) -> pd.DataFrame:
    """Додає стовпець total_compensation з урахуванням пільг."""
    df = df.copy()
    # гарантуємо числові значення 0/1
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
    """Повертає CSV байти для завантаження."""
    return df.to_csv(index=False).encode("utf-8")


# === ГОЛОВНА ФУНКЦІЯ ===
def main():
    st.set_page_config(
        page_title="HR Analytics – Compensation & Benefits",
        page_icon="💼",
        layout="wide",
    )

    # ---- ЗАГАЛЬНІ СТИЛІ (збільшуємо шрифт) ----
    st.markdown(
        """
        <style>
        html, body, [class*="css"] {
            font-size: 18px;
        }
        .stMetric label, .stMetric span {
            font-size: 18px !important;
        }
        .stDataFrame, .stTable {
            font-size: 16px !important;
        }
        .main-title {
            font-size: 34px;
            font-weight: 700;
            margin-bottom: 0px;
        }
        .sub-title {
            font-size: 20px;
            color: #555;
            margin-top: 0px;
            margin-bottom: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ---- ШАПКА СТОРІНКИ ----
    st.markdown(
        '<p class="main-title">HR Analytics – Аналіз компенсацій і пільг</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="sub-title">Умовна компанія Adidas Ukraine • змодельована база співробітників</p>',
        unsafe_allow_html=True,
    )

    st.markdown("### Опис проєкту")
    st.write(
        "Дашборд показує структуру компенсаційних пакетів співробітників: "
        "базову заробітну плату, бонуси та пільги (медичне страхування, спортзал, "
        "компенсацію віддаленої роботи). Користувач може фільтрувати дані за відділами, "
        "діапазоном окладів і наявністю пільг, отримуючи агреговані показники, графіки "
        "та детальні таблиці."
    )

    st.markdown("---")

    # ---- ЗАВАНТАЖЕННЯ ДАНИХ ----
    df = pd.read_csv("compensation.csv")
    df = add_total_compensation(df)

    # ---- SIDEBAR: ФІЛЬТРИ ----
    st.sidebar.title("🔎 Панель фільтрів")

    departments = st.sidebar.multiselect(
        "Відділи:",
        options=sorted(df["department"].unique()),
        default=None,
    )

    salary_min = int(df["base_salary"].min())
    salary_max = int(df["base_salary"].max())
    salary_range = st.sidebar.slider(
        "Діапазон базової зарплати:",
        min_value=salary_min,
        max_value=salary_max,
        value=(salary_min, salary_max),
        step=1000,
    )

    st.sidebar.markdown("**Пільги:**")
    only_health = st.sidebar.checkbox("Тільки з медстрахуванням")
    only_sport = st.sidebar.checkbox("Тільки зі спортивною пільгою")
    only_remote = st.sidebar.checkbox("Тільки з remote allowance")

    # ---- ЗАСТОСУВАННЯ ФІЛЬТРІВ ----
    filtered_df = df.copy()

    if departments:
        filtered_df = filtered_df[filtered_df["department"].isin(departments)]

    filtered_df = filtered_df[
        (filtered_df["base_salary"] >= salary_range[0])
        & (filtered_df["base_salary"] <= salary_range[1])
    ]

    if only_health:
        filtered_df = filtered_df[filtered_df["health_insurance"] == 1]
    if only_sport:
        filtered_df = filtered_df[filtered_df["sport"] == 1]
    if only_remote:
        filtered_df = filtered_df[filtered_df["remote_allowance"] == 1]

    if filtered_df.empty:
        st.warning(
            "За обраними фільтрами немає жодного співробітника. "
            "Послабте умови фільтрації."
        )
        return

    # ---- КЛЮЧОВІ ПОКАЗНИКИ ----
    st.markdown("### 📊 Ключові показники (з урахуванням фільтрів)")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Кількість співробітників", len(filtered_df))
    col2.metric(
        "Середня базова зарплата",
        f"{filtered_df['base_salary'].mean():,.0f} грн",
    )
    col3.metric(
        "Середній бонус",
        f"{filtered_df['bonus'].mean():,.0f} грн",
    )
    col4.metric(
        "Середній повний пакет",
        f"{filtered_df['total_compensation'].mean():,.0f} грн",
    )

    st.markdown("---")

    # ---- ГРАФІКИ ПО ВІДДІЛАХ ----
    st.markdown("### 🏢 Середня компенсація по відділах")

    dept_comp = (
        filtered_df.groupby("department")[["base_salary", "bonus", "total_compensation"]]
        .mean()
        .reset_index()
    )

    fig_salary_bonus = px.bar(
        dept_comp,
        x="department",
        y=["base_salary", "bonus"],
        barmode="group",
        title="Середня базова зарплата та бонус по відділах",
        labels={"value": "Сума, грн", "department": "Відділ", "variable": "Компонент"},
    )
    st.plotly_chart(fig_salary_bonus, use_container_width=True)

    fig_total = px.bar(
        dept_comp,
        x="department",
        y="total_compensation",
        title="Середній повний компенсаційний пакет по відділах",
        labels={"total_compensation": "Сума, грн", "department": "Відділ"},
    )
    st.plotly_chart(fig_total, use_container_width=True)

    st.markdown("---")

    # ---- ПІЛЬГИ ----
    st.markdown("### 🎁 Розподіл пільг серед співробітників")

    benefits_count = {
        "Медстрахування": int(filtered_df["health_insurance"].sum()),
        "Спортзал": int(filtered_df["sport"].sum()),
        "Remote allowance": int(filtered_df["remote_allowance"].sum()),
    }
    benefits_df = pd.DataFrame(
        list(benefits_count.items()), columns=["Пільга", "Кількість"]
    )

    col_pie, col_tbl = st.columns(2)
    with col_pie:
        fig_benefits = px.pie(
            benefits_df,
            names="Пільга",
            values="Кількість",
            title="Частка співробітників із різними пільгами",
        )
        st.plotly_chart(fig_benefits, use_container_width=True)

    with col_tbl:
        st.write("Табличний вигляд розподілу пільг:")
        st.dataframe(benefits_df, use_container_width=True)

    st.markdown("---")

    # ---- ТОП СПІВРОБІТНИКІВ ----
    st.markdown("### 🏆 ТОП співробітників за повністю пакетом")

    top_n = st.slider(
        "Кількість у ТОП‑списку:",
        min_value=3,
        max_value=min(50, len(filtered_df)),
        value=10,
    )

    top_df = (
        filtered_df.sort_values("total_compensation", ascending=False)
        .head(top_n)[
            [
                "name",
                "department",
                "base_salary",
                "bonus",
                "health_insurance",
                "sport",
                "remote_allowance",
                "total_compensation",
            ]
        ]
    )
    st.dataframe(top_df, use_container_width=True)

    # ---- ДЕТАЛЬНА ТАБЛИЦЯ ----
    st.markdown("### 📋 Детальна таблиця співробітників (з урахуванням фільтрів)")

    details_df = filtered_df[
        [
            "name",
            "department",
            "base_salary",
            "bonus",
            "health_insurance",
            "sport",
            "remote_allowance",
            "total_compensation",
        ]
    ].sort_values("name")

    st.dataframe(details_df, use_container_width=True)

    st.markdown("---")

    # ---- ЕКСПОРТ ----
    st.markdown("### 📤 Експорт відфільтрованих даних")

    csv_bytes = convert_df_to_csv(filtered_df)
    st.download_button(
        label="⬇️ Завантажити CSV",
        data=csv_bytes,
        file_name="filtered_compensation.csv",
        mime="text/csv",
    )

    # ---- ФУТЕР ----
    st.markdown(
        "<br><hr><small>Проєкт: аналіз компенсацій і пільг співробітників "
        "в умовній компанії Adidas Ukraine. Усі дані є змодельованими для навчальних цілей.</small>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

