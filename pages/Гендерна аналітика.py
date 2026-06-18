import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import importlib.util
import sys

st.set_page_config(page_title="Гендерна аналітика", layout="wide")

# Імпорт з app.py
module_path = Path(__file__).parent.parent / "app.py"
spec = importlib.util.spec_from_file_location("app", str(module_path))
app_module = importlib.util.module_from_spec(spec)
sys.modules["app"] = app_module
spec.loader.exec_module(app_module)
add_total_compensation = app_module.add_total_compensation


def main():
    df = pd.read_csv("compensation.csv")
    df.columns = df.columns.str.strip()

    # Генерація відсутніх колонок
    if "gender" not in df.columns:
        df["gender"] = np.random.choice(["Жінка", "Чоловік"], size=len(df))
    if "employee_id" not in df.columns and "id" in df.columns:
        df["employee_id"] = df["id"]
    if "performance_score" not in df.columns:
        df["performance_score"] = np.random.randint(1, 11, size=len(df))

    df = add_total_compensation(df)

    # Нормалізація значень гендеру
    gender_col = next((c for c in df.columns if c.lower() == "gender"), None)
    if gender_col:
        df["gender"] = df[gender_col].astype(str).str.strip()

    st.title("👩‍💼 Гендерна аналітика")
    st.markdown("Аналіз гендерної рівності у зарплатах, бонусах та компенсаційних пакетах компанії.")
    st.divider()

    unique_genders = df["gender"].unique().tolist()
    gender_stats = df.groupby("gender")["base_salary"].agg(["count", "mean", "median", "std"]).reset_index()

    # ── KPI метрики ───────────────────────────────────────────────────────────
    cols = st.columns(len(unique_genders) + 2)
    for i, g in enumerate(unique_genders):
        row = gender_stats[gender_stats["gender"] == g]
        if not row.empty:
            cols[i].metric(f"👤 {g}", f"{int(row['count'].values[0])} осіб",
                           f"сер. {row['mean'].values[0]:,.0f} грн")

    if len(gender_stats) >= 2:
        means = gender_stats.set_index("gender")["mean"]
        vals = list(means.values)
        diff = vals[0] - vals[1]
        diff_pct = abs(diff) / max(vals) * 100
        cols[-2].metric("📊 Різниця зарплат", f"{abs(diff):,.0f} грн")
        cols[-1].metric("📉 Гендерний розрив", f"{diff_pct:.1f}%",
                        delta="нижче ринку" if diff < 0 else "вище ринку",
                        delta_color="inverse" if diff < 0 else "normal")

    st.divider()

    # ── Ряд 1 ─────────────────────────────────────────────────────────────────
    left, right = st.columns(2)

    with left:
        st.markdown("#### Середня зарплата за гендером")
        fig1 = px.bar(
            gender_stats, x="gender", y="mean", color="gender",
            text=gender_stats["mean"].apply(lambda x: f"{x:,.0f} грн"),
            color_discrete_sequence=["#a855f7", "#3b82f6"],
            labels={"gender": "", "mean": "Середня зарплата, грн"},
        )
        fig1.update_traces(textposition="outside")
        fig1.update_layout(height=340, showlegend=False,
                           margin=dict(t=10, b=10), plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig1, use_container_width=True)

    with right:
        st.markdown("#### Розподіл зарплат (violin)")
        fig2 = px.violin(
            df, x="gender", y="base_salary", color="gender", box=True, points="outliers",
            color_discrete_sequence=["#a855f7", "#3b82f6"],
            labels={"gender": "", "base_salary": "Базова зарплата, грн"},
        )
        fig2.update_layout(height=340, showlegend=False,
                           margin=dict(t=10, b=10), plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # ── Ряд 2 ─────────────────────────────────────────────────────────────────
    left2, right2 = st.columns(2)

    with left2:
        st.markdown("#### Зарплата vs Бонус")
        fig3 = px.scatter(
            df, x="base_salary", y="bonus",
            color="gender", size="total_compensation",
            color_discrete_sequence=["#a855f7", "#3b82f6"],
            labels={"base_salary": "Базова зарплата, грн",
                    "bonus": "Бонус, грн", "gender": "Гендер"},
            hover_data=["department"] if "department" in df.columns else None,
        )
        fig3.update_layout(height=360, margin=dict(t=10, b=10))
        st.plotly_chart(fig3, use_container_width=True)

    with right2:
        st.markdown("#### Середній бонус за гендером")
        bonus_stats = df.groupby("gender")["bonus"].mean().reset_index()
        fig4 = px.bar(
            bonus_stats, x="gender", y="bonus", color="gender",
            text=bonus_stats["bonus"].apply(lambda x: f"{x:,.0f} грн"),
            color_discrete_sequence=["#a855f7", "#3b82f6"],
            labels={"gender": "", "bonus": "Середній бонус, грн"},
        )
        fig4.update_traces(textposition="outside")
        fig4.update_layout(height=360, showlegend=False,
                           margin=dict(t=10, b=10), plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig4, use_container_width=True)

    st.divider()

    # ── Ряд 3 ─────────────────────────────────────────────────────────────────
    left3, right3 = st.columns(2)

    with left3:
        st.markdown("#### Гендерний розподіл по відділах")
        if "department" in df.columns:
            dept_gender = df.groupby(["department", "gender"]).size().reset_index(name="count")
            fig5 = px.bar(
                dept_gender, x="department", y="count", color="gender", barmode="group",
                color_discrete_sequence=["#a855f7", "#3b82f6"],
                labels={"department": "Відділ", "count": "К-сть", "gender": "Гендер"},
            )
            fig5.update_layout(height=360, margin=dict(t=10, b=10), plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig5, use_container_width=True)

    with right3:
        st.markdown("#### Performance Score за гендером")
        if "performance_score" in df.columns:
            fig6 = px.box(
                df, x="gender", y="performance_score", color="gender",
                color_discrete_sequence=["#a855f7", "#3b82f6"],
                labels={"gender": "", "performance_score": "Performance Score"},
            )
            fig6.update_layout(height=360, showlegend=False,
                               margin=dict(t=10, b=10), plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig6, use_container_width=True)

    st.divider()

    # ── Середня зарплата по відділах та гендеру ───────────────────────────────
    if "department" in df.columns:
        st.markdown("#### Середня зарплата по відділах та гендеру")
        dept_gender_salary = df.groupby(["department", "gender"])["base_salary"].mean().reset_index()
        fig7 = px.bar(
            dept_gender_salary, x="department", y="base_salary", color="gender", barmode="group",
            color_discrete_sequence=["#a855f7", "#3b82f6"],
            labels={"department": "Відділ", "base_salary": "Середня зарплата, грн", "gender": "Гендер"},
            text=dept_gender_salary["base_salary"].apply(lambda x: f"{x:,.0f}"),
        )
        fig7.update_traces(textposition="outside")
        fig7.update_layout(height=400, margin=dict(t=10, b=10), plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig7, use_container_width=True)

    st.divider()

    # ── Висновок ──────────────────────────────────────────────────────────────
    if len(gender_stats) >= 2:
        means = gender_stats.set_index("gender")["mean"]
        vals = list(means.values)
        diff_pct = abs(vals[0] - vals[1]) / max(vals) * 100
        if diff_pct < 5:
            st.success("✅ Гендерний розрив у зарплатах **мінімальний** (< 5%). Компанія демонструє рівність оплати праці.")
        elif diff_pct < 15:
            st.warning(f"🟡 Гендерний розрив складає **{diff_pct:.1f}%**. Рекомендується провести додатковий аналіз причин.")
        else:
            st.error(f"🔴 Значний гендерний розрив — **{diff_pct:.1f}%**. Необхідний перегляд політики оплати праці.")


main()
