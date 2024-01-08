import streamlit as st
import numpy as np
import pandas as pd

if 'clicked' not in st.session_state:
    st.session_state.clicked = False

L = np.array(['benefit', 'benefit', 'benefit', 'cost', 'benefit'])

W = np.array([0.3, 0.2, 0.2, 0.15, 0.15])


def click_button():
    st.session_state.clicked = True

def sample_norm(values, label):
    if not values.shape[0] == label.shape[0]:
        st.write('Jumlah kriteria dan label tidak sama')
        return

    norm_value = []
    norm_all = []

    for i in range(values.shape[0]):
        # Mengonversi nilai ke tipe data numerik
        numeric_values = values[i].astype(float)

        if np.max(numeric_values) == np.min(numeric_values):
            st.write(f'Nilai kriteria untuk alternatif {i + 1} tidak dapat dinormalisasi karena semua nilainya sama.')
            return

        if label[i] == 'benefit':
            for j in range(numeric_values.shape[0]):
                norm_c = (numeric_values[j] - np.min(numeric_values)) / (np.max(numeric_values) - np.min(numeric_values))
                norm_value.append(norm_c)
        elif label[i] == 'cost':
            for j in range(numeric_values.shape[0]):
                norm_c = (np.max(numeric_values) - numeric_values[j]) / (np.max(numeric_values) - np.min(numeric_values))
                norm_value.append(norm_c)

        norm_all.append(norm_value)
        norm_value = []

    return np.array(norm_all)

def calculate_topsis(values, weight):
    if not values.shape[0] == weight.shape[0]:
        print('Jumlah kriteria dan bobot tidak sama')
        return

    alt_crit_value = []
    all_value = []
    positive_ideal = []
    negative_ideal = []

    values = np.transpose(values)

    for i in range(values.shape[0]):
        for j in range(values[i].shape[0]):
            val = values[i][j] * weight[j]
            alt_crit_value.append(val)

        all_value.append(alt_crit_value)
        alt_crit_value = []
# menghitung nilai batas min dan min setiap alternativ
        positive_ideal.append(np.max(all_value[i]))
        negative_ideal.append(np.min(all_value[i]))

    positive_ideal = np.array(positive_ideal)
    negative_ideal = np.array(negative_ideal)
#hitung jarak alternatif 
    s_positive = np.sqrt(np.sum((np.array(all_value) - positive_ideal.reshape(1, -1))**2, axis=1))
    s_negative = np.sqrt(np.sum((np.array(all_value) - negative_ideal.reshape(1, -1))**2, axis=1))

    closeness = s_negative / (s_positive + s_negative)

    return closeness

def ranking(vector):
    temp = vector.argsort()
    ranks = np.empty_like(temp)
    ranks[temp] = np.arange(len(vector))

    return len(vector) - ranks

def run():
    st.set_page_config(
        page_title="Implementasi TOPSIS UAS",
        page_icon="🏆",
    )

    st.write("# Implementasi Metode TOPSIS")
    st.write("Dibuat oleh Andri untuk tugas UAS")

    st.markdown(
        """
        Metode TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution) adalah metode pemilihan alternatif dalam pengambilan keputusan multi-kriteria yang mempertimbangkan kedekatan relatif suatu alternatif terhadap solusi ideal positif dan negatif.

        Kriteria seleksi yang dipertimbangkan untuk memilih club terbaik adalah sebagai berikut:

        - Jumlah Kemenangan (C1), contoh: 10 pertandingan 
        - Jumlah Kekalahan (C2), contoh: 6 pertandingan kalah 
        - Jumlah Draw (C3), contoh: 4 pertandingan seri
        - Uang Keluar (C4), rentang: 1 (nilai terkecil) hingga 4 (nilai terbesar), semakin rendah semakin baik
        - Jumlah Pemain Bintang (C5), rentang: 0 (nilai terkecil) hingga 10 (nilai terbesar)
    """
    )

    st.divider()

    st.write("## Input Informasi Klub dan Nilai Kriteria")

    nama_club = st.text_input("Nama Klub")
    c1 = st.number_input("Jumlah Kemenangan (C1)", min_value=0, value=0)
    c2 = st.number_input("Jumlah Kekalahan (C2)", min_value=0, value=0)
    c3 = st.number_input("Jumlah Draw (C3)", min_value=0, value=0)
    c4 = st.slider("Uang Keluar (C4)", min_value=1, max_value=4, step=1, value=1)
    c5 = st.slider("Jumlah Pemain Bintang (C5)", min_value=0, max_value=10, step=1, value=0)

    if st.button("Simpan", type='primary', on_click=click_button):
        simpanData(nama_club, c1, c2, c3, c4, c5)

    if st.session_state.clicked:
        data = st.session_state.nilai_kriteria
        df = pd.DataFrame(data, columns=('Nama Klub', 'C1', 'C2', 'C3', 'C4', 'C5'))
        st.dataframe(df)

        if st.button("Proses"):
            prosesData()


def simpanData(nama_club, c1, c2, c3, c4, c5):
    if 'nilai_kriteria' not in st.session_state:
        st.session_state.nilai_kriteria = np.array([[nama_club, c1, c2, c3, c4, c5]])
    else:
        dataLama = st.session_state.nilai_kriteria
        dataBaru = np.append(dataLama, [[nama_club, c1, c2, c3, c4, c5]], axis=0)
        st.session_state.nilai_kriteria = dataBaru

def prosesData():
    data_kriteria = st.session_state.nilai_kriteria
    nama_club = data_kriteria[:, 0]  # Ambil kolom Nama Klub
    A = data_kriteria[:, 1:]

    norm_a = sample_norm(A, L)
    topsis_result = calculate_topsis(norm_a, W)
    rank = ranking(np.asarray(topsis_result))

    st.write("Nilai alternatif:")
    df_alternatif = pd.DataFrame(A, columns=('C1', 'C2', 'C3', 'C4', 'C5'), index=nama_club)
    st.dataframe(df_alternatif)

    st.write("Normalisasi nilai alternatif:")
    df_norm = pd.DataFrame(norm_a, columns=('C1', 'C2', 'C3', 'C4', 'C5'), index=nama_club)
    st.dataframe(df_norm)

    st.write("Perhitungan nilai TOPSIS:")
    df_topsis_result = pd.DataFrame({'Nama Klub': nama_club, 'TOPSIS Value': topsis_result})
    st.dataframe(df_topsis_result)

    st.write("Perankingan:")
    df_rank = pd.DataFrame({'Nama Klub': nama_club, 'Ranking': rank + 0})  # +1 karena indeks dimulai dari 0
    st.dataframe(df_rank)


if __name__ == "__main__":
    run()
