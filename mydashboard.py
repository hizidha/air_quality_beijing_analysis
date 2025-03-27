import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from streamlit_folium import folium_static

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("Air_Quality_Cleaned.csv")
    df["datetime"] = pd.to_datetime(df[["year", "month", "day", "hour"]], errors="coerce")
    return df

df = load_data()

# Sidebar
st.sidebar.title("Air Quality Dashboard")
st.sidebar.subheader("Filter Data")
station_options = ["All"] + list(df["station"].unique())
station = st.sidebar.selectbox("Pilih Stasiun Pemantauan", station_options)

if station != "All":
    df = df[df["station"] == station]

st.title("Analisis Kualitas Udara Beijing")
st.write("Dashboard ini menyajikan analisis kualitas udara berdasarkan data historis.")

# PM2.5 Distribution
st.subheader("Distribusi Konsentrasi PM2.5")
fig, ax = plt.subplots()
sns.histplot(df["PM2.5"], bins=50, kde=True, color='red', ax=ax)
ax.set_xlabel("Konsentrasi PM2.5")
ax.set_ylabel("Frekuensi")
ax.set_title("Histogram PM2.5 untuk " + (station if station != "All" else "Semua Stasiun"))
st.pyplot(fig)

# Correlation Heatmap (Excluding year, month, day, hour)
st.subheader("Korelasi Antar Faktor Polusi Udara")
cols_to_exclude = ["year", "month", "day", "hour"]
num_cols = df.select_dtypes(include=[np.number]).columns.difference(cols_to_exclude)
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(df[num_cols].corr(), annot=True, cmap="coolwarm", ax=ax)
ax.set_title("Matriks Korelasi Faktor Kualitas Udara")
st.pyplot(fig)

# Monthly PM2.5 Trend per Station
st.subheader("Tren Bulanan Rata-rata PM2.5")
df_monthly = df.groupby([df["datetime"].dt.to_period("M")])["PM2.5"].mean()
fig, ax = plt.subplots(figsize=(12, 6))
df_monthly.plot(ax=ax)
ax.set_xlabel("Tahun")
ax.set_ylabel("Rata-rata PM2.5")
ax.set_title("Perubahan PM2.5 dari Waktu ke Waktu untuk " + (station if station != "All" else "Semua Stasiun"))
st.pyplot(fig)

# Air Pollution Patterns by Season
st.subheader("Pola Polusi Udara Berdasarkan Musim")
season_map = {1: 'Winter', 2: 'Winter', 3: 'Spring', 4: 'Spring', 5: 'Spring', 6: 'Summer',
                7: 'Summer', 8: 'Summer', 9: 'Fall', 10: 'Fall', 11: 'Fall', 12: 'Winter'}
df["season"] = df["month"].map(season_map)
df_season = df.groupby("season")["PM2.5"].mean()
fig, ax = plt.subplots(figsize=(12, 6))
df_season.plot(kind='bar', ax=ax, color='skyblue')
ax.set_xlabel("Musim")
ax.set_ylabel("Rata-rata PM2.5")
ax.set_title("Polusi Udara Berdasarkan Musim untuk " + (station if station != "All" else "Semua Stasiun"))
st.pyplot(fig)

# Air Pollution Map
st.subheader("Peta Sebaran Polusi Udara di Beijing")
m = folium.Map(location=[39.9, 116.4], zoom_start=10)

station_coords = {
    "Aotizhongxin": [39.982, 116.417], "Changping": [40.218, 116.23],
    "Dingling": [40.29, 116.22], "Dongsi": [39.929, 116.417],
    "Guanyuan": [39.933, 116.36], "Gucheng": [39.911, 116.184],
    "Huairou": [40.317, 116.62], "Nongzhanguan": [39.933, 116.45],
    "Shunyi": [40.125, 116.65], "Tiantan": [39.886, 116.417],
    "Wanliu": [39.95, 116.283], "Wanshouxigong": [39.886, 116.366]
}

def get_color(value):
    if value > 150:
        return "darkred"
    elif value > 100:
        return "red"
    elif value > 50:
        return "orange"
    else:
        return "green"

df_avg_pm = df.groupby("station")["PM2.5"].mean().reset_index()
for _, row in df_avg_pm.iterrows():
    if row["station"] in station_coords:
        folium.CircleMarker(
            location=station_coords[row["station"]],
            radius=max(5, row["PM2.5"] / 20),
            color=get_color(row["PM2.5"]),
            fill=True,
            fill_color=get_color(row["PM2.5"]),
            fill_opacity=0.6,
            popup=f"{row['station']}: {row['PM2.5']:.2f}"
        ).add_to(m)

folium_static(m)