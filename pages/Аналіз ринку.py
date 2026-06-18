import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from app import add_total_compensation, get_market_data, generate_random_market_research


def main():
    st.title("📑 Аналіз ринку")
    st.markdown("Порівняння внутрішніх зарплат з ринковими даними та оцінка конкурентоспроможності компанії.")
    st.divider()

    # Завантаження даних
    df = pd.read_csv("compensation.csv")
    df.columns = df.columns.str.strip()
    if "market_median" not in df.columns:
        df["market_median"] = (df["base_salary"] * np.random.uniform(0.85, 1.2, size=len(df))).astype(int)
    if "employee_id" not in df.columns and "id" in df.columns:
        df["employee_id"] = df["id"]
    df = add_total_compensation(df)

    if "Role_ua" not in df.columns:
        st.warning("Колонка 'Role_ua' відсутня.")
        return

    # Фільтри
    col_sel, col_src = st.columns([2, 2])
    with col_sel:
        selected_role = st.selectbox("Оберіть посаду:", sorted(df["Role_ua"].unique()))
    with col_src:
        source_option = st.radio("Джерело ринкових даних:", ["Work.ua/DOU", "Власне дослідження"], horizontal=True)

    role_df = df[df["Role_ua"] == selected_role]
    avg_internal = role_df["base_salary"].mean() if not role_df.empty else None

    # Ринкова зарплата
    market_salary = None
    if source_option == "Власне дослідження":
        custom_df = generate_random_market_research()
        with st.expander("📋 Дані власного дослідження"):
            st.dataframe(custom_df, use_container_width=True)
        row = custom_df.loc[custom_df["Role"] == selected_role]
        if not row.empty:
            market_salary = float(row["Market_Salary"].values[0])
    else:
        data = get_market_data(selected_role)
        if data and data.get("salary") not in (None, "Не вказано"):
            market_salary = int(data["salary"])

    if not avg_internal or not market_salary:
        st.info("Недостатньо даних для порівняння на цю посаду.")
        return

    diff = (avg_internal - market_salary) / market_salary * 100
    diff_abs = avg_internal - market_salary

    # KPI метрики
    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Внутрішня зарплата", f"{avg_internal:,.0f} грн")
    m2.metric("Ринкова зарплата", f"{market_salary:,.0f} грн")
    m3.metric("Відхилення", f"{diff:+.1f}%", delta=f"{diff_abs:+,.0f} грн")
    m4.metric("Кількість на посаді", len(role_df))

    st.divider()

    # Ряд 1: Gauge + Bar
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
            title={"text": f"{selected_role}<br><span style='font-size:13px;color:gray'>ринок = 100%</span>"},
        ))
        fig_gauge.update_layout(height=320, margin=dict(t=60, b=20, l=30, r=30))
        st.plotly_chart(fig_gauge, use_container_width=True)

    with right:
        st.markdown("#### Внутрішня зарплата vs Ринок")
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=["Внутрішня зарплата", "Ринкова зарплата"],
            y=[avg_internal, market_salary],
            marker_color=["#4F8CFF", "#FBBF24"],
            text=[f"{avg_internal:,.0f} грн", f"{market_salary:,.0f} грн"],
            textposition="outside",
            width=0.4,
        ))
        fig_bar.update_layout(
            height=320, yaxis_title="Зарплата, грн",
            showlegend=False, margin=dict(t=40, b=20),
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # Ряд 2: Відхилення по всіх посадах + Розподіл зарплат
    left2, right2 = st.columns(2)

    with left2:
        st.markdown("#### Відхилення від ринку по всіх посадах")
        all_roles_avg = df.groupby("Role_ua")["base_salary"].mean().reset_index()
        all_roles_avg.columns = ["Role_ua", "avg_salary"]
        market_by_role = df.groupby("Role_ua")["market_median"].mean().reset_index()
        all_roles_avg = all_roles_avg.merge(market_by_role, on="Role_ua", how="left")
        all_roles_avg["diff_pct"] = (
            (all_roles_avg["avg_salary"] - all_roles_avg["market_median"])
            / all_roles_avg["market_median"] * 100
        )
        fig_roles = px.bar(
            all_roles_avg.sort_values("diff_pct"),
            x="diff_pct", y="Role_ua", orientation="h",
            color="diff_pct",
            color_continuous_scale=["#FF4B4B", "#FBBF24", "#34D399"],
            labels={"diff_pct": "Відхилення, %", "Role_ua": ""},
        )
        fig_roles.update_layout(height=380, margin=dict(t=20, b=20), coloraxis_showscale=False)
        fig_roles.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)
        st.plotly_chart(fig_roles, use_container_width=True)

    with right2:
        st.markdown(f"#### Розподіл зарплат: {selected_role}")
        fig_hist = px.histogram(
            role_df, x="base_salary", nbins=15,
            labels={"base_salary": "Базова зарплата, грн"},
            color_discrete_sequence=["#4F8CFF"],
        )
        fig_hist.add_vline(x=avg_internal, line_color="#34D399", line_width=2,
                           annotation_text=f"Внутрішня: {avg_internal:,.0f}", annotation_position="top right")
        fig_hist.add_vline(x=market_salary, line_dash="dash", line_color="#FBBF24", line_width=2,
                           annotation_text=f"Ринок: {market_salary:,.0f}", annotation_position="top left")
        fig_hist.update_layout(height=380, margin=dict(t=20, b=20), plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_hist, use_container_width=True)

    st.divider()

    # Висновок
    if diff >= 10:
        st.success(f"✅ Компанія **вище ринку** на {diff:.1f}% для посади **{selected_role}**.")
    elif diff >= 0:
        st.info(f"🟡 Зарплата **на рівні ринку** ({diff:+.1f}%) для посади **{selected_role}**.")
    else:
        st.error(f"🔴 Зарплата **нижче ринку** на {abs(diff):.1f}% для посади **{selected_role}**. Рекомендується перегляд.")


main()
