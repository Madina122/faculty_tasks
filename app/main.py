import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import os

main_path = os.path.join(os.path.dirname(__file__), "..", "data", "main.csv")
inflation_path = os.path.join(os.path.dirname(__file__), "..", "data", "inflation.csv")

df = pd.read_csv(main_path, sep=';', encoding='utf-8')
df = df.set_index('Год').T
df.index = pd.to_numeric(df.index)
colors = ['#1f77b4', '#ff7f0e', '#2ca02c']

st.title('Анализ динамики зарплат по отраслям')
st.markdown("---")

st.subheader('Исходные данные')
st.dataframe(df)

st.subheader('Динамика зарплат по отраслям')
selected_industry = st.selectbox('Выберите отрасль для детального анализа:', df.columns)

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df.index, df[selected_industry], marker='o', color=colors[list(df.columns).index(selected_industry)], linewidth=2)
ax.set_title(f'Динамика зарплаты: {selected_industry}')
ax.set_xlabel('Год')
ax.set_ylabel('Зарплата, руб.')
ax.grid(True, linestyle='--', alpha=0.5)
last_value = df[selected_industry].iloc[-1]
ax.text(df.index[-1], last_value, f'{last_value:.0f}', ha='left', va='center')
st.pyplot(fig)


st.subheader('Сравнение зарплат по отраслям')

fig2, ax2 = plt.subplots(figsize=(10, 5))
for i, column in enumerate(df.columns):
    ax2.plot(df.index, df[column], marker='o', color=colors[i], linewidth=2, label=column)

ax2.set_title('Сравнение зарплат по отраслям')
ax2.set_xlabel('Год')
ax2.set_ylabel('Зарплата, руб.')
ax2.legend()
ax2.grid(True, linestyle='--', alpha=0.5)
st.pyplot(fig2)

# Анализ изменений и выводы
st.subheader('Анализ изменений')
st.write("""
На графиках представлена динамика изменения зарплат по различным отраслям за несколько лет.
Можно заметить следующие тенденции:
- Все отрасли демонстрируют рост зарплат
- Темпы роста различаются между отраслями
- В некоторые годы наблюдаются скачки или замедления роста
""")

st.subheader('Основные выводы')
st.write(f"""
1. Наибольший рост зарплат наблюдается в отрасли: {df.columns[df.iloc[-1].argmax()]}
2. Наименьший рост зарплат наблюдается в отрасли: {df.columns[df.iloc[-1].argmin()]}
3. Средний уровень зарплат за последний год: {df.iloc[-1].mean():.0f} руб.
4. Разница между максимальной и минимальной зарплатой в последнем году: {df.iloc[-1].max() - df.iloc[-1].min():.0f} руб.
""")



##### 2 часть ##############
salary_df = pd.read_csv(main_path, sep=';', encoding='utf-8')
salary_df = salary_df.set_index('Год').T
salary_df.index = pd.to_numeric(salary_df.index)
inflation_df = pd.read_csv(inflation_path , sep=';', encoding='utf-8')
inflation_df = inflation_df[['Год', 'Всего']] 

inflation_df['Всего'] = inflation_df['Всего'].str.replace(',', '.').astype(float)
inflation_df['Год'] = pd.to_numeric(inflation_df['Год'])
inflation_df = inflation_df.set_index('Год')

df = salary_df.join(inflation_df, how='inner')

def adjust_for_inflation(df, base_year=2000):
    adjusted_df = pd.DataFrame(index=df.index)
    inflation_factors = (1 + df['Всего']/100).cumprod()
    
    for column in salary_df.columns:
        adjusted_df[column] = df[column] / inflation_factors
    
    return adjusted_df

st.title("📊 Анализ влияния инфляции на динамику реальных зарплат по отраслям")
st.subheader('Исходные данные')
st.dataframe(inflation_df)
with st.sidebar:
    st.header("Настройки анализа")
    base_year = st.selectbox(
        "Базовый год для расчета реальных зарплат", 
        df.index, 
        index=list(df.index).index(2000),
        help="Все зарплаты будут пересчитаны в покупательную способность выбранного года"
    )
    
    st.markdown("""
    **Методология:**
    - Реальные зарплаты рассчитаны с поправкой на ИПЦ
    - Базовый год: 2000 (по умолчанию)
    - Данные: Росстат
    """)

