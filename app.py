import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

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

# === ЗАВАНТАЖЕННЯ ДАНИХ ===
internal_df = pd.read_csv("compensation.csv")
internal_df = add_total_compensation(internal_df)

market_df = pd.read_csv("market_data.csv")  # файл з ринковими даними

# === ВКЛАДКИ ===
tab1, tab2, tab3, tab4, tab5, tab_market = st.tabs([
    "Time to Hire", "Turnover", "Attrition Reasons", "Tenure", "Compa Ratio", "Market Analysis"
])

# === 1. Time to Hire ===
with tab1:
    st.subheader("Середній час найму")
    st.metric("Середній час найму (днів)", round(internal_df["TimeToHire"].mean(), 2))

    fig, ax = plt.subplots()
    internal_df["TimeToHire"].hist(ax=ax)
    ax.set_title("Розподіл часу найму")
    st.pyplot(fig)

# === 2. Turnover ===
with tab2:
    st.subheader("Плинність персоналу")
    turnover_rate = internal_df["Attrition"].mean()
    st.metric("Загальна плинність (%)", round(turnover_rate * 100, 2))

    fig, ax = plt.subplots()
    internal_df["Attrition"].value_counts().plot(kind="bar", ax=ax)
    ax.set_title("Attrition Counts")
    st.pyplot(fig)

# === 3. Reasons for Attrition ===
with tab3:
    st.subheader("Причини звільнень")
    st.bar_chart(internal_df["Reason"].value_counts())

    fig, ax = plt.subplots()
    sns.heatmap(pd.crosstab(internal_df["Department"], internal_df["Reason"]), cmap="Blues", ax=ax)
    st.pyplot(fig)

# === 4. Tenure ===
with tab4:
    st.subheader("Стаж роботи")
    st.metric("Середній стаж (років)", round(internal_df["Tenure"].mean(), 2))

    fig, ax = plt.subplots()
    internal_df["Tenure"].hist(ax=ax)
    ax.set_title("Розподіл стажу")
    st.pyplot(fig)

# === 5. Compa Ratio Base Pay


def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    """Повертає CSV-байти для завантаження."""
    return df.to_csv(index=False).encode("utf-8")


# === ГОЛОВНА ФУНКЦІЯ ===
def main():
    st.set_page_config(
        page_title="HR Analytics – Compensation & Benefits",
        page_icon="💼",
        layout="wide",
    )

    # ---- ЗАГАЛЬНІ СТИЛІ (збільшуємо шрифти) ----
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

    median_salary = np.median(filtered_df["base_salary"])
    std_salary = np.std(filtered_df["base_salary"])

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Кількість співробітників", len(filtered_df))
    col2.metric(
        "Середня базова зарплата",
        f"{filtered_df['base_salary'].mean():,.0f} грн",
    )
    col3.metric(
        "Медіанна базова зарплата",
        f"{median_salary:,.0f} грн",
    )
    col4.metric(
        "Станд. відхилення окладу",
        f"{std_salary:,.0f} грн",
    )
    col5.metric(
        "Середній бонус",
        f"{filtered_df['bonus'].mean():,.0f} грн",
    )
    col6.metric(
        "Середній повний пакет",
        f"{filtered_df['total_compensation'].mean():,.0f} грн",
    )

    st.markdown("---")

    # ---- ГРАФІКИ ПО ВІДДІЛАХ (Plotly) ----
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
    st.plotly_chart(fig_salary_bonus, width="stretch")

    fig_total = px.bar(
        dept_comp,
        x="department",
        y="total_compensation",
        title="Середній повний компенсаційний пакет по відділах",
        labels={"total_compensation": "Сума, грн", "department": "Відділ"},
    )
    st.plotly_chart(fig_total, width="stretch")

    st.markdown("---")

    # ---- ДОДАТКОВИЙ ГРАФІК (Seaborn Boxplot) ----
    st.markdown("### 📦 Розподіл базової зарплати по відділах (boxplot)")

    fig_box, ax = plt.subplots(figsize=(8, 4))
    sns.boxplot(data=filtered_df, x="department", y="base_salary", ax=ax)
    ax.set_xlabel("Відділ")
    ax.set_ylabel("Базова зарплата, грн")
    ax.set_title("Розподіл базової зарплати по відділах")
    plt.xticks(rotation=30)
    st.pyplot(fig_box)

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
        st.plotly_chart(fig_benefits, width="stretch")

    with col_tbl:
        st.write("Табличний вигляд розподілу пільг:")
        st.dataframe(benefits_df, width="stretch")

    st.markdown("---")

    # ---- ТОП СПІВРОБІТНИКІВ ----
    st.markdown("### 🏆 ТОП співробітників за повним пакетом")

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
    st.dataframe(top_df, width="stretch")

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

    st.dataframe(details_df, width="stretch")

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
