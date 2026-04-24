import streamlit as st
import sqlite3
from datetime import datetime, date
import pandas as pd
import hashlib

# --- 1. FUNGSI DATABASE & KEAMANAN ---
def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def init_db():
    conn = sqlite3.connect('sistem_pakar.db')
    c = conn.cursor()
    # Tabel Basis Pengetahuan
    c.execute('''CREATE TABLE IF NOT EXISTS basis_pengetahuan 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nama_penyakit TEXT, gejala TEXT)''')
    
    # Tabel History
    c.execute('''CREATE TABLE IF NOT EXISTS history_diagnosa 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nama_pasien TEXT, tgl_lahir TEXT, 
                  usia INTEGER, tb INTEGER, bb INTEGER, jenis_kelamin TEXT, 
                  gol_darah TEXT, riwayat_penyakit TEXT, tanggal_input TEXT, 
                  gejala_input TEXT, hasil_diagnosa TEXT)''')
    
    # Tabel Users
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, 
                  password TEXT, role TEXT)''')
    
    # User Admin Default
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        pw_admin = hash_password("admin123")
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                  ("admin", pw_admin, "Admin"))
    
    # Data Penyakit & Gejala Sesuai Gambar 3 (Update Database)
    c.execute("SELECT COUNT(*) FROM basis_pengetahuan")
    if c.fetchone()[0] == 0:
        # Mapping Gejala berdasarkan Kode G01-G20 untuk akurasi diagnosa
        default_data = [
            ("Gastritis (Maag)", "Nyeri atau perih pada ulu hati, Mual, Perut terasa kembung atau begah, Cepat merasa kenyang saat makan"),
            ("GERD (Asam Lambung)", "Nyeri atau perih pada ulu hati, Sensasi panas atau terbakar di dada (heartburn), Mulut terasa pahit atau asam, Sering bersendawa"),
            ("Diare", "Buang air besar (BAB) cair lebih dari 3 kali sehari, Sakit perut atau kram perut yang melilit, Badan terasa lemas dan mudah lelah"),
            ("Demam Tifoid (Tipes)", "Demam (suhu tubuh meningkat), Badan terasa lemas dan mudah lelah, Sakit kepala atau pusing, Kehilangan nafsu makan"),
            ("Apendisitis (Usus Buntu)", "Nyeri perut yang berawal dari pusar lalu berpindah ke perut bagian kanan bawah, Rasa sakit semakin parah saat batuk, berjalan, atau bergerak, Mual, Demam (suhu tubuh meningkat)"),
            ("Konstipasi (Sembelit)", "Susah buang air besar (BAB) atau frekuensi BAB kurang dari 3 kali seminggu, Feses keras, kering, atau menggumpal, Perlu mengejan keras saat BAB"),
            ("Disentri", "Buang air besar (BAB) cair lebih dari 3 kali sehari, Sakit perut atau kram perut yang melilit, BAB disertai darah atau lendir, Demam (suhu tubuh meningkat)")
        ]
        c.executemany("INSERT INTO basis_pengetahuan (nama_penyakit, gejala) VALUES (?, ?)", default_data)
        
    conn.commit()
    conn.close()

# --- 2. FUNGSI CRUD & UTILITAS ---
def ambil_basis():
    conn = sqlite3.connect('sistem_pakar.db')
    c = conn.cursor()
    c.execute("SELECT * FROM basis_pengetahuan")
    data = c.fetchall()
    conn.close()
    return data

def tambah_penyakit(nama, gejala):
    conn = sqlite3.connect('sistem_pakar.db')
    c = conn.cursor()
    c.execute("INSERT INTO basis_pengetahuan (nama_penyakit, gejala) VALUES (?, ?)", (nama, gejala))
    conn.commit()
    conn.close()

def update_penyakit(id_p, nama, gejala):
    conn = sqlite3.connect('sistem_pakar.db')
    c = conn.cursor()
    c.execute("UPDATE basis_pengetahuan SET nama_penyakit=?, gejala=? WHERE id=?", (nama, gejala, id_p))
    conn.commit()
    conn.close()

def hapus_penyakit(id_p):
    conn = sqlite3.connect('sistem_pakar.db')
    c = conn.cursor()
    c.execute("DELETE FROM basis_pengetahuan WHERE id=?", (id_p,))
    conn.commit()
    conn.close()

def ambil_history():
    conn = sqlite3.connect('sistem_pakar.db')
    c = conn.cursor()
    c.execute("SELECT * FROM history_diagnosa ORDER BY id DESC")
    data = c.fetchall()
    conn.close()
    return data

def tambah_user(username, password, role):
    try:
        conn = sqlite3.connect('sistem_pakar.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                  (username, hash_password(password), role))
        conn.commit()
        conn.close()
        return True
    except: return False

def ganti_password(username, password_baru):
    conn = sqlite3.connect('sistem_pakar.db')
    c = conn.cursor()
    c.execute("UPDATE users SET password=? WHERE username=?", 
              (hash_password(password_baru), username))
    conn.commit()
    conn.close()

init_db()

# --- 3. UI SIDEBAR ---
with st.sidebar:
    st.title("🩺 SDP EXPERT SYSTEM")
    menu = st.radio("Navigasi Menu Utama", ["Home", "Mulai Diagnosa", "Riwayat Analisa", "Login Staf"])

# --- 4. HALAMAN HOME ---
if menu == "Home":
    st.header("Selamat Datang")
    st.image("https://img.freepik.com/free-vector/doctors-concept-illustration_114360-1515.jpg", width=500)
    st.markdown("""
    ### Sistem Pakar Diagnosa Penyakit Pencernaan Manusia
    Aplikasi ini dikembangkan oleh **Septyan Dwi Priyanto** sebagai syarat kelulusan Skripsi di **Universitas Indraprasta PGRI (UNINDRA)**.
    
    **Detail Akademik:**
    * **Jenjang:** Sarjana (S1)
    * **NIM:** 202243502061
    * **Program Studi:** Teknik Informatika
    """)
    st.write("©️2026 SDP Production - Sistem Pakar Diagnosa Penyakit Pencernaan Manusia v1.0")

# --- 5. HALAMAN DIAGNOSA ---
elif menu == "Mulai Diagnosa":
    st.header("Form Diagnosa & Rekam Medis")
    col1, col2 = st.columns(2)
    with col1:
        nama_p = st.text_input("Nama Lengkap Pasien*")
        tgl_l = st.date_input("Tanggal Lahir*", value=date(2000, 1, 1))
        usia = st.number_input("Usia (Tahun)*", min_value=0)
    with col2:
        tb = st.number_input("Tinggi Badan (cm)*", min_value=0)
        bb = st.number_input("Berat Badan (kg)*", min_value=0)
        jk = st.selectbox("Jenis Kelamin*", ["Laki-laki", "Perempuan"])
    
    goldar = st.selectbox("Golongan Darah*", ["A", "B", "AB", "O"])
    riwayat_p = st.text_area("Riwayat Penyakit (Opsional)")

    st.divider()
    
    # LIST GEJALA BERDASARKAN GAMBAR 3 (G01-G20)
    st.subheader("Pilih Gejala yang Dirasakan:")
    gejala_list = [
        "Nyeri atau perih pada ulu hati", "Mual", "Muntah", "Perut terasa kembung atau begah",
        "Cepat merasa kenyang saat makan", "Sensasi panas atau terbakar di dada (heartburn)",
        "Mulut terasa pahit atau asam", "Sering bersendawa", "Buang air besar (BAB) cair lebih dari 3 kali sehari",
        "Sakit perut atau kram perut yang melilit", "Demam (suhu tubuh meningkat)", 
        "Badan terasa lemas dan mudah lelah", "Sakit kepala atau pusing", 
        "Nyeri perut yang berawal dari pusar lalu berpindah ke perut bagian kanan bawah",
        "Rasa sakit semakin parah saat batuk, berjalan, atau bergerak", "Kehilangan nafsu makan",
        "Susah buang air besar (BAB) atau frekuensi BAB kurang dari 3 kali seminggu",
        "Feses keras, kering, atau menggumpal", "Perlu mengejan keras saat BAB", "BAB disertai darah atau lendir"
    ]
    
    gejala_user = []
    cols = st.columns(2)
    for i, g in enumerate(gejala_list):
        if cols[i % 2].checkbox(g, key=f"gj_{i}"):
            gejala_user.append(g)

    if st.button("Proses Analisa Diagnosa"):
        if not nama_p or tb == 0:
            st.error("Mohon lengkapi biodata pasien!")
        elif not gejala_user:
            st.error("Silakan pilih minimal satu gejala!")
        else:
            raw_p = ambil_basis()
            data_map = {item[1]: [g.strip() for g in item[2].split(",")] for item in raw_p}
            
            hasil = []
            for p_nm, p_gj in data_map.items():
                match = set(gejala_user).intersection(p_gj)
                if match:
                    persen = (len(match)/len(p_gj))*100
                    hasil.append(f"{p_nm} ({persen:.0f}%)")
            
            hasil_txt = ", ".join(hasil) if hasil else "Tidak Terdeteksi Penyakit Spesifik"
            
            # Simpan ke DB
            conn = sqlite3.connect('sistem_pakar.db')
            conn.execute('''INSERT INTO history_diagnosa 
                            (nama_pasien, tgl_lahir, usia, tb, bb, jenis_kelamin, 
                             gol_darah, riwayat_penyakit, tanggal_input, 
                             gejala_input, hasil_diagnosa) VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
                         (nama_p, str(tgl_l), usia, tb, bb, jk, goldar, riwayat_p, 
                          datetime.now().strftime("%Y-%m-%d %H:%M"), 
                          ", ".join(gejala_user), hasil_txt))
            conn.commit()
            conn.close()
            st.success(f"Hasil Diagnosa: {hasil_txt}")

