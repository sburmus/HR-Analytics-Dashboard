#import importlib.util
import sys
#from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
import os

#""" # ── Динамічний імпорт parser.py ──────────────────────────────────────────────
#module_path = Path(__file__).parent / "parsers" / "parser.py"
#spec = importlib.util.spec_from_file_location("parser", str(module_path))
#parser = importlib.util.module_from_spec(spec)
#sys.modules["parser"] = parser
#spec.loader.exec_module(parser)
#get_market_data = parser.get_market_data
#generate_random_market_research = parser.generate_random_market_research """

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
import streamlit as st
import pandas as pd
import plotly.express as px

def page_home(filtered_df: pd.DataFrame):
    # CSS для вкладок
    st.markdown(
        """
        <style>
        /* Збільшення шрифту у вкладках */
        .stTabs [data-baseweb="tab"] {
            font-size: 20px;
            font-weight: bold;
        }
        /* Активна вкладка */
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            color: #4CAF50;
            border-bottom: 3px solid #4CAF50;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Великий заголовок по центру
    st.markdown(
        "<h1 style='text-align:center; font-size:48px;'>🏢 HR Analytics Dashboard</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<h3 style='text-align:center; font-size:24px; color:gray;'>💰 Salary • 🎁 Compensation • 💎 Benefits</h3>",
        unsafe_allow_html=True,
    )

    st.success(
        """
        👋 Ласкаво просимо!  
        Це сучасний HR Dashboard для аналізу зарплат, бонусів та пільг співробітників.  
        Використовуйте меню та фільтри зліва, щоб отримати індивідуальні зрізи даних.
        """
    )

    st.divider()

    # Метрики
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👥 Співробітників", len(filtered_df))
    c2.metric("💰 Середня зарплата", f"{filtered_df['base_salary'].mean():,.0f} грн")
    c3.metric("🎁 Середній бонус", f"{filtered_df['bonus'].mean():,.0f} грн")
    c4.metric("💎 Повний пакет", f"{filtered_df['total_compensation'].mean():,.0f} грн")

    st.divider()

    # Вкладки
    tab1, tab2, tab3 = st.tabs(["📊 Основні можливості", "🏆 Для HR", "📌 Структура компанії"])

    with tab1:
        st.markdown(
            """
            ### 📊 Основні можливості
            Тут ви знайдете ключові інструменти для аналізу:
            - Зарплат та бонусів
            - Гендерної аналітики
            - Порівняння внутрішніх даних із ринком
            """,
            unsafe_allow_html=True
        )
        
        

    with tab2:
        st.markdown(
            """
            ### 🏆 Для HR та менеджерів
            Цей розділ допомагає:
            - Виявляти ключових талантів
            - Оцінювати конкурентоспроможність компанії
            - Приймати стратегічні рішення на основі даних
            """,
            unsafe_allow_html=True
        )

    with tab3:
        st.markdown(
            """
            ### 📌 Структура компанії
            Візуалізація розподілу співробітників по відділах.
            Це допомагає зрозуміти баланс ресурсів та структуру організації.
            """,
            unsafe_allow_html=True
        )
        dept_count = filtered_df["department"].value_counts().reset_index()
        dept_count.columns = ["department", "count"]
        fig = px.pie(dept_count, names="department", values="count", title="Структура компанії")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
  



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
    st.dataframe(filtered_df, width="stretch")

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
    st.title("🎁 Бонуси та компенсації")
    st.markdown("Детальний аналіз бонусних програм, структури компенсацій та використання пільг по відділах.")
    st.divider()

    tab1, tab2, tab3 = st.tabs(["💰 Бонуси", "📊 Компенсації по відділах", "🩺 Пільги"])

    # ── Бонуси ────────────────────────────────────────────────────────────────
    with tab1:
        st.markdown("### 💰 Аналіз бонусів")
        st.caption("Бонуси — змінна частина доходу, що залежить від результатів роботи та KPI.")

        unique_emp = filtered_df["employee_id"].nunique() if "employee_id" in filtered_df.columns else len(filtered_df)
        emp_with_bonus = (
            filtered_df[filtered_df["bonus"] > 0]["employee_id"].nunique()
            if "employee_id" in filtered_df.columns
            else (filtered_df["bonus"] > 0).sum()
        )
        pct_bonus = emp_with_bonus / unique_emp * 100 if unique_emp else 0
        avg_bonus = filtered_df["bonus"].mean()
        df_tmp = filtered_df.copy()
        df_tmp["bonus_pct"] = np.where(df_tmp["base_salary"] > 0, df_tmp["bonus"] / df_tmp["base_salary"] * 100, 0)

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("👥 Співробітників", unique_emp)
        m2.metric("🎯 Отримали бонус", f"{emp_with_bonus} ({pct_bonus:.0f}%)")
        m3.metric("💰 Середній бонус", f"{avg_bonus:,.0f} грн")
        m4.metric("📈 Бонус % від бази", f"{df_tmp['bonus_pct'].mean():.1f}%")
        m5.metric("🏆 Макс. бонус", f"{filtered_df['bonus'].max():,.0f} грн")

        st.divider()

        left, right = st.columns(2)
        with left:
            st.markdown("#### Середній бонус по відділах")
            avg_by_dept = filtered_df.groupby("department")["bonus"].mean().reset_index().sort_values("bonus")
            fig1 = px.bar(avg_by_dept, x="bonus", y="department", orientation="h",
                          color="bonus", color_continuous_scale="Blues",
                          labels={"bonus": "Середній бонус, грн", "department": ""},
                          text=avg_by_dept["bonus"].apply(lambda x: f"{x:,.0f} грн"))
            fig1.update_traces(textposition="outside")
            fig1.update_layout(height=350, coloraxis_showscale=False,
                               margin=dict(t=10, b=10), plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig1, width="stretch")

        with right:
            st.markdown("#### Розподіл бонусів")
            fig2 = px.histogram(filtered_df, x="bonus", nbins=30,
                                color_discrete_sequence=["#4F8CFF"],
                                labels={"bonus": "Бонус, грн"})
            fig2.add_vline(x=avg_bonus, line_dash="dash", line_color="#34D399", line_width=2,
                           annotation_text=f"Середній: {avg_bonus:,.0f}", annotation_position="top right")
            fig2.update_layout(height=350, margin=dict(t=10, b=10), plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig2, width="stretch")

        st.divider()

        left2, right2 = st.columns(2)
        with left2:
            st.markdown("#### Бонус як % від базової зарплати")
            bp = df_tmp.groupby("department")["bonus_pct"].mean().reset_index().sort_values("bonus_pct")
            fig3 = px.bar(bp, x="bonus_pct", y="department", orientation="h",
                          color="bonus_pct", color_continuous_scale="Greens",
                          labels={"bonus_pct": "Бонус, %", "department": ""},
                          text=bp["bonus_pct"].apply(lambda x: f"{x:.1f}%"))
            fig3.update_traces(textposition="outside")
            fig3.update_layout(height=350, coloraxis_showscale=False,
                               margin=dict(t=10, b=10), plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig3, width="stretch")

        with right2:
            st.markdown("#### Частка співробітників з бонусом по відділах")
            bs = filtered_df.groupby("department").apply(lambda x: (x["bonus"] > 0).mean() * 100).reset_index()
            bs.columns = ["department", "share"]
            bs_sorted = bs.sort_values("share")
            fig4 = px.bar(bs_sorted, x="share", y="department", orientation="h",
                          color="share", color_continuous_scale="Oranges",
                          labels={"share": "Частка, %", "department": ""},
                          text=bs_sorted["share"].apply(lambda x: f"{x:.0f}%"))
            fig4.update_traces(textposition="outside")
            fig4.update_layout(height=350, coloraxis_showscale=False,
                               margin=dict(t=10, b=10), plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig4, width="stretch")

        st.info("💡 **Висновок:** високий середній бонус та широке охоплення свідчать про розвинену систему мотивації.")

    # ── Компенсації ───────────────────────────────────────────────────────────
    with tab2:
        st.markdown("### 📊 Компенсації по відділах")
        st.caption("Повний компенсаційний пакет = базова зарплата + бонус + вартість пільг.")

        total_budget = filtered_df["total_compensation"].sum()
        avg_total = filtered_df["total_compensation"].mean()
        base_share = filtered_df["base_salary"].sum() / total_budget * 100 if total_budget else 0
        bonus_share = filtered_df["bonus"].sum() / total_budget * 100 if total_budget else 0
        benefits_share = max(100 - base_share - bonus_share, 0)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("💎 Загальний бюджет", f"{total_budget:,.0f} грн")
        m2.metric("📦 Середній пакет", f"{avg_total:,.0f} грн")
        m3.metric("💰 Середня база", f"{filtered_df['base_salary'].mean():,.0f} грн")
        m4.metric("🎁 Частка пільг", f"{benefits_share:.1f}%")

        st.divider()

        dept_comp = filtered_df.groupby("department")[["base_salary", "bonus", "total_compensation"]].mean().reset_index()
        benefit_cols = list(BENEFIT_COSTS.keys())

        left, right = st.columns(2)
        with left:
            st.markdown("#### Структура компенсації (stacked)")
            dept_b = filtered_df.groupby("department")[benefit_cols].mean().reset_index()
            dept_bb = filtered_df.groupby("department")[["base_salary", "bonus"]].mean().reset_index()
            merged = dept_bb.merge(dept_b, on="department")
            fig5 = go.Figure()
            fig5.add_trace(go.Bar(name="База", x=merged["department"], y=merged["base_salary"], marker_color="#4F8CFF"))
            fig5.add_trace(go.Bar(name="Бонус", x=merged["department"], y=merged["bonus"], marker_color="#34D399"))
            for col, label, color in zip(benefit_cols, list(BENEFIT_LABELS.values()), ["#FBBF24", "#F87171", "#A78BFA"]):
                fig5.add_trace(go.Bar(name=label, x=merged["department"],
                                      y=merged[col] * BENEFIT_COSTS[col], marker_color=color))
            fig5.update_layout(barmode="stack", height=380, margin=dict(t=10, b=10),
                               plot_bgcolor="rgba(0,0,0,0)", yaxis_title="грн")
            st.plotly_chart(fig5, width="stretch")

        with right:
            st.markdown("#### База vs Повний пакет")
            fig6 = go.Figure()
            fig6.add_trace(go.Bar(name="Базова зарплата", x=dept_comp["department"],
                                  y=dept_comp["base_salary"], marker_color="#4F8CFF"))
            fig6.add_trace(go.Bar(name="Повний пакет", x=dept_comp["department"],
                                  y=dept_comp["total_compensation"], marker_color="#34D399"))
            fig6.update_layout(barmode="group", height=380, margin=dict(t=10, b=10),
                               plot_bgcolor="rgba(0,0,0,0)", yaxis_title="грн")
            st.plotly_chart(fig6, width="stretch")

        st.divider()

        left2, right2 = st.columns(2)
        with left2:
            st.markdown("#### Бульбашковий: зарплата vs бонус")
            fig7 = px.scatter(dept_comp, x="base_salary", y="bonus",
                              size="total_compensation", color="department",
                              labels={"base_salary": "Середня база, грн", "bonus": "Середній бонус, грн"})
            fig7.update_layout(height=350, margin=dict(t=10, b=10))
            st.plotly_chart(fig7, width="stretch")

        with right2:
            st.markdown("#### Частка компенсацій по відділах")
            fig8 = px.pie(dept_comp, names="department", values="total_compensation",
                          color_discrete_sequence=px.colors.qualitative.Pastel, hole=0.4)
            fig8.update_layout(height=350, margin=dict(t=10, b=10))
            st.plotly_chart(fig8, width="stretch")

        st.info("💡 **Висновок:** stacked графік показує реальну структуру витрат на кожного співробітника по відділах.")

    # ── Пільги ────────────────────────────────────────────────────────────────
    with tab3:
        st.markdown("### 🩺 Аналіз пільг")
        st.caption("Пільги збільшують цінність компенсаційного пакету без прямого підвищення зарплати.")

        benefit_cols = list(BENEFIT_COSTS.keys())
        adoption = pd.DataFrame({
            "Пільга": list(BENEFIT_LABELS.values()),
            "Охоплення, %": [(filtered_df[c] > 0).mean() * 100 for c in benefit_cols],
            "Витрати компанії, грн": [(filtered_df[c] > 0).sum() * BENEFIT_COSTS[c] for c in benefit_cols],
            "К-сть співробітників": [(filtered_df[c] > 0).sum() for c in benefit_cols],
        })

        m1, m2, m3 = st.columns(3)
        for col_widget, (_, row) in zip([m1, m2, m3], adoption.iterrows()):
            col_widget.metric(row["Пільга"], f"{row['Охоплення, %']:.1f}%", f"{int(row['К-сть співробітників'])} осіб")

        st.divider()

        left, right = st.columns(2)
        with left:
            st.markdown("#### Охоплення пільгами, %")
            fig9 = px.bar(adoption, x="Пільга", y="Охоплення, %", color="Пільга",
                          text=adoption["Охоплення, %"].apply(lambda x: f"{x:.1f}%"),
                          color_discrete_sequence=["#34D399", "#FBBF24", "#38BDF8"])
            fig9.update_traces(textposition="outside")
            fig9.update_layout(height=320, showlegend=False,
                               margin=dict(t=10, b=10), plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig9, width="stretch")

        with right:
            st.markdown("#### Розподіл витрат на пільги")
            fig10 = px.pie(adoption, names="Пільга", values="Витрати компанії, грн",
                           color_discrete_sequence=["#34D399", "#FBBF24", "#38BDF8"], hole=0.4)
            fig10.update_layout(height=320, margin=dict(t=10, b=10))
            st.plotly_chart(fig10, width="stretch")

        st.divider()
        st.markdown("#### Охоплення пільгами по відділах")
        dept_benefits = filtered_df.groupby("department")[benefit_cols].mean().reset_index()
        melt = dept_benefits.melt(id_vars="department", var_name="Пільга", value_name="Частка")
        melt["Пільга"] = melt["Пільга"].map(BENEFIT_LABELS)
        melt["Частка, %"] = melt["Частка"] * 100
        fig11 = px.bar(melt, x="department", y="Частка, %", color="Пільга", barmode="group",
                       color_discrete_sequence=["#34D399", "#FBBF24", "#38BDF8"],
                       labels={"department": "Відділ"})
        fig11.update_layout(height=360, margin=dict(t=10, b=10), plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig11, width="stretch")

        st.dataframe(adoption, width="stretch")
        st.info("💡 **Висновок:** нерівномірне охоплення між відділами може бути сигналом для HR-перегляду політики компенсацій.")

def show_gender_gap(filtered_df: pd.DataFrame):
    st.title("👩‍💼 Гендерна аналітика")
    st.markdown("Аналіз гендерної рівності у зарплатах, бонусах та компенсаційних пакетах компанії.")
    st.divider()

    df = filtered_df.copy()

    # Генерація якщо відсутня
    gender_col = next((c for c in df.columns if c.lower() == "gender"), None)
    if gender_col is None:
        df["gender"] = np.random.choice(["Жінка", "Чоловік"], size=len(df))
    else:
        df["gender"] = df[gender_col].astype(str).str.strip()

    if "performance_score" not in df.columns:
        df["performance_score"] = np.random.randint(1, 11, size=len(df))

    unique_genders = df["gender"].unique().tolist()
    gender_stats = df.groupby("gender")["base_salary"].agg(["count", "mean", "median", "std"]).reset_index()

    # KPI
    cols = st.columns(len(unique_genders) + 2)
    for i, g in enumerate(unique_genders):
        row = gender_stats[gender_stats["gender"] == g]
        if not row.empty:
            cols[i].metric(f"👤 {g}", f"{int(row['count'].values[0])} осіб",
                           f"сер. {row['mean'].values[0]:,.0f} грн")
    if len(gender_stats) >= 2:
        vals = gender_stats["mean"].values
        diff = vals[0] - vals[1]
        diff_pct = abs(diff) / max(vals) * 100
        cols[-2].metric("📊 Різниця зарплат", f"{abs(diff):,.0f} грн")
        cols[-1].metric("📉 Гендерний розрив", f"{diff_pct:.1f}%")

    st.divider()

    # Ряд 1
    left, right = st.columns(2)
    with left:
        st.markdown("#### Середня зарплата за гендером")
        fig1 = px.bar(gender_stats, x="gender", y="mean", color="gender",
                      text=gender_stats["mean"].apply(lambda x: f"{x:,.0f} грн"),
                      color_discrete_sequence=["#a855f7", "#3b82f6"],
                      labels={"gender": "", "mean": "Середня зарплата, грн"})
        fig1.update_traces(textposition="outside")
        fig1.update_layout(height=340, showlegend=False,
                           margin=dict(t=10, b=10), plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig1, width="stretch")

    with right:
        st.markdown("#### Розподіл зарплат (violin)")
        fig2 = px.violin(df, x="gender", y="base_salary", color="gender",
                         box=True, points="outliers",
                         color_discrete_sequence=["#a855f7", "#3b82f6"],
                         labels={"gender": "", "base_salary": "Базова зарплата, грн"})
        fig2.update_layout(height=340, showlegend=False,
                           margin=dict(t=10, b=10), plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig2, width="stretch")

    st.divider()

    # Ряд 2
    left2, right2 = st.columns(2)
    with left2:
        st.markdown("#### Зарплата vs Бонус")
        fig3 = px.scatter(df, x="base_salary", y="bonus", color="gender",
                          size="total_compensation",
                          color_discrete_sequence=["#a855f7", "#3b82f6"],
                          labels={"base_salary": "Базова зарплата, грн",
                                  "bonus": "Бонус, грн", "gender": "Гендер"},
                          hover_data=["department"] if "department" in df.columns else None)
        fig3.update_layout(height=360, margin=dict(t=10, b=10))
        st.plotly_chart(fig3, width="stretch")

    with right2:
        st.markdown("#### Середній бонус за гендером")
        bonus_stats = df.groupby("gender")["bonus"].mean().reset_index()
        fig4 = px.bar(bonus_stats, x="gender", y="bonus", color="gender",
                      text=bonus_stats["bonus"].apply(lambda x: f"{x:,.0f} грн"),
                      color_discrete_sequence=["#a855f7", "#3b82f6"],
                      labels={"gender": "", "bonus": "Середній бонус, грн"})
        fig4.update_traces(textposition="outside")
        fig4.update_layout(height=360, showlegend=False,
                           margin=dict(t=10, b=10), plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig4, width="stretch")

    st.divider()

    # Ряд 3
    left3, right3 = st.columns(2)
    with left3:
        st.markdown("#### Гендерний розподіл по відділах")
        if "department" in df.columns:
            dept_gender = df.groupby(["department", "gender"]).size().reset_index(name="count")
            fig5 = px.bar(dept_gender, x="department", y="count", color="gender", barmode="group",
                          color_discrete_sequence=["#a855f7", "#3b82f6"],
                          labels={"department": "Відділ", "count": "К-сть", "gender": "Гендер"})
            fig5.update_layout(height=360, margin=dict(t=10, b=10), plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig5, width="stretch")

    with right3:
        st.markdown("#### Performance Score за гендером")
        fig6 = px.box(df, x="gender", y="performance_score", color="gender",
                      color_discrete_sequence=["#a855f7", "#3b82f6"],
                      labels={"gender": "", "performance_score": "Performance Score"})
        fig6.update_layout(height=360, showlegend=False,
                           margin=dict(t=10, b=10), plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig6, width="stretch")

    st.divider()

    # Середня зарплата по відділах та гендеру
    if "department" in df.columns:
        st.markdown("#### Середня зарплата по відділах та гендеру")
        dept_gender_salary = df.groupby(["department", "gender"])["base_salary"].mean().reset_index()
        fig7 = px.bar(dept_gender_salary, x="department", y="base_salary",
                      color="gender", barmode="group",
                      color_discrete_sequence=["#a855f7", "#3b82f6"],
                      text=dept_gender_salary["base_salary"].apply(lambda x: f"{x:,.0f}"),
                      labels={"department": "Відділ", "base_salary": "Середня зарплата, грн", "gender": "Гендер"})
        fig7.update_traces(textposition="outside")
        fig7.update_layout(height=400, margin=dict(t=10, b=10), plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig7, width="stretch")

    st.divider()

    # Висновок
    if len(gender_stats) >= 2:
        vals = gender_stats["mean"].values
        diff_pct = abs(vals[0] - vals[1]) / max(vals) * 100
        if diff_pct < 5:
            st.success("✅ Гендерний розрив у зарплатах **мінімальний** (< 5%). Компанія демонструє рівність оплати праці.")
        elif diff_pct < 15:
            st.warning(f"🟡 Гендерний розрив складає **{diff_pct:.1f}%**. Рекомендується провести додатковий аналіз.")
        else:
            st.error(f"🔴 Значний гендерний розрив — **{diff_pct:.1f}%**. Необхідний перегляд політики оплати праці.")

# --- Виклик у маршрутизації ---
def page_gender(df):
    st.title("👩‍💼 Гендерна аналітика")
    role_col = "Role_ua"
    selected_role = st.selectbox("Оберіть роль:", df[role_col].unique())
    filtered_df = df[df[role_col] == selected_role]
    show_gender_gap(filtered_df)

                    
# ── Реальні ринкові дані (3 джерела) ─────────────────────────────────────────
MARKET_SOURCES = {
    "Work.ua": "market_data/market_salaries_by_work.csv",
    "Служба зайнятості (СЗУ)": "market_data/market_salaries_by_SZU.csv",
    "Jooble": "market_data/market_salaries_by_jooble.csv",
}


@st.cache_data
def load_market_data(path: str) -> pd.DataFrame:
    mdf = pd.read_csv(path)
    mdf.columns = mdf.columns.str.strip()
    return mdf


def page_market(filtered_df: pd.DataFrame, full_df: pd.DataFrame):
    st.title("📑 Аналіз ринку")
    st.markdown("Порівняння внутрішніх зарплат з реальними ринковими даними з трьох джерел.")
    st.divider()
# ── Оновлення ринкових даних прямо з інтерфейсу ──────────────────────────
    with st.expander("🔄 Оновити ринкові дані"):
        st.caption(
            "Запускає всі три парсери та перезаписує CSV-файли в market_data/. "
            "Може зайняти кілька хвилин залежно від швидкості інтернету."
        )
        if st.button("Оновити зараз", key="update_market_btn"):
            import subprocess

            parser_files = [
                ("Work.ua", "parsers/work_parser.py"),
                ("Служба зайнятості", "parsers/parser_SZU.py"),
                ("Jooble", "parsers/jooble_parser.py"),
            ]
            progress = st.progress(0)
            status = st.empty()

            for i, (name, path) in enumerate(parser_files):
                status.info(f"Оновлюю: {name}...")
                import os
                env = os.environ.copy()
                env["PYTHONIOENCODING"] = "utf-8"

                result = subprocess.run(
                    [sys.executable, path],
                    capture_output=True, text=True,
                    encoding="utf-8", errors="replace",
                    env=env,
                )
                if result.returncode != 0:
                    st.error(f"❌ Помилка при оновленні «{name}»:\n```\n{result.stderr[:500]}\n```")
                else:
                    st.success(f"✅ {name} оновлено")
                progress.progress((i + 1) / len(parser_files))

            st.cache_data.clear()
            status.success("Готово! Перезавантажую сторінку...")
            st.rerun()
                                  
    if "Role_ua" not in full_df.columns:
        st.warning("Колонка 'Role_ua' відсутня.")
        return

    col_sel, col_src = st.columns([2, 2])
    with col_sel:
        selected_role = st.selectbox("Оберіть посаду:", sorted(full_df["Role_ua"].unique()))
    with col_src:
        source_option = st.radio("Джерело ринкових даних:", list(MARKET_SOURCES.keys()), horizontal=True)

    market_df = load_market_data(MARKET_SOURCES[source_option])

    role_df = filtered_df[filtered_df["Role_ua"] == selected_role]
    avg_internal = role_df["base_salary"].mean() if not role_df.empty else None

    market_role_df = market_df[market_df["Role_ua"] == selected_role]
    market_salary = market_role_df["Average_Market_Salary_UAH"].mean() if not market_role_df.empty else None
    last_updated = (
        market_role_df["Last_Updated"].iloc[0]
        if not market_role_df.empty and "Last_Updated" in market_role_df.columns
        else None
    )

    if not avg_internal or not market_salary:
        st.info("Недостатньо даних для порівняння на цю посаду в обраному джерелі.")
        return

    if last_updated:
        st.caption(f"📅 Дані по джерелу «{source_option}» станом на: {last_updated}")

    diff = (avg_internal - market_salary) / market_salary * 100
    diff_abs = avg_internal - market_salary

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Внутрішня зарплата", f"{avg_internal:,.0f} грн")
    m2.metric(f"Ринок ({source_option})", f"{market_salary:,.0f} грн")
    m3.metric("Відхилення", f"{diff:+.1f}%", delta=f"{diff_abs:+,.0f} грн")
    m4.metric("Кількість на посаді", len(role_df))

    st.divider()

    left, right = st.columns(2)
    with left:
        st.markdown("#### Індекс конкурентоспроможності")
        competitiveness = min(max((avg_internal / market_salary) * 100, 0), 150)
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=competitiveness,
            delta={"reference": 100, "valueformat": ".1f", "suffix": "%"},
            number={"suffix": "%", "valueformat": ".1f"},
            gauge={
                "axis": {"range": [0, 150]},
                "bar": {"color": "#4F8CFF"},
                "steps": [
                    {"range": [0, 85], "color": "#FF4B4B"},
                    {"range": [85, 100], "color": "#FBBF24"},
                    {"range": [100, 150], "color": "#34D399"},
                ],
                "threshold": {"line": {"color": "white", "width": 3}, "thickness": 0.75, "value": 100},
            },
            title={"text": f"{selected_role}<br><span style='font-size:13px;color:gray'>{source_option} = 100%</span>"},
        ))
        fig_gauge.update_layout(height=320, margin=dict(t=60, b=20, l=30, r=30))
        st.plotly_chart(fig_gauge, width="stretch")

    with right:
        st.markdown("#### Внутрішня зарплата vs Ринок")
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=["Внутрішня зарплата", f"Ринок ({source_option})"],
            y=[avg_internal, market_salary],
            marker_color=["#4F8CFF", "#FBBF24"],
            text=[f"{avg_internal:,.0f} грн", f"{market_salary:,.0f} грн"],
            textposition="outside", width=0.4,
        ))
        fig_bar.update_layout(height=320, yaxis_title="Зарплата, грн",
                              showlegend=False, margin=dict(t=40, b=20),
                              plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_bar, width="stretch")

    st.divider()

    left2, right2 = st.columns(2)
    with left2:
        st.markdown(f"#### Відхилення від ринку ({source_option}) по всіх посадах")
        all_roles_avg = full_df.groupby("Role_ua")["base_salary"].mean().reset_index()
        all_roles_avg.columns = ["Role_ua", "avg_salary"]
        market_by_role = market_df.groupby("Role_ua")["Average_Market_Salary_UAH"].mean().reset_index()
        all_roles_avg = all_roles_avg.merge(market_by_role, on="Role_ua", how="left")
        all_roles_avg["diff_pct"] = (
            (all_roles_avg["avg_salary"] - all_roles_avg["Average_Market_Salary_UAH"])
            / all_roles_avg["Average_Market_Salary_UAH"] * 100
        )
        fig_roles = px.bar(
            all_roles_avg.dropna(subset=["diff_pct"]).sort_values("diff_pct"),
            x="diff_pct", y="Role_ua", orientation="h",
            color="diff_pct", color_continuous_scale=["#FF4B4B", "#FBBF24", "#34D399"],
            labels={"diff_pct": "Відхилення, %", "Role_ua": ""},
        )
        fig_roles.update_layout(height=380, margin=dict(t=20, b=20), coloraxis_showscale=False)
        fig_roles.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)
        st.plotly_chart(fig_roles, width="stretch")

    with right2:
        st.markdown(f"#### Розподіл зарплат: {selected_role}")
        fig_hist = px.histogram(role_df, x="base_salary", nbins=15,
                                labels={"base_salary": "Базова зарплата, грн"},
                                color_discrete_sequence=["#4F8CFF"])
        fig_hist.add_vline(x=avg_internal, line_color="#34D399", line_width=2,
                           annotation_text=f"Внутрішня: {avg_internal:,.0f}", annotation_position="top right")
        fig_hist.add_vline(x=market_salary, line_dash="dash", line_color="#FBBF24", line_width=2,
                           annotation_text=f"Ринок: {market_salary:,.0f}", annotation_position="top left")
        fig_hist.update_layout(height=380, margin=dict(t=20, b=20), plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_hist, width="stretch")

    st.divider()

    st.markdown(f"#### Порівняння всіх джерел для посади «{selected_role}»")
    compare_rows = []
    for src_name, src_path in MARKET_SOURCES.items():
        src_df = load_market_data(src_path)
        src_role = src_df[src_df["Role_ua"] == selected_role]
        if not src_role.empty:
            compare_rows.append({"Джерело": src_name, "Зарплата, грн": src_role["Average_Market_Salary_UAH"].mean()})
    compare_rows.append({"Джерело": "Внутрішня (компанія)", "Зарплата, грн": avg_internal})
    compare_df = pd.DataFrame(compare_rows)
    fig_compare = px.bar(
        compare_df, x="Джерело", y="Зарплата, грн", color="Джерело",
        text=compare_df["Зарплата, грн"].apply(lambda x: f"{x:,.0f} грн"),
    )
    fig_compare.update_traces(textposition="outside")
    fig_compare.update_layout(height=360, showlegend=False, margin=dict(t=20, b=20), plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_compare, width="stretch")

    st.divider()
    if diff >= 10:
        st.success(f"✅ Компанія **вище ринку** ({source_option}) на {diff:.1f}% для посади **{selected_role}**.")
    elif diff >= 0:
        st.info(f"🟡 Зарплата **на рівні ринку** ({source_option}, {diff:+.1f}%) для посади **{selected_role}**.")
    else:
        st.error(f"🔴 Зарплата **нижче ринку** ({source_option}) на {abs(diff):.1f}% для посади **{selected_role}**.")

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
    st.dataframe(top_df[cols_to_show], width="stretch")

    if "performance_score" in filtered_df.columns:
        st.markdown("#### Зв'язок performance_score та компенсації")
        fig = px.scatter(
            top_df, x="performance_score", y="total_compensation",
            color="department", hover_data=["name", "Role_ua"],
            title="Performance Score vs Повний пакет (ТОП співробітників)"
        )
        st.plotly_chart(fig, width="stretch")

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