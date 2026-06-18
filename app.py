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


def inject_metrics_css():
    """Стилі тільки для сторінки 'Ключові показники'."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap');

        .kpi-hero {
            background: linear-gradient(135deg, #16203A 0%, #0E1525 100%);
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 18px;
            padding: 28px 32px;
            margin-bottom: 20px;
        }
        .kpi-hero-label {
            font-family: 'Inter', sans-serif;
            color: #8B96B2;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: .08em;
            margin-bottom: 6px;
        }
        .kpi-hero-value {
            font-family: 'Sora', sans-serif;
            color: #F4F7FF;
            font-size: 42px;
            font-weight: 800;
            line-height: 1.15;
        }
        .kpi-hero-sub {
            font-family: 'Inter', sans-serif;
            color: #6E7A99;
            font-size: 13.5px;
            margin-top: 4px;
        }
        .mix-bar {
            display: flex;
            height: 14px;
            border-radius: 8px;
            overflow: hidden;
            margin-top: 18px;
            background: rgba(255,255,255,0.05);
        }
        .mix-seg { height: 100%; }
        .mix-legend {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-top: 10px;
            font-family: 'Inter', sans-serif;
            font-size: 12.5px;
            color: #9AA5C4;
        }
        .mix-dot {
            display: inline-block;
            width: 9px; height: 9px;
            border-radius: 50%;
            margin-right: 6px;
        }
        .kpi-card {
            background: #141A2B;
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 14px;
            padding: 18px 20px;
            height: 100%;
            margin-bottom: 14px;
        }
        .kpi-card .icon { font-size: 19px; margin-bottom: 8px; opacity: .9; }
        .kpi-card .label {
            font-family: 'Inter', sans-serif;
            color: #7E89A8;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: .05em;
            margin-bottom: 4px;
        }
        .kpi-card .value {
            font-family: 'Sora', sans-serif;
            color: #F4F7FF;
            font-size: 23px;
            font-weight: 700;
        }
        .coverage-row { margin-bottom: 14px; }
        .coverage-label {
            font-family: 'Inter', sans-serif;
            color: #C3CBE0;
            font-size: 13.5px;
            display: flex;
            justify-content: space-between;
            margin-bottom: 6px;
        }
        .coverage-track {
            height: 9px;
            background: rgba(255,255,255,0.06);
            border-radius: 6px;
            overflow: hidden;
        }
        .coverage-fill { height: 100%; border-radius: 6px; }
        .section-title {
            font-family: 'Inter', sans-serif;
            color: #C3CBE0;
            font-size: 15px;
            font-weight: 600;
            margin: 6px 0 14px 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(icon: str, label: str, value: str):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="icon">{icon}</div>
            <div class="label">{label}</div>
            <div class="value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def coverage_bar(label: str, share: float, color: str):
    st.markdown(
        f"""
        <div class="coverage-row">
            <div class="coverage-label"><span>{label}</span><span>{share:.1f}%</span></div>
            <div class="coverage-track">
                <div class="coverage-fill" style="width:{share:.1f}%; background:{color};"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


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
    inject_metrics_css()

    # ── Розрахунки ────────────────────────────────────────────────────────────
    n = len(filtered_df)
    avg_base = filtered_df["base_salary"].mean()
    median_base = np.median(filtered_df["base_salary"])
    std_base = filtered_df["base_salary"].std()
    min_base = filtered_df["base_salary"].min()
    max_base = filtered_df["base_salary"].max()
    avg_bonus = filtered_df["bonus"].mean()
    total_budget = filtered_df["total_compensation"].sum()
    avg_total = filtered_df["total_compensation"].mean()
    cv = std_base / avg_base * 100 if avg_base else 0

    total_base_sum = filtered_df["base_salary"].sum()
    total_bonus_sum = filtered_df["bonus"].sum()
    total_benefits_sum = max(total_budget - total_base_sum - total_bonus_sum, 0)
    base_pct = total_base_sum / total_budget * 100 if total_budget else 0
    bonus_pct = total_bonus_sum / total_budget * 100 if total_budget else 0
    benefits_pct = max(100 - base_pct - bonus_pct, 0)

    # ── Hero: загальний бюджет + структура компенсації ─────────────────────────
    st.markdown(
        f"""
        <div class="kpi-hero">
            <div class="kpi-hero-label">Загальний бюджет компенсацій</div>
            <div class="kpi-hero-value">{total_budget:,.0f} грн</div>
            <div class="kpi-hero-sub">{n} співробітників · середній пакет {avg_total:,.0f} грн</div>
            <div class="mix-bar">
                <div class="mix-seg" style="width:{base_pct:.1f}%; background:#4F8CFF;"></div>
                <div class="mix-seg" style="width:{bonus_pct:.1f}%; background:#34D399;"></div>
                <div class="mix-seg" style="width:{benefits_pct:.1f}%; background:#FBBF24;"></div>
            </div>
            <div class="mix-legend">
                <span><span class="mix-dot" style="background:#4F8CFF;"></span>Базова зарплата · {base_pct:.0f}%</span>
                <span><span class="mix-dot" style="background:#34D399;"></span>Бонуси · {bonus_pct:.0f}%</span>
                <span><span class="mix-dot" style="background:#FBBF24;"></span>Пільги · {benefits_pct:.0f}%</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── KPI картки ────────────────────────────────────────────────────────────
    row1 = [
        ("👥", "Співробітників", f"{n}"),
        ("💰", "Середня база", f"{avg_base:,.0f} грн"),
        ("📍", "Медіана бази", f"{median_base:,.0f} грн"),
        ("📈", "Std. відхилення", f"{std_base:,.0f} грн"),
    ]
    row2 = [
        ("⬇️", "Мінімум бази", f"{min_base:,.0f} грн"),
        ("⬆️", "Максимум бази", f"{max_base:,.0f} грн"),
        ("🎁", "Середній бонус", f"{avg_bonus:,.0f} грн"),
        ("🎯", "Коеф. варіації", f"{cv:.1f}%"),
    ]
    for row in (row1, row2):
        cols = st.columns(4)
        for col, (icon, label, value) in zip(cols, row):
            with col:
                kpi_card(icon, label, value)

    # ── Охоплення пільгами ───────────────────────────────────────────────────
    st.markdown('<div class="section-title">Охоплення пільгами</div>', unsafe_allow_html=True)
    coverage_colors = {
        "health_insurance": "#34D399",
        "sport": "#FBBF24",
        "remote_allowance": "#38BDF8",
    }
    cov_cols = st.columns(3)
    for col, (col_name, label) in zip(cov_cols, BENEFIT_LABELS.items()):
        share = (filtered_df[col_name] > 0).mean() * 100
        with col:
            coverage_bar(label, share, coverage_colors[col_name])

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


def show_gender_gap(filtered_df: pd.DataFrame):
    st.markdown("### 👩‍🦰👨 Гендерна аналітика")

    # Шукаємо колонку гендеру (незалежно від регістру)
    gender_col = next((c for c in filtered_df.columns if c.lower() == "gender"), None)
    if gender_col is None:
        st.warning("⚠️ Дані про стать відсутні.")
        return

    df = filtered_df.copy()
    df["gender"] = df[gender_col].astype(str).str.strip()

    # Визначаємо унікальні значення
    unique_genders = df["gender"].unique().tolist()

    gender_stats = (
        df.groupby("gender")["base_salary"]
        .agg(["count", "mean", "median"])
        .reset_index()
    )

    c1, c2, c3 = st.columns(3)
    for i, g in enumerate(unique_genders[:2]):
        val = gender_stats.loc[gender_stats["gender"] == g, "count"].values
        [c1, c2][i].metric(f"Кількість: {g}", int(val[0]) if len(val) else 0)

    if len(gender_stats) >= 2:
        diff = gender_stats["mean"].max() - gender_stats["mean"].min()
        c3.metric("Різниця середніх зарплат", f"{diff:,.0f} грн")

    st.divider()

    fig1 = px.bar(
        gender_stats, x="gender", y="mean", color="gender",
        title="Середня зарплата за гендером",
        labels={"gender": "Гендер", "mean": "Середня зарплата, грн"},
    )
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.scatter(
        df, x="base_salary", y="bonus",
        size="total_compensation", color="gender",
        title="Зарплата vs Бонус (розмір = повний пакет)",
    )
    st.plotly_chart(fig2, use_container_width=True)

    if "performance_score" in df.columns:
        fig3 = px.box(
            df, x="gender", y="performance_score", color="gender",
            title="Розподіл Performance Score за гендером",
        )
        st.plotly_chart(fig3, use_container_width=True)

    # KPI метрики
    gender_stats = (
        filtered_df.groupby("gender")["base_salary"]
        .agg(["count", "mean", "median"])
        .reset_index()
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Кількість жінок",
              gender_stats.loc[gender_stats["gender"] == "Жінка", "count"].values[0]
              if "Жінка" in gender_stats["gender"].values else 0)
    c2.metric("Кількість чоловіків",
              gender_stats.loc[gender_stats["gender"] == "Чоловік", "count"].values[0]
              if "Чоловік" in gender_stats["gender"].values else 0)

    if len(gender_stats) == 2:
        diff = gender_stats.loc[gender_stats["gender"] == "Чоловік", "mean"].values[0] - \
               gender_stats.loc[gender_stats["gender"] == "Жінка", "mean"].values[0]
        c3.metric("Різниця середніх зарплат", f"{diff:,.0f} грн")

    st.divider()

    # Графік: середня зарплата за гендером
    fig1 = px.bar(
        gender_stats,
        x="gender", y="mean", color="gender",
        title="Середня зарплата за гендером",
        labels={"gender": "Гендер", "mean": "Середня зарплата, грн"},
        color_discrete_sequence=["#a64ca6", "#4c6ca6"]
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Графік: розподіл співробітників
    st.subheader("📊 Розподіл співробітників за гендером")
    st.bar_chart(filtered_df["gender"].value_counts())

# --- Виклик у маршрутизації ---
def page_gender(df):
    st.title("👩‍💼 Гендерна аналітика")
    role_col = "Role_ua"
    selected_role = st.selectbox("Оберіть роль:", df[role_col].unique())
    filtered_df = df[df[role_col] == selected_role]
    show_gender_gap(filtered_df)

                    
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
def page_top(filtered_df: pd.DataFrame):
    st.markdown("### 🏆 Рейтинг співробітників")
    st.markdown("ТОП співробітників за повним компенсаційним пакетом. Корисно для виявлення ключових талантів.")

    top_n = st.slider("Кількість у рейтингу:", min_value=3, max_value=min(50, len(filtered_df)), value=10)

    cols_to_show = [c for c in [
        "name", "department", "Role_ua", "base_salary", "bonus",
        "health_insurance", "sport", "remote_allowance",
        "total_compensation", "performance_score"
    ] if c in filtered_df.columns]

    top_df = filtered_df.sort_values("total_compensation", ascending=False).head(top_n)
    st.dataframe(top_df[cols_to_show], use_container_width=True)

    if "performance_score" in filtered_df.columns:
        st.markdown("#### Зв'язок performance_score та компенсації")
        fig = px.scatter(
            top_df, x="performance_score", y="total_compensation",
            color="department", hover_data=["name", "Role_ua"],
            title="Performance Score vs Повний пакет (ТОП співробітників)"
        )
        st.plotly_chart(fig, use_container_width=True)

# ── Головна функція ───────────────────────────────────────────────────────────
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
        show_gender_gap(filtered_df)
    elif page == "Рейтинг співробітників":
        page_top(filtered_df)
    elif page == "Аналіз ринку":
        page_market(filtered_df, df)


if __name__ == "__main__":
    main()