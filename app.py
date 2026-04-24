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
    
    # Tabel History (Pastikan kolom usia, tb, bb ada)
    c.execute('''CREATE TABLE IF NOT EXISTS history_diagnosa 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nama_pasien TEXT, tgl_lahir TEXT, 
                  usia INTEGER, tb INTEGER, bb INTEGER, jenis_kelamin TEXT, 
                  gol_darah TEXT, riwayat_penyakit TEXT, tanggal_input TEXT, 
                  gejala_input TEXT, hasil_diagnosa TEXT)''')
    
    # Tabel Users untuk Login Staf
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, 
                  password TEXT, role TEXT)''')
    
    # User Admin Default: admin / admin123
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        pw_admin = hash_password("admin123")
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                  ("admin", pw_admin, "Admin"))
    
    # Data Penyakit Default
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
    st.title("🩺 SISTEM PAKAR")
    menu = st.radio("Navigasi Utama", ["Home", "Mulai Diagnosa", "Riwayat Analisa", "Login Staf"])

# --- 4. HALAMAN HOME ---
if menu == "Home":
    st.header("🏠 Selamat Datang")
    st.image("https://img.freepik.com/free-vector/doctors-concept-illustration_114360-1515.jpg", width=500)
    st.write("Sistem Pakar Diagnosa Penyakit Pencernaan Manusia v2.0")

# --- 5. HALAMAN DIAGNOSA ---
elif menu == "Mulai Diagnosa":
    st.header("📋 Form Diagnosa & Rekam Medis")
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
    
    # Logika Pengambilan Gejala dari DB
    raw_p = ambil_basis()
    if raw_p:
        data_map = {item[1]: [g.strip() for g in item[2].split(",")] for item in raw_p}
        semua_gejala = sorted(list(set([g for daftar in data_map.values() for g in daftar])))
        
        st.subheader("Pilih Gejala yang Dirasakan:")
        gejala_user = []
        cols = st.columns(3)
        for i, g in enumerate(semua_gejala):
            if cols[i % 3].checkbox(g):
                gejala_user.append(g)

        if st.button("Proses Analisa Diagnosa"):
            if not nama_p or tb == 0:
                st.error("Mohon lengkapi biodata pasien!")
            elif not gejala_user:
                st.error("Silakan pilih minimal satu gejala!")
            else:
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
                st.success(f"📌 Hasil Diagnosa: {hasil_txt}")

# --- 6. HALAMAN RIWAYAT ---
elif menu == "Riwayat Analisa":
    st.header("📜 Riwayat Diagnosa Pasien")
    h_data = ambil_history()
    if h_data:
        df = pd.DataFrame(h_data, columns=["ID", "Nama", "Lahir", "Usia", "TB", "BB", 
                                           "Gender", "GolDar", "Riwayat", "Waktu", 
                                           "Gejala", "Hasil"])
        st.dataframe(df.drop(columns=["ID"]), use_container_width=True)
    else:
        st.info("Belum ada data riwayat.")

# --- 7. PANEL LOGIN STAF (ADMIN & PETUGAS) ---
elif menu == "Login Staf":
    if 'role' not in st.session_state: st.session_state.role = None
    if 'user' not in st.session_state: st.session_state.user = None

    if not st.session_state.role:
        st.subheader("🔐 Login Staf")
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
        st.title(f"🛠️ Panel Kontrol {st.session_state.role}")
        
        # Pengaturan Tab Berdasarkan Role
        if st.session_state.role == "Admin":
            tabs = st.tabs(["Basis Pengetahuan", "Riwayat & Export", "Manajemen User", "Akun Saya"])
            t1, t2, t3, t4 = tabs
        else:
            tabs = st.tabs(["Riwayat & Export", "Akun Saya"])
            t2, t4 = tabs
            t1, t3 = None, None

        # TAB 1: BASIS PENGETAHUAN (Hanya Admin)
        if t1:
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
                        
                        if c_b.button("✏️", key=f"btn_ed_{idp}"):
                            st.session_state[f"em_{idp}"] = True
                        if c_b.button("🗑️", key=f"btn_dl_{idp}"):
                            hapus_penyakit(idp)
                            st.rerun()
                        
                        if st.session_state.get(f"em_{idp}"):
                            up_nm = st.text_input("Edit Nama", value=nm, key=f"u_nm_{idp}")
                            up_gj = st.text_area("Edit Gejala", value=gj, key=f"u_gj_{idp}")
                            col_c1, col_c2 = st.columns(2)
                            if col_c1.button("Update", key=f"upd_{idp}"):
                                update_penyakit(idp, up_nm, up_gj)
                                st.session_state[f"em_{idp}"] = False
                                st.rerun()
                            if col_c2.button("Batal", key=f"btl_{idp}"):
                                st.session_state[f"em_{idp}"] = False
                                st.rerun()

        # TAB 2: RIWAYAT & EXPORT (Semua Role)
        with t2:
            st.subheader("Export Data Diagnosa")
            h_data_all = ambil_history()
            if h_data_all:
                df_export = pd.DataFrame(h_data_all, columns=["ID","Nama","Lahir","Usia","TB","BB","Gender","GolDar","Riwayat","Waktu","Gejala","Hasil"])
                csv_data = df_export.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Report CSV", csv_data, "laporan_diagnosa.csv", "text/csv")
                st.dataframe(df_export)
            else: st.info("Tidak ada data untuk di-export.")

        # TAB 3: MANAJEMEN USER (Hanya Admin)
        if t3:
            with t3:
                st.subheader("Registrasi Staf Baru")
                u_new = st.text_input("Username Baru", key="input_reg_user")
                p_new = st.text_input("Password Baru", type="password", key="input_reg_pass")
                r_new = st.selectbox("Role Akses", ["Petugas", "Admin"])
                if st.button("Daftarkan"):
                    if tambah_user(u_new, p_new, r_new):
                        st.success(f"User {u_new} berhasil dibuat!")
                    else: st.error("Gagal! Username mungkin sudah ada.")

        # TAB 4: AKUN SAYA (Semua Role)
        with t4:
            st.subheader("Ganti Password Akun")
            pw_update = st.text_input("Password Baru", type="password", key="input_change_pass")
            if st.button("Perbarui Password"):
                ganti_password(st.session_state.user, pw_update)
                st.success("Password berhasil diperbarui!")

        if st.button("Keluar (Logout)"):
            st.session_state.role = None
            st.session_state.user = None
            st.rerun()
