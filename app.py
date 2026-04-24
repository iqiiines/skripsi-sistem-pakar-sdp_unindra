import streamlit as st
import sqlite3
from datetime import datetime, date
import pandas as pd

# --- 1. FUNGSI DATABASE (SANGAT KRUSIAL) ---
def init_db():
    conn = sqlite3.connect('sistem_pakar.db')
    c = conn.cursor()
    # Tabel Basis Pengetahuan
    c.execute('''CREATE TABLE IF NOT EXISTS basis_pengetahuan 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nama_penyakit TEXT, gejala TEXT)''')
    
    # Tabel History
    c.execute('''CREATE TABLE IF NOT EXISTS history_diagnosa 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  nama_pasien TEXT, tgl_lahir TEXT, usia INTEGER, tb INTEGER, bb INTEGER, 
                  jenis_kelamin TEXT, gol_darah TEXT, riwayat_penyakit TEXT, 
                  tanggal_input TEXT, gejala_input TEXT, hasil_diagnosa TEXT)''')
    
    # CEK DATA DEFAULT: Jika kosong, isi otomatis agar list gejala muncul
    c.execute("SELECT COUNT(*) FROM basis_pengetahuan")
    if c.fetchone()[0] == 0:
        default_data = [
            ("Maag (Gastritis)", "Mual, Perih Lambung, Perut Kembung, Cepat Kenyang"),
            ("Diare", "Buang Air Besar Cair, Kram Perut, Demam, Dehidrasi"),
            ("Asam Lambung (GERD)", "Dada Terbakar, Mulut Pahit, Sulit Menelan, Batuk Kering"),
            ("Sembelit", "BAB Jarang, Tinja Keras, Mengejan Berlebih, Perut Begah")
        ]
        c.executemany("INSERT INTO basis_pengetahuan (nama_penyakit, gejala) VALUES (?, ?)", default_data)
    
    conn.commit()
    conn.close()

# --- FUNGSI AMBIL DATA ---
def ambil_basis_pengetahuan():
    conn = sqlite3.connect('sistem_pakar.db')
    c = conn.cursor()
    c.execute("SELECT * FROM basis_pengetahuan")
    data = c.fetchall()
    conn.close()
    return data

def ambil_history():
    conn = sqlite3.connect('sistem_pakar.db')
    c = conn.cursor()
    c.execute("SELECT * FROM history_diagnosa ORDER BY id DESC")
    data = c.fetchall()
    conn.close()
    return data

# --- FUNGSI CRUD ADMIN ---
def tambah_penyakit(nama, gejala):
    conn = sqlite3.connect('sistem_pakar.db')
    c = conn.cursor()
    c.execute("INSERT INTO basis_pengetahuan (nama_penyakit, gejala) VALUES (?, ?)", (nama, gejala))
    conn.commit()
    conn.close()

def hapus_penyakit(id_p):
    conn = sqlite3.connect('sistem_pakar.db')
    c = conn.cursor()
    c.execute("DELETE FROM basis_pengetahuan WHERE id=?", (id_p,))
    conn.commit()
    conn.close()

def hapus_history(id_h):
    conn = sqlite3.connect('sistem_pakar.db')
    c = conn.cursor()
    c.execute("DELETE FROM history_diagnosa WHERE id=?", (id_h,))
    conn.commit()
    conn.close()

