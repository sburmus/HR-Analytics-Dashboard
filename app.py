import importlib.util
import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt


# ==== Імпорт функцій із parser.py динамічно ====
module_path = Path(__file__).parent / "parser.py"
spec = importlib.util.spec_from_file_location("parser", str(module_path))
parser = importlib.util.module_from_spec(spec)
sys.modules["parser"] = parser
spec.loader.exec_module(parser)

get_market_data = parser.get_market_data
generate_random_market_research = parser.generate_random_market_research

BENEFIT_COSTS = {
    "health_insurance": 5000,
    "sport": 2000,
    "remote_allowance": 3000,
}

def add_total_compensation(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in ["health_insurance", "sport", "remote_allowance"]:
        df[col] = df[col].fillna(0).astype(float)
    df["total_compensation"] = (
        df["base_salary"] +
        df["bonus"] +
        df["health_insurance"] * BENEFIT_COSTS["health_insurance"] +
        df["sport"] * BENEFIT_COSTS["sport"] +
        df["remote_allowance"] * BENEFIT_COSTS["remote_allowance"]
    )
    return df

def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")

def convert_df_to_excel(df: pd.DataFrame) -> bytes:
    from io import BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def main():
    st.set_page_config(page_title="HR Analytics – Compensation & Benefits", layout="wide")

    st.markdown("""
    # HR Analytics Dashboard – Compensation & Benefits
    Дашборд для аналізу заробітних плат та пільг співробітників компанії,
    а також для порівняння внутрішніх зарплат з ринковими даними (з Work.ua/DOU або власних досліджень).
    """)

    df = pd.read_csv("compensation.csv", sep=",")
    df.columns = df.columns.str.strip()
    df = add_total_compensation(df)

    # Фільтри
    st.sidebar.title("🔎 Панель фільтрів")

    departments = st.sidebar.multiselect("Відділи:", options=sorted(df["department"].unique()))

    if departments:
        available_roles = sorted(df[df["department"].isin(departments)]["Role_ua"].unique())
    else:
        available_roles = sorted(df["Role_ua"].unique())
    selected_roles = st.sidebar.multiselect("Посади:", options=available_roles)

    salary_min, salary_max = int(df["base_salary"].min()), int(df["base_salary"].max())
    salary_range = st.sidebar.slider("Діапазон базової зарплати:",
                                     min_value=salary_min, max_value=salary_max,
                                     value=(salary_min, salary_max), step=1000)

    st.sidebar.markdown("### Пільги")
    only_health = st.sidebar.checkbox("Тільки з медстрахуванням")
    only_sport = st.sidebar.checkbox("Тільки зі спортивною пільгою")
    only_remote = st.sidebar.checkbox("Тільки з remote allowance")

    only_bonus = st.sidebar.checkbox("Тільки зі бонусом")

    # Застосування фільтрів
    filtered_df = df.copy()
    if departments:
        filtered_df = filtered_df[filtered_df["department"].isin(departments)]
    if selected_roles:
        filtered_df = filtered_df[filtered_df["Role_ua"].isin(selected_roles)]
    filtered_df = filtered_df[
        (filtered_df["base_salary"] >= salary_range[0]) &
        (filtered_df["base_salary"] <= salary_range[1])
    ]
    if only_health:
        filtered_df = filtered_df[filtered_df["health_insurance"] == 1]
    if only_sport:
        filtered_df = filtered_df[filtered_df["sport"] == 1]
    if only_remote:
        filtered_df = filtered_df[filtered_df["remote_allowance"] == 1]
    if only_bonus:
        filtered_df = filtered_df[filtered_df["bonus"] > 0]

    if filtered_df.empty:
        st.warning(
            "За обраними фільтрами немає жодного співробітника.\n"
            "Спробуйте зняти деякі обмеження у фільтрах, щоб побачити дані."
        )
        return

    # Ключові показники
    st.markdown("### 📊 Ключові показники")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Кількість співробітників", len(filtered_df))
    col2.metric("Середня базова зарплата", f"{filtered_df['base_salary'].mean():,.0f} грн")
    col3.metric("Медіанна базова зарплата", f"{np.median(filtered_df['base_salary']):,.0f} грн")
    col4.metric("Станд. відхилення окладу", f"{np.std(filtered_df['base_salary']):,.0f} грн")
    col5.metric("Середній бонус", f"{filtered_df['bonus'].mean():,.0f} грн")
    col6.metric("Середній повний пакет", f"{filtered_df['total_compensation'].mean():,.0f} грн")

    st.markdown("---")

    # Аналіз бонусів
    st.markdown("### 🎁 Аналіз бонусів")
    st.markdown("""
    Цей розділ показує, скільки співробітників отримують бонуси, як вони розподіляються по відділах,
    та який розмір бонусів серед співробітників.
    """)
    bonus_recipients = filtered_df[filtered_df["bonus"] > 0].shape[0]
    total_employees = filtered_df.shape[0]
    percent_bonus = (bonus_recipients / total_employees) * 100 if total_employees > 0 else 0
    st.metric("Співробітників з бонусами", f"{percent_bonus:.1f}% ({bonus_recipients} з {total_employees})")

    avg_bonus_by_dept = filtered_df.groupby("department")["bonus"].mean().reset_index()
    fig_bonus_dept = px.bar(avg_bonus_by_dept, x="department", y="bonus",
                            title="Середній бонус по відділах",
                            labels={"bonus": "Середній бонус, грн", "department": "Відділ"})
    st.plotly_chart(fig_bonus_dept, use_container_width=True)

    fig_bonus_dist = px.histogram(filtered_df, x="bonus", nbins=30,
                                  title="Розподіл бонусів серед співробітників",
                                  labels={"bonus": "Розмір бонусу, грн"})
    st.plotly_chart(fig_bonus_dist, use_container_width=True)

    st.markdown("---")

    # Графіки
    dept_comp = filtered_df.groupby("department")[["base_salary", "bonus", "total_compensation"]].mean().reset_index()
    chart_type = st.radio("Тип графіка:", ["Стовпчиковий", "Лінійний", "Кругова діаграма", "Теплова карта"])

    if chart_type == "Стовпчиковий":
        st.plotly_chart(px.bar(dept_comp, x="department", y="total_compensation", title="Середній повний пакет по відділах"),
                        use_container_width=True)
    elif chart_type == "Лінійний":
        st.plotly_chart(px.line(dept_comp, x="department", y="total_compensation", title="Динаміка повного пакету по відділах"),
                        use_container_width=True)
    elif chart_type == "Кругова діаграма":
        st.plotly_chart(px.pie(dept_comp, names="department", values="total_compensation",
                              title="Розподіл повного пакету по відділах"),
                        use_container_width=True)
    elif chart_type == "Теплова карта":
        fig, ax = plt.subplots(figsize=(8, 4))
        pivot = filtered_df.pivot_table(values="base_salary", index="department", columns="Role_ua", aggfunc="mean")
        sns.heatmap(pivot.fillna(0), cmap="YlGnBu", annot=True, fmt=".0f", ax=ax)
        st.pyplot(fig, use_container_width=True)

    st.markdown("---")

    # ТОП співробітників
    st.markdown("### 🏆 ТОП співробітників за повним пакетом")
    top_n = st.slider("Кількість у ТОП‑списку:", min_value=3, max_value=min(50, len(filtered_df)), value=10)
    top_df = filtered_df.sort_values("total_compensation", ascending=False).head(top_n)
    st.dataframe(top_df[[
        "name", "department", "Role_ua", "base_salary", "bonus",
        "health_insurance", "sport", "remote_allowance", "total_compensation"
    ]], use_container_width=True)

    st.markdown("---")

    # Експорт
    st.markdown("### 📤 Експорт відфільтрованих даних")
    csv_bytes = convert_df_to_csv(filtered_df)
    st.download_button(label="⬇️ Завантажити CSV", data=csv_bytes,
                       file_name="filtered_compensation.csv", mime="text/csv")

    excel_bytes = convert_df_to_excel(filtered_df)
    st.download_button(label="⬇️ Завантажити Excel", data=excel_bytes,
                       file_name="filtered_compensation.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.markdown("---")

    # Власне дослідження ринку
    st.markdown("### 📑 Власне дослідження ринку")
    custom_df = generate_random_market_research()
    st.dataframe(custom_df, use_container_width=True)

    # Аналіз ринку
    st.title("Market Analysis")
    selected_role = st.selectbox("Посада для аналізу:", sorted(df["Role_ua"].unique()))

    source_option = st.radio("Джерело ринкових даних:", ["Work.ua/DOU", "Власне дослідження"])

    if source_option == "Власне дослідження":
        role_match = custom_df.loc[custom_df["Role"] == selected_role, "Market_Salary"]
        if not role_match.empty:
            market_salary = role_match.values[0]
        else:
            st.warning(f"⚠️ Для ролі {selected_role} немає даних у власному дослідженні.")
            market_salary = None
    else:
        data = get_market_data(selected_role)
        market_salary = int(data["salary"]) if data["salary"] != "Не вказано" else None

    avg_internal = filtered_df[filtered_df["Role_ua"] == selected_role]["base_salary"].mean()

    if not np.isnan(avg_internal) and market_salary:
        diff = ((avg_internal - market_salary) / market_salary) * 100

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[0, 1],
            y=[avg_internal, avg_internal],
            mode='lines',
            name='Внутрішня зарплата',
            line=dict(color='blue', width=3),
        ))
        fig.add_trace(go.Scatter(
            x=[0, 1],
            y=[market_salary, market_salary],
            mode='lines',
            name='Ринкова зарплата',
            line=dict(color='orange', width=3),
        ))
        fig.update_layout(
            title=f"Порівняння зарплат: {selected_role}",
            xaxis=dict(visible=False),
            yaxis_title="Зарплата (грн)",
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"📈 **Внутрішня середня зарплата:** {avg_internal:,.0f} грн")
        st.markdown(f"📊 **Ринкова зарплата ({source_option}):** {market_salary:,.0f} грн")

        color = "green" if diff >= 0 else "red"
        st.markdown(f"🔍 **Відхилення:** <span style='color:{color};'>{diff:+.1f}%</span>", unsafe_allow_html=True)
    else:
        st.info("Інформація для порівняння не повна.")

if __name__ == "__main__":
    main()
