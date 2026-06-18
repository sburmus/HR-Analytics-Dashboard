import streamlit as st
import pandas as pd
from pathlib import Path
import importlib.util
import sys
import plotly.express as px

# --- Широке розташування сторінки ---
st.set_page_config(page_title="HR Dashboard - Гендерна складова", layout="wide")

# Імпорт функцій з головного app.py
module_path = Path(__file__).parent.parent / "app.py"
spec = importlib.util.spec_from_file_location("app", str(module_path))
app = importlib.util.module_from_spec(spec)
sys.modules["app"] = app
spec.loader.exec_module(app)

add_total_compensation = app.add_total_compensation

def main():
    df = pd.read_csv("compensation.csv")
    df = add_total_compensation(df)

    st.title("⚖️ Гендерна складова")
    st.markdown("""
    Ця сторінка аналізує **гендерний баланс та різницю в оплаті праці**.  
    - **Гендерний розподіл** показує кількість чоловіків та жінок у компанії.  
    - **Гендерний розрив у зарплатах** демонструє, чи є різниця між середніми доходами чоловіків та жінок.  
    - **Compa Ratio за гендером** допомагає оцінити відповідність зарплат ринку для кожної групи.
    """)

    # --- Гендерний розподіл ---
    st.subheader("Гендерний розподіл")
    gender_counts = df["gender"].value_counts()
    st.bar_chart(gender_counts)
    st.markdown(f"**Висновок:** у компанії {gender_counts.get('Жінка',0)} жінок та {gender_counts.get('Чоловік',0)} чоловіків. Це показує загальний баланс персоналу.")

    st.markdown("---")

    # --- Гендерний розрив у зарплатах (бульбашки) ---
    st.subheader("Гендерний розрив у зарплатах")

    avg_salary_by_gender = df.groupby("gender")["base_salary"].mean().reset_index()
    bonus_by_gender = df.groupby("gender")["bonus"].mean().reset_index()
    count_by_gender = df["gender"].value_counts().reset_index()
    count_by_gender.columns = ["gender", "count"]

    # Об'єднуємо дані
    gender_stats = avg_salary_by_gender.merge(bonus_by_gender, on="gender")
    gender_stats = gender_stats.merge(count_by_gender, on="gender")

    fig = px.scatter(
        gender_stats,
        x="base_salary",          # середня зарплата
        y="bonus",                # середній бонус
        size="count",             # розмір бульбашки = кількість співробітників
        color="gender",
        hover_name="gender",
        title="Бульбашкова діаграма: зарплата, бонуси та кількість співробітників"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    **Пояснення:**  
    - Вісь X показує середню зарплату за гендером.  
    - Вісь Y показує середній бонус.  
    - Розмір бульбашки відображає кількість співробітників.  

    **Висновок:** цей графік дозволяє одночасно оцінити рівень зарплат, бонусів та чисельність групи. Якщо бульбашка чоловіків більша й розташована правіше — це означає, що чоловіки отримують вищу зарплату та бонуси, і їх більше у компанії.
    """)


    # --- Compa Ratio за гендером ---
    if "market_median" in df.columns:
        st.subheader("Compa Ratio за гендером")
        compa_ratio = df.groupby("gender").apply(lambda g: (g["base_salary"].mean() / g["market_median"].mean()) * 100)
        st.dataframe(compa_ratio)

        fig2 = px.bar(compa_ratio, x=compa_ratio.index, y=compa_ratio.values,
                      color=compa_ratio.index, title="Compa Ratio (%) за гендером")
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("**Висновок:** Compa Ratio показує, наскільки зарплати чоловіків та жінок відповідають ринковим значенням.")

if __name__ == "__main__":
    main()
