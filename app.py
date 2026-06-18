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
st.set_page_config(layout="wide")

# Динамічний імпорт допоміжних функцій
module_path = Path(__file__).parent / "parser.py"
spec = importlib.util.spec_from_file_location("parser", str(module_path))
parser = importlib.util.module_from_spec(spec)
sys.modules["parser"] = parser
spec.loader.exec_module(parser)
get_market_data = parser.get_market_data
generate_random_market_research = parser.generate_random_market_research

# Вартість пільг (грн), використовується для розрахунку повного компенсаційного пакету
BENEFIT_COSTS = {
    "health_insurance": 5000,
    "sport": 2000,
    "remote_allowance": 3000
}


def add_total_compensation(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in ["health_insurance", "sport", "remote_allowance"]:
        df[col] = df[col].fillna(0).astype(float)
    df["total_compensation"] = (
        df["base_salary"] +
        df["bonus"] +
        df["health_insurance"] * BENEFIT_COSTS["health_insurance"] +
        df["sport"] * BENEFIT_COSTS["sport"] +
        df["remote_allowance"] * BENEFIT_COSTS["remote_allowance"]
    )
    return df


def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def convert_df_to_excel(df: pd.DataFrame) -> bytes:
    from io import BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()


def show_page_description(page):
    descriptions = {
        "Головна": """
        Ласкаво просимо до **HR Analytics Dashboard – Compensation & Benefits**.
        Інтерактивний дашборд для аналізу зарплат, бонусів та пільг співробітників.
        Використовуйте меню зліва для навігації.
        """,
        "Ключові показники": """
        Огляд базових метрик зарплат, бонусів та компенсацій по компанії, а також
        додаткові показники: розкид зарплат, бюджет компенсацій та охоплення пільгами.
        """,
        "Аналіз бонусів та компенсацій": """
        Детальний аналіз бонусів та компенсацій: частка отримувачів, розподіл розмірів,
        порівняння по відділах та рівень використання пільг (медстрахування, спорт, remote).
        """,
        "Гендерна аналітика": """
        Аналіз гендерної рівності за оплатою та бонусами.
        Оцінка гендерного розриву і відповідні візуалізації.
        """,
        "Рейтинг співробітників": """
        ТОП співробітників за розміром повного компенсаційного пакету.
        Корисно для виявлення ключових талантів.
        """,
        "Аналіз ринку": """
        Порівняння внутрішніх зарплат з ринковими даними Work.ua/DOU та власних досліджень.
        Допомагає оцінити конкурентоспроможність компанії.
        """
    }
    text = descriptions.get(page, "")
    if text:
        st.markdown(f"### {page}")
        st.markdown(text)


def show_metrics(df):
    st.markdown("### 📊 Ключові показники")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Кількість співробітників", len(df))
    c2.metric("Середня базова зарплата", f"{df['base_salary'].mean():,.0f} грн")
    c3.metric("Медіанна базова зарплата", f"{np.median(df['base_salary']):,.0f} грн")
    c4.metric("Стандартне відхилення окладу", f"{np.std(df['base_salary']):,.0f} грн")
    c5.metric("Середній бонус", f"{df['bonus'].mean():,.0f} грн")
    c6.metric("Середній повний пакет", f"{df['total_compensation'].mean():,.0f} грн")

    st.markdown("#### Додаткові показники")
    c7, c8, c9, c10 = st.columns(4)
    c7.metric("Мін. базова зарплата", f"{df['base_salary'].min():,.0f} грн")
    c8.metric("Макс. базова зарплата", f"{df['base_salary'].max():,.0f} грн")
    c9.metric("Загальний бюджет компенсацій", f"{df['total_compensation'].sum():,.0f} грн")
    coef_var = (df['base_salary'].std() / df['base_salary'].mean() * 100) if df['base_salary'].mean() else 0
    c10.metric("Коефіцієнт варіації окладу", f"{coef_var:.1f}%")

    st.markdown("#### Охоплення пільгами")
    benefit_cols = ["health_insurance", "sport", "remote_allowance"]
    benefit_labels = {"health_insurance": "Медстрахування", "sport": "Спорт", "remote_allowance": "Remote"}
    cols = st.columns(len(benefit_cols))
    for col_widget, col_name in zip(cols, benefit_cols):
        share = (df[col_name] > 0).mean() * 100
        col_widget.metric(f"Охоплення: {benefit_labels[col_name]}", f"{share:.1f}%")


def show_bonus(df):
    st.markdown("### 🎁 Аналіз бонусів")
    unique_emp = df['employee_id'].nunique() if 'employee_id' in df else len(df)
    emp_with_bonus = df[df['bonus'] > 0]['employee_id'].nunique() if 'employee_id' in df else df[df['bonus'] > 0].shape[0]
    pct_bonus = (emp_with_bonus / unique_emp) * 100 if unique_emp else 0
    avg_bonus = df['bonus'].mean()
    df['bonus_pct'] = np.where(df['base_salary'] > 0, df['bonus'] / df['base_salary'] * 100, 0)
    avg_bonus_pct = df['bonus_pct'].mean()
    std_bonus = df['bonus'].std()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Унікальних співробітників", unique_emp)
    c2.metric("Отримали бонуси", f"{emp_with_bonus} ({pct_bonus:.1f}%)")
    c3.metric("Середній бонус", f"{avg_bonus:,.0f} грн")
    c4.metric("Середній бонус (% від бази)", f"{avg_bonus_pct:.1f}%")
    st.metric("Стандартне відхилення бонусів", f"{std_bonus:,.0f} грн")

    avg_bonus_by_dept = df.groupby('department')['bonus'].mean().reset_index()
    fig = px.bar(avg_bonus_by_dept, x='department', y='bonus', title="Середній бонус по відділах")
    st.plotly_chart(fig, use_container_width=True)

    fig_hist = px.histogram(df, x='bonus', nbins=30, title="Розподіл бонусів")
    st.plotly_chart(fig_hist, use_container_width=True)


def show_benefits_analysis(df):
    st.markdown("### 🩺 Аналіз пільг")

    benefit_cols = ["health_insurance", "sport", "remote_allowance"]
    benefit_labels = {"health_insurance": "Медстрахування", "sport": "Спорт", "remote_allowance": "Remote"}

    adoption = pd.DataFrame({
        "Пільга": [benefit_labels[c] for c in benefit_cols],
        "Охоплення, %": [(df[c] > 0).mean() * 100 for c in benefit_cols],
        "Витрати компанії, грн": [(df[c] > 0).sum() * BENEFIT_COSTS[c] for c in benefit_cols],
    })

    c1, c2 = st.columns(2)
    with c1:
        fig_adopt = px.bar(adoption, x="Пільга", y="Охоплення, %", title="Охоплення пільгами, %", color="Пільга")
        st.plotly_chart(fig_adopt, use_container_width=True)
    with c2:
        fig_cost = px.pie(adoption, names="Пільга", values="Витрати компанії, грн", title="Розподіл витрат на пільги")
        st.plotly_chart(fig_cost, use_container_width=True)

    st.dataframe(adoption, use_container_width=True)

    benefits_by_dept = df.groupby('department')[benefit_cols].mean().reset_index()
    benefits_by_dept_melt = benefits_by_dept.melt(id_vars='department', var_name='Пільга', value_name='Частка')
    benefits_by_dept_melt['Пільга'] = benefits_by_dept_melt['Пільга'].map(benefit_labels)
    fig_dept = px.bar(benefits_by_dept_melt, x='department', y='Частка', color='Пільга', barmode='group',
                       title="Охоплення пільгами по відділах")
    st.plotly_chart(fig_dept, use_container_width=True)


def show_compensation(df):
    st.markdown("### 📊 Компенсації по відділах")
    dept_comp = df.groupby('department')[['base_salary', 'bonus', 'total_compensation']].mean().reset_index()
    chart_type = st.radio("Тип графіка", ["Стовпчиковий", "Лінійний", "Кругова діаграма", "Теплова карта", "Бульбашковий"])

    if chart_type == "Стовпчиковий":
        st.plotly_chart(px.bar(dept_comp, x='department', y='total_compensation', color='department', title="Середня компенсація по відділах"), use_container_width=True)
    elif chart_type == "Лінійний":
        st.plotly_chart(px.line(dept_comp, x='department', y='total_compensation', color='department', markers=True, title="Динаміка компенсацій"), use_container_width=True)
    elif chart_type == "Кругова діаграма":
        st.plotly_chart(px.pie(dept_comp, names='department', values='total_compensation', title="Частка компенсацій по відділах"), use_container_width=True)
    elif chart_type == "Теплова карта":
        fig, ax = plt.subplots(figsize=(8,4))
        pivot = df.pivot_table(values='base_salary', index='department', columns='Role_ua', aggfunc='mean')
        sns.heatmap(pivot.fillna(0), cmap='YlOrRd', annot=True, fmt='.0f', ax=ax)
        st.pyplot(fig, use_container_width=True)
    elif chart_type == "Бульбашковий":
        st.plotly_chart(px.scatter(dept_comp, x='base_salary', y='bonus', size='total_compensation', color='department',
                                  title="Бульбашковий графік: зарплата vs бонус"), use_container_width=True)


def show_top(df):
    st.markdown("### 🏆 ТОП співробітників")
    top_n = st.slider("Обрати кількість:", min_value=3, max_value=min(50, len(df)), value=10)
    top_df = df.sort_values('total_compensation', ascending=False).head(top_n)
    st.dataframe(top_df[['name','department','Role_ua','base_salary','bonus','health_insurance','sport','remote_allowance','total_compensation']], use_container_width=True)


def show_market_analysis(filtered_df, full_df):
    st.markdown("### 📑 Аналіз ринку: внутрішня зарплата та ринкові дані")

    selected_role = st.selectbox("Оберіть посаду:", sorted(full_df['Role_ua'].unique()))
    source_option = st.radio("Джерело ринкових даних:", ['Work.ua/DOU', 'Власне дослідження'])

    avg_internal = filtered_df[filtered_df['Role_ua'] == selected_role]['base_salary'].mean()

    if source_option == 'Власне дослідження':
        custom_df = generate_random_market_research()
        st.dataframe(custom_df, use_container_width=True)
        market_salary_row = custom_df.loc[custom_df['Role'] == selected_role]
        market_salary = market_salary_row['Market_Salary'].values[0] if not market_salary_row.empty else None
    else:
        data = get_market_data(selected_role)
        market_salary = int(data['salary']) if data['salary'] != "Не вказано" else None

    if avg_internal and market_salary:
        diff = (avg_internal - market_salary) / market_salary * 100

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[0,1], y=[avg_internal, avg_internal], mode='lines+markers', name='Внутрішня зарплата', line=dict(color='blue', width=3)))
        fig.add_trace(go.Scatter(x=[0,1], y=[market_salary, market_salary], mode='lines+markers', name=f'Ринкова зарплата ({source_option})', line=dict(color='orange', width=3)))

        fig.update_layout(title=f"Порівняння зарплат: {selected_role}", yaxis_title="Зарплата (грн)", xaxis=dict(visible=False), height=400)

        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"📈 Внутрішня середня зарплата: {avg_internal:,.0f} грн")
        st.markdown(f"📊 Ринкова зарплата: {market_salary:,.0f} грн")
        color = "green" if diff >= 0 else "red"
        st.markdown(f"🔍 Відхилення: <span style='color:{color};'>{diff:+.1f}%</span>", unsafe_allow_html=True)
    else:
        st.info("Недостатньо даних для порівняння на цю посаду.")


