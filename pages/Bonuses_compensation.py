import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import importlib.util
import sys

st.set_page_config(page_title="Бонуси та компенсації", layout="wide")

# Імпорт з app.py
module_path = Path(__file__).parent.parent / "app.py"
spec = importlib.util.spec_from_file_location("app", str(module_path))
app_module = importlib.util.module_from_spec(spec)
sys.modules["app"] = app_module
spec.loader.exec_module(app_module)
add_total_compensation = app_module.add_total_compensation
BENEFIT_COSTS = app_module.BENEFIT_COSTS
BENEFIT_LABELS = app_module.BENEFIT_LABELS


def main():
    # Завантаження даних
    df = pd.read_csv("compensation.csv")
    df.columns = df.columns.str.strip()
    if "employee_id" not in df.columns and "id" in df.columns:
        df["employee_id"] = df["id"]
    df = add_total_compensation(df)

    st.title("🎁 Бонуси та компенсації")
    st.markdown("Детальний аналіз бонусних програм, структури компенсацій та використання пільг по відділах.")
    st.divider()

    # ── Вкладки ───────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["💰 Бонуси", "📊 Компенсації по відділах", "🩺 Пільги"])

    # ══════════════════════════════════════════════════════════════════════════
    with tab1:
        st.markdown("### 💰 Аналіз бонусів")
        st.caption("Бонуси — змінна частина доходу, що залежить від результатів роботи та KPI.")

        # KPI метрики
        unique_emp = df["employee_id"].nunique() if "employee_id" in df.columns else len(df)
        emp_with_bonus = (
            df[df["bonus"] > 0]["employee_id"].nunique()
            if "employee_id" in df.columns
            else (df["bonus"] > 0).sum()
        )
        pct_bonus = emp_with_bonus / unique_emp * 100 if unique_emp else 0
        avg_bonus = df["bonus"].mean()
        df["bonus_pct"] = np.where(df["base_salary"] > 0, df["bonus"] / df["base_salary"] * 100, 0)
        avg_bonus_pct = df["bonus_pct"].mean()
        max_bonus = df["bonus"].max()
        std_bonus = df["bonus"].std()

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("👥 Співробітників", unique_emp)
        m2.metric("🎯 Отримали бонус", f"{emp_with_bonus} ({pct_bonus:.0f}%)")
        m3.metric("💰 Середній бонус", f"{avg_bonus:,.0f} грн")
        m4.metric("📈 Бонус % від бази", f"{avg_bonus_pct:.1f}%")
        m5.metric("🏆 Макс. бонус", f"{max_bonus:,.0f} грн")

        st.divider()

        # Два графіки поряд
        left, right = st.columns(2)

        with left:
            st.markdown("#### Середній бонус по відділах")
            avg_by_dept = df.groupby("department")["bonus"].mean().reset_index().sort_values("bonus", ascending=True)
            fig1 = px.bar(
                avg_by_dept, x="bonus", y="department", orientation="h",
                color="bonus", color_continuous_scale="Blues",
                labels={"bonus": "Середній бонус, грн", "department": ""},
                text=avg_by_dept["bonus"].apply(lambda x: f"{x:,.0f} грн"),
            )
            fig1.update_traces(textposition="outside")
            fig1.update_layout(height=350, coloraxis_showscale=False,
                               margin=dict(t=10, b=10), plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig1, use_container_width=True)

        with right:
            st.markdown("#### Розподіл бонусів")
            fig2 = px.histogram(
                df, x="bonus", nbins=30,
                color_discrete_sequence=["#4F8CFF"],
                labels={"bonus": "Бонус, грн"},
            )
            fig2.add_vline(x=avg_bonus, line_dash="dash", line_color="#34D399", line_width=2,
                           annotation_text=f"Середній: {avg_bonus:,.0f}", annotation_position="top right")
            fig2.update_layout(height=350, margin=dict(t=10, b=10), plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig2, use_container_width=True)

        st.divider()

        # Другий ряд
        left2, right2 = st.columns(2)

        with left2:
            st.markdown("#### Бонус як % від базової зарплати")
            bonus_pct_dept = df.groupby("department")["bonus_pct"].mean().reset_index().sort_values("bonus_pct")
            fig3 = px.bar(
                bonus_pct_dept, x="bonus_pct", y="department", orientation="h",
                color="bonus_pct", color_continuous_scale="Greens",
                labels={"bonus_pct": "Бонус, %", "department": ""},
                text=bonus_pct_dept["bonus_pct"].apply(lambda x: f"{x:.1f}%"),
            )
            fig3.update_traces(textposition="outside")
            fig3.update_layout(height=350, coloraxis_showscale=False,
                               margin=dict(t=10, b=10), plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig3, use_container_width=True)

        with right2:
            st.markdown("#### Частка співробітників з бонусом по відділах")
            bonus_share = df.groupby("department").apply(
                lambda x: (x["bonus"] > 0).mean() * 100
            ).reset_index()
            bonus_share.columns = ["department", "share"]
            fig4 = px.bar(
                bonus_share.sort_values("share"),
                x="share", y="department", orientation="h",
                color="share", color_continuous_scale="Oranges",
                labels={"share": "Частка, %", "department": ""},
                text=bonus_share.sort_values("share")["share"].apply(lambda x: f"{x:.0f}%"),
            )
            fig4.update_traces(textposition="outside")
            fig4.update_layout(height=350, coloraxis_showscale=False,
                               margin=dict(t=10, b=10), plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig4, use_container_width=True)

        st.info("💡 **Висновок:** високий середній бонус та широке охоплення свідчать про розвинену систему мотивації. Нерівномірність між відділами може вказувати на різні KPI-системи.")

    # ══════════════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown("### 📊 Компенсації по відділах")
        st.caption("Повний компенсаційний пакет = базова зарплата + бонус + вартість пільг.")

        # KPI метрики
        total_budget = df["total_compensation"].sum()
        avg_total = df["total_compensation"].mean()
        avg_base = df["base_salary"].mean()
        base_share = df["base_salary"].sum() / total_budget * 100
        bonus_share_total = df["bonus"].sum() / total_budget * 100
        benefits_share = max(100 - base_share - bonus_share_total, 0)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("💎 Загальний бюджет", f"{total_budget:,.0f} грн")
        m2.metric("📦 Середній пакет", f"{avg_total:,.0f} грн")
        m3.metric("💰 Середня база", f"{avg_base:,.0f} грн")
        m4.metric("🎁 Частка пільг", f"{benefits_share:.1f}%")

        st.divider()

        dept_comp = df.groupby("department")[["base_salary", "bonus", "total_compensation"]].mean().reset_index()

        left, right = st.columns(2)

        with left:
            st.markdown("#### Структура компенсації по відділах")
            # Stacked bar
            benefit_cols = list(BENEFIT_COSTS.keys())
            dept_benefits = df.groupby("department")[benefit_cols].mean().reset_index()
            dept_base_bonus = df.groupby("department")[["base_salary", "bonus"]].mean().reset_index()
            merged = dept_base_bonus.merge(dept_benefits, on="department")

            fig5 = go.Figure()
            fig5.add_trace(go.Bar(name="База", x=merged["department"], y=merged["base_salary"], marker_color="#4F8CFF"))
            fig5.add_trace(go.Bar(name="Бонус", x=merged["department"], y=merged["bonus"], marker_color="#34D399"))
            for col, label, color in zip(
                benefit_cols, list(BENEFIT_LABELS.values()), ["#FBBF24", "#F87171", "#A78BFA"]
            ):
                fig5.add_trace(go.Bar(name=label, x=merged["department"], y=merged[col] * BENEFIT_COSTS[col], marker_color=color))
            fig5.update_layout(barmode="stack", height=380, margin=dict(t=10, b=10),
                               plot_bgcolor="rgba(0,0,0,0)", yaxis_title="грн")
            st.plotly_chart(fig5, use_container_width=True)

        with right:
            st.markdown("#### Середня компенсація vs база")
            fig6 = go.Figure()
            fig6.add_trace(go.Bar(
                name="Базова зарплата", x=dept_comp["department"], y=dept_comp["base_salary"],
                marker_color="#4F8CFF",
            ))
            fig6.add_trace(go.Bar(
                name="Повний пакет", x=dept_comp["department"], y=dept_comp["total_compensation"],
                marker_color="#34D399",
            ))
            fig6.update_layout(barmode="group", height=380, margin=dict(t=10, b=10),
                               plot_bgcolor="rgba(0,0,0,0)", yaxis_title="грн")
            st.plotly_chart(fig6, use_container_width=True)

        st.divider()

        left2, right2 = st.columns(2)

        with left2:
            st.markdown("#### Бульбашковий: зарплата vs бонус")
            fig7 = px.scatter(
                dept_comp, x="base_salary", y="bonus",
                size="total_compensation", color="department",
                labels={"base_salary": "Середня база, грн", "bonus": "Середній бонус, грн"},
                hover_data=["total_compensation"],
            )
            fig7.update_layout(height=350, margin=dict(t=10, b=10))
            st.plotly_chart(fig7, use_container_width=True)

        with right2:
            st.markdown("#### Частка компенсацій по відділах")
            fig8 = px.pie(
                dept_comp, names="department", values="total_compensation",
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig8.update_layout(height=350, margin=dict(t=10, b=10))
            st.plotly_chart(fig8, use_container_width=True)

        st.info("💡 **Висновок:** стекований графік показує реальну структуру витрат на кожного співробітника. Відділи з великою часткою пільг мають вищу лояльність працівників.")

    # ══════════════════════════════════════════════════════════════════════════
    with tab3:
        st.markdown("### 🩺 Аналіз пільг")
        st.caption("Пільги збільшують цінність компенсаційного пакету без прямого підвищення зарплати.")

        benefit_cols = list(BENEFIT_COSTS.keys())
        labels = list(BENEFIT_LABELS.values())

        adoption = pd.DataFrame({
            "Пільга": labels,
            "Охоплення, %": [(df[c] > 0).mean() * 100 for c in benefit_cols],
            "Витрати компанії, грн": [(df[c] > 0).sum() * BENEFIT_COSTS[c] for c in benefit_cols],
            "К-сть співробітників": [(df[c] > 0).sum() for c in benefit_cols],
        })

        m1, m2, m3 = st.columns(3)
        for col_widget, (_, row) in zip([m1, m2, m3], adoption.iterrows()):
            col_widget.metric(
                row["Пільга"],
                f"{row['Охоплення, %']:.1f}%",
                f"{row['К-сть співробітників']} осіб",
            )

        st.divider()

        left, right = st.columns(2)

        with left:
            st.markdown("#### Охоплення пільгами, %")
            fig9 = px.bar(
                adoption, x="Пільга", y="Охоплення, %",
                color="Пільга", text=adoption["Охоплення, %"].apply(lambda x: f"{x:.1f}%"),
                color_discrete_sequence=["#34D399", "#FBBF24", "#38BDF8"],
            )
            fig9.update_traces(textposition="outside")
            fig9.update_layout(height=320, showlegend=False,
                               margin=dict(t=10, b=10), plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig9, use_container_width=True)

        with right:
            st.markdown("#### Розподіл витрат на пільги")
            fig10 = px.pie(
                adoption, names="Пільга", values="Витрати компанії, грн",
                color_discrete_sequence=["#34D399", "#FBBF24", "#38BDF8"],
                hole=0.4,
            )
            fig10.update_layout(height=320, margin=dict(t=10, b=10))
            st.plotly_chart(fig10, use_container_width=True)

        st.divider()

        st.markdown("#### Охоплення пільгами по відділах")
        dept_benefits = df.groupby("department")[benefit_cols].mean().reset_index()
        melt = dept_benefits.melt(id_vars="department", var_name="Пільга", value_name="Частка")
        melt["Пільга"] = melt["Пільга"].map(BENEFIT_LABELS)
        melt["Частка, %"] = melt["Частка"] * 100
        fig11 = px.bar(
            melt, x="department", y="Частка, %", color="Пільга", barmode="group",
            color_discrete_sequence=["#34D399", "#FBBF24", "#38BDF8"],
            labels={"department": "Відділ", "Частка, %": "Охоплення, %"},
        )
        fig11.update_layout(height=360, margin=dict(t=10, b=10), plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig11, use_container_width=True)

        st.dataframe(adoption, use_container_width=True)
        st.info("💡 **Висновок:** нерівномірне охоплення пільгами між відділами може бути сигналом для HR-перегляду політики компенсацій.")


main()
