import streamlit as st
import re
import itertools
from typing import List

def buat_kamus_dari_kumpulan(kumpulan):
    return {kata.lower(): {'bobot': bobot, 'deskripsi': deskripsi} for kata, bobot, deskripsi in kumpulan}

def hitung_relevansi(kunci_dict, jawaban):
    jawaban = jawaban.lower()
    total_bobot = sum(item['bobot'] for item in kunci_dict.values())
    bobot_ditemukan = 0
    for kata, info in kunci_dict.items():
        pattern = r'\b' + re.escape(kata) + r'\b'
        if re.search(pattern, jawaban):
            bobot_ditemukan += info['bobot']
    return bobot_ditemukan / total_bobot if total_bobot > 0 else 0

def hitung_kelengkapan(kunci_dict, jawaban):
    jawaban = jawaban.lower()
    total_kata_kunci = len(kunci_dict)
    jumlah_ditemukan = 0
    for kata in kunci_dict:
        pattern = r'\b' + re.escape(kata) + r'\b'
        if re.search(pattern, jawaban):
            jumlah_ditemukan += 1
    return jumlah_ditemukan / total_kata_kunci if total_kata_kunci > 0 else 0

def hitung_argumen(jawaban_mahasiswa, kunci_jawaban):
    jumlah_kata_jawaban = len(jawaban_mahasiswa.strip().split())
    jumlah_kata_kunci_jawaban = len(kunci_jawaban.strip().split())
    if jumlah_kata_kunci_jawaban == 0:
        return 0
    rasio = jumlah_kata_jawaban / jumlah_kata_kunci_jawaban
    return rasio

def cek_kata_kunci_ditemukan(kunci_dict, jawaban):
    jawaban = jawaban.lower()
    ditemukan = []
    belum = []
    for kata in kunci_dict:
        pattern = r'\b' + re.escape(kata) + r'\b'
        if re.search(pattern, jawaban):
            ditemukan.append(kata)
        else:
            belum.append(kata)
    return ditemukan, belum

def buat_feedback(kunci_dict, belum_disebut):
    feedback = []
    for kata in belum_disebut:
        info = kunci_dict.get(kata, {'bobot': 0, 'deskripsi': ''})
        if info['bobot'] >= 2:
            feedback.append(f"Kata kunci penting belum disebut: **{kata}** (bobot {info['bobot']}) - *{info['deskripsi']}*")
        else:
            feedback.append(f"Anda belum menyebutkan **{kata}** - *{info['deskripsi']}*")
    if not feedback:
        feedback.append("Semua kata kunci telah disebut. Jawaban sangat lengkap.")
    return feedback

def miu_rendah(x):
    if x <= 0.2:
        return 1
    elif 0.2 < x <= 0.5:
        return (0.5 - x) / 0.3
    else:
        return 0

def miu_sedang(x):
    if 0.2 < x <= 0.5:
        return (x - 0.2) / 0.3
    elif 0.5 < x <= 0.8:
        return (0.8 - x) / 0.3
    elif x == 0.5:
        return 1
    else:
        return 0

def miu_tinggi(x):
    if x <= 0.5:
        return 0
    elif 0.5 < x <= 0.8:
        return (x - 0.5) / 0.3
    elif x > 0.8:
        return 1

def hitung_miu_rules(r, k, a):
    r_mius = [miu_rendah(r), miu_sedang(r), miu_tinggi(r)]
    k_mius = [miu_rendah(k), miu_sedang(k), miu_tinggi(k)]
    a_mius = [miu_rendah(a), miu_sedang(a), miu_tinggi(a)]
    miu_rules = []
    for mr, mk, ma in itertools.product(r_mius, k_mius, a_mius):
        miu_rules.append(min(mr, mk, ma))
    return miu_rules

def hitung_nilai_rules():
    r_values = [0.1, 0.5, 1]
    k_values = [0.1, 0.5, 1]
    a_values = [0.1, 0.5, 1]
    nilai_rules = []
    for r, k, a in itertools.product(r_values, k_values, a_values):
        nilai = 100 * (0.4 * r + 0.3 * k + 0.3 * a)
        nilai_rules.append(nilai)
    return nilai_rules

def defuzzifikasi_average(miu_rules, nilai_rules):
    total_miu = sum(miu_rules)
    if total_miu == 0:
        return 0
    hasil = sum(m * n for m, n in zip(miu_rules, nilai_rules)) / total_miu
    return hasil

def sistem_fuzzy(r, k, a):
    miu_rules = hitung_miu_rules(r, k, a)
    nilai_rules = hitung_nilai_rules()
    hasil_akhir = defuzzifikasi_average(miu_rules, nilai_rules)
    return hasil_akhir

