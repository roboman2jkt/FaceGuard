import streamlit as st

# --- TAMPILAN ---
st.set_page_config(
    page_title = "Dashboard Madrasah Digital",
)
# Header
st.image("https://yt3.googleusercontent.com/6UpF8AEHlaHmxgt5LpSrbcxFbRceiVTfaWLCDyXzEC4Tc4o9Eebcq9bvWAekHqxWvWYsji1hbA=s900-c-k-c0x00ffffff-no-rj", width=200)  # Ganti dengan path logo Anda
st.title("Selamat Datang di Platform FaceGuard MAN 2 Jakarta")
st.sidebar.success("Select a page above.")
# Konten Utama
st.write("""
FaceGuard adalah platform untuk menampilkan data presensi harian siswa di MAN 2 Jakarta.
Pengguna dapat mengakses data presensi harian pada halaman "Rekap Presensi Siswa".
""")


# Footer (Opsional)
st.markdown("---")
st.write("© 2024 MAN 2 Jakarta. Hak Cipta Dilindungi.")