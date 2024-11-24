#Import Libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg') 
import seaborn as sns
import streamlit as st
from plotly import express as px

# Set visual style
sns.set(style='whitegrid')

# Load dataset
url = "https://raw.githubusercontent.com/netania01/Dicoding-Dashboard-Project/refs/heads/main/Dashboard/all_data.csv"
data_df = pd.read_csv(url)

# Memastikan kolom 'date' dalam format datetime
data_df['date'] = pd.to_datetime(data_df['date'])
data_df.sort_values(by='date', inplace=True)
data_df.reset_index(drop=True, inplace=True)

# Memfilter tanggal untuk rentang yang dipilih
max_date = pd.to_datetime(data_df['date']).dt.date.max()
min_date = pd.to_datetime(data_df['date']).dt.date.min()

#URL gambar di Github
image_url = "https://github.com/netania01/Dicoding-Dashboard-Project/blob/main/Dashboard/Bike%20logo%20concept%20take%202.jpg?raw=true"

with st.sidebar:
    st.image(image_url)
    st.markdown("## Filter Rentang Tanggal")
    start_date, end_date = st.date_input(
        label='Pilih Rentang Waktu',
        max_value=max_date,
        min_value=min_date,
        value=[min_date, max_date]
    )
    if st.checkbox("Tampilkan Dataset"):
        st.subheader("Dataset")
        st.write(data_df)
        
    st.title("Made By")
    st.write(
        """
        **Netania Pangalinan**\n
        Email: **netaniapangalinan@gmail.com**
        Dicoding Account: **netania01**
        """

    )

# Menyaring data sesuai rentang tanggal yang dipilih
main_df = data_df[(data_df['date'] >= str(start_date)) & 
                   (data_df['date'] <= str(end_date))]

#menyiapkan dataframe yang diperlukan

#Create Yearly Recap
def create_yearly_recap(df):
    df['year'] = df['date'].dt.year
    yearly_data = df.groupby('year')['total_users'].sum().reset_index()
    yearly_data.columns = ['Year', 'Total Rentals']
    return yearly_data

yearly_recap_df = create_yearly_recap(main_df)

#Create Workingday Weekend Comparison Recap
def create_workingday_weekend_comparison(df):
    comparison_data = df.groupby('is_workingday')['total_users'].sum().reset_index()
    comparison_data['Day Type'] = comparison_data['is_workingday'].map({0: 'Weekend', 1: 'Working Day'})
    return comparison_data

workingday_weekend_df = create_workingday_weekend_comparison(main_df)

#Create Season Comparison Recap
def create_season_comparison(df):
    season_data = df.groupby('season')['total_users'].sum().reset_index()
    return season_data

season_comparison_df = create_season_comparison(main_df)

#Create Casual Registered Comparison Recap
def create_casual_registered_comparison(df):
    comparison = df.groupby(['is_workingday'])[['casual_users', 'registered_users']].sum().reset_index()
    comparison['Day Type'] = comparison['is_workingday'].map({0: 'Weekend', 1: 'Working Day'})
    return comparison

casual_registered_comparison_df = create_casual_registered_comparison(main_df)

# RFM Recap
def create_rfm_recap(df):
    # Grupkan data berdasarkan jam (hour) dan hitung metrik RFM
    rfm_df = df.groupby(by='hour', as_index=False).agg({
        'date': 'max',  # Tanggal terakhir transaksi di jam tersebut (Recency)
        'casual_users': 'sum',  # Total kontribusi (monetary) berdasarkan pengguna kasual
        'registered_users': 'sum',  # Total kontribusi berdasarkan pengguna terdaftar
    })

    # Menghitung order_count (jumlah transaksi per jam)
    rfm_df['order_count'] = df.groupby('hour')['hour'].count().values

    # Ganti nama kolom untuk metrik RFM
    rfm_df.columns = ['hour', 'last_order_date', 'casual_revenue', 'registered_revenue', 'order_count']

    # Perhitungan Recency per jam
    rfm_df['last_order_date'] = rfm_df['last_order_date'].dt.date
    recent_date = df['date'].dt.date.max()  # Tanggal terkini dalam dataset
    rfm_df['recency'] = rfm_df['last_order_date'].apply(lambda x: (recent_date - x).days)

    # Total revenue = casual + registered revenue
    rfm_df['revenue'] = rfm_df['casual_revenue'] + rfm_df['registered_revenue']

    # Hapus kolom 'last_order_date' karena tidak diperlukan untuk analisis lebih lanjut
    rfm_df.drop('last_order_date', axis=1, inplace=True)
    
    return rfm_df

