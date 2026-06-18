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
from io import BytesIO

# ── Динамічний імпорт parser.py ──────────────────────────────────────────────
module_path = Path(__file__).parent / "parser.py"
spec = importlib.util.spec_from_file_location("parser", str(module_path))
parser = importlib.util.module_from_spec(spec)
sys.modules["parser"] = parser
spec.loader.exec_module(parser)
get_market_data = parser.get_market_data
generate_random_market_research = parser.generate_random_market_research

# ── Вартість пільг (грн) ─────────────────────────────────────────────────────
BENEFIT_COSTS = {
    "health_insurance": 5000,
    "sport": 2000,
    "remote_allowance": 3000,
}

BENEFIT_LABELS = {
    "health_insurance": "Медстрахування",
    "sport": "Спорт",
    "remote_allowance": "Remote",
}


# ── Утиліти ───────────────────────────────────────────────────────────────────
def add_total_compensation(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in BENEFIT_COSTS:
        if col in df.columns:
            df[col] = df[col].fillna(0).astype(float)
        else:
            df[col] = 0.0
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
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()


# ── Сторінки ──────────────────────────────────────────────────────────────────
def page_home(filtered_df: pd.DataFrame):
    st.title("🏢 HR Analytics Dashboard")
    st.subheader("Compensation & Benefits")
    st.markdown(
        "Система призначена для аналізу зарплат, бонусів, компенсацій та пільг співробітників."
    )
    st.divider()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👥 Співробітників", len(filtered_df))
    c2.metric("💰 Середня зарплата", f"{filtered_df['base_salary'].mean():,.0f} грн")
    c3.metric("🎁 Середній бонус", f"{filtered_df['bonus'].mean():,.0f} грн")
    c4.metric(
        "💎 Середній повний пакет",
        f"{filtered_df['total_compensation'].mean():,.0f} грн",
    )

    st.divider()

    left, right = st.columns(2)
    with left:
        st.success("### 📊 Ключові показники\n- Аналіз зарплат\n- Медіана\n- Бюджет компенсацій")
        st.info("### 🎁 Бонуси та пільги\n- Аналіз бонусів\n- Медстрахування\n- Спорт\n- Remote")
        st.warning("### 👩‍🦰👨 Гендерна аналітика\n- Середня зарплата\n- Бонуси\n- Гендерний розрив")
    with right:
        st.success("### 🏆 Рейтинг співробітників\n- ТОП працівників\n- Повний пакет")
        st.info("### 📈 Аналіз ринку\n- Work.ua/DOU\n- Власні дослідження\n- Конкурентність")

    st.divider()
    st.subheader("📌 Розподіл співробітників по відділах")
    dept_count = filtered_df["department"].value_counts().reset_index()
    dept_count.columns = ["department", "count"]
    fig = px.pie(dept_count, names="department", values="count", title="Структура компанії")
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.success("👈 Використовуйте меню та фільтри зліва для переходу між розділами.")


def page_metrics(df: pd.DataFrame, filtered_df: pd.DataFrame):
    st.markdown("### 📊 Ключові показники")

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Кількість співробітників", len(filtered_df))
    c2.metric("Середня базова зарплата", f"{filtered_df['base_salary'].mean():,.0f} грн")
    c3.metric("Медіанна базова зарплата", f"{np.median(filtered_df['base_salary']):,.0f} грн")
    c4.metric("Стандартне відхилення окладу", f"{filtered_df['base_salary'].std():,.0f} грн")
    c5.metric("Середній бонус", f"{filtered_df['bonus'].mean():,.0f} грн")
    c6.metric("Середній повний пакет", f"{filtered_df['total_compensation'].mean():,.0f} грн")

    st.markdown("#### Додаткові показники")
    c7, c8, c9, c10 = st.columns(4)
    c7.metric("Мін. базова зарплата", f"{filtered_df['base_salary'].min():,.0f} грн")
    c8.metric("Макс. базова зарплата", f"{filtered_df['base_salary'].max():,.0f} грн")
    c9.metric("Загальний бюджет компенсацій", f"{filtered_df['total_compensation'].sum():,.0f} грн")
    coef_var = (
        filtered_df["base_salary"].std() / filtered_df["base_salary"].mean() * 100
        if filtered_df["base_salary"].mean()
        else 0
    )
    c10.metric("Коефіцієнт варіації окладу", f"{coef_var:.1f}%")

    st.markdown("#### Охоплення пільгами")
    cols = st.columns(len(BENEFIT_COSTS))
    for col_widget, (col_name, label) in zip(cols, BENEFIT_LABELS.items()):
        share = (filtered_df[col_name] > 0).mean() * 100
        col_widget.metric(f"Охоплення: {label}", f"{share:.1f}%")

    st.divider()
    st.subheader("Таблиця даних")
    st.dataframe(filtered_df, use_container_width=True)

    col_csv, col_xlsx = st.columns(2)
    col_csv.download_button(
        "⬇️ Завантажити CSV",
        data=convert_df_to_csv(filtered_df),
        file_name="compensation_filtered.csv",
        mime="text/csv",
    )
    col_xlsx.download_button(
        "⬇️ Завантажити Excel",
        data=convert_df_to_excel(filtered_df),
        file_name="compensation_filtered.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


def page_bonus_compensation(filtered_df: pd.DataFrame):
    st.markdown("### 🎁 Аналіз бонусів та компенсацій")

    # ── Бонуси ────────────────────────────────────────────────────────────────
    st.markdown("#### Бонуси")
    unique_emp = (
        filtered_df["employee_id"].nunique() if "employee_id" in filtered_df.columns else len(filtered_df)
    )
    emp_with_bonus = (
        filtered_df[filtered_df["bonus"] > 0]["employee_id"].nunique()
        if "employee_id" in filtered_df.columns
        else (filtered_df["bonus"] > 0).sum()
    )
    pct_bonus = emp_with_bonus / unique_emp * 100 if unique_emp else 0
    df_tmp = filtered_df.copy()
    df_tmp["bonus_pct"] = np.where(
        df_tmp["base_salary"] > 0, df_tmp["bonus"] / df_tmp["base_salary"] * 100, 0
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Унікальних співробітників", unique_emp)
    c2.metric("Отримали бонуси", f"{emp_with_bonus} ({pct_bonus:.1f}%)")
    c3.metric("Середній бонус", f"{filtered_df['bonus'].mean():,.0f} грн")
    c4.metric("Середній бонус (% від бази)", f"{df_tmp['bonus_pct'].mean():.1f}%")
    st.metric("Стандартне відхилення бонусів", f"{filtered_df['bonus'].std():,.0f} грн")

    col1, col2 = st.columns(2)
    with col1:
        avg_bonus_by_dept = filtered_df.groupby("department")["bonus"].mean().reset_index()
        st.plotly_chart(
            px.bar(avg_bonus_by_dept, x="department", y="bonus", title="Середній бонус по відділах"),
            use_container_width=True,
        )
    with col2:
        st.plotly_chart(
            px.histogram(filtered_df, x="bonus", nbins=30, title="Розподіл бонусів"),
            use_container_width=True,
        )

    # ── Пільги ────────────────────────────────────────────────────────────────
    st.markdown("#### Пільги")
    benefit_cols = list(BENEFIT_COSTS.keys())

    adoption = pd.DataFrame(
        {
            "Пільга": list(BENEFIT_LABELS.values()),
            "Охоплення, %": [(filtered_df[c] > 0).mean() * 100 for c in benefit_cols],
            "Витрати компанії, грн": [
                (filtered_df[c] > 0).sum() * BENEFIT_COSTS[c] for c in benefit_cols
            ],
        }
    )

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(
            px.bar(adoption, x="Пільга", y="Охоплення, %", title="Охоплення пільгами, %", color="Пільга"),
            use_container_width=True,
        )
    with c2:
        st.plotly_chart(
            px.pie(adoption, names="Пільга", values="Витрати компанії, грн", title="Розподіл витрат на пільги"),
            use_container_width=True,
        )

    st.dataframe(adoption, use_container_width=True)

    benefits_by_dept = filtered_df.groupby("department")[benefit_cols].mean().reset_index()
    melt = benefits_by_dept.melt(id_vars="department", var_name="Пільга", value_name="Частка")
    melt["Пільга"] = melt["Пільга"].map(BENEFIT_LABELS)
    st.plotly_chart(
        px.bar(melt, x="department", y="Частка", color="Пільга", barmode="group",
               title="Охоплення пільгами по відділах"),
        use_container_width=True,
    )

    # ── Компенсації по відділах ───────────────────────────────────────────────
    st.markdown("#### Компенсації по відділах")
    dept_comp = (
        filtered_df.groupby("department")[["base_salary", "bonus", "total_compensation"]]
        .mean()
        .reset_index()
    )
    chart_type = st.radio(
        "Тип графіка",
        ["Стовпчиковий", "Лінійний", "Кругова діаграма", "Теплова карта", "Бульбашковий"],
        horizontal=True,
    )

    if chart_type == "Стовпчиковий":
        st.plotly_chart(
            px.bar(dept_comp, x="department", y="total_compensation", color="department",
                   title="Середня компенсація по відділах"),
            use_container_width=True,
        )
    elif chart_type == "Лінійний":
        st.plotly_chart(
            px.line(dept_comp, x="department", y="total_compensation", color="department",
                    markers=True, title="Динаміка компенсацій"),
            use_container_width=True,
        )
    elif chart_type == "Кругова діаграма":
        st.plotly_chart(
            px.pie(dept_comp, names="department", values="total_compensation",
                   title="Частка компенсацій по відділах"),
            use_container_width=True,
        )
    elif chart_type == "Теплова карта":
        if "Role_ua" in filtered_df.columns:
            fig, ax = plt.subplots(figsize=(10, 5))
            pivot = filtered_df.pivot_table(
                values="base_salary", index="department", columns="Role_ua", aggfunc="mean"
            )
            sns.heatmap(pivot.fillna(0), cmap="YlOrRd", annot=True, fmt=".0f", ax=ax)
            st.pyplot(fig, use_container_width=True)
        else:
            st.warning("Колонка 'Role_ua' відсутня для теплової карти.")
    elif chart_type == "Бульбашковий":
        st.plotly_chart(
            px.scatter(dept_comp, x="base_salary", y="bonus", size="total_compensation",
                       color="department", title="Бульбашковий графік: зарплата vs бонус"),
            use_container_width=True,
        )


def page_gender(filtered_df: pd.DataFrame):
    st.markdown("### 👩‍🦰👨 Гендерна аналітика")

    if "gender" not in filtered_df.columns:
        st.warning("Дані про стать відсутні у файлі.")
        return

    gender_stats = (
        filtered_df.groupby("gender")["base_salary"]
        .agg(["count", "mean", "median"])
        .reset_index()
    )

    c1, c2, c3 = st.columns(3)
    women_count = (
        gender_stats.loc[gender_stats["gender"] == "Жінка", "count"].values[0]
        if "Жінка" in gender_stats["gender"].values
        else 0
    )
    men_count = (
        gender_stats.loc[gender_stats["gender"] == "Чоловік", "count"].values[0]
        if "Чоловік" in gender_stats["gender"].values
        else 0
    )
    c1.metric("Кількість жінок", women_count)
    c2.metric("Кількість чоловіків", men_count)
    if len(gender_stats) >= 2:
        diff = gender_stats["mean"].max() - gender_stats["mean"].min()
        c3.metric("Різниця середньої зарплати", f"{diff:,.0f} грн")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(
            px.bar(
                gender_stats, x="mean", y="gender", orientation="h",
                color="gender", title="Середня зарплата за статтю",
                color_discrete_map={"Жінка": "purple", "Чоловік": "blue"},
                labels={"mean": "Середня зарплата, грн", "gender": "Стать"},
            ),
            use_container_width=True,
        )
    with col2:
        st.plotly_chart(
            px.box(
                filtered_df, x="gender", y="base_salary", color="gender",
                title="Розподіл зарплат за статтю",
                color_discrete_map={"Жінка": "purple", "Чоловік": "blue"},
            ),
            use_container_width=True,
        )

    st.plotly_chart(
        px.scatter(
            filtered_df, x="base_salary", y="bonus",
            size="total_compensation", color="gender",
            title="Зарплата vs Бонус (розмір = повний пакет)",
            color_discrete_map={"Жінка": "purple", "Чоловік": "blue"},
        ),
        use_container_width=True,
    )


def page_top(filtered_df: pd.DataFrame):
    st.markdown("### 🏆 Рейтинг співробітників")
    top_n = st.slider("Обрати кількість:", min_value=3, max_value=min(50, len(filtered_df)), value=10)
    cols_to_show = [
        c for c in [
            "name", "department", "Role_ua", "base_salary", "bonus",
            "health_insurance", "sport", "remote_allowance", "total_compensation",
        ]
        if c in filtered_df.columns
    ]
    top_df = filtered_df.sort_values("total_compensation", ascending=False).head(top_n)
    st.dataframe(top_df[cols_to_show], use_container_width=True)

    st.plotly_chart(
        px.bar(
            top_df.sort_values("total_compensation"),
            x="total_compensation",
            y="name" if "name" in top_df.columns else top_df.index.astype(str),
            orientation="h",
            color="department" if "department" in top_df.columns else None,
            title=f"ТОП-{top_n} за повним компенсаційним пакетом",
        ),
        use_container_width=True,
    )


def page_market(filtered_df: pd.DataFrame, full_df: pd.DataFrame):
    st.markdown("### 📑 Аналіз ринку: внутрішня зарплата та ринкові дані")

    if "Role_ua" not in full_df.columns:
        st.warning("Колонка 'Role_ua' відсутня.")
        return

    selected_role = st.selectbox("Оберіть посаду:", sorted(full_df["Role_ua"].unique()))
    source_option = st.radio("Джерело ринкових даних:", ["Work.ua/DOU", "Власне дослідження"])

    role_df = filtered_df[filtered_df["Role_ua"] == selected_role]
    avg_internal = role_df["base_salary"].mean() if not role_df.empty else None

    market_salary = None
    if source_option == "Власне дослідження":
        custom_df = generate_random_market_research()
        st.dataframe(custom_df, use_container_width=True)
        row = custom_df.loc[custom_df["Role"] == selected_role]
        if not row.empty:
            market_salary = float(row["Market_Salary"].values[0])
    else:
        data = get_market_data(selected_role)
        if data and data.get("salary") not in (None, "Не вказано"):
            market_salary = int(data["salary"])

    if avg_internal and market_salary:
        diff = (avg_internal - market_salary) / market_salary * 100

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[0, 1], y=[avg_internal, avg_internal],
            mode="lines+markers", name="Внутрішня зарплата",
            line=dict(color="blue", width=3)
        ))
        fig.add_trace(go.Scatter(
            x=[0, 1], y=[market_salary, market_salary],
            mode="lines+markers", name=f"Ринкова зарплата ({source_option})",
            line=dict(color="orange", width=3)
        ))
        fig.update_layout(
            title=f"Порівняння зарплат: {selected_role}",
            yaxis_title="Зарплата (грн)",
            xaxis=dict(visible=False),
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(f"📈 Внутрішня середня зарплата: **{avg_internal:,.0f} грн**")
        st.markdown(f"📊 Ринкова зарплата: **{market_salary:,.0f} грн**")
        color = "green" if diff >= 0 else "red"
        st.markdown(
            f"🔍 Відхилення: <span style='color:{color};font-weight:bold'>{diff:+.1f}%</span>",
            unsafe_allow_html=True,
        )
    else:
        st.info("Недостатньо даних для порівняння на цю посаду.")


# ── Головна функція ───────────────────────────────────────────────────────────
def main():
    st.set_page_config(page_title="HR Analytics Dashboard", layout="wide")
def main():
    st.set_page_config(page_title="HR Analytics Dashboard", layout="wide")

    # Приховуємо автоматичну навігацію Streamlit (верхній список сторінок)
    st.markdown(
        """
        <style>
        [data-testid="stSidebarNav"] {display: none;}
        </style>
        """,
        unsafe_allow_html=True,
    )

  
    # Завантаження та підготовка даних
    df = pd.read_csv("compensation.csv")
    df.columns = df.columns.str.strip()
    df = add_total_compensation(df)  # ← розраховуємо total_compensation

    # Сайдбар: меню
    st.sidebar.title("Меню")
    page = st.sidebar.radio(
        "Оберіть сторінку:",
        [
            "Головна",
            "Ключові показники",
            "Аналіз бонусів та компенсацій",
            "Гендерна аналітика",
            "Рейтинг співробітників",
            "Аналіз ринку",
        ],
    )

    # Сайдбар: фільтри
    st.sidebar.title("Фільтри")
    departments = st.sidebar.multiselect("Відділи:", sorted(df["department"].unique()))
    if departments:
        available_roles = sorted(df[df["department"].isin(departments)]["Role_ua"].unique())
    else:
        available_roles = sorted(df["Role_ua"].unique())
    selected_roles = st.sidebar.multiselect("Посади:", available_roles)

    salary_min = int(df["base_salary"].min())
    salary_max = int(df["base_salary"].max())
    salary_range = st.sidebar.slider(
        "Діапазон базової зарплати:", salary_min, salary_max, (salary_min, salary_max), step=1000
    )

    benefits_options = {
        "Медстрахування": "health_insurance",
        "Спортивна пільга": "sport",
        "Виплати на remote": "remote_allowance",
    }
    selected_benefits = st.sidebar.multiselect("Обрати пільги:", list(benefits_options.keys()))
    only_bonus = st.sidebar.checkbox("Тільки зі бонусом")

    # Застосування фільтрів
    filtered_df = df.copy()
    if departments:
        filtered_df = filtered_df[filtered_df["department"].isin(departments)]
    if selected_roles:
        filtered_df = filtered_df[filtered_df["Role_ua"].isin(selected_roles)]
    filtered_df = filtered_df[
        (filtered_df["base_salary"] >= salary_range[0])
        & (filtered_df["base_salary"] <= salary_range[1])
    ]
    if selected_benefits:
        benefit_cols = [benefits_options[b] for b in selected_benefits]
        filtered_df = filtered_df[filtered_df[benefit_cols].sum(axis=1) > 0]
    if only_bonus:
        filtered_df = filtered_df[filtered_df["bonus"] > 0]

    if filtered_df.empty:
        st.warning("За обраними фільтрами немає співробітників. Змініть параметри фільтру.")
        return

    # Маршрутизація сторінок
    if page == "Головна":
        page_home(filtered_df)
    elif page == "Ключові показники":
        page_metrics(df, filtered_df)
    elif page == "Аналіз бонусів та компенсацій":
        page_bonus_compensation(filtered_df)
    elif page == "Гендерна аналітика":
        page_gender(filtered_df)
    elif page == "Рейтинг співробітників":
        page_top(filtered_df)
    elif page == "Аналіз ринку":
        page_market(filtered_df, df)


if __name__ == "__main__":
    main()