# Streamlit Ui
st.title("Penilai Esai Mahasiswa (Fuzzy)")

with st.expander("Input Kata Kunci"):
    st.markdown("Masukkan kata kunci satu per satu di bawah ini:")

    if "kata_kunci_list" not in st.session_state:
        st.session_state.kata_kunci_list = [
            { "kata": "metode",     "bobot": 8, "deskripsi": "Merujuk pada cara atau teknik yang digunakan dalam akses media." },
            { "kata": "akses",      "bobot": 7, "deskripsi": "Menunjukkan proses menghubungkan atau menggunakan jaringan." },
            { "kata": "media",      "bobot": 6, "deskripsi": "Sarana fisik atau logis untuk transmisi data." },
            { "kata": "jaringan",   "bobot": 5, "deskripsi": "Kumpulan perangkat yang saling terhubung untuk komunikasi data." },
            { "kata": "berbagi",    "bobot": 4, "deskripsi": "Menunjukkan bahwa beberapa host menggunakan sumber daya bersama." },
            { "kata": "bandwidth",  "bobot": 3, "deskripsi": "Kapasitas maksimum transfer data dalam jaringan." },
            { "kata": "sama",       "bobot": 2, "deskripsi": "Mengindikasikan kesetaraan penggunaan oleh semua host." },
            { "kata": "link",       "bobot": 1, "deskripsi": "Sambungan fisik atau logis antar perangkat dalam jaringan." }
        ]

    kata_kunci_baru = []

    for i, item in enumerate(st.session_state.kata_kunci_list):
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"**Kata Kunci #{i+1}**")
            kata = st.text_input(f"Kata #{i+1}", item["kata"], key=f"kata_{i}")
            bobot = st.number_input(f"Bobot #{i+1}", min_value=1, max_value=10, value=item["bobot"], key=f"bobot_{i}")
            deskripsi = st.text_input(f"Deskripsi #{i+1}", item["deskripsi"], key=f"desk_{i}")
            kata_kunci_baru.append((kata.strip(), int(bobot), deskripsi.strip()))
        with col2:
            if st.button("Hapus", key=f"hapus_{i}"):
                st.session_state.kata_kunci_list.pop(i)
                st.rerun()
        st.markdown("---")


    if st.button("Tambah Kata Kunci"):
        st.session_state.kata_kunci_list.append({"kata": "", "bobot": 1, "deskripsi": ""})
        st.rerun()

    kumpulan_kata_kunci = kata_kunci_baru

kunci_jawaban = st.text_area("Kunci Jawaban", value="Ethernet adalah sebuah metode akses media jaringan di mana semua host di jaringan tersebut berbagi bandwitdh yang sama dari sebuah link.")
jawaban_mahasiswa = st.text_area("Jawaban Mahasiswa", value="Ethernet adalah sebuah interfaces atau sebuah jenis pengkabelan dan pemprosesan sinyal untuk data jaringan.")

if st.button("Proses Penilaian"):
    kunci_dict = buat_kamus_dari_kumpulan(kumpulan_kata_kunci)
    relevansi = hitung_relevansi(kunci_dict, jawaban_mahasiswa)
    kelengkapan = hitung_kelengkapan(kunci_dict, jawaban_mahasiswa)
    rasio_argumen = hitung_argumen(jawaban_mahasiswa, kunci_jawaban)
    ditemukan, belum_disebut = cek_kata_kunci_ditemukan(kunci_dict, jawaban_mahasiswa)
    feedback = buat_feedback(kunci_dict, belum_disebut)
    skor_akhir = sistem_fuzzy(relevansi, kelengkapan, rasio_argumen)

    st.subheader("Ringkasan Input")
    
    st.markdown("**Kata Kunci & Bobot:**")
    for kata, info in kunci_dict.items():
        st.markdown(f"- **{kata}** (Bobot: {info['bobot']}) - *{info['deskripsi']}*")

    st.markdown("**Kunci Jawaban:**")
    st.info(kunci_jawaban)

    st.markdown("**Jawaban Mahasiswa:**")
    st.warning(jawaban_mahasiswa)

    st.subheader("Hasil Analisis:")
    st.write(f"**Relevansi:** {relevansi:.2f}")
    st.write(f"**Kelengkapan:** {kelengkapan:.2f}")
    st.write(f"**Argumen:** {rasio_argumen:.2f}")
    st.write(f"**Skor Akhir (Fuzzy):** {skor_akhir:.2f}")

    st.subheader("Feedback:")
    for f in feedback:
        st.markdown(f"- {f}")