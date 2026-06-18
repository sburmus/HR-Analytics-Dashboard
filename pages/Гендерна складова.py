import streamlit as st
import pandas as pd
import plotly.express as px

def show_gender_gap(df):
    st.markdown("### 👩‍🦰👨 Гендерна аналітика")

    # Перевірка наявності колонки
    if "gender" not in df.columns:
        st.warning("⚠️ У цьому наборі даних немає колонки 'gender'.")
        return

    # KPI метрики
    gender_stats = (
        df.groupby("gender")["base_salary"]
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
    st.bar_chart(df["gender"].value_counts())

def main():
    # Завантаження даних
    df = pd.read_csv("compensation.csv")

    st.title("👩‍💼 Гендерна складова")

    # Виклик функції аналізу
    show_gender_gap(df)

if __name__ == "__main__":
    main()