adjusted_salaries = adjust_for_inflation(df, base_year)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Динамика", 
    "🔄 Сравнение", 
    "📉 Разница роста",
    "💰 Инфляция",
    "📝 Выводы"
])

colors = ['#4e79a7', '#f28e2b', '#e15759']

with tab1:
    st.header("Динамика номинальных и реальных зарплат")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_columns = st.multiselect(
            "Выберите отрасли", 
            salary_df.columns, 
            default=salary_df.columns.tolist()
        )
    
    for column in selected_columns:
        fig, ax = plt.subplots(figsize=(10, 4))
        
        ax.plot(salary_df.index, salary_df[column], 
                marker='o', color=colors[0], linewidth=2, 
                label='Номинальная зарплата')
        
        ax.plot(adjusted_salaries.index, adjusted_salaries[column], 
                marker='s', linestyle='--', color=colors[1], linewidth=2,
                label=f'Реальная зарплата (в ценах {base_year})')
        
        ax.set_title(f'{column}: сравнение номинальной и реальной динамики')
        ax.set_xlabel('Год')
        ax.set_ylabel('Зарплата, руб.')
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.5)
        
        last_nominal = salary_df[column].iloc[-1]
        last_real = adjusted_salaries[column].iloc[-1]
        ax.text(salary_df.index[-1], last_nominal, f'{last_nominal:,.0f}', ha='left', va='center')
        ax.text(adjusted_salaries.index[-1], last_real, f'{last_real:,.0f}', ha='left', va='center')
        
        st.pyplot(fig)

# Вкладка 2: Сравнение
with tab2:
    st.header("Сравнение реальных зарплат по отраслям")
    
    selected_columns = st.multiselect(
        "Выберите отрасли для сравнения", 
        adjusted_salaries.columns, 
        default=adjusted_salaries.columns.tolist(),
        key="tab2_select"
    )
    
    fig, ax = plt.subplots(figsize=(10, 5))
    for i, column in enumerate(selected_columns):
        ax.plot(adjusted_salaries.index, adjusted_salaries[column], 
                marker='o', linewidth=2, color=colors[i],
                label=f'{column}')
    
    ax.set_title(f'Сравнение реальных зарплат (в ценах {base_year} года)')
    ax.set_xlabel('Год')
    ax.set_ylabel('Зарплата, руб.')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.5)
    
    st.pyplot(fig)

# Вкладка 3: Разница роста
with tab3:
    st.header("Разница между номинальным и реальным ростом")
    
    annual_real_growth = adjusted_salaries.pct_change() * 100
    
    selected_columns = st.multiselect(
        "Выберите отрасли", 
        salary_df.columns, 
        default=salary_df.columns.tolist(),
        key="tab3_select"
    )
    
    fig, ax = plt.subplots(figsize=(10, 5))
    for col in selected_columns:
        diff = salary_df[col].pct_change()*100 - annual_real_growth[col]
        ax.plot(diff.index, diff, label=col, marker='o', linewidth=2)
    
    ax.axhline(0, color='gray', linestyle='--')
    ax.set_title("Разница между номинальным и реальным ростом зарплат")
    ax.set_ylabel("Разница, процентные пункты")
    ax.set_xlabel("Год")
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.5)
    
    st.pyplot(fig)

