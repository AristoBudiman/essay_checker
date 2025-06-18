import streamlit as st
import re
import itertools
from typing import List

def buat_kamus_dari_kumpulan(kumpulan):
    kamus = {}
    for item in kumpulan:
        kata_input = item["kata"]
        bobot = item["bobot"]
        deskripsi = item["deskripsi"]
        alternatif = [k.strip().lower() for k in kata_input.split('|')]
        kamus[tuple(alternatif)] = {'bobot': bobot, 'deskripsi': deskripsi}
    return kamus

def hitung_relevansi(kunci_dict, jawaban):
    jawaban = jawaban.lower()
    total_bobot = sum(info['bobot'] for info in kunci_dict.values())
    bobot_ditemukan = 0
    for kata_list, info in kunci_dict.items():
        if any(re.search(r'\b' + re.escape(k) + r'\b', jawaban) for k in kata_list):
            bobot_ditemukan += info['bobot']
    return bobot_ditemukan / total_bobot if total_bobot > 0 else 0

def hitung_kelengkapan(kunci_dict, jawaban):
    jawaban = jawaban.lower()
    total_kata_kunci = len(kunci_dict)
    jumlah_ditemukan = 0
    for kata_list in kunci_dict:
        if any(re.search(r'\b' + re.escape(k) + r'\b', jawaban) for k in kata_list):
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
    for kata_list in kunci_dict:
        if any(re.search(r'\b' + re.escape(k) + r'\b', jawaban) for k in kata_list):
            ditemukan.append(' | '.join(kata_list)) 
        else:
            belum.append(' | '.join(kata_list))
    return ditemukan, belum

def buat_feedback(kunci_dict, belum_disebut):
    feedback = []
    for key_str in belum_disebut:
        kata_tuple = tuple(k.strip() for k in key_str.split('|'))
        info = kunci_dict.get(kata_tuple, {'bobot': 0, 'deskripsi': ''})
        if info['bobot'] >= 2:
            feedback.append(f"Kata kunci penting belum disebut: **{key_str}** (bobot {info['bobot']}) - *{info['deskripsi']}*")
        else:
            feedback.append(f"Anda belum menyebutkan **{key_str}** - *{info['deskripsi']}*")
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
            { "kata": "neural | neuron | neurons | ann", "bobot": 10, "deskripsi": "Refers to artificial neural system concepts." },
            { "kata": "network | networks | system | systems", "bobot": 9, "deskripsi": "A network of processing units." },
            { "kata": "learning | learn | learns | learned | train | trains | trained | training", "bobot": 8, "deskripsi": "The process of acquiring knowledge from data or environment." },
            { "kata": "brain | brains", "bobot": 7, "deskripsi": "The biological organ that inspires artificial neural networks." },
            { "kata": "synaptic | synapse | synapses", "bobot": 6, "deskripsi": "Related to the connections between neurons." },
            { "kata": "weights | weight | weighted", "bobot": 6, "deskripsi": "Numerical values that affect output results." },
            { "kata": "knowledge | knowledges", "bobot": 7, "deskripsi": "Information or experience stored in the network." },
            { "kata": "processor | processors", "bobot": 7, "deskripsi": "The unit that processes information within the network." },
            { "kata": "parallel | parallels", "bobot": 6, "deskripsi": "Simultaneous processing across multiple units." },
            { "kata": "units | unit", "bobot": 7, "deskripsi": "Basic elements in the network that perform simple processing." },
            { "kata": "acquire | acquires | acquired | acquiring | obtain | obtains | obtained", "bobot": 6, "deskripsi": "The act of the network gaining data from the environment." },
            { "kata": "store | stores | stored | storing", "bobot": 6, "deskripsi": "The ability to retain knowledge." },
            { "kata": "connection | connections", "bobot": 5, "deskripsi": "Links between units enabling data flow." }
        ]

    kata_kunci_baru = []

    for i, item in enumerate(st.session_state.kata_kunci_list):
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"**Kata Kunci #{i+1}**")
            kata = st.text_input(f"Kata #{i+1} (gunakan `|` untuk sinonim)", item["kata"], key=f"kata_{i}")
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

    kumpulan_kata_kunci = [
        {"kata": k, "bobot": b, "deskripsi": d}
        for k, b, d in kata_kunci_baru
    ]

kunci_jawaban = st.text_area("Kunci Jawaban", value="A neural network is a massively parallel distributed processor which is made up of simple processing units. It has a natural propensity for storing experiential knowledge. Neural networks resemble the brain in two aspects; knowledge is acquired by the network from its environment through a learning process, interneuron connection strength known as synaptic weights are used to store the acquired knowledge.")
jawaban_mahasiswa = st.text_area("Jawaban Mahasiswa", value="Artificial neural network is a massively parrallal distributed processor made up of simple processing units which has a natural propensity to acquire knowledge from the environment and make it available for future use. It resembels the human brain in following ways. 1. Both of them acquire knowledge from the environment. 2. The neurons are connected by synapses cahrecterized by their weights which can be adjusted.")

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