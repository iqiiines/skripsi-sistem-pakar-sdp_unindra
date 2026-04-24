import streamlit as st
import sqlite3
from datetime import datetime, date
import pandas as pd
import hashlib
import io

# --- 1. FUNGSI DATABASE & KEAMANAN ---
def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def init_db():
    conn = sqlite3.connect('sistem_pakar.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS basis_pengetahuan 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nama_penyakit TEXT, gejala TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS history_diagnosa 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nama_pasien TEXT, tgl_lahir TEXT, 
                  usia INTEGER, tb INTEGER, bb INTEGER, jenis_kelamin TEXT, 
                  gol_darah TEXT, riwayat_penyakit TEXT, tanggal_input TEXT, 
                  gejala_input TEXT, hasil_diagnosa TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, 
                  password TEXT, role TEXT)''')
    
    # User Admin Default
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        pw_admin = hash_password("admin123")
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                 ("admin", pw_admin, "Admin"))
    
    conn.commit()
    conn.close()

# --- 2. FUNGSI CRUD & UTILITAS ---
def ambil_basis():
    conn = sqlite3.connect('sistem_pakar.db')
    df = pd.read_sql_query("SELECT * FROM basis_pengetahuan", conn)
    conn.close()
    return df

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

def ambil_history():
    conn = sqlite3.connect('sistem_pakar.db')
    df = pd.read_sql_query("SELECT * FROM history_diagnosa ORDER BY id DESC", conn)
    conn.close()
    return df

def update_history(df_updated):
    conn = sqlite3.connect('sistem_pakar.db')
    df_updated.to_sql('history_diagnosa', conn, if_exists='replace', index=False)
    conn.close()

def ambil_users():
    conn = sqlite3.connect('sistem_pakar.db')
    df = pd.read_sql_query("SELECT id, username, role FROM users", conn)
    conn.close()
    return df

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

def hapus_user(user_id):
    conn = sqlite3.connect('sistem_pakar.db')
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

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
            # Algoritma sederhana (Intersection)
            df_bp = ambil_basis()
            hasil = []
            for _, row in df_bp.iterrows():
                p_gj = [x.strip() for x in row['gejala'].split(',')]
                match = set(gejala_user).intersection(p_gj)
                if match:
                    persen = (len(match)/len(p_gj))*100
                    hasil.append(f"{row['nama_penyakit']} ({persen:.0f}%)")
            
            hasil_txt = ", ".join(hasil) if hasil else "Tidak Terdeteksi"
            
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

# --- 6. HALAMAN RIWAYAT (PUBLIC) ---
elif menu == "Riwayat Analisa":
    st.header("Riwayat Diagnosa Pasien")
    df_h = ambil_history()
    if not df_h.empty:
        st.dataframe(df_h.drop(columns=["id"]), use_container_width=True)
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
            c.execute("SELECT role FROM users WHERE username=? AND password=?", (u, hash_password(p)))
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
                if st.button("Simpan Penyakit"):
                    tambah_penyakit(n_p, n_g)
                    st.success("Data berhasil ditambahkan!")
                    st.rerun()
            
            df_basis = ambil_basis()
            for _, row in df_basis.iterrows():
                with st.container(border=True):
                    c_a, c_b = st.columns([4, 1])
                    c_a.write(f"**{row['nama_penyakit']}**")
                    c_a.caption(f"Gejala: {row['gejala']}")
                    if c_b.button("Hapus", key=f"del_bp_{row['id']}"):
                        hapus_penyakit(row['id'])
                        st.rerun()

        # TAB 2: RIWAYAT & EXPORT (DENGAN FITUR EDIT)
        with t2:
            st.subheader("Riwayat Analisa & Export Data")
            df_history = ambil_history()
            
            if not df_history.empty:
                # Fitur Edit menggunakan st.data_editor
                st.write("Silakan edit data langsung pada tabel di bawah jika diperlukan:")
                edited_df = st.data_editor(df_history, num_rows="dynamic", key="editor_history")
                
                if st.button("Simpan Perubahan Tabel"):
                    update_history(edited_df)
                    st.success("Perubahan riwayat berhasil disimpan!")
                    st.rerun()

                st.divider()
                col_exp1, col_exp2 = st.columns(2)
                
                # Export ke CSV
                csv = df_history.to_csv(index=False).encode('utf-8')
                col_exp1.download_button("📥 Download CSV", csv, "riwayat_diagnosa.csv", "text/csv")
                
                # Export ke Excel
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df_history.to_excel(writer, index=False, sheet_name='Sheet1')
                col_exp2.download_button("📥 Download Excel (XLSX)", buffer.getvalue(), "riwayat_diagnosa.xlsx")
                
                st.info("Tip: Gunakan fitur 'Print' pada browser (Ctrl+P) untuk mencetak halaman ini sebagai PDF.")
            else:
                st.info("Data riwayat kosong.")

        # TAB 3: MANAJEMEN USER (RBAC)
        with t3:
            st.subheader("Manajemen Pengguna (RBAC)")
            if st.session_state.role == "Admin":
                with st.expander("➕ Tambah Staf Baru"):
                    new_u = st.text_input("Username Baru")
                    new_p = st.text_input("Password Baru", type="password")
                    new_r = st.selectbox("Role", ["Admin", "Staf/Dokter"])
                    if st.button("Daftarkan User"):
                        if tambah_user(new_u, new_p, new_r):
                            st.success("User berhasil didaftarkan!")
                            st.rerun()
                        else: st.error("Username sudah ada!")
                
                st.write("Daftar User Aktif:")
                df_u = ambil_users()
                for _, u_row in df_u.iterrows():
                    c1, c2, c3 = st.columns([2,2,1])
                    c1.write(u_row['username'])
                    c2.write(f"Role: {u_row['role']}")
                    if u_row['username'] != "admin": # Admin utama tidak bisa dihapus
                        if c3.button("Hapus", key=f"del_u_{u_row['id']}"):
                            hapus_user(u_row['id'])
                            st.rerun()
            else:
                st.warning("Hanya role Admin yang dapat mengelola user.")

        # TAB 4: AKUN SAYA
        with t4:
            st.subheader("Pengaturan Akun")
            st.write(f"Username Aktif: **{st.session_state.user}**")
            with st.form("form_ganti_pw"):
                pw_lama = st.text_input("Password Saat Ini", type="password")
                pw_baru = st.text_input("Password Baru", type="password")
                pw_konf = st.text_input("Konfirmasi Password Baru", type="password")
                
                if st.form_submit_button("Perbarui Password"):
                    # Verifikasi password lama
                    conn = sqlite3.connect('sistem_pakar.db')
                    c = conn.cursor()
                    c.execute("SELECT password FROM users WHERE username=?", (st.session_state.user,))
                    stored_pw = c.fetchone()[0]
                    conn.close()
                    
                    if hash_password(pw_lama) != stored_pw:
                        st.error("Password lama salah!")
                    elif pw_baru != pw_konf:
                        st.error("Konfirmasi password tidak cocok!")
                    elif len(pw_baru) < 6:
                        st.error("Password minimal 6 karakter!")
                    else:
                        ganti_password(st.session_state.user, pw_baru)
                        st.success("Password berhasil diperbarui!")

        if st.button("Keluar (Logout)", type="primary"):
            st.session_state.role = None
            st.session_state.user = None
            st.rerun()
