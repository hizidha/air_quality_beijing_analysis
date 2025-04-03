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
station_options = ["All Station"] + list(df["station"].unique())
selected_station = st.sidebar.selectbox("Pilih Stasiun Pemantauan", station_options)

# Apply filter
filtered_df = df if selected_station == "All Station" else df[df["station"] == selected_station]

# Visualisasi 1: Tren Tahunan PM2.5
st.subheader("Tren Tahunan Rata-rata PM2.5")
df_trend = filtered_df.groupby(["station", "year"])["PM2.5"].mean().reset_index()
fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(data=df_trend, x="year", y="PM2.5", hue="station", marker="o", ax=ax)
ax.set_xlabel("Tahun")
ax.set_ylabel("Rata-rata PM2.5")
ax.set_title("Tren PM2.5 di Setiap Station dari Tahun ke Tahun")
plt.xticks(df_trend["year"].unique())
plt.grid()
st.pyplot(fig)

# Visualisasi 2: Polusi Udara Berdasarkan Musim
st.subheader("Pola Polusi Udara Berdasarkan Musim")
season_map = {1: 'Winter', 2: 'Winter', 3: 'Spring', 4: 'Spring', 5: 'Spring', 
            6: 'Summer', 7: 'Summer', 8: 'Summer', 9: 'Fall', 10: 'Fall', 
            11: 'Fall', 12: 'Winter'}
df["season"] = df["month"].map(season_map)
filtered_df["season"] = filtered_df["month"].map(season_map)

df_season_avg = df.groupby("season")["PM2.5"].mean().reset_index()
df_season_filtered = filtered_df.groupby("season")["PM2.5"].mean().reset_index()

fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(x="season", y="PM2.5", data=df_season_avg if selected_station == "All Station" else df_season_filtered, palette="coolwarm", ax=ax)
ax.set_xlabel("Musim")
ax.set_ylabel("Rata-rata Polusi")
ax.set_title("Pola Polusi Udara Berdasarkan Musim")
st.pyplot(fig)

# Visualisasi 3: Korelasi PM2.5 dan Faktor Cuaca
st.subheader("Korelasi PM2.5 dan Faktor Cuaca")
correlation = filtered_df[["PM2.5", "TEMP", "PRES", "DEWP"]].corr()
fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(correlation, annot=True, cmap="coolwarm", linewidths=0.5, vmin=-1, vmax=1, fmt=".2f", ax=ax)
ax.set_title("Heatmap Korelasi PM2.5 dan Faktor Cuaca")
st.pyplot(fig)

# Visualisasi 4: Stasiun dengan Rata-rata PM2.5 Tertinggi
st.subheader("Stasiun dengan Rata-rata PM2.5 Tertinggi")
df_pollution_rank = df.groupby("station", as_index=False)["PM2.5"].mean()
df_pollution_rank = df_pollution_rank.sort_values(by="PM2.5", ascending=False)

if selected_station == "All Station":
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=df_pollution_rank, x="PM2.5", y="station", hue="station", palette="coolwarm", legend=False, ax=ax)
    ax.set_xlabel("Rata-rata PM2.5")
    ax.set_ylabel("Stasiun")
    ax.set_title("Stasiun dengan Rata-rata PM2.5 Tertinggi")
    ax.grid(axis="x", linestyle="--", alpha=0.7)
    st.pyplot(fig)
else:
    avg_pm25 = df["PM2.5"].mean()
    station_pm25 = df[df["station"] == selected_station]["PM2.5"].mean()
    df_selected = pd.DataFrame({"station": [selected_station, "All Station"], "PM2.5": [station_pm25, avg_pm25]})
    
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=df_selected, x="PM2.5", y="station", palette="coolwarm", ax=ax)
    ax.set_xlabel("Rata-rata PM2.5")
    ax.set_ylabel("Kategori")
    ax.set_title("Perbandingan Rata-rata PM2.5")
    st.pyplot(fig)

# Visualisasi 5: Peta Distribusi Polusi Udara
def get_color(pm_value):
    if pm_value <= 50:
        return "green"
    elif pm_value <= 100:
        return "yellow"
    elif pm_value <= 150:
        return "orange"
    else:
        return "red"

st.subheader("Peta Distribusi Polusi Udara")
station_coords = {"Aotizhongxin": [39.982, 116.417], "Changping": [40.218, 116.23],
                "Dingling": [40.29, 116.22], "Dongsi": [39.929, 116.417],
                "Guanyuan": [39.933, 116.36], "Gucheng": [39.911, 116.184],
                "Huairou": [40.317, 116.62], "Nongzhanguan": [39.933, 116.45],
                "Shunyi": [40.125, 116.65], "Tiantan": [39.886, 116.417],
                "Wanliu": [39.95, 116.283], "Wanshouxigong": [39.886, 116.366]}

df_pollution_rank = df_pollution_rank[df_pollution_rank["station"] == selected_station] if selected_station != "All Station" else df_pollution_rank
m = folium.Map(location=[39.9, 116.4], zoom_start=10)
for _, row in df_pollution_rank.iterrows():
    folium.CircleMarker(
        location=[station_coords.get(row["station"], [np.nan, np.nan])[0], station_coords.get(row["station"], [np.nan, np.nan])[1]],
        radius=row["PM2.5"] / 10,
        color=get_color(row["PM2.5"]),
        fill=True,
        fill_color=get_color(row["PM2.5"]),
        fill_opacity=0.7,
        popup=f"{row['station']}: {row['PM2.5']:.2f}"
    ).add_to(m)
folium_static(m)
