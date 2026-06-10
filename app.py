import streamlit as st
import pandas as pd
import plotly.express as px

# === Константи ===
BENEFIT_COSTS = {
    "health_insurance": 5000,
    "sport": 2000,
    "remote_allowance": 3000,
}

# === Функції ===
def add_total_compensation(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # про всяк випадок переконаємось, що це числа (0/1 або 0/1.0)
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


# === Основна логіка ===
def main():
    st.set_page_config(
        page_title="HR Analytics – Compensation & Benefits",
        page_icon="💼",
        layout="wide",
    )

    # ---- Стилі для заголовків ----
    st.markdown(
        """
        <style>
        .main-title {
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 0px;
        }
        .sub-title {
            font-size: 18px;
            color: #555;
            margin-top: 0px;
            margin-bottom: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ---- Шапка сторінки ----
    st.markdown('<p class="main-title">HR Analytics – Аналіз компенсацій і пільг</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-title">Умовна компанія Adidas Ukraine • 200+ співробітників • Дані згенеровані для навчальних цілей</p>',
        unsafe_allow_html=True,
    )

    st.markdown("### Опис проєкту")
    st.write(
        "Дашборд показує структуру компенсаційних пакетів співробітників: "
        "базовий оклад, бонуси та пільги (медичне страхування, спортзал, компенсація віддаленої роботи). "
        "Користувач може фільтрувати дані за відділами, рівнем зарплати й наявністю пільг, "
        "а також отримувати узагальнені показники, графіки та детальні таблиці."
    )

    st.markdown("---")

    # ---- Завантаження даних ----
    df = pd.read_csv("compensation.csv")
    df = add_total_compensation(df)

    # ---- Фільтри (sidebar) ----
    st.sidebar.header("🔎 Фільтри")

    departments = st.sidebar.multiselect(
        "Виберіть відділи:",
        options=sorted(df["department"].unique()),
        default=None,
    )

    salary_min = int(df["base_salary"].min())
    salary_max = int(df["base_salary"].max())
    salary_range = st.sidebar.slider(
        "Діапазон базової зарплати:",
        salary_min,
        salary_max,
        (salary_min, salary_max),
        step=1000,
    )

    st.sidebar.markdown("**Пільги:**")
    only_health = st.sidebar.checkbox("Тільки з медстрахуванням")
    only_sport = st.sidebar.checkbox("Тільки зі спортом")
    only_remote = st.sidebar.checkbox("Тільки з remote allowance")

    # ---- Фільтрація даних ----
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
        st.warning("За обраними фільтрами немає жодного співробітника. Змініть умови фільтрації.")
        return  # далі немає сенсу нічого будувати

    # ---- Блок метрик ----
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

    # ---- Графік 1: середня компенсація по відділах ----
    st.markdown("### 🏢 Середня компенсація по відділах")

    dept_comp = (
        filtered_df.groupby("department")[["base_salary", "bonus", "total_compensation"]]
        .mean()
        .reset_index()
    )

    fig1 = px.bar(
        dept_comp,
        x="department",
        y=["base_salary", "bonus"],
        barmode="group",
        title="Середня базова зарплата та бонус по відділах",
        labels={"value": "Сума, грн", "department": "Відділ"},
    )
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.bar(
        dept_comp,
        x="department",
        y="total_compensation",
        title="Середній повний компенсаційний пакет по відділах",
        labels={"total_compensation": "Сума, грн", "department": "Відділ"},
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ---- Графік 2: розподіл пільг ----
    st.markdown("### 🎁 Розподіл пільг серед співробітників")

    benefits_count = {
        "Медстрахування": int(filtered_df["health_insurance"].sum()),
        "Спортзал": int(filtered_df["sport"].sum()),
        "Remote allowance": int(filtered_df["remote_allowance"].sum()),
    }
    benefits_df = pd.DataFrame(
        list(benefits_count.items()), columns=["Пільга", "Кількість"]
    )

    col_pie, col_table = st.columns(2)
    with col_pie:
        fig3 = px.pie(
            benefits_df,
            names="Пільга",
            values="Кількість",
            title="Частка співробітників із різними пільгами",
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col_table:
        st.write("Табличний вигляд розподілу пільг:")
        st.dataframe(benefits_df, use_container_width=True)

    st.markdown("---")

    # ---- Таблиці: топ і деталі ----
    st.markdown("### 🏆 Топ співробітників за повним пакетом")

    top_n = st.slider(
        "Скільки показати у ТОП‑списку:", 3, min(50, len(filtered_df)), 10
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

    st.markdown("### 📋 Детальна таблиця співробітників (з урахуванням фільтрів)")
    st.dataframe(
        filtered_df[
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
        ].sort_values("name"),
        use_container_width=True,
    )

    st.markdown("---")

    # ---- Експорт ----
    st.markdown("### 📤 Експорт відфільтрованих даних")
    csv = convert_df_to_csv(filtered_df)
    st.download_button(
        "⬇️ Завантажити CSV",
        data=csv,
        file_name="filtered_compensation.csv",
        mime="text/csv",
    )

    # ---- Футер ----
    st.markdown(
        "<br><hr><small>Проєкт: аналіз компенсацій і пільг співробітників в умовній компанії Adidas Ukraine. "
        "Усі дані є змодельованими для навчальних цілей.</small>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
