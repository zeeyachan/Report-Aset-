import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# Load logo KAI dan ubah ke base64
def get_base64_logo(path):
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

logo_path = r"C:\KP\KAI (Kereta Api Indonesia) 2020 Logo (PNG2160p) - Vector69Com.png"
logo_base64 = get_base64_logo(logo_path)

# Layout lebar penuh
st.set_page_config(layout="wide")

# Inject CSS untuk styling yang lebih baik
st.markdown(f"""
    <style>
    /* Hide deprecation warning and streamlit elements */
    .stAlert, .stException {{
        display: none !important;
    }}
    
    /* Custom header styling */
    .custom-header {{
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 20px;
        height: 60px;
    }}
    
    .logo-container img {{
        height: 50px;
        width: auto;
    }}
    
    .title-container h2 {{
        margin: 0 !important;
        padding: 0 !important;
        line-height: 50px;
        font-size: 2rem;
    }}
    
    /* Logo transparan di background grafik dan tabel */
    .element-container:has(.stPlotlyChart), .element-container:has(.stDataFrame) {{
        position: relative;
    }}
    
    .element-container:has(.stPlotlyChart)::before, .element-container:has(.stDataFrame)::before {{
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 150px;
        height: 150px;
        background-image: url("data:image/png;base64,{logo_base64}");
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
        opacity: 0.08;
        z-index: 1;
        pointer-events: none;
    }}
    
    /* Ensure content is above the background */
    .stPlotlyChart, .stDataFrame {{
        position: relative;
        z-index: 2;
    }}
    </style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():  
    df = pd.read_excel(r"C:\KP\Report Aset Teknologi Informasi.xlsx", engine='openpyxl')
    df.columns = df.columns.str.strip()
    df['Production Date'] = pd.to_datetime(df['Production Date'], errors='coerce')
    return df

# HEADER DENGAN LOGO 
st.markdown(f"""
    <div class="custom-header">
        <div class="logo-container">
            <img src="data:image/png;base64,{logo_base64}" alt="KAI Logo">
        </div>
        <div class="title-container">
            <h2> Report Aset Teknologi Informasi</h2>
        </div>
    </div>
""", unsafe_allow_html=True)

# FILTER DAN RINGKASAN 
data = load_data()

# Handle missing or null values properly
status_list = ['All'] + sorted([str(x) for x in data['Status*'].dropna().unique() if pd.notna(x) and str(x) != 'nan'])
manufacturer_list = ['All'] + sorted([str(x) for x in data['Manufacturer'].dropna().unique() if pd.notna(x) and str(x) != 'nan'])

# Handle date filtering
valid_dates = data['Production Date'].dropna()
if not valid_dates.empty:
    min_date = valid_dates.min().date()
    max_date = valid_dates.max().date()
else:
    min_date = pd.Timestamp.now().date()
    max_date = pd.Timestamp.now().date()

f1, f2, f3, f4 = st.columns([1.2, 1.2, 1.2, 1.2])

with f2:
    status_filter = st.selectbox("Status Aset", status_list)
with f3:
    manufacturer_filter = st.selectbox("Manufacturer", manufacturer_list)
with f4:
    start_date, end_date = st.date_input(
        "Rentang Tanggal Produksi", 
        [min_date, max_date],
        min_value=min_date, 
        max_value=max_date
    )

# Apply filters
filtered_data = data.copy()
if status_filter != 'All':
    filtered_data = filtered_data[filtered_data['Status*'] == status_filter]
if manufacturer_filter != 'All':
    filtered_data = filtered_data[filtered_data['Manufacturer'] == manufacturer_filter]

# Date filtering
filtered_data = filtered_data[
    (filtered_data['Production Date'] >= pd.to_datetime(start_date)) &
    (filtered_data['Production Date'] <= pd.to_datetime(end_date))
]

with f1:
    st.metric("Total Aset", f"{filtered_data.shape[0]:,}")

# VISUALISASI 
st.markdown("---")

grafik1, grafik2 = st.columns(2)

with grafik1:
    st.markdown("### 📈 Sebaran Aset")
    if not filtered_data.empty and filtered_data['Production Date'].notna().any():
        # Clean data and handle NaN values
        valid_production_dates = filtered_data['Production Date'].dropna()
        count_by_date = valid_production_dates.value_counts().sort_index().reset_index()
        count_by_date.columns = ['production_date', 'count']
        
        fig_time = px.line(
            count_by_date, 
            x='production_date', 
            y='count',
            markers=True
        )
        fig_time.update_layout(
            title=None,
            xaxis_title="Tanggal Produksi",
            yaxis_title="Jumlah Aset",
            showlegend=False
        )
        fig_time.update_xaxes(showgrid=True)
        fig_time.update_yaxes(showgrid=True)
        st.plotly_chart(fig_time, use_container_width=True, config={'displayModeBar': False})
    else:
        st.info("Tidak ada data tanggal produksi yang valid untuk ditampilkan.")

with grafik2:
    st.markdown("### 📊 Jenis Aset")
    if 'Tier 2' in filtered_data.columns and not filtered_data.empty:
        # Clean and filter Tier 2 data
        tier2_data = filtered_data['Tier 2'].dropna()
        tier2_data = tier2_data[tier2_data.astype(str) != 'nan']
        
        if not tier2_data.empty:
            asset_type = tier2_data.value_counts().reset_index()
            asset_type.columns = ['tier2', 'count']
            
            fig_type = px.bar(
                asset_type, 
                x='count', 
                y='tier2', 
                orientation='h'
            )
            fig_type.update_layout(
                title=None,
                xaxis_title="Jumlah Aset",
                yaxis_title="Jenis Aset",
                showlegend=False
            )
            fig_type.update_xaxes(showgrid=True)
            fig_type.update_yaxes(showgrid=True)
            st.plotly_chart(fig_type, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("Tidak ada data jenis aset yang valid.")
    else:
        st.info("Kolom 'Tier 2' tidak tersedia dalam data.")

grafik3, grafik4 = st.columns(2)

with grafik3:
    st.markdown("### 🧩 Status Aset")
    if not filtered_data.empty:
        status_data = filtered_data['Status*'].dropna()
        status_data = status_data[status_data.astype(str) != 'nan']
        
        if not status_data.empty:
            status_count = status_data.value_counts()
            
            fig_status = px.pie(
                values=status_count.values,
                names=status_count.index,
                hole=0.4
            )
            fig_status.update_layout(
                title=None,
                showlegend=True
            )
            fig_status.update_traces(
                textposition='inside', 
                textinfo='percent+label'
            )
            st.plotly_chart(fig_status, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("Tidak ada data status yang valid.")
    else:
        st.warning("Tidak ada data status untuk ditampilkan.")

with grafik4:
    st.markdown("### 📋 Detail Aset")  
    detail_cols = ['Manufacturer', 'Procurement Type']
    available_detail_cols = [col for col in detail_cols if col in filtered_data.columns]
    
    if available_detail_cols and not filtered_data.empty:
        # Clean data and replace NaN with "Tidak Diketahui"
        detail_data = filtered_data[available_detail_cols].copy()
        for col in available_detail_cols:
            detail_data[col] = detail_data[col].fillna("Tidak Diketahui")
            # Also handle 'nan' strings
            detail_data[col] = detail_data[col].replace('nan', 'Tidak Diketahui')
        
        detail_df = (
            detail_data
            .groupby(available_detail_cols)
            .size()
            .reset_index(name="Jumlah")
            .sort_values("Jumlah", ascending=False)
        )
        
        # Rename columns to Indonesian
        column_rename = {
            'Manufacturer': 'Manufaktur',
            'Procurement Type': 'Jenis Pengadaan'
        }
        detail_df = detail_df.rename(columns=column_rename)
        
        st.dataframe(detail_df, use_container_width=True, hide_index=True)
    else:
        st.info("Tidak ada data detail yang tersedia atau kolom tidak ditemukan.")

# FOOTER
st.markdown("---")
st.caption(f"Data Terakhir Diperbarui: {pd.Timestamp.now():%d/%m/%Y %H:%M:%S} | Powered by KAI")