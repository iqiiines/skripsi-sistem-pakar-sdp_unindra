import streamlit as st
import sqlite3
from datetime import datetime, date
import pandas as pd

# --- 1. FUNGSI DATABASE ---
def init_db():
    conn = sqlite3.connect('sistem_pakar.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS basis_pengetahuan 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nama_penyakit TEXT, gejala TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS history_diagnosa 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  nama_pasien TEXT, tgl_lahir TEXT, usia INTEGER, tb INTEGER, bb INTEGER, 
                  jenis_kelamin TEXT, gol_darah TEXT, riwayat_penyakit TEXT, 
                  tanggal_input TEXT, gejala_input TEXT, hasil_diagnosa TEXT)''')
    
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

# --- FUNGSI CRUD & UTILITAS ---
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

def update_penyakit(id_p, nama, gejala):
    conn = sqlite3.connect('sistem_pakar.db')
    c = conn.cursor()
    c.execute("UPDATE basis_pengetahuan SET nama_penyakit=?, gejala=? WHERE id=?", (nama, gejala, id_p))
    conn.commit()
    conn.close()

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

init_db()

# --- 2. UI SIDEBAR ---
with st.sidebar:
    st.title("🩺 SISTEM PAKAR")
    menu = st.radio("Menu Utama", ["Home", "Mulai Diagnosa", "Riwayat Analisa", "Login Admin"])

# --- 3. HALAMAN DIAGNOSA ---
if menu == "Home":
    st.header("🏠 Selamat Datang")
    st.image("https://img.freepik.com/free-vector/doctors-concept-illustration_114360-1515.jpg", width=500)
    st.write("Sistem Pakar Diagnosa Penyakit Pencernaan.")

elif menu == "Mulai Diagnosa":
    st.header("📋 Form Diagnosa")
    # (Kode form diagnosa sama seperti sebelumnya...)
    st.info("Silakan isi biodata dan pilih gejala.")

elif menu == "Riwayat Analisa":
    st.header("📜 Riwayat Diagnosa")
    h_data = ambil_history()
    if h_data:
        df = pd.DataFrame(h_data, columns=["ID", "Nama", "Tgl Lahir", "Usia", "TB", "BB", "Gender", "GolDarah", "Riwayat", "Waktu", "Gejala", "Hasil"])
        st.dataframe(df.drop(columns=["ID"]), use_container_width=True)
    else:
        st.info("Riwayat masih kosong.")

# --- 4. PANEL ADMIN (UPDATE FITUR EDIT & EXPORT) ---
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
        t1, t2 = st.tabs(["Manajemen Basis Pengetahuan", "Manajemen Riwayat & Export"])
        
        with t1:
            st.subheader("Edit/Hapus Penyakit & Gejala")
            with st.expander("➕ Tambah Penyakit Baru"):
                n_p = st.text_input("Nama Penyakit Baru")
                n_g = st.text_area("Daftar Gejala (pisahkan dengan koma)")
                if st.button("Simpan Penyakit"):
                    tambah_penyakit(n_p, n_g)
                    st.success("Data berhasil ditambah!")
                    st.rerun()
            
            st.divider()
            # List data untuk Edit
            for idp, nm, gj in ambil_basis_pengetahuan():
                with st.container(border=True):
                    col_text, col_btn = st.columns([3, 1])
                    col_text.write(f"**{nm}**")
                    col_text.caption(f"Gejala: {gj}")
                    
                    if col_btn.button("✏️ Edit Gejala", key=f"edit_btn_{idp}"):
                        st.session_state[f"mode_edit_{idp}"] = True
                    
                    if col_btn.button("🗑️ Hapus", key=f"del_p_{idp}"):
                        hapus_penyakit(idp)
                        st.rerun()
                    
                    # Form Edit yang muncul jika tombol edit ditekan
                    if st.session_state.get(f"mode_edit_{idp}"):
                        new_nm = st.text_input("Nama Penyakit", value=nm, key=f"in_nm_{idp}")
                        new_gj = st.text_area("Daftar Gejala", value=gj, key=f"in_gj_{idp}")
                        c1, c2 = st.columns(2)
                        if c1.button("Update Data", key=f"save_upd_{idp}"):
                            update_penyakit(idp, new_nm, new_gj)
                            st.session_state[f"mode_edit_{idp}"] = False
                            st.rerun()
                        if c2.button("Batal", key=f"cancel_{idp}"):
                            st.session_state[f"mode_edit_{idp}"] = False
                            st.rerun()

        with t2:
            st.subheader("Data Riwayat Analisa")
            h_data = ambil_history()
            if h_data:
                df_export = pd.DataFrame(h_data, columns=["ID", "Nama Pasien", "Tgl Lahir", "Usia", "TB", "BB", "Gender", "Gol Darah", "Riwayat Penyakit", "Waktu Input", "Gejala Input", "Hasil Diagnosa"])
                
                # Fitur EXPORT ke CSV
                csv = df_export.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Export Riwayat ke CSV/Excel",
                    data=csv,
                    file_name=f'riwayat_sistem_pakar_{datetime.now().strftime("%Y%m%d")}.csv',
                    mime='text/csv',
                )
                
                st.divider()
                # List Riwayat untuk dihapus jika perlu
                for h in h_data:
                    c_a, c_b = st.columns([4, 1])
                    c_a.write(f"**{h[1]}** ({h[9]}) - Hasil: {h[11]}")
                    if c_b.button("Hapus Record", key=f"h_del_{h[0]}"):
                        hapus_history(h[0])
                        st.rerun()
            else:
                st.info("Belum ada data untuk di-export.")
        
        st.divider()
        if st.button("Keluar (Logout)"):
            st.session_state.auth = False
            st.rerun()
