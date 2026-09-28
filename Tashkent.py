import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------
# 1. SAHIFA KONFIGURATSIYASI VA MAXSUS CSS DIZAYN
# ---------------------------------------------------------
st.set_page_config(
    page_title="Toshkent Ko'chmas Mulk Bozori Tahlili",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    /* Asosiy fon va shriftlar */
    .main {
        background-color: #F8F9FA;
    }
    /* KPI Kartochkalar dizayni */
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E9ECEF;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.08);
    }
    .metric-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #6C757D;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1E293B;
        margin-top: 5px;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #10B981;
        margin-top: 4px;
        font-weight: 500;
    }
    /* Sarlavha bloki */
    .header-box {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        padding: 28px;
        border-radius: 14px;
        color: white;
        margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(CURRENT_DIR, "tashkent_real_estate_large.csv")


# ---------------------------------------------------------
# 2. MA'LUMOTLARNI YUKLASH VA ISHLOV BERISH
# ---------------------------------------------------------
@st.cache_data
def load_and_preprocess_data(path):
    if not os.path.exists(path):
        return None, None

    # Sarlavha qatorini dinamik aniqlash
    raw_sample = pd.read_csv(path, sep=None, engine='python', header=None, nrows=15)
    header_idx = 0
    for idx, row in raw_sample.iterrows():
        row_str = " ".join(row.dropna().astype(str).tolist()).lower()
        if any(keyword in row_str for keyword in ['district', 'price', 'area', 'tuman', 'narx']):
            header_idx = idx
            break

    df = pd.read_csv(path, sep=None, engine='python', header=header_idx)
    df = df.loc[:, ~df.columns.astype(str).str.contains('^Unnamed', na=False)]
    df.columns = df.columns.astype(str).str.strip()

    # Ustunlarni xaritalash
    mapping = {}
    for col in df.columns:
        c = col.lower()
        if 'district' in c or 'tuman' in c:
            mapping[col] = 'District'
        elif 'room' in c or 'xona' in c:
            mapping[col] = 'Rooms'
        elif 'renovation' in c or 'tamir' in c:
            mapping[col] = 'Renovation'
        elif 'price' in c or 'narx' in c:
            mapping[col] = 'Price_USD'
        elif 'area' in c or 'maydon' in c:
            mapping[col] = 'Area_Sqm'
        elif 'distance' in c or 'masofa' in c:
            mapping[col] = 'Distance_to_Center_Km'
        elif 'building' in c or 'bino' in c:
            mapping[col] = 'Building_Type'

    df = df.rename(columns=mapping)

    # Sonli formatlarni to'g'irlash
    num_cols = ['Price_USD', 'Area_Sqm', 'Rooms']
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')

    df = df.dropna(subset=['Price_USD', 'Area_Sqm', 'District', 'Rooms'])
    df['Rooms'] = df['Rooms'].astype(int)
    df['Price_per_Sqm'] = df['Price_USD'] / df['Area_Sqm']

    # IQR yordamida anomaliyalarni ajratish
    q1 = df['Price_USD'].quantile(0.25)
    q3 = df['Price_USD'].quantile(0.75)
    iqr = q3 - q1
    upper_bound = q3 + 1.5 * iqr
    lower_bound = q1 - 1.5 * iqr

    df['Is_Outlier'] = np.where((df['Price_USD'] < lower_bound) | (df['Price_USD'] > upper_bound), 'Yes', 'No')

    clean_df = df[df['Is_Outlier'] == 'No'].copy()
    return clean_df, df


clean_df, full_df = load_and_preprocess_data(FILE_PATH)

if clean_df is None:
    st.error("⚠️ `tashkent_real_estate_large.csv` fayli topilmadi!")
    st.info(f"Faylni quyidagi katalogga joylashtiring:\n`{CURRENT_DIR}`")
    st.stop()

# ---------------------------------------------------------
# 3. YON PANEL (SIDEBAR) - FILTRLAR
# ---------------------------------------------------------
st.sidebar.image("https://img.icons8.com/fluency/96/real-estate.png", width=64)
st.sidebar.title("Filtrlash Markazi")
st.sidebar.caption("Tahlil parametrlarini tanlang")

# Tuman tanlash
all_districts = sorted(clean_df['District'].unique())
selected_districts = st.sidebar.multiselect(
    "📍 Tumanlar:",
    options=all_districts,
    default=all_districts
)

# Xonalar soni
all_rooms = sorted(clean_df['Rooms'].unique())
selected_rooms = st.sidebar.multiselect(
    "🚪 Xonalar soni:",
    options=all_rooms,
    default=all_rooms
)

# Ta'mir turi
if 'Renovation' in clean_df.columns:
    all_renovations = sorted(clean_df['Renovation'].unique())
    selected_renovations = st.sidebar.multiselect(
        "🛠️ Ta'mir holati:",
        options=all_renovations,
        default=all_renovations
    )
else:
    selected_renovations = []

# Narx oralig'i (Slider)
min_p, max_p = int(clean_df['Price_USD'].min()), int(clean_df['Price_USD'].max())
price_range = st.sidebar.slider(
    "💵 Narx oralig'i (USD):",
    min_value=min_p,
    max_value=max_p,
    value=(min_p, max_p),
    step=2000
)

# Filtrlash mantiqi
mask = (
        clean_df['District'].isin(selected_districts) &
        clean_df['Rooms'].isin(selected_rooms) &
        (clean_df['Price_USD'] >= price_range[0]) &
        (clean_df['Price_USD'] <= price_range[1])
)
if selected_renovations:
    mask = mask & clean_df['Renovation'].isin(selected_renovations)

filtered = clean_df[mask]

# ---------------------------------------------------------
# 4. ASOSIY PANJARA (DASHBOARD)
# ---------------------------------------------------------
st.markdown("""
    <div class="header-box">
        <h1 style='margin:0; font-size: 2.2rem;'>🏙️ Toshkent Ko'chmas Mulk Bozori</h1>
        <p style='margin:5px 0 0 0; opacity: 0.9;'>Interaktiv tahlil paneli, narx indekslari va bashorat kalkulyatori</p>
    </div>
""", unsafe_allow_html=True)

if filtered.empty:
    st.warning("⚠️ Tanlangan parametrlar bo'yicha hech qanday ma'lumot topilmadi. Filtrlarni kengaytiring.")
    st.stop()

# KPI Kartochkalari
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Jami E'lonlar</div>
            <div class="metric-value">{len(filtered):,} <span style="font-size:1rem; font-weight:400;">ta</span></div>
            <div class="metric-sub">Bozor hajmining {len(filtered) / len(clean_df) * 100:.1f}% qismi</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    avg_price = filtered['Price_USD'].mean()
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">O'rtacha Narx</div>
            <div class="metric-value">${avg_price:,.0f}</div>
            <div class="metric-sub">Mediana: ${filtered['Price_USD'].median():,.0f}</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    avg_sqm = filtered['Price_per_Sqm'].mean()
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">1 m² O'rtacha Narxi</div>
            <div class="metric-value">${avg_sqm:,.0f}</div>
            <div class="metric-sub">Min: ${filtered['Price_per_Sqm'].min():,.0f} | Max: ${filtered['Price_per_Sqm'].max():,.0f}</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    avg_area = filtered['Area_Sqm'].mean()
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">O'rtacha Maydon</div>
            <div class="metric-value">{avg_area:.1f} <span style="font-size:1.1rem; font-weight:400;">m²</span></div>
            <div class="metric-sub">O'rtacha xona: {filtered['Rooms'].mean():.1f} ta</div>
        </div>
    """, unsafe_allow_html=True)

st.write("")
st.write("")

# ---------------------------------------------------------
# 5. GRAFIKLAR BLOKI
# ---------------------------------------------------------
tab_analytics, tab_calculator, tab_data = st.tabs(
    ["📊 Bozor Analitikasi", "🧮 Narx Kalkulyatori", "📋 Ma'lumotlar Jadvali"])

with tab_analytics:
    g1, g2 = st.columns([1.6, 1.2])

    with g1:
        # Tumanlar bo'yicha narx reytingi (Bar Chart)
        dist_agg = filtered.groupby('District')['Price_per_Sqm'].mean().reset_index().sort_values(by='Price_per_Sqm',
                                                                                                  ascending=True)
        fig_bar = px.bar(
            dist_agg,
            x='Price_per_Sqm',
            y='District',
            orientation='h',
            text_auto='.0f',
            title="<b>Tumanlar kesimida 1 m² narxi ($)</b>",
            color='Price_per_Sqm',
            color_continuous_scale='Blues'
        )
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title="O'rtacha narx ($/m²)",
            yaxis_title=None,
            coloraxis_showscale=False,
            margin=dict(l=0, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with g2:
        # Ta'mir holati ulushi (Donut Chart)
        if 'Renovation' in filtered.columns:
            fig_donut = px.pie(
                filtered,
                names='Renovation',
                hole=0.55,
                title="<b>Ta'mir holati bo'yicha ulush</b>",
                color_discrete_sequence=['#2563EB', '#60A5FA', '#93C5FD']
            )
            fig_donut.update_traces(textposition='inside', textinfo='percent+label')
            fig_donut.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=40, b=20),
                showlegend=False
            )
            st.plotly_chart(fig_donut, use_container_width=True)

    g3, g4 = st.columns(2)

    with g3:
        # Maydon va narx bog'liqligi (Scatter Plot)
        fig_scatter = px.scatter(
            filtered,
            x='Area_Sqm',
            y='Price_USD',
            color='Rooms',
            size='Price_per_Sqm',
            title="<b>Maydon va narx bog'liqligi (Xonalar kesimida)</b>",
            labels={'Area_Sqm': 'Maydon (m²)', 'Price_USD': 'Narx ($)', 'Rooms': 'Xonalar'},
            color_continuous_scale='Viridis',
            hover_data=['District']
        )
        fig_scatter.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_scatter, use_container_width=True)

    with g4:
        # Xonalar soni bo'yicha narxlar taqsimoti (Boxplot)
        fig_box = px.box(
            filtered,
            x='Rooms',
            y='Price_USD',
            color='Rooms',
            title="<b>Xonalar soni bo'yicha narx diapazoni (Box Plot)</b>",
            labels={'Rooms': 'Xonalar soni', 'Price_USD': 'Narx ($)'}
        )
        fig_box.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)

# ---------------------------------------------------------
# 6. INTERAKTIV NARX KALKULYATORI
# ---------------------------------------------------------
with tab_calculator:
    st.subheader("💡 Obyekt narxini baholash kalkulyatori")
    st.caption(
        "Ushbu kalkulyator mavjud bozor ma'lumotlaridagi o'rtacha m² narxlari asosida taxminiy qiymatni hisoblab beradi.")

    c_calc1, c_calc2, c_calc3 = st.columns(3)
    with c_calc1:
        calc_district = st.selectbox("Tumanni tanlang:", options=all_districts)
    with c_calc2:
        calc_area = st.number_input("Maydoni (m²):", min_value=20.0, max_value=300.0, value=65.0, step=1.0)
    with c_calc3:
        calc_renovation = st.selectbox("Ta'mir turi:", options=clean_df[
            'Renovation'].unique() if 'Renovation' in clean_df.columns else ["Standart"])

    # Baholash hisobi
    sub_data = clean_df[(clean_df['District'] == calc_district)]
    if 'Renovation' in clean_df.columns:
        sub_data = sub_data[sub_data['Renovation'] == calc_renovation]

    if not sub_data.empty:
        sqm_benchmark = sub_data['Price_per_Sqm'].mean()
        est_price = sqm_benchmark * calc_area
        range_min = est_price * 0.93
        range_max = est_price * 1.07

        st.success(f"### 🎯 Taxminiy Bozor Qiymati: **${est_price:,.0f}**")
        st.info(
            f"Kutilayotgan narx oralig'i (±7%): **${range_min:,.0f} —${range_max:,.0f}** | Ushbu parametrlar bo'yicha 1 m² ning o'rtacha narxi: **${sqm_benchmark:,.0f}**")
    else:
        st.warning("Ushbu kombinatsiya bo'yicha yetarli ma'lumot mavjud emas.")

# ---------------------------------------------------------
# 7. MA'LUMOTLAR JADVALI VA YUKLAB OLISH
# ---------------------------------------------------------
with tab_data:
    st.subheader("Filtrlangan ma'lumotlar to'plami")
    st.dataframe(filtered, use_container_width=True)

    csv_data = filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Filtrlangan ma'lumotlarni CSV ko'rinishida yuklab olish",
        data=csv_data,
        file_name='tashkent_filtered_real_estate.csv',
        mime='text/csv',
    )