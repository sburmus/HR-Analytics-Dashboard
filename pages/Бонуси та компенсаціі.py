import streamlit as st
import pandas as pd
from pathlib import Path
import importlib.util
import sys

# --- Широке розташування сторінки ---
st.set_page_config(page_title="HR Dashboard - Бонуси та компенсації", layout="wide")

# Імпорт функцій з головного app.py
module_path = Path(__file__).parent.parent / "app.py"
spec = importlib.util.spec_from_file_location("app", str(module_path))
app = importlib.util.module_from_spec(spec)
sys.modules["app"] = app
spec.loader.exec_module(app)

add_total_compensation = app.add_total_compensation
show_bonus = app.show_bonus
show_compensation = app.show_compensation

def main():
    df = pd.read_csv("compensation.csv")
    df = add_total_compensation(df)

    st.title("🎁 Бонуси та компенсації")
    st.markdown("""
    На цій сторінці ми аналізуємо **бонуси та компенсації**.  
    - **Бонуси** — додаткові виплати до базової зарплати (премії, KPI‑бонуси).  
    - **Компенсації** — грошові виплати, що покривають витрати співробітника (наприклад, віддалена робота, транспорт).  
    """)

    # --- Вкладки ---
    tab1, tab2 = st.tabs(["💰 Бонуси", "📊 Компенсації"])

    with tab1:
        st.subheader("Аналіз бонусів")
        show_bonus(df)
        st.markdown("""
        **Пояснення:** бонуси — це змінна частина доходу, яка залежить від результатів роботи.  
        **Висновок:** високий середній бонус свідчить про сильну систему мотивації, а низький — про фокус на фіксованій зарплаті.
        """)

    with tab2:
        st.subheader("Аналіз компенсацій")
        show_compensation(df)
        st.markdown("""
        **Пояснення:** компенсації включають базову зарплату та додаткові виплати (наприклад, надбавки за віддалену роботу).  
        **Висновок:** цей показник відображає реальну вартість співробітника для компанії та допомагає оцінити конкурентоспроможність пакету оплати праці.
        """)

if __name__ == "__main__":
    main()
