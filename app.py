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
    c.execute('CREATE TABLE IF NOT EXISTS basis_pengetahuan (id INTEGER PRIMARY KEY AUTOINCREMENT, nama_penyakit TEXT, gejala TEXT)')
    c.execute('''CREATE TABLE IF NOT EXISTS history_diagnosa 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nama_pasien TEXT, tgl_lahir TEXT, usia INTEGER, tb INTEGER, bb INTEGER, 
                  jenis_kelamin TEXT, gol_darah TEXT, riwayat_penyakit TEXT, tanggal_input TEXT, gejala_input TEXT, hasil_diagnosa TEXT)''')
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT)')
    
    # Default Admin: admin / admin123
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("admin", hash_password("admin123"), "Admin"))
    
    # Default Penyakit
    c.execute("SELECT COUNT(*) FROM basis_pengetahuan")
    if c.fetchone()[0] == 0:
        data = [("Maag", "Mual, Perih Lambung, Kembung"), ("Diare", "BAB Cair, Lemas"), ("GERD", "Dada Terbakar, Mulut Pahit")]
        c.executemany("INSERT INTO basis_pengetahuan (nama_penyakit, gejala) VALUES (?, ?)", data)
    conn.commit()
    conn.close()

# --- FUNGSI AMBIL DATA ---
def ambil_basis():
    conn = sqlite3.connect('sistem_pakar.db')
    c = conn.cursor()
    c.execute("SELECT * FROM basis_pengetahuan")
    res = c.fetchall()
    conn.close()
    return res

def ambil_history():
    conn = sqlite3.connect('sistem_pakar.db')
    c = conn.cursor()
    c.execute("SELECT * FROM history_diagnosa ORDER BY id DESC")
    res = c.fetchall()
    conn.close()
    return res

init_db()

# --- 2. NAVIGASI SIDEBAR ---
with st.sidebar:
    st.title("🩺 SISTEM PAKAR")
    menu = st.radio("Navigasi", ["Home", "Mulai Diagnosa", "Riwayat Analisa", "Login Staf"])

# --- 3. HALAMAN HOME ---
if menu == "Home":
    st.header("🏠 Selamat Datang")
    st.image("https://img.freepik.com/free-vector/doctors-concept-illustration_114360-1515.jpg", width=500)
    st.write("Sistem Pakar Diagnosa Penyakit Pencernaan Manusia.")

