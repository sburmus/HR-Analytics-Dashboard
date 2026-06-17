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
import chardet

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

def main():
    st.set_page_config(page_title="HR Analytics – Compensation & Benefits", layout="wide")

    st.markdown("""
    # HR Analytics Dashboard – Compensation & Benefits
    Дашборд для аналізу заробітних плат та пільг співробітників компанії,
    а також для порівняння внутрішніх зарплат із ринковими даними.
    """)

    # Завантаження та підготовка даних
    df = pd.read_csv("compensation.csv")
    df.columns = df.columns.str.strip()
    df = add_total_compensation(df)

    # Панель фільтрів
    st.sidebar.title("🔎 Панель фільтрів")
    departments = st.sidebar.multiselect("Відділи:", sorted(df["department"].unique()))
    if departments:
        available_roles = sorted(df[df["department"].isin(departments)]["Role_ua"].unique())
    else:
        available_roles = sorted(df["Role_ua"].unique())
    selected_roles = st.sidebar.multiselect("Посади:", available_roles)

    salary_min, salary_max = int(df["base_salary"].min()), int(df["base_salary"].max())
    salary_range = st.sidebar.slider("Діапазон базової зарплати:", salary_min, salary_max,
                                     (salary_min, salary_max), 1000)

    benefits_options = {
        "Медстрахування": "health_insurance",
        "Спортивна пільга": "sport",
        "Виплати на remote": "remote_allowance",
    }
    selected_benefits = st.sidebar.multiselect("Обрати пільги:", list(benefits_options.keys()))
    only_bonus = st.sidebar.checkbox("Тільки зі бонусом")

    # Фільтрація
    filtered_df = df.copy()
    if departments:
        filtered_df = filtered_df[filtered_df["department"].isin(departments)]
    if selected_roles:
        filtered_df = filtered_df[filtered_df["Role_ua"].isin(selected_roles)]
    filtered_df = filtered_df[(filtered_df["base_salary"] >= salary_range[0]) &
                              (filtered_df["base_salary"] <= salary_range[1])]
    if selected_benefits:
        cols = [benefits_options[benefit] for benefit in selected_benefits]
        filtered_df = filtered_df[filtered_df[cols].sum(axis=1) > 0]
    if only_bonus:
        filtered_df = filtered_df[filtered_df["bonus"] > 0]

    if filtered_df.empty:
        st.warning("За обраними фільтрами немає жодного співробітника.")
        return

    # 📊 Ключові показники
    st.markdown("### 📊 Ключові показники")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Кількість співробітників", len(filtered_df))
    col2.metric("Середня базова зарплата", f"{filtered_df['base_salary'].mean():,.0f} грн")
    col3.metric("Медіанна базова зарплата", f"{np.median(filtered_df['base_salary']):,.0f} грн")
    col4.metric("Станд. відхилення окладу", f"{np.std(filtered_df['base_salary']):,.0f} грн")
    col5.metric("Середній бонус", f"{filtered_df['bonus'].mean():,.0f} грн")
    col6.metric("Середній повний пакет", f"{filtered_df['total_compensation'].mean():,.0f} грн")

    # 🎁 Графіки бонусів
    avg_bonus_by_dept = filtered_df.groupby("department")["bonus"].mean().reset_index()
    fig_bonus_dept = px.bar(avg_bonus_by_dept, x="department", y="bonus", color="department",
                            title="Середній бонус по відділах")
    fig_bonus_dept.update_layout(showlegend=False)
    fig_bonus_dist = px.histogram(filtered_df, x="bonus", nbins=30, color="department",
                                  title="Розподіл бонусів серед співробітників")
    fig_bonus_dist.update_layout(showlegend=False)

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_bonus_dept, use_container_width=True, key="bonus_dept")
    with col2:
        st.plotly_chart(fig_bonus_dist, use_container_width=True, key="bonus_dist")

    # 📊 Компенсації по відділах
    dept_comp = filtered_df.groupby("department")[["base_salary","bonus","total_compensation"]].mean().reset_index()
    chart_type = st.radio("Тип графіка", ["Стовпчиковий","Лінійний","Кругова діаграма","Теплова карта"])
    if chart_type == "Стовпчиковий":
        st.plotly_chart(px.bar(dept_comp, x="department", y="total_compensation",
                               title="Середній повний пакет по відділах"),
                        use_container_width=True, key="dept_bar")
    elif chart_type == "Лінійний":
        st.plotly_chart(px.line(dept_comp, x="department", y="total_compensation",
                                title="Динаміка повного пакету по відділах"),
                        use_container_width=True, key="dept_line")
    elif chart_type == "Кругова діаграма":
        st.plotly_chart(px.pie(dept_comp, names="department", values="total_compensation",
                               title="Розподіл повного пакету по відділах"),
                        use_container_width=True, key="dept_pie")
    elif chart_type == "Теплова карта":
        fig, ax = plt.subplots(figsize=(8,4))
        pivot = filtered_df.pivot_table(values="base_salary", index="department", columns="Role_ua", aggfunc="mean")
        sns.heatmap(pivot.fillna(0), cmap="YlGnBu", annot=True, fmt=".0f", ax=ax)
        st.pyplot(fig, use_container_width=True, key="dept_heatmap")
    # 👩‍💼👨‍💼 Гендерний розрив у зарплатах
    st.markdown("## Гендерний розрив у зарплатах")

    if "gender" in filtered_df.columns:
        gender_stats = filtered_df.groupby("gender")["base_salary"].agg(["count","mean"]).reset_index()

        # Метрики
        col1, col2, col3 = st.columns(3)
        col1.metric("Кількість жінок", int(gender_stats.loc[gender_stats["gender"]=="Жінка","count"].values[0]) if "Жінка" in gender_stats["gender"].values else 0)
        col2.metric("Кількість чоловіків", int(gender_stats.loc[gender_stats["gender"]=="Чоловік","count"].values[0]) if "Чоловік" in gender_stats["gender"].values else 0)
        col3.metric("Різниця середньої зарплати", f"{gender_stats['mean'].max()-gender_stats['mean'].min():,.0f} грн")

        # Горизонтальний бар-чарт
        fig_gender = px.bar(
            gender_stats,
            x="mean",
            y="gender",
            orientation="h",
            color="gender",
            title="Середня зарплата за гендером",
            labels={"mean":"Середня зарплата, грн","gender":"Стать"},
            color_discrete_map={"Жінка":"purple","Чоловік":"blue"}
        )
        fig_gender.update_layout(showlegend=False)
        st.plotly_chart(fig_gender, use_container_width=True, key="gender_chart")

        # Bubble-чарт
        fig_bubble = px.scatter(
            filtered_df,
            x="base_salary",
            y="bonus",
            size="total_compensation",
            color="gender",
            title="Зарплата vs Бонус · розмір = повний пакет",
            labels={"base_salary":"Базова зарплата","bonus":"Бонус","gender":"Стать"},
            color_discrete_map={"Жінка":"purple","Чоловік":"blue"}
        )
        st.plotly_chart(fig_bubble, use_container_width=True, key="bubble_chart")

        # 📌 Висновок по повному пакету
        avg_total = filtered_df["total_compensation"].mean()
        min_total = filtered_df["total_compensation"].min()
        max_total = filtered_df["total_compensation"].max()

        st.markdown("### 📌 Висновок по повному пакету")
        st.write(f"Середній повний пакет становить **{avg_total:,.0f} грн**.")
        st.write(f"Діапазон компенсацій: від **{min_total:,.0f} грн** до **{max_total:,.0f} грн**.")
    else:
        st.info("Дані про стать відсутні для аналізу гендерного розриву.")

    # 🏆 ТОП співробітників
    st.markdown("### 🏆 ТОП співробітників за повним пакетом")
    max_top = min(50, len(filtered_df))
    top_n = st.slider("Кількість у ТОП-списку", min_value=3, max_value=max_top, value=10)
    top_df = filtered_df.sort_values("total_compensation", ascending=False).head(top_n)
    st.dataframe(top_df[[
        "name", "department", "Role_ua", "base_salary", "bonus",
        "health_insurance", "sport", "remote_allowance", "total_compensation"
    ]], use_container_width=True)

    # 📑 Ринковий аналіз
    st.markdown("### Market Analysis")
    selected_role = st.selectbox("Посада для аналізу:", sorted(df["Role_ua"].unique()))
    source_option = st.radio("Джерело ринкових даних:", ["Work.ua/DOU", "Власне дослідження"])

    if source_option == "Власне дослідження":
        custom_df = generate_random_market_research()
        st.dataframe(custom_df, use_container_width=True)
        role_match = custom_df.loc[custom_df["Role"] == selected_role, "Market_Salary"]
        market_salary = role_match.values[0] if not role_match.empty else None
    else:
        data = get_market_data(selected_role)
        market_salary = int(data["salary"]) if data["salary"] != "Не вказано" else None

    avg_internal = filtered_df[filtered_df["Role_ua"] == selected_role]["base_salary"].mean()

    if not np.isnan(avg_internal) and market_salary:
        diff = ((avg_internal - market_salary) / market_salary) * 100
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[0,1], y=[avg_internal,avg_internal],
                                mode="lines", name="Внутрішня зарплата",
                                line=dict(color="blue",width=3)))
        fig.add_trace(go.Scatter(x=[0,1], y=[market_salary,market_salary],
                                mode="lines", name="Ринкова зарплата",
                                line=dict(color="orange",width=3)))
        fig.update_layout(title=f"Порівняння зарплат: {selected_role}",
                        xaxis=dict(visible=False), yaxis_title="Зарплата (грн)")
        st.plotly_chart(fig, use_container_width=True, key="market_compare")

        st.markdown(f"📈 **Внутрішня середня зарплата:** {avg_internal:,.0f} грн")
        st.markdown(f"📊 **Ринкова зарплата ({source_option}):** {market_salary:,.0f} грн")
        color = "green" if diff >= 0 else "red"
        st.markdown(f"🔍 **Відхилення:** <span style='color:{color};'>{diff:+.1f}%</span>", unsafe_allow_html=True)
    else:
        st.info("Інформація для порівняння не повна.")

if __name__ == "__main__":
    main()
       