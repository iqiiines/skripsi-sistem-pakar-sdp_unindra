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
    c.execute('CREATE TABLE IF NOT EXISTS basis_pengetahuan (id INTEGER PRIMARY KEY AUTOINCREMENT, nama_penyakit TEXT, gejala TEXT)')
    # Tabel History
    c.execute('''CREATE TABLE IF NOT EXISTS history_diagnosa 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nama_pasien TEXT, tgl_lahir TEXT, usia INTEGER, tb INTEGER, bb INTEGER, 
                  jenis_kelamin TEXT, gol_darah TEXT, riwayat_penyakit TEXT, tanggal_input TEXT, gejala_input TEXT, hasil_diagnosa TEXT)''')
    # Tabel Users (Baru)
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT)''')
    
    # Buat User Admin Default jika belum ada
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        pw_admin = hash_password("admin123")
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("admin", pw_admin, "Admin"))
    
    # Data Default Penyakit
    c.execute("SELECT COUNT(*) FROM basis_pengetahuan")
    if c.fetchone()[0] == 0:
        default_p = [("Maag", "Mual, Perih"), ("Diare", "BAB Cair"), ("GERD", "Dada Terbakar")]
        c.executemany("INSERT INTO basis_pengetahuan (nama_penyakit, gejala) VALUES (?, ?)", default_p)
        
    conn.commit()
    conn.close()

# --- FUNGSI MANAJEMEN USER ---
def tambah_user(username, password, role):
    try:
        conn = sqlite3.connect('sistem_pakar.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hash_password(password), role))
        conn.commit()
        conn.close()
        return True
    except: return False

def ganti_password(username, password_baru):
    conn = sqlite3.connect('sistem_pakar.db')
    c = conn.cursor()
    c.execute("UPDATE users SET password=? WHERE username=?", (hash_password(password_baru), username))
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = sqlite3.connect('sistem_pakar.db')
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE username=? AND password=?", (username, hash_password(password)))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

init_db()

# --- 2. SIDEBAR ---
with st.sidebar:
    st.title("🩺 SISTEM PAKAR")
    menu = st.radio("Navigasi", ["Home", "Mulai Diagnosa", "Riwayat Analisa", "Login Staf"])

# --- 3. LOGIKA HALAMAN (Home & Diagnosa tetap sama) ---
if menu == "Home":
    st.header("🏠 Selamat Datang")
    st.write("Silakan pilih menu untuk memulai.")

elif menu == "Mulai Diagnosa":
    st.header("📋 Form Diagnosa Mandiri")
    st.info("Input data pasien untuk mendapatkan hasil analisa.")
    # (Kode form diagnosa Anda sebelumnya dimasukkan di sini)

elif menu == "Riwayat Analisa":
    st.header("📜 Riwayat Publik")
    st.warning("Hanya menampilkan data terbatas. Login untuk detail lengkap.")
    # Tampilkan dataframe sederhana tanpa detail medis sensitif jika diinginkan

# --- 4. PANEL LOGIN & KONTROL (ADMIN & PETUGAS) ---
elif menu == "Login Staf":
    if 'user_role' not in st.session_state: st.session_state.user_role = None
    if 'username' not in st.session_state: st.session_state.username = None

    if not st.session_state.user_role:
        st.subheader("🔐 Login Sistem")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Masuk"):
            role = login_user(u, p)
            if role:
                st.session_state.user_role = role
                st.session_state.username = u
                st.success(f"Selamat datang {u} ({role})")
                st.rerun()
            else: st.error("Akun tidak ditemukan!")
    else:
        st.title(f"🛠️ Panel {st.session_state.user_role}")
        
        # TAB BERDASARKAN ROLE
        if st.session_state.user_role == "Admin":
            t1, t2, t3, t4 = st.tabs(["Penyakit", "Riwayat & Export", "Tambah User", "Akun Saya"])
        else: # Role: Petugas
            t2, t4 = st.tabs(["Riwayat & Export", "Akun Saya"])
            t1, t3 = None, None

        # Tab 1: Manajemen Penyakit (Hanya Admin)
        if t1:
            with t1:
                st.subheader("Kelola Basis Pengetahuan")
                # (Masukkan kode edit/hapus penyakit Anda di sini)

        # Tab 2: Riwayat & Export (Admin & Petugas)
        with t2:
            st.subheader("Data Riwayat Pasien")
            # Ambil data dari sqlite3 dan tampilkan st.download_button untuk CSV

        # Tab 3: Tambah User Baru (Hanya Admin)
        if t3:
            with t3:
                st.subheader("Registrasi User Baru")
                new_u = st.text_input("Username Baru")
                new_p = st.text_input("Password Baru", type="password")
                new_r = st.selectbox("Role", ["Petugas", "Admin"])
                if st.button("Daftarkan User"):
                    if tambah_user(new_u, new_p, new_r):
                        st.success(f"User {new_u} berhasil dibuat!")
                    else: st.error("Username sudah ada!")

        # Tab 4: Ganti Password (Semua Role)
        with t4:
            st.subheader("Pengaturan Akun")
            pw_skrg = st.text_input("Konfirmasi Password Baru", type="password")
            if st.button("Update Password"):
                ganti_password(st.session_state.username, pw_skrg)
                st.success("Password berhasil diperbarui!")

        if st.button("Keluar (Logout)"):
            st.session_state.user_role = None
            st.rerun()