# --- 6. HALAMAN RIWAYAT ---
elif menu == "Riwayat Analisa":
    st.header("Riwayat Diagnosa Pasien")
    h_data = ambil_history()
    if h_data:
        df = pd.DataFrame(h_data, columns=["ID", "Nama", "Lahir", "Usia", "TB", "BB", 
                                           "Gender", "GolDar", "Riwayat", "Waktu", 
                                           "Gejala", "Hasil"])
        st.dataframe(df.drop(columns=["ID"]), use_container_width=True)
    else:
        st.info("Belum ada data riwayat.")

# --- 7. PANEL LOGIN STAF ---
elif menu == "Login Staf":
    if 'role' not in st.session_state: st.session_state.role = None
    if 'user' not in st.session_state: st.session_state.user = None

    if not st.session_state.role:
        st.subheader("Login Staf")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Masuk"):
            conn = sqlite3.connect('sistem_pakar.db')
            c = conn.cursor()
            c.execute("SELECT role FROM users WHERE username=? AND password=?", 
                      (u, hash_password(p)))
            res = c.fetchone()
            conn.close()
            if res:
                st.session_state.role = res[0]
                st.session_state.user = u
                st.rerun()
            else: st.error("Username atau Password salah!")
    else:
        st.title(f"Panel Kontrol {st.session_state.role}")
        tabs = st.tabs(["Basis Pengetahuan", "Riwayat & Export", "Manajemen User", "Akun Saya"])
        t1, t2, t3, t4 = tabs

        # TAB 1: BASIS PENGETAHUAN
        with t1:
            st.subheader("Kelola Daftar Penyakit & Gejala")
            with st.expander("➕ Tambah Penyakit Baru"):
                n_p = st.text_input("Nama Penyakit")
                n_g = st.text_area("Gejala (pisahkan dengan koma)")
                if st.button("Simpan Data"):
                    tambah_penyakit(n_p, n_g)
                    st.success("Data berhasil ditambahkan!")
                    st.rerun()
            
            st.divider()
            for idp, nm, gj in ambil_basis():
                with st.container(border=True):
                    c_a, c_b = st.columns([4, 1])
                    c_a.write(f"**{nm}**")
                    c_a.caption(f"Gejala: {gj}")
                    if c_b.button("Hapus", key=f"btn_dl_{idp}"):
                        hapus_penyakit(idp)
                        st.rerun()

        # TAB 2-4 (Riwayat, User, Akun) tetap sama...
        with t2:
            st.subheader("Export Data")
            h_all = ambil_history()
            if h_all:
                df_exp = pd.DataFrame(h_all)
                st.download_button("📥 Download CSV", df_exp.to_csv().encode('utf-8'), "report.csv")
                st.dataframe(df_exp)

        if st.button("Keluar (Logout)"):
            st.session_state.role = None
            st.rerun()
