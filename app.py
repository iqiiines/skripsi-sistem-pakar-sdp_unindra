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
    # Tabel Basis Pengetahuan (Ditambah kolom Organ, Arah, dan Solusi)
    c.execute('''CREATE TABLE IF NOT EXISTS basis_pengetahuan 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  nama_penyakit TEXT, 
                  gejala TEXT,
                  organ TEXT,
                  arah TEXT,
                  solusi TEXT)''')
    
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
    
    # Data Penyakit & Gejala Master (Update dengan Detail Organ & Solusi)
    c.execute("SELECT COUNT(*) FROM basis_pengetahuan")
    if c.fetchone()[0] == 0:
        default_data = [
            ("Gastritis (Maag)", "Nyeri atau perih pada ulu hati, Mual, Perut terasa kembung atau begah, Cepat merasa kenyang saat makan", "Lambung", "Bagian Tengah Atas (Ulu Hati)", "Makan teratur porsi kecil. Hindari pedas, asam, dan kafein."),
            ("GERD (Asam Lambung)", "Nyeri atau perih pada ulu hati, Sensasi panas atau terbakar di dada (heartburn), Mulut terasa pahit atau asam, Sering bersendawa", "Kerongkongan", "Dada tengah hingga tenggorokan", "Jangan berbaring setelah makan. Tidur dengan posisi kepala lebih tinggi."),
            ("Diare", "Buang air besar (BAB) cair lebih dari 3 kali sehari, Sakit perut atau kram perut yang melilit, Badan terasa lemas dan mudah lelah", "Usus Besar & Halus", "Seluruh area perut (kram)", "Perbanyak cairan/oralit untuk mencegah dehidrasi."),
            ("Demam Tifoid (Tipes)", "Demam (suhu tubuh meningkat), Badan terasa lemas dan mudah lelah, Sakit kepala atau pusing, Kehilangan nafsu makan", "Usus Halus", "Area perut tengah (sekitar pusar)", "Istirahat total (bed rest) dan konsumsi makanan lunak."),
            ("Apendisitis (Usus Buntu)", "Nyeri perut yang berawal dari pusar lalu berpindah ke perut bagian kanan bawah, Rasa sakit semakin parah saat batuk, berjalan, atau bergerak, Mual, Demam (suhu tubuh meningkat)", "Umbai Cacing", "Perut bagian kanan bawah", "Segera ke UGD. Memerlukan penanganan medis/bedah darurat."),
            ("Konstipasi (Sembelit)", "Susah buang air besar (BAB) atau frekuensi BAB kurang dari 3 kali seminggu, Feses keras, kering, atau menggumpal, Perlu mengejan keras saat BAB", "Rektum", "Bagian bawah perut", "Perbanyak serat (buah/sayur) dan minum air putih."),
            ("Disentri", "Buang air besar (BAB) cair lebih dari 3 kali sehari, Sakit perut atau kram perut yang melilit, BAB disertai darah atau lendir, Demam (suhu tubuh meningkat)", "Usus Besar", "Perut bawah dan tengah", "Segera periksa ke dokter untuk penanganan infeksi.")
        ]
        c.executemany("INSERT INTO basis_pengetahuan (nama_penyakit, gejala, organ, arah, solusi) VALUES (?, ?, ?, ?, ?)", default_data)
        
    conn.commit()
    conn.close()

# --- 2. FUNGSI CRUD ---
def ambil_basis():
    conn = sqlite3.connect('sistem_pakar.db')
    c = conn.cursor()
    c.execute("SELECT * FROM basis_pengetahuan")
    data = c.fetchall()
    conn.close()
    return data

def tambah_penyakit(nama, gejala, organ, arah, solusi):
    conn = sqlite3.connect('sistem_pakar.db')
    c = conn.cursor()
    c.execute("INSERT INTO basis_pengetahuan (nama_penyakit, gejala, organ, arah, solusi) VALUES (?, ?, ?, ?, ?)", 
              (nama, gejala, organ, arah, solusi))
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

init_db()

# --- 3. UI SIDEBAR ---
with st.sidebar:
    st.title("🩺 SDP EXPERT SYSTEM")
    menu = st.radio("Navigasi Menu Utama", ["Home", "Mulai Diagnosa", "Riwayat Analisa", "Login Staf"])