def simpan_history(nama, tgl_l, usia, tb, bb, jk, goldar, riwayat, gejala_in, hasil):
    conn = sqlite3.connect('sistem_pakar.db')
    c = conn.cursor()
    tgl_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query = '''INSERT INTO history_diagnosa 
               (nama_pasien, tgl_lahir, usia, tb, bb, jenis_kelamin, gol_darah, riwayat_penyakit, tanggal_input, gejala_input, hasil_diagnosa) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
    c.execute(query, (nama, str(tgl_l), usia, tb, bb, jk, goldar, riwayat, tgl_now, gejala_in, hasil))
    conn.commit()
    conn.close()

# Jalankan Inisialisasi
init_db()

# --- 2. UI STREAMLIT ---
st.set_page_config(page_title="Sistem Pakar Pencernaan", layout="wide")

with st.sidebar:
    st.title("🩺 SISTEM PAKAR")
    menu = st.radio("Menu Utama", ["Home", "Mulai Diagnosa", "Riwayat Analisa", "Login Admin"])

# --- 3. LOGIKA HALAMAN ---
if menu == "Home":
    st.header("🏠 Selamat Datang")
    st.image("https://img.freepik.com/free-vector/doctors-concept-illustration_114360-1515.jpg", width=500)
    st.write("Aplikasi diagnosa penyakit pencernaan manusia berbasis sistem pakar.")

elif menu == "Mulai Diagnosa":
    st.header("📋 Form Diagnosa & Rekam Medis")
    
    # Form Pasien
    col1, col2 = st.columns(2)
    with col1:
        nama_pasien = st.text_input("Nama Lengkap*")
        tgl_lahir = st.date_input("Tanggal Lahir*", value=date(2000, 1, 1))
        usia = st.number_input("Usia*", min_value=0)
    with col2:
        tb = st.number_input("TB (cm)*", min_value=0)
        bb = st.number_input("BB (kg)*", min_value=0)
        jk = st.selectbox("Gender*", ["Laki-laki", "Perempuan"])
    
    goldar = st.selectbox("Gol Darah*", ["A", "B", "AB", "O"])
    riwayat_p = st.text_area("Riwayat Penyakit")

    st.divider()

    # Tampilkan Gejala dari Database
    raw_penyakit = ambil_basis_pengetahuan()
    if not raw_penyakit:
        st.warning("List gejala kosong. Tambahkan data di menu Admin.")
    else:
        # Map penyakit dan gejalanya
        data_map = {item[1]: [g.strip() for g in item[2].split(",")] for item in raw_penyakit}
        semua_gejala = sorted(list(set([g for daftar in data_map.values() for g in daftar])))
        
        st.subheader("Pilih Gejala yang Dirasakan:")
        gejala_user = []
        cols = st.columns(3)
        for i, g in enumerate(semua_gejala):
            if cols[i % 3].checkbox(g):
                gejala_user.append(g)

        if st.button("Proses Analisa"):
            if not nama_pasien or tb == 0 or bb == 0:
                st.error("Lengkapi biodata!")
            elif not gejala_user:
                st.error("Pilih minimal satu gejala!")
            else:
                # Proses Diagnosa (Inference)
                hasil_list = []
                for p_nama, p_gejala in data_map.items():
                    match = set(gejala_user).intersection(p_gejala)
                    if match:
                        persen = (len(match) / len(p_gejala)) * 100
                        hasil_list.append(f"{p_nama} ({persen:.0f}%)")
                
                hasil_final = ", ".join(hasil_list) if hasil_list else "Tidak ditemukan diagnosa"
                
                simpan_history(nama_pasien, tgl_lahir, usia, tb, bb, jk, goldar, riwayat_p, ", ".join(gejala_user), hasil_final)
                st.success(f"Hasil untuk {nama_pasien}: {hasil_final}")

elif menu == "Riwayat Analisa":
    st.header("📜 Riwayat Diagnosa")
    h_data = ambil_history()
    if h_data:
        df = pd.DataFrame(h_data, columns=["ID", "Nama", "Tgl Lahir", "Usia", "TB", "BB", "Gender", "GolDarah", "Riwayat", "Waktu", "Gejala", "Hasil"])
        st.dataframe(df.drop(columns=["ID"]), use_container_width=True)
    else:
        st.info("Riwayat masih kosong.")

elif menu == "Login Admin":
    if 'auth' not in st.session_state: st.session_state.auth = False

    if not st.session_state.auth:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if u == "admin" and p == "admin":
                st.session_state.auth = True
                st.rerun()
    else:
        st.title("🛠️ Panel Admin")
        t1, t2 = st.tabs(["Basis Pengetahuan", "Data History"])
        
        with t1:
            st.subheader("Kelola Penyakit")
            with st.expander("Tambah Data"):
                n_p = st.text_input("Nama Penyakit")
                n_g = st.text_area("Gejala (pisah dengan koma)")
                if st.button("Simpan"):
                    tambah_penyakit(n_p, n_g)
                    st.rerun()
            
            for idp, nm, gj in ambil_basis_pengetahuan():
                c1, c2 = st.columns([4, 1])
                c1.write(f"**{nm}**: {gj}")
                if c2.button("Hapus", key=f"p_{idp}"):
                    hapus_penyakit(idp)
                    st.rerun()

        with t2:
            st.subheader("Hapus History")
            for h in ambil_history():
                c_a, c_b = st.columns([4, 1])
                c_a.write(f"{h[1]} - {h[11]}")
                if c_b.button("Hapus", key=f"h_{h[0]}"):
                    hapus_history(h[0])
                    st.rerun()
        
        if st.button("Logout"):
            st.session_state.auth = False
            st.rerun()