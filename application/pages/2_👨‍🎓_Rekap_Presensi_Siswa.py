import streamlit as st
import pymongo
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# Koneksi ke MongoDB
client = pymongo.MongoClient("mongodb+srv://robotikman2jkt:DdlJaVXGJO4Lo91o@cluster0.knymo2f.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["data_presensi"]
collection_kehadiran = db["data_siswa_harian"]
collection_siswa = db["data_siswa"]

st.header("Data Presensi MAN 2 JAKARTA")
with st.expander("Filter Data"):
    selected_class = st.selectbox("Pilih Kelas:", collection_siswa.distinct("class"))
    default_date = datetime(2024, 7, 26).date()
    selected_date = st.date_input("Pilih Tanggal:", value=default_date)

# Dapatkan semua kelas yang unik
all_classes = collection_siswa.distinct("class")

# Ambil data kehadiran berdasarkan filter
filtered_kehadiran = collection_kehadiran.find({
    "class": selected_class,
    "date": selected_date.strftime("%Y-%m-%d")
})
df_kehadiran = pd.DataFrame(list(filtered_kehadiran))

# Ambil data seluruh siswa dalam kelas yang dipilih
siswa_kelas = collection_siswa.find({"class": selected_class})
df_siswa = pd.DataFrame(list(siswa_kelas))

# Buat kamus untuk menyimpan status kehadiran berdasarkan nama
status_kehadiran = {}
for _, row in df_kehadiran.iterrows():
    status_kehadiran[row["name"]] = {
        "status": "HADIR",
        "timestamp": row["timestamp"],
        "date": row["date"]
    }

# Gabungkan status kehadiran ke DataFrame siswa
df_siswa["status"] = df_siswa["name"].apply(lambda x: status_kehadiran.get(x, {"status": "TIDAK HADIR"})["status"])
df_siswa["timestamp"] = df_siswa["name"].apply(lambda x: status_kehadiran.get(x, {"timestamp": None})["timestamp"])
df_siswa["date"] = df_siswa["name"].apply(lambda x: status_kehadiran.get(x, {"date": selected_date.strftime("%Y-%m-%d")})["date"])

# Logika untuk menentukan status kehadiran
for index, row in df_siswa.iterrows():
    if row["timestamp"] and row["timestamp"] > "06:40:00":
        df_siswa.at[index, "status"] = "TERLAMBAT"
        
# Ganti nama kolom (sebelum menambahkan kolom No.)
df_siswa = df_siswa.rename(columns={
    "name": "Nama",
    "class": "Kelas",
    "date": "Tanggal",
    "timestamp": "Waktu Presensi"
})

# Tambahkan kolom "No." (setelah mengganti nama kolom)
df_siswa.insert(0, "No.", range(1, len(df_siswa) + 1))

# Modifikasi kolom "status" menjadi badge HTML dengan class CSS
df_siswa["Status"] = df_siswa["status"].apply(lambda status:
    f'<span class="badge badge-{status.lower().replace(" ", "-")}">{status}</span>'
)

# Mengganti nilai None pada kolom Waktu Presensi menjadi "Tidak Ada"
df_siswa['Waktu Presensi'] = df_siswa['Waktu Presensi'].fillna("Tidak Ada")

# Menempatkan tombol di sisi kanan dan sejajar
_, col1, col2, _ = st.columns([1, 1, 1, 1])  # Menciptakan 4 kolom, 2 kolom di tengah untuk tombol

with col1:
    if st.button("Print ke XLSX"):
        df_siswa[["No.", "Nama", "Kelas", "status", "Tanggal", "Waktu Presensi"]].to_excel("data_presensi.xlsx", index=False)
        st.success("File XLSX berhasil disimpan!")

with col2:
    if st.button("Print ke PDF"):
        # Membuat objek PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Menambahkan judul
        pdf.cell(200, 10, txt=f"Data Presensi Kelas {selected_class} pada {selected_date}", ln=1, align="C")

        # Menambahkan header tabel
        for col in ["No.", "Nama", "Kelas", "Status", "Tanggal", "Waktu Presensi"]:
            pdf.cell(40, 10, txt=col, border=1, align="C")
        pdf.ln()

        # Menambahkan data ke tabel
        for _, row in df_siswa[["No.", "Nama", "Kelas", "Status", "Tanggal", "Waktu Presensi"]].iterrows():
            for item in row:
                # Check if the item is a string before applying startswith()
                if isinstance(item, str) and item.startswith("<span"):
                    item = item[item.find(">")+1:item.rfind("<")]  
                pdf.cell(40, 10, txt=str(item), border=1, align="C")  # Convert item to string
            pdf.ln()

        # Menyimpan file PDF
        pdf.output("data_presensi.pdf")
        st.success("File PDF berhasil disimpan!")

# Tampilkan DataFrame dengan badges
st.write(f"Data Presensi Kelas {selected_class} pada {selected_date}")

# Styling CSS untuk badge dan header
st.markdown("""
<style>
.badge {
    padding: 5px 10px;
    border-radius: 5px;
    font-weight: bold;
    white-space: nowrap;
    display: inline-block;
    vertical-align: middle;
}
.badge-hadir {
    background-color: #3B82F6;
    color: white;
}
.badge-terlambat {
    background-color: #EF4444;
    color: white;
}
.badge-tidak-hadir {
    background-color: #D1D5DB;
    color: black;
}
/* CSS untuk mengatur header dan teks menjadi rata tengah */
.dataframe th, .dataframe td {
    text-align: center; 
}
</style>
""", unsafe_allow_html=True)

# Tampilkan DataFrame sebagai tabel dengan HTML yang di-render
st.write(df_siswa[["No.", "Nama", "Kelas", "Status", "Tanggal", "Waktu Presensi"]].to_html(escape=False, index=False), unsafe_allow_html=True)