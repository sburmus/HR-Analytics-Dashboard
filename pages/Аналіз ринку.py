import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="HR Dashboard - Аналіз ринку", layout="wide")

def main():
    # 1. Завантаження внутрішніх даних
    df = pd.read_csv("compensation.csv")

    st.title("🌍 Аналіз ринку")
    st.markdown("Порівняння внутрішніх зарплат із ринковими та власним дослідженням.")

    # 2. Вибір ролі
    role_col = "Role_ua" if "Role_ua" in df.columns else "Role"
    roles = df[role_col].unique()
    selected_role = st.selectbox("Оберіть роль для аналізу:", roles)

    # 3. Середня внутрішня зарплата
    avg_internal = df[df[role_col] == selected_role]["base_salary"].mean()

    # 4. Ринкові дані (median)
    market_salary = df[df[role_col] == selected_role]["market_median"].mean()

    # 5. Власне дослідження (автоматично для всіх ролей)
    roles_list = df[role_col].unique()
    custom_df = pd.DataFrame({
        "Role": roles_list,
        "Market_Salary": [
            int(df[df[role_col] == r]["base_salary"].mean() * np.random.uniform(0.9, 1.2))
            for r in roles_list
        ]
    })
    custom_salary = custom_df.loc[custom_df["Role"] == selected_role]["Market_Salary"].values[0]

    # --- Побудова графіків ---
    fig1 = px.bar(
        pd.DataFrame({"Джерело": ["Внутрішні дані", "Ринок (median)"],
                      "Зарплата": [avg_internal, market_salary]}),
        x="Джерело", y="Зарплата", color="Джерело",
        title=f"Внутрішні vs Ринок ({selected_role})", text_auto=True
    )

    fig2 = px.bar(
        pd.DataFrame({"Джерело": ["Внутрішні дані", "Власне дослідження"],
                      "Зарплата": [avg_internal, custom_salary]}),
        x="Джерело", y="Зарплата", color="Джерело",
        title=f"Внутрішні vs Власне дослідження ({selected_role})", text_auto=True
    )

    fig3 = px.bar(
        pd.DataFrame({"Джерело": ["Внутрішні дані", "Ринок (median)", "Власне дослідження"],
                      "Зарплата": [avg_internal, market_salary, custom_salary]}),
        x="Джерело", y="Зарплата", color="Джерело",
        title=f"Комбіноване порівняння ({selected_role})", text_auto=True
    )

    # --- Розташування в один рядок ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)
    with col3:
        st.plotly_chart(fig3, use_container_width=True)

if __name__ == "__main__":
    main()
