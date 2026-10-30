import streamlit as st
import re

# -----------------------------------------------------------------------------
# CONFIG & PAGE TITLE
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Sistem Pengajuan & Auto-Review Judul MP/MPI",
    page_icon="🎓",
    layout="wide"
)

# Initialize Session State
if "database_proposals" not in st.session_state:
    st.session_state.database_proposals = [
        {
            "id": 1,
            "nama": "Siti Nurhaliza",
            "nim": "210101001",
            "prodi": "MPI",
            "jenjang": "S1 Skripsi",
            "rumpun": "Manajemen Pesantren & Madrasah",
            "judul": "Strategi Kepemimpinan Kyai Dalam Meningkatkan Mutu Pendidikan Di Pesantren X",
            "lokus": "Pesantren X",
            "metode": "Kualitatif",
            "rumusan": "1. Bagaimana perencanaan mutu? 2. Bagaimana pelaksanaan?",
            "integrasi": "QS. An-Nisa: 58 tentang Amanah",
            "status": "APPROVED",
            "score": 88,
            "notes": "Judul relevan dan metodologi jelas."
        }
    ]

# -----------------------------------------------------------------------------
# ENGINE & ALGORITMA SIMILARITY TANPA SCIKIT-LEARN (BUILT-IN PYTHON)
# -----------------------------------------------------------------------------
STOPWORDS_ID = set([
    'pengaruh', 'hubungan', 'analisis', 'strategi', 'efektivitas', 'studi', 
    'kasus', 'terhadap', 'dalam', 'di', 'ke', 'dari', 'yang', 'pada', 'dan', 
    'untuk', 'dengan', 'tingkat', 'upaya', 'peningkatan', 'pelaksanaan'
])

def preprocess_words(text: str) -> set:
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    words = text.split()
    return set([w for w in words if w not in STOPWORDS_ID])

def check_similarity(new_title: str, existing_proposals: list):
    if not existing_proposals:
        return 0.0, ""
    
    new_words = preprocess_words(new_title)
    if not new_words:
        return 0.0, ""
        
    max_score = 0.0
    matched_title = ""
    
    for p in existing_proposals:
        db_words = preprocess_words(p["judul"])
        if not db_words:
            continue
            
        intersection = new_words.intersection(db_words)
        union = new_words.union(db_words)
        
        jaccard_score = (len(intersection) / len(union)) * 100 if union else 0
        
        if jaccard_score > max_score:
            max_score = jaccard_score
            matched_title = p["judul"]
            
    return round(max_score, 2), matched_title

def generate_auto_review(title: str, prodi: str, method: str, lokus: str, rumusan: str, integrasi: str, sim_score: float):
    notes = []
    score = 100
    
    # 1. Evaluasi Similarity
    if sim_score > 60:
        score -= 30
        notes.append(f"⚠️ **Kemiripan Tinggi ({sim_score}%)**: Judul terlalu mirip dengan arsip terdahulu.")
    elif sim_score > 30:
        score -= 10
        notes.append(f"ℹ️ **Kemiripan Sedang ({sim_score}%)**: Ada potensi irisan topik.")
    else:
        notes.append("✅ **Orisinalitas Baik**: Kemiripan dengan database di bawah 30%.")
        
    # 2. Evaluasi Kata Kunci MP/MPI
    keywords_mp = ['manajemen', 'kepemimpinan', 'mutu', 'strategi', 'evaluasi', 'sdm', 'kurikulum', 'organisasi', 'kinerja']
    if not any(kw in title.lower() for kw in keywords_mp):
        score -= 15
        notes.append("⚠️ **Substansi**: Judul belum memuat variabel manajerial yang tegas (misal: Kepemimpinan, Mutu, SDM, Strategi).")
    else:
        notes.append("✅ **Rumpun Kajian**: Sesuai dengan bidang Manajemen Pendidikan.")
        
    # 3. Evaluasi Integrasi Keislaman (MPI)
    if prodi == "MPI":
        if not integrasi or len(integrasi.strip()) < 5:
            score -= 15
            notes.append("⚠️ **Integrasi MPI**: Landasan nilai Al-Qur'an/Hadis/Kaidah Fiqhiyah belum diisi.")
        else:
            notes.append("✅ **Integrasi MPI**: Rujukan nilai keislaman telah dicantumkan.")
            
    # 4. Rekomendasi Status
    if score >= 80:
        rec_status = "RECOMMENDED_ACC"
        rec_label = "LAYAK ACC"
    elif score >= 60:
        rec_status = "RECOMMENDED_REVISION"
        rec_label = "PERLU REVISI"
    else:
        rec_status = "RECOMMENDED_REJECT"
        rec_label = "DIREKOMENDASIKAN TOLAK"
        
    # 5. Generator 3 Opsi Judul Alternatif
    clean_core = " ".join(preprocess_words(title)).title()
    suggested_options = [
        f"Strategi Transformasi Digital {clean_core} Dalam Penjaminan Mutu Lembaga (Pendekatan {method})",
        f"Internalisasi Nilai-Nilai Kepemimpinan Prophetic Dalam {clean_core} di {lokus}",
        f"Pengaruh {clean_core} dan Budaya Organisasi Terhadap Efektivitas Kerja Pengajar di {lokus}"
    ]
    
    return {
        "score": max(score, 0),
        "rec_status": rec_status,
        "rec_label": rec_label,
        "notes": notes,
        "suggested_options": suggested_options
    }