# --- 4. HALAMAN DIAGNOSA (Field yang tadi hilang sudah kembali di sini) ---
elif menu == "Mulai Diagnosa":
    st.header("📋 Form Diagnosa Mandiri")
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
    
    # Logika Diagnosa
    raw_p = ambil_basis()
    if raw_p:
        data_map = {item[1]: [g.strip() for g in item[2].split(",")] for item in raw_p}
        semua_gejala = sorted(list(set([g for daftar in data_map.values() for g in daftar])))
        
        st.subheader("Pilih Gejala yang Dirasakan:")
        gejala_user = []
        c_gejala = st.columns(3)
        for i, g in enumerate(semua_gejala):
            if c_gejala[i % 3].checkbox(g): gejala_user.append(g)

        if st.button("Proses Analisa"):
            if not nama_p or tb == 0: st.error("Lengkapi data pasien!")
            elif not gejala_user: st.error("Pilih gejala!")
            else:
                # Simpan & Tampilkan Hasil
                hasil = []
                for p_nm, p_gj in data_map.items():
                    match = set(gejala_user).intersection(p_gj)
                    if match:
                        persen = (len(match)/len(p_gj))*100
                        hasil.append(f"{p_nm} ({persen:.0f}%)")
                
                hasil_txt = ", ".join(hasil) if hasil else "Tidak Terdeteksi"
                # Simpan ke DB
                conn = sqlite3.connect('sistem_pakar.db')
                conn.execute("INSERT INTO history_diagnosa (nama_pasien, tgl_lahir, usia, tb, bb, jenis_kelamin, gol_darah, riwayat_penyakit, tanggal_input, gejala_input, hasil_diagnosa) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                             (nama_p, str(tgl_l), usia, tb, bb, jk, goldar, riwayat_p, datetime.now().strftime("%Y-%m-%d %H:%M"), ", ".join(gejala_user), hasil_txt))
                conn.commit()
                conn.close()
                st.success(f"Hasil Analisa: {hasil_txt}")

# --- 5. RIWAYAT ANALISA ---
elif menu == "Riwayat Analisa":
    st.header("📜 Riwayat Diagnosa")
    data = ambil_history()
    if data:
        df = pd.DataFrame(data, columns=["ID", "Nama", "Tgl Lahir", "Usia", "TB", "BB", "Gender", "GolDarah", "Riwayat", "Waktu", "Gejala", "Hasil"])
        st.dataframe(df.drop(columns=["ID"]), use_container_width=True)

# --- 6. LOGIN STAF (Admin & Petugas) ---
elif menu == "Login Staf":
    if 'role' not in st.session_state: st.session_state.role = None
    
    if not st.session_state.role:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            conn = sqlite3.connect('sistem_pakar.db')
            c = conn.cursor()
            c.execute("SELECT role FROM users WHERE username=? AND password=?", (u, hash_password(p)))
            res = c.fetchone()
            if res:
                st.session_state.role = res[0]
                st.session_state.user = u
                st.rerun()
            else: st.error("Gagal Login!")
    else:
        st.title(f"🛠️ Panel {st.session_state.role}")
        
        # Inisialisasi Tab berdasarkan Role
        if st.session_state.role == "Admin":
            t1, t2, t3, t4 = st.tabs(["Basis Pengetahuan", "Riwayat & Export", "Manajemen User", "Akun Saya"])
        else:
            t2, t4 = st.tabs(["Riwayat & Export", "Akun Saya"])
            t1, t3 = None, None

        # --- TAB 1: KELOLA GEJALA (Hanya Admin) ---
        if t1:
            with t1:
                st.subheader("Edit/Hapus Penyakit & Gejala")
                with st.expander("➕ Tambah Penyakit Baru"):
                    n_p = st.text_input("Nama Penyakit Baru")
                    n_g = st.text_area("Gejala (pisahkan dengan koma)")
                    if st.button("Simpan Penyakit"):
                        tambah_penyakit(n_p, n_g) # Pastikan fungsi ini sudah ada di bagian atas script
                        st.success("Berhasil ditambah!")
                        st.rerun()
                
                st.divider()
                for idp, nm, gj in ambil_basis():
                    with st.container(border=True):
                        col_a, col_b = st.columns([3, 1])
                        col_a.write(f"**{nm}**")
                        col_a.caption(f"Gejala: {gj}")
                        
                        if col_b.button("✏️ Edit", key=f"ed_{idp}"):
                            st.session_state[f"edit_mode_{idp}"] = True
                        if col_b.button("🗑️", key=f"del_{idp}"):
                            hapus_penyakit(idp)
                            st.rerun()
                        
                        if st.session_state.get(f"edit_mode_{idp}"):
                            new_nm = st.text_input("Nama", value=nm, key=f"nnm_{idp}")
                            new_gj = st.text_area("Gejala", value=gj, key=f"ngj_{idp}")
                            if st.button("Update", key=f"up_{idp}"):
                                update_penyakit(idp, new_nm, new_gj)
                                st.session_state[f"edit_mode_{idp}"] = False
                                st.rerun()

        # --- TAB 2: RIWAYAT & EXPORT ---
        with t2:
            st.subheader("Data Riwayat Pasien")
            h_data = ambil_history()
            if h_data:
                df_exp = pd.DataFrame(h_data, columns=["ID", "Nama", "Lahir", "Usia", "TB", "BB", "Gender", "GolDar", "Riwayat", "Waktu", "Gejala", "Hasil"])
                st.download_button("📥 Export CSV", df_exp.to_csv(index=False).encode('utf-8'), "riwayat.csv", "text/csv")
                st.dataframe(df_exp.drop(columns=["ID"]))
            else:
                st.info("Belum ada riwayat.")

        # --- TAB 3: MANAJEMEN USER (Hanya Admin) ---
        if t3:
            with t3:
                st.subheader("Tambah User & Role Baru")
                u_new = st.text_input("Username Baru")
                p_new = st.text_input("Password Baru", type="password")
                r_new = st.selectbox("Role", ["Petugas", "Admin"])
                if st.button("Daftarkan User"):
                    if tambah_user(u_new, p_new, r_new):
                        st.success(f"User {u_new} aktif!")
                    else: st.error("Username sudah ada!")

        # --- TAB 4: GANTI PASSWORD (Semua Role) ---
        with t4:
            st.subheader("Ganti Password Akun")
            pw_baru = st.text_input("Password Baru", type="password")
            if st.button("Perbarui Password"):
                ganti_password(st.session_state.user, pw_baru)
                st.success("Password diperbarui!")

        if st.button("Logout"):
            st.session_state.role = None
            st.rerun()