def show_gender_gap(filtered_df):
    st.markdown("### 👩‍🦰👨 Гендерна аналітика")

    if 'gender' not in filtered_df.columns:
        st.warning("Дані про стать відсутні.")
        return

    gender_stats = filtered_df.groupby('gender')['base_salary'].agg(['count','mean','median']).reset_index()
    c1, c2, c3 = st.columns(3)
    c1.metric("Кількість жінок", gender_stats.loc[gender_stats['gender']=='Жінка', 'count'].values[0] if 'Жінка' in gender_stats['gender'].values else 0)
    c2.metric("Кількість чоловіків", gender_stats.loc[gender_stats['gender']=='Чоловік', 'count'].values[0] if 'Чоловік' in gender_stats['gender'].values else 0)
    if len(gender_stats) == 2:
        diff = gender_stats['mean'].max() - gender_stats['mean'].min()
        c3.metric("Різниця середньої зарплати", f"{diff:,.0f} грн")

    fig_bar = px.bar(gender_stats, x='mean', y='gender', orientation='h',
                     color='gender', title='Середня зарплата за статтю',
                     color_discrete_map={"Жінка":"purple", "Чоловік":"blue"},
                     labels={'mean':'Середня зарплата, грн','gender':'Стать'})
    fig_bar.update_layout(showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)

    fig_scatter = px.scatter(filtered_df, x='base_salary', y='bonus',
                             size='total_compensation', color='gender',
                             title="Зарплата vs Бонус (розмір = повний пакет)",
                             color_discrete_map={"Жінка":"purple","Чоловік":"blue"})
    st.plotly_chart(fig_scatter, use_container_width=True)