# -----------------------------------------------------------------------------
# USER INTERFACE (STREAMLIT TABS)
# -----------------------------------------------------------------------------
st.title("🎓 Sistem Pengajuan & Auto-Review Judul MP/MPI")
st.caption("Asisten Smart Reviewer Akademik Kaprodi Manajemen Pendidikan / Manajemen Pendidikan Islam")

tab_mahasiswa, tab_kaprodi, tab_db = st.tabs([
    "📝 Form Pengajuan (Mahasiswa)", 
    "👨‍💼 Dashboard Review (Kaprodi)", 
    "📚 Database Judul Terdaftar"
])

# -----------------------------------------------------------------------------
# TAB 1: MAHASISWA
# -----------------------------------------------------------------------------
with tab_mahasiswa:
    st.header("Formulir Pengajuan Judul Skripsi / Tesis")
    
    with st.form("form_pengajuan"):
        col1, col2 = st.columns(2)
        with col1:
            nama = st.text_input("Nama Lengkap Mahasiswa", value="Ahmad Fulan")
            nim = st.text_input("NIM / ID Mahasiswa", value="210101234")
            prodi = st.selectbox("Program Studi", ["MPI (Manajemen Pendidikan Islam)", "MP (Manajemen Pendidikan)"])
            jenjang = st.radio("Jenjang Program", ["S1 Skripsi", "S2 Tesis"])
        
        with col2:
            rumpun = st.selectbox("Rumpun / Scope Kajian", [
                "Manajemen Pesantren & Madrasah",
                "Manajemen SDM & Kepemimpinan Pendidikan",
                "Manajemen Kurikulum & Pembelajaran",
                "Manajemen Mutu & Akreditasi",
                "Manajemen Keuangan & Sarpras Lembaga Islam"
            ])
            metode = st.selectbox("Metode Penelitian", ["Kualitatif", "Kuantitatif", "Mixed Methods", "R&D"])
            lokus = st.text_input("Lokasi / Lokus Penelitian", value="MAN 1 Surabaya")

        judul = st.text_area("Usulan Judul Skripsi / Tesis", value="Strategi Kepemimpinan Kyai Dalam Meningkatkan Mutu Pendidikan", height=70)
        rumusan = st.text_area("Rumusan Masalah Utama", value="1. Bagaimana perencanaan mutu?\n2. Bagaimana evaluasi kepemimpinan?", height=80)
        
        integrasi = ""
        if "MPI" in prodi:
            integrasi = st.text_input("Integrasi Nilai Keislaman (Khusus MPI: Ayat/Hadis/Kaidah Fiqhiyah)", value="QS. An-Nisa: 58 tentang Amanah Manajerial")

        submitted = st.form_submit_button("🚀 Submit Pengajuan Judul")

    if submitted:
        prodi_code = "MPI" if "MPI" in prodi else "MP"
        
        sim_score, matched_title = check_similarity(judul, st.session_state.database_proposals)
        review_res = generate_auto_review(judul, prodi_code, metode, lokus, rumusan, integrasi, sim_score)
        
        new_entry = {
            "id": len(st.session_state.database_proposals) + 1,
            "nama": nama,
            "nim": nim,
            "prodi": prodi_code,
            "jenjang": jenjang,
            "rumpun": rumpun,
            "judul": judul,
            "lokus": lokus,
            "metode": metode,
            "rumusan": rumusan,
            "integrasi": integrasi,
            "status": "PENDING_REVIEW",
            "sim_score": sim_score,
            "matched_title": matched_title,
            "auto_review": review_res,
            "score": review_res["score"],
            "notes": ""
        }
        st.session_state.database_proposals.append(new_entry)
        st.success("✅ Pengajuan berhasil dikirim! Selanjutnya akan dievaluasi oleh sistem dan Kaprodi.")