rfm_recap_df = create_rfm_recap(main_df)

# **Visualisasi**

# **1. Yearly Bike Rentals**

# Menghitung total penggunaan sepeda per tahun (pastikan 'yearly_recap_df' sudah terdefinisi)
yearly_usage = yearly_recap_df.groupby('Year')['Total Rentals'].sum().reset_index()

# Membuat bar chart untuk menghitung pengguna sepeda tiap tahun
fig_yearly = px.bar(
    yearly_usage,
    x='Year',
    y='Total Rentals',
    labels={'Year': 'Tahun', 'Total Rentals': 'Total Pengguna'},
    title='Total Penggunaan Sepeda per Tahun',
    color='Total Rentals',
    color_continuous_scale='reds'  # Mengganti palet warna ke merah
)

# Update layout
fig_yearly.update_layout(
    xaxis_title='Tahun',
    yaxis_title='Total Pengguna Sepeda',
    plot_bgcolor='white',
    paper_bgcolor='white',
    title_font=dict(size=20, family='Arial', color='black'),
    xaxis=dict(tickmode='linear', tick0=yearly_usage['Year'].min(), dtick=1)
)

# Menampilkan plot di Streamlit
st.subheader('📅 Yearly Bike Rentals')
st.plotly_chart(fig_yearly)

# **2. Working Day vs Weekend Comparison**

# Menghitung rata-rata penggunaan sepeda per hari kerja vs akhir pekan
workday_usage = day_df.groupby('is_workingday')['total_users'].mean().reset_index()

# Membuat Pie Chart untuk perbandingan penggunaan sepeda antara hari kerja dan akhir pekan
fig = px.pie(
    workday_usage,
    names='is_workingday',
    values='total_users',
    title='<b>Rata-rata Penggunaan Sepeda per Hari Kerja vs Akhir Pekan<b>',
    color='is_workingday',  # Menggunakan 'is_workingday' untuk menentukan warna
    color_discrete_sequence=['#FFCDD2', '#F44336']  # Warna dari merah muda terang ke merah terang
)

# Memperbarui label dan tampilan
fig.update_traces(textinfo='percent+label')
fig.update_layout(
    title_font=dict(size=20, family='Arial', color='black'),
    legend_title_text='Hari (0=Weekend, 1=Workday)',
    plot_bgcolor='white',
    paper_bgcolor='white'
)

# Menampilkan Pie Chart di Streamlit
st.subheader('🚲 Bike Usage on Working Day vs Weekend')
st.plotly_chart(fig)

st.plotly_chart(fig_comparison)

# **3. Bike Rentals by Season**

# Menghitung rata-rata penggunaan sepeda per musim (pastikan 'season_comparison_df' sudah ada)
seasonal_usage = season_comparison_df.groupby('season')['total_users'].sum().reset_index()

# Membuat bar chart untuk perbandingan penggunaan sepeda berdasarkan musim
fig_season = px.bar(
    seasonal_usage,
    x='season',
    y='total_users',
    title='<b>Rata-rata Penggunaan Sepeda per Musim<b>',
    color='total_users',
    color_continuous_scale='reds',  # Mengganti palet warna ke merah
    labels={'season': 'Musim', 'total_users': 'Rata-rata Pengguna Sepeda'}
)