def main():
    st.set_page_config(page_title="HR Analytics Dashboard", layout="wide")

    st.title("HR Analytics Dashboard – Compensation & Benefits")
    st.markdown("""
    Інтерактивний інструмент для аналізу зарплат, бонусів, компенсацій і порівняння з ринковими даними.
    Використовуйте меню зліва для переходу між розділами.
    """)

    df = pd.read_csv("compensation.csv")
    df.columns = df.columns.str.strip()
    df = add_total_compensation(df)

    st.sidebar.title("Меню")
    page = st.sidebar.radio("Оберіть сторінку:", [
        "Головна",
        "Ключові показники",
        "Аналіз бонусів та компенсацій",
        "Гендерна аналітика",
        "Рейтинг співробітників",
        "Аналіз ринку"
    ])

    st.sidebar.title("Фільтри")
    departments = st.sidebar.multiselect("Відділи:", sorted(df["department"].unique()))
    if departments:
        available_roles = sorted(df[df["department"].isin(departments)]["Role_ua"].unique())
    else:
        available_roles = sorted(df["Role_ua"].unique())
    selected_roles = st.sidebar.multiselect("Посади:", available_roles)

    salary_min, salary_max = int(df["base_salary"].min()), int(df["base_salary"].max())
    salary_range = st.sidebar.slider("Діапазон базової зарплати:", salary_min, salary_max, (salary_min, salary_max), 1000)

    benefits_options = {
        "Медстрахування": "health_insurance",
        "Спортивна пільга": "sport",
        "Виплати на remote": "remote_allowance",
    }
    selected_benefits = st.sidebar.multiselect("Обрати пільги:", list(benefits_options.keys()))
    only_bonus = st.sidebar.checkbox("Тільки зі бонусом")

    filtered_df = df.copy()
    if departments:
        filtered_df = filtered_df[filtered_df["department"].isin(departments)]
    if selected_roles:
        filtered_df = filtered_df[filtered_df["Role_ua"].isin(selected_roles)]
    filtered_df = filtered_df[(filtered_df["base_salary"] >= salary_range[0]) & (filtered_df["base_salary"] <= salary_range[1])]
    if selected_benefits:
        cols = [benefits_options[b] for b in selected_benefits]
        filtered_df = filtered_df[filtered_df[cols].sum(axis=1) > 0]
    if only_bonus:
        filtered_df = filtered_df[filtered_df["bonus"] > 0]

    if filtered_df.empty:
        st.warning("За обраними фільтрами немає співробітників. Змініть параметри фільтру.")
        return

    if page == "Головна":
        show_page_description(page)

    elif page == "Ключові показники":
        show_page_description(page)
        show_metrics(filtered_df)

    elif page == "Аналіз бонусів та компенсацій":
        show_page_description(page)
        show_bonus(filtered_df)
        show_compensation(filtered_df)
        show_benefits_analysis(filtered_df)

    elif page == "Гендерна аналітика":
        show_page_description(page)
        show_gender_gap(filtered_df)

    elif page == "Рейтинг співробітників":
        show_page_description(page)
        show_top(filtered_df)

    elif page == "Аналіз ринку":
        show_page_description(page)
        show_market_analysis(filtered_df, df)


if __name__ == "__main__":
    main()