# Вкладка 4: Инфляция
with tab4:
    st.header("Динамика инфляции в России")
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    ax1.bar(inflation_df.index, inflation_df['Всего'], 
           color='#d62728', alpha=0.7)
    ax1.set_title('Годовая инфляция (%)')
    ax1.set_ylabel('Инфляция, %')
    ax1.grid(True, linestyle='--', alpha=0.5, axis='y')
    
    cumulative_inflation = (1 + inflation_df['Всего']/100).cumprod() - 1
    cumulative_inflation *= 100
    ax2.plot(cumulative_inflation.index, cumulative_inflation,
            marker='o', color='#9467bd', linewidth=2)
    ax2.set_title('Накопленная инфляция с 2000 года (%)')
    ax2.set_ylabel('Накопленная инфляция, %')
    ax2.set_xlabel('Год')
    ax2.grid(True, linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    st.pyplot(fig)

# Вкладка 5: Выводы
with tab5:

    with st.header("1. Общий тренд за весь период (2000-2024)"):
        st.markdown("""
        **1. Общий тренд за весь период (2000-2024)**
        Рыболовство: +552.9% (максимальный рост)
        Химическая промышленность: +367.1%
        Нефтепродукты: +221.9% (минимальный рост)
        Интерпретация: Несмотря на инфляцию, все отрасли показали значительный рост реальных зарплат, что свидетельствует об опережающем росте номинальных зарплат по сравнению с инфляцией.
        """)
    
    # 2. Кризисные периоды
    with st.expander("2. Ключевые периоды и влияние инфляции"):
        st.markdown("""
        2000-2008 (период роста):
        -Высокая инфляция (5-15%), но еще более быстрый рост зарплат
        -Особенно в нефтепереработке (+171% за 8 лет)
        -Инфляция "съедала" около 30-50% номинального роста

        2009-2010 (кризисный период):
        -Резкий скачок инфляции (13-15% в 2008-2009)
        -Во всех отраслях замедление роста реальных зарплат
        -В нефтепереработке - фактическая стагнация

        2014-2016 (санкционный период):
        -Инфляция 11-13% (2014-2015)
        -В нефтепереработке - падение реальных зарплат (-4.3% в 2015)
        -В химии - кратковременное снижение (-3.8% в 2015)
        -Рыболовство показало устойчивость (+11.5% в 2015)

        2020-2024 (пандемия и постпандемия):
        -Всплеск инфляции (6-8%)
        -В нефтепереработке - волатильность (-4.2% в 2020, +7.5% в 2024)
        -В химии - ускоренный рост (+8.9% в 2024)
        -В рыболовстве - спад в 2024 (-3.5%)
        """)
    
    # 3. Отраслевые особенности
    with st.expander("3. Отраслевые особенности"):
        cols = st.columns(3)
        
        with cols[0]:
            st.markdown("### 🐟 Рыболовство")
            st.markdown("""
            -Наименее чувствительно к инфляции
            -Даже при высокой инфляции показывает рост
            -В 2024 впервые за 10 лет - снижение реальной зарплаты
            """)
        
        with cols[1]:
            st.markdown("### ⚗️ Химическая промышленность")
            st.markdown("""
            -Средняя чувствительность к инфляции
            -В последние годы - ускоренный рост реальных зарплат
            -Вероятно, эффект импортозамещения
            """)
        
        with cols[2]:
            st.markdown("### 🛢️ Нефтепереработка")
            st.markdown("""
            -Наиболее чувствительна к инфляции
            -В периоды высокой инфляции + кризисов - падение реальных зарплат
            -Сильная зависимость от цен на нефть
            """)
    
    # 4. Прогнозы
    with st.expander("4. Выводы"):
        st.markdown("""
        Инфляция существенно влияет на покупательную способность зарплат:
        -В "хорошие" годы (низкая инфляция) реальный рост максимален
        -В кризисы высокая инфляция может полностью нивелировать рост номинальных зарплат

        Отраслевая устойчивость:
        -Рыболовство наиболее устойчиво к инфляции
        -Нефтепереработка наиболее уязвима
        -Химия демонстрирует сбалансированную динамику

        Последние тенденции (2020-2024):
        -Инфляционное давление сохраняется
        -В химии и нефтепереработке - признаки восстановления
        -В рыболовстве - риск перегрева рынка труда
        """)

st.sidebar.download_button(
    label="📥 Скачать данные по зарплатам",
    data=salary_df.to_csv().encode('utf-8'),
    file_name='salary_data.csv'
)

st.sidebar.download_button(
    label="📥 Скачать данные по инфляции",
    data=inflation_df.to_csv().encode('utf-8'),
    file_name='inflation_data.csv'
)