# --- 4. HALAMAN HOME ---
if menu == "Home":
    st.header("Selamat Datang")
    st.image("https://img.freepik.com/free-vector/doctors-concept-illustration_114360-1515.jpg", width=500)
    st.markdown(f"""
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
    col_a, col_b = st.columns(2)
    with col_a:
        nama_p = st.text_input("Nama Lengkap Pasien*")
        tgl_l = st.date_input("Tanggal Lahir*", value=date(2000, 1, 1))
        usia = st.number_input("Usia (Tahun)*", min_value=0)
    with col_b:
        tb = st.number_input("Tinggi Badan (cm)*", min_value=0)
        bb = st.number_input("Berat Badan (kg)*", min_value=0)
        jk = st.selectbox("Jenis Kelamin*", ["Laki-laki", "Perempuan"])
    
    goldar = st.selectbox("Golongan Darah*", ["A", "B", "AB", "O"])
    riwayat_p = st.text_area("Riwayat Penyakit Sebelumnya")

    st.divider()
    
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

    if st.button("Proses Analisa Diagnosa", type="primary"):
        if not nama_p or tb == 0:
            st.error("Mohon lengkapi biodata pasien!")
        elif not gejala_user:
            st.error("Silakan pilih minimal satu gejala!")
        else:
            raw_p = ambil_basis()
            hasil_list = []
            
            st.subheader("Hasil Analisis Medis:")
            
            for item in raw_p:
                id_p, nm, gj_p, org, arh, sol = item
                p_gj_list = [gx.strip() for gx in gj_p.split(",")]
                
                # Menghitung kecocokan
                match = set(gejala_user).intersection(p_gj_list)
                if match:
                    persen = (len(match)/len(p_gj_list))*100
                    if persen >= 50: # Tampilkan jika kecocokan >= 50%
                        hasil_list.append(f"{nm} ({persen:.0f}%)")
                        with st.expander(f"➔ {nm} (Tingkat Keyakinan: {persen:.0f}%)", expanded=True):
                            c1, c2 = st.columns(2)
                            c1.write(f"**Organ Terdampak:** {org}")
                            c2.write(f"**Titik Lokasi Nyeri:** :red[{arh}]")
                            st.info(f"**Saran Tindakan:** {sol}")

            hasil_txt = ", ".join(hasil_list) if hasil_list else "Tidak Terdeteksi"
            
            # Simpan ke History
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
    
    if not st.session_state.role:
        st.subheader("Login Staf Admin")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Masuk"):
            conn = sqlite3.connect('sistem_pakar.db')
            c = conn.cursor()
            c.execute("SELECT role FROM users WHERE username=? AND password=?", (u, hash_password(p)))
            res = c.fetchone()
            conn.close()
            if res:
                st.session_state.role = res[0]
                st.rerun()
            else: st.error("Akses Ditolak!")
    else:
        st.title(f"Panel {st.session_state.role}")
        t1, t2 = st.tabs(["Kelola Basis Pengetahuan", "Logout"])
        
        with t1:
            with st.expander("➕ Tambah Data Penyakit"):
                n_p = st.text_input("Nama Penyakit")
                n_g = st.text_area("Gejala (pisahkan dengan koma)")
                n_o = st.text_input("Organ")
                n_a = st.text_input("Arah/Lokasi Nyeri")
                n_s = st.text_area("Solusi Medis")
                if st.button("Simpan ke Database"):
                    tambah_penyakit(n_p, n_g, n_o, n_a, n_s)
                    st.success("Data Berhasil Disimpan!")
                    st.rerun()
            
            st.divider()
            for row in ambil_basis():
                with st.container(border=True):
                    col_1, col_2 = st.columns([4,1])
                    col_1.write(f"**{row[1]}** ({row[3]})")
                    col_1.caption(f"Gejala: {row[2]}")
                    if col_2.button("Hapus", key=f"del_{row[0]}"):
                        hapus_penyakit(row[0])
                        st.rerun()
        
        with t2:
            if st.button("Keluar Sistem"):
                st.session_state.role = None
                st.rerun()
