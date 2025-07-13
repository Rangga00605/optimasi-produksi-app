import streamlit as st
import pandas as pd
import plotly.express as px

# Data produk
PRODUCTS = {
    "Sepatu Olahraga": {
        "harga_jual": 250000,
        "biaya_produksi": 180000,
        "waktu_produksi": 0.8  # jam
    },
    "Sepatu Kasual": {
        "harga_jual": 200000,
        "biaya_produksi": 150000,
        "waktu_produksi": 0.10  # jam
    },
    "Sepatu Formal": {
        "harga_jual": 180000,
        "biaya_produksi": 145000,
        "waktu_produksi": 0.15  # jam
    }
}

# Fungsi optimasi produksi satu produk
def optimize_single_product(product_data, kapasitas_harian, efisiensi):
    profit_per_unit = product_data["harga_jual"] - product_data["biaya_produksi"]
    waktu_per_unit = product_data["waktu_produksi"]

    total_jam_tersedia = kapasitas_harian * efisiensi
    unit_maksimal = int(total_jam_tersedia / waktu_per_unit)
    total_profit = unit_maksimal * profit_per_unit
    total_waktu_terpakai = unit_maksimal * waktu_per_unit
    efisiensi_tercapai = (total_waktu_terpakai / total_jam_tersedia) * 100 if total_jam_tersedia > 0 else 0

    return {
        "Unit Diproduksi": unit_maksimal,
        "Total Profit": round(total_profit, 2),
        "Total Waktu Terpakai (jam)": round(total_waktu_terpakai, 2),
        "Efisiensi Tercapai (%)": round(efisiensi_tercapai, 1),
        "Profit per Unit": profit_per_unit,
        "Total Waktu Tersedia (jam)": round(total_jam_tersedia, 2)
    }

# Streamlit app
st.set_page_config(page_title="Optimasi Produksi Per Produk", page_icon="👟", layout="wide")
st.title("🎯 Optimasi Produksi - Pilih Satu Produk")

st.sidebar.header("⚙️ Parameter Optimasi")
selected_product = st.sidebar.selectbox("Pilih Produk:", list(PRODUCTS.keys()))
kapasitas_harian = st.sidebar.number_input("Kapasitas Produksi Harian (jam)", value=16, min_value=8, max_value=24)
efisiensi_mesin = st.sidebar.slider("Efisiensi Mesin (%)", 60, 100, 85) / 100
target_profit = st.sidebar.number_input("Target Profit Harian (Rp)", value=4000000, min_value=0)

# Ambil data produk terpilih
product_data = PRODUCTS[selected_product]

# Hitung optimasi
hasil = optimize_single_product(product_data, kapasitas_harian, efisiensi_mesin)

# Tampilkan detail produk
st.subheader(f"📦 Detail Produk: {selected_product}")
detail_df = pd.DataFrame({
    "Harga Jual": [product_data["harga_jual"]],
    "Biaya Produksi": [product_data["biaya_produksi"]],
    "Profit per Unit": [hasil["Profit per Unit"]],
    "Waktu Produksi per Unit (jam)": [product_data["waktu_produksi"]],
})
st.dataframe(detail_df, use_container_width=True)

# Rencana produksi
st.subheader("📊 Rencana Produksi")
plan_df = pd.DataFrame([{
    "Produk": selected_product,
    "Unit Diproduksi": hasil["Unit Diproduksi"],
    "Total Waktu Terpakai (jam)": hasil["Total Waktu Terpakai (jam)"],
    "Total Profit": hasil["Total Profit"]
}])
st.dataframe(plan_df, use_container_width=True)

# Perhitungan pencapaian target
selisih = hasil["Total Profit"] - target_profit
pencapaian = (hasil["Total Profit"] / target_profit * 100) if target_profit > 0 else 0
status = "✅ Target tercapai!" if hasil["Total Profit"] >= target_profit else "⚠️ Target belum tercapai"

# Ringkasan metrik
col1, col2, col3, col4 = st.columns(4)
col1.metric("Unit Diproduksi", hasil["Unit Diproduksi"])
col2.metric("Total Profit", f"Rp {hasil['Total Profit']:,.0f}")
col3.metric("Efisiensi Tercapai", f"{hasil['Efisiensi Tercapai (%)']}%")
col4.metric("Pencapaian Target", f"{pencapaian:.1f}%", status)

# Tabel perhitungan target vs realisasi
st.subheader("📌 Perhitungan Target vs Realisasi")
target_df = pd.DataFrame({
    "Keterangan": ["Target Profit Harian", "Total Profit Tercapai", "Selisih", "Persentase Pencapaian"],
    "Nilai": [f"Rp {target_profit:,.0f}", f"Rp {hasil['Total Profit']:,.0f}", 
              f"Rp {selisih:,.0f}", f"{pencapaian:.1f}%"]
})
st.table(target_df)

# Grafik bar: Target vs Realisasi
st.subheader("📊 Grafik Target vs Realisasi Profit")
bar_df = pd.DataFrame({
    "Kategori": ["Target Profit", "Realisasi Profit"],
    "Jumlah": [target_profit, hasil["Total Profit"]]
})
fig_bar = px.bar(bar_df, x="Kategori", y="Jumlah", text_auto=True, color="Kategori", 
                 title="Perbandingan Target vs Realisasi Profit")
st.plotly_chart(fig_bar, use_container_width=True)

# Pie chart distribusi waktu
st.subheader("🥧 Grafik Distribusi Pemakaian Waktu Produksi")
pie_df = pd.DataFrame({
    "Kategori": ["Total Waktu Terpakai", "Sisa Waktu Tersedia"],
    "Jumlah": [hasil["Total Waktu Terpakai (jam)"], hasil["Total Waktu Tersedia (jam)"] - hasil["Total Waktu Terpakai (jam)"]]
})
fig_pie = px.pie(pie_df, values="Jumlah", names="Kategori", hole=0.4,
                 title="Distribusi Waktu Produksi (jam)")
st.plotly_chart(fig_pie, use_container_width=True)

# Trend profit mingguan (simulasi)
st.subheader("📈 Trend Profit Mingguan (Simulasi)")
trend_df = pd.DataFrame({
    "Hari": ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"],
    "Profit": [hasil["Total Profit"] * r for r in [1.0, 0.9, 1.1, 1.05, 0.95, 1.0, 1.2]]
})
fig_trend = px.line(trend_df, x="Hari", y="Profit", markers=True,
                    title="Simulasi Trend Profit Mingguan")
st.plotly_chart(fig_trend, use_container_width=True)
