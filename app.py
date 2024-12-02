import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from folium import Map, Marker
from streamlit_folium import st_folium

# Địa chỉ API
API_URL = "https://he-thong-canh-bao-sat-lo-7b9446780d45.herokuapp.com/get_data"

# Hàm lấy dữ liệu từ API
def fetch_data():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Lỗi khi gọi API: {e}")
        return []

# Hiển thị bản đồ
def display_map(lat, lng, danger_level):
    color = "red" if danger_level > 50 else "green"
    m = Map(location=[lat, lng], zoom_start=15)
    Marker([lat, lng], popup="Mức độ nguy hiểm", icon_color=color).add_to(m)
    st_folium(m, width=700, height=400)

# Hàm hiển thị biểu đồ
def display_charts(data):
    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    # Biểu đồ độ ẩm đất
    fig1 = px.line(df, x="timestamp", y="temperature", title="Độ ẩm đất (%)")
    st.plotly_chart(fig1)

    # Biểu đồ thời gian mưa
    fig2 = px.bar(df, x="timestamp", y="humidity", title="Thời gian mưa (phút)")
    st.plotly_chart(fig2)

    # Biểu đồ tỷ lệ sạt lở
    latest = df.iloc[-1]
    fig3 = px.pie(values=[100 - latest["total"], latest["total"]],
                  names=["Tỉ lệ an toàn", "Tỉ lệ sạt lở"],
                  title="Tỷ lệ sạt lở")
    st.plotly_chart(fig3)

# Main
st.title("Hệ thống cảnh báo sạt lở")
data = fetch_data()

if data:
    latest_data = data[-1]
    st.sidebar.header("Thông số mới nhất")
    st.sidebar.write(f"Thời gian: {latest_data['timestamp']}")
    st.sidebar.write(f"Độ ẩm đất: {latest_data['temperature']}%")
    st.sidebar.write(f"Thời gian mưa: {latest_data['humidity']} phút")
    st.sidebar.write(f"Tỷ lệ sạt lở: {latest_data['total']}%")

    # Hiển thị mức độ nguy hiểm
    level = "Nguy cơ rất cao" if latest_data["total"] > 80 else (
        "Nguy cơ cao" if latest_data["total"] > 50 else "An toàn")
    st.sidebar.write(f"Mức độ nguy hiểm: {level}")

    # Hiển thị bản đồ và biểu đồ
    st.subheader("Bản đồ")
    display_map(20.5331669, 105.9313111, latest_data["total"])

    st.subheader("Biểu đồ dữ liệu")
    display_charts(data)
else:
    st.error("Không có dữ liệu để hiển thị!")