# Update layout untuk tampilan yang lebih baik
fig_season.update_layout(
    xaxis_title='Musim',
    yaxis_title='Rata-rata Pengguna Sepeda',
    title_font=dict(size=20, family='Arial', color='black'),
    plot_bgcolor='white',
    paper_bgcolor='white'
)

# Menampilkan bar chart di Streamlit
st.subheader('🌳 Bike Usage by Season')
st.plotly_chart(fig_season)

# **4. Casual vs Registered Users on Working Day vs Weekend**

# Menghitung rata-rata penggunaan sepeda per kategori pengguna pada hari kerja dan akhir pekan
user_contribution = day_df.groupby(['is_workingday']).agg(
    casual_users=('casual_users', 'mean'),
    registered_users=('registered_users', 'mean')
).reset_index()

# Mengubah data ke format long
user_contribution_melted = user_contribution.melt(id_vars='is_workingday', value_vars=['casual_users', 'registered_users'],
                                                  var_name='user_type', value_name='average_users')

# Memperbarui nama tipe pengguna untuk label yang lebih deskriptif
user_contribution_melted['user_type'] = user_contribution_melted['user_type'].replace({
    'casual_users': 'Casual Users',
    'registered_users': 'Registered Users'
})

# Membuat visualisasi barplot dengan skema warna merah
fig = px.bar(
    user_contribution_melted,
    x='is_workingday',
    y='average_users',
    color='user_type',  # Menggunakan user_type sebagai kategori warna
    barmode='group',
    color_discrete_sequence=['#FFCDD2', '#F44336'],  # Warna dari merah muda ke merah
    labels={
        'is_workingday': 'Hari (0=Weekend, 1=Weekday)',
        'average_users': 'Rata-rata Jumlah Pengguna',
        'user_type': 'Tipe Pengguna'
    },
    title='<b>Rata-rata Penggunaan Kasual vs Terdaftar pada Hari Kerja dan Akhir Pekan</b>'
)

# Update x-axis ticks
fig.update_xaxes(tickvals=[0, 1], ticktext=['Akhir Pekan', 'Hari Kerja'])

# Menampilkan plot di Streamlit
st.subheader('👥 Casual vs Registered Users on Working Day vs Weekend')
st.plotly_chart(fig)

# RFM Recap Visualization
st.subheader('RFM Recap')

col1, col2, col3 = st.columns(3)

# Recency Plot (Menampilkan Jam dengan Recency Terendah)
with col1:
    top_recency = rfm_recap_df.sort_values(by='recency', ascending=True).head(5)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=top_recency, x='hour', y='recency', color='royalblue', ax=ax)
    ax.set_title('Recency (Days) - Most Recent Rentals', fontsize=20, fontweight='bold')
    ax.set_xlabel('Hour of Day', fontsize=15)
    ax.set_ylabel('Recency (Days)', fontsize=15)
    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=12)
    st.pyplot(fig)

# Frequency Plot (Menampilkan Jam dengan Jumlah Transaksi Terbanyak)
with col2:
    top_frequency = rfm_recap_df.sort_values(by='order_count', ascending=False).head(5)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=top_frequency, x='hour', y='order_count', color='tomato', ax=ax)
    ax.set_title('Frequency - Most Frequent Rentals', fontsize=20, fontweight='bold')
    ax.set_xlabel('Hour of Day', fontsize=15)
    ax.set_ylabel('Number of Rentals', fontsize=15)
    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=12)
    st.pyplot(fig)

# Monetary Plot (Menampilkan Jam dengan Pendapatan Terbesar)
with col3:
    top_monetary = rfm_recap_df.sort_values(by='revenue', ascending=False).head(5)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=top_monetary, x='hour', y='revenue', color='forestgreen', ax=ax)
    ax.set_title('Monetary - Highest Revenue', fontsize=20, fontweight='bold')
    ax.set_xlabel('Hour of Day', fontsize=15)
    ax.set_ylabel('Revenue (USD)', fontsize=15)
    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=12)
    st.pyplot(fig)
    
st.caption('Bike Sharing Dashboard Analysis')
