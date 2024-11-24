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
url = "https://raw.githubusercontent.com/netania01/Dicoding-Dashboard-Project/refs/heads/master/Dashboard/all_data.csv"
data_df = pd.read_csv(url)

# Memastikan kolom 'date' dalam format datetime
data_df['date'] = pd.to_datetime(data_df['date'])
data_df.sort_values(by='date', inplace=True)
data_df.reset_index(drop=True, inplace=True)

# Memfilter tanggal untuk rentang yang dipilih
max_date = pd.to_datetime(data_df['date']).dt.date.max()
min_date = pd.to_datetime(data_df['date']).dt.date.min()

with st.sidebar:
    st.image(r'Dashboard\Bike logo concept take 2.jpg', use_container_width=True)
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
st.subheader('📅 Yearly Bike Rentals')
fig_yearly = px.line(yearly_recap_df, x='Year', y='Total Rentals', 
                     title="Total Bike Rentals by Year", markers=True, template="plotly_dark")
st.plotly_chart(fig_yearly)

# **2. Working Day vs Weekend Comparison**
st.subheader('🚲 Bike Usage on Working Day vs Weekend')
fig_comparison = px.bar(workingday_weekend_df, x='Day Type', y='total_users', color='Day Type', 
                        title="Bike Usage Comparison: Working Day vs Weekend", template="plotly_dark")
st.plotly_chart(fig_comparison)

# **3. Bike Rentals by Season**
st.subheader('🌳 Bike Usage by Season')
fig_season = px.bar(season_comparison_df, x='season', y='total_users', 
                    title="Bike Rentals by Season", color='season', template="plotly_dark")
st.plotly_chart(fig_season)

# **4. Casual vs Registered Users on Working Day vs Weekend**
st.subheader('👥 Casual vs Registered Users on Working Day vs Weekend')
fig_casual_registered = px.bar(casual_registered_comparison_df, x='Day Type', y=['casual_users', 'registered_users'],
                               title="Casual vs Registered Users: Working Day vs Weekend", 
                               barmode='group', color='Day Type', template="plotly_dark")
st.plotly_chart(fig_casual_registered)

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