# -----------------------------------------------------------------------------
# TAB 2: KAPRODI
# -----------------------------------------------------------------------------
with tab_kaprodi:
    st.header("Dashboard Asisten Review Kaprodi")
    
    pending_list = [p for p in st.session_state.database_proposals if p.get("status") == "PENDING_REVIEW"]
    
    if not pending_list:
        st.info("🎉 Belum ada pengajuan baru yang membutuhkan review saat ini.")
    else:
        st.subheader(f"Terdapat {len(pending_list)} Pengajuan Menunggu Keputusan")
        
        for item in pending_list:
            with st.expander(f"📌 [{item['jenjang']} - {item['prodi']}] {item['nama']} ({item['nim']}) - Skor AI: {item['score']}/100", expanded=True):
                c1, c2 = st.columns([2, 1])
                
                with c1:
                    st.markdown(f"**Judul Diusulkan:**\n> {item['judul']}")
                    st.write(f"**Rumpun:** {item['rumpun']} | **Metode:** {item['metode']} | **Lokus:** {item['lokus']}")
                    st.write(f"**Rumusan Masalah:**\n{item['rumusan']}")
                    if item['integrasi']:
                        st.write(f"**Integrasi Keislaman:** {item['integrasi']}")
                        
                with c2:
                    st.metric(label="Skor Kelayakan AI", value=f"{item['score']} / 100", delta=item['auto_review']['rec_label'])
                    st.markdown("**Hasil Evaluasi Otomatis Aplikasi:**")
                    for note in item['auto_review']['notes']:
                        st.write(note)

                st.divider()
                st.subheader("💡 Saran Pilihan Judul Alternatif (Auto-Generated):")
                selected_option = st.radio(
                    "Pilih salah satu judul alternatif untuk disarankannya ke mahasiswa (opsional):",
                    ["Gunakan Judul Asli Mahasiswa"] + item['auto_review']['suggested_options'],
                    key=f"opt_{item['id']}"
                )

                st.divider()
                catatan_kaprodi = st.text_area("Catatan Tambahan Kaprodi untuk Mahasiswa:", value="Judul sudah bagus, silakan perbaiki bagian yang tercantum pada catatan evaluasi.", key=f"notes_{item['id']}")
                
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                
                final_title = item['judul'] if selected_option == "Gunakan Judul Asli Mahasiswa" else selected_option
                
                if col_btn1.button("✅ ACC / Setujui Judul", key=f"acc_{item['id']}"):
                    item['status'] = "APPROVED"
                    item['judul'] = final_title
                    item['notes'] = catatan_kaprodi
                    st.success(f"Judul '{final_title}' BERHASIL DI-ACC!")
                    st.rerun()
                    
                if col_btn2.button("⚠️ Minta Revisi Judul", key=f"rev_{item['id']}"):
                    item['status'] = "REVISION_REQUIRED"
                    item['judul'] = final_title
                    item['notes'] = catatan_kaprodi
                    st.warning("Status diperbarui: MINTA REVISI")
                    st.rerun()
                    
                if col_btn3.button("❌ Tolak Pengajuan", key=f"rej_{item['id']}"):
                    item['status'] = "REJECTED"
                    item['notes'] = catatan_kaprodi
                    st.error("Pengajuan DITOLAK.")
                    st.rerun()

# -----------------------------------------------------------------------------
# TAB 3: DATABASE JUDUL
# -----------------------------------------------------------------------------
with tab_db:
    st.header("Bank Data Judul Skripsi & Tesis")
    st.dataframe(st.session_state.database_proposals, use_container_width=True)