from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd

def extract_data(**kwargs):
    # Menarik data dari file CSV
    file_path = "/home/abiyasa/airflow/dags/MentalHealthSurvey.csv"
    data = pd.read_csv(file_path)
    # Menghapus spasi ekstra dari nama kolom
    data.columns = data.columns.str.strip()
    
    # Menambahkan kolom student_id dan survey_id menggunakan indeks
    data['student_id'] = data.index + 1  # Membuat ID unik untuk setiap mahasiswa
    data['survey_id'] = data.index + 1  # Membuat ID unik untuk setiap survei (menggunakan indeks)

    # Push the data to XCom
    kwargs['ti'].xcom_push(key='raw_data', value=data)
    return data

def transform_data(**kwargs):
    ti = kwargs['ti']
    # Mengambil data yang telah diekstrak dari XCom
    data = ti.xcom_pull(task_ids='extract_data', key='raw_data')

    # Menyaring dan membersihkan data yang hilang
    data_cleaned = data.dropna()

    # Menambahkan kolom untuk total_stress berdasarkan depression, anxiety, isolation
    data_cleaned['total_stress'] = data_cleaned[['depression', 'anxiety', 'isolation']].sum(axis=1)

    # Menambahkan kategori stress_level berdasarkan total_stress
    data_cleaned['stress_level'] = data_cleaned['total_stress'].apply(
        lambda x: 'high' if x > 12 else ('medium' if x > 6 else 'low')
    )

    # Debug: Memastikan kolom 'stress_level' ada
    print("Kolom setelah transformasi:", data_cleaned.columns)  # Pastikan kolom 'stress_level' ada

    # Menambahkan kategori social_support dan financial concern level
    data_cleaned['social_support'] = data_cleaned['social_relationships'].apply(lambda x: 'good' if x > 3 else 'poor')
    data_cleaned['financial_concern_level'] = data_cleaned['financial_concerns'].apply(
        lambda x: 'high' if x > 3 else ('medium' if x > 2 else 'low')
    )

    # Debugging: Memeriksa apakah kolom 'stress_level' ada
    print("Data setelah transformasi:", data_cleaned.head())  # Lihat beberapa baris pertama data

    # Menambahkan ID unik untuk dimensi lainnya
    demographics = data_cleaned[['student_id', 'gender', 'age', 'university', 'degree_level']].drop_duplicates()
    demographics['demographics_id'] = demographics.index + 1

    mental_health = data_cleaned[['student_id', 'depression', 'anxiety', 'isolation', 'social_relationships']].drop_duplicates()
    mental_health['mental_health_id'] = mental_health.index + 1

    engagement = data_cleaned[['student_id', 'study_satisfaction', 'academic_workload', 'sports_engagement']].drop_duplicates()
    engagement['engagement_id'] = engagement.index + 1

    # Menyiapkan data untuk tabel fakta (MentalHealthAssessmentFact)
    fact_table = data_cleaned[['survey_id', 'student_id', 'depression', 'anxiety', 'isolation', 'study_satisfaction',
                               'academic_workload', 'academic_pressure', 'financial_concerns']]
    fact_table['fact_id'] = fact_table.index + 1  # Membuat ID unik untuk tabel fakta

    # Menggabungkan tabel fakta dan dimensi menjadi satu dataset OLAP
    olap_data = fact_table.merge(demographics, on='student_id', how='left') \
                          .merge(mental_health, on='student_id', how='left') \
                          .merge(engagement, on='student_id', how='left')

    # Mendorong data yang telah diproses ke XCom
    ti.xcom_push(key='transformed_data', value=olap_data)
    return olap_data


def analyze_stress(**kwargs):
    ti = kwargs['ti']
    # Mengambil data yang telah diproses dari XCom
    data = ti.xcom_pull(task_ids='transform_data', key='transformed_data')

    # Periksa apakah kolom 'stress_level' ada
    if 'stress_level' not in data.columns:
        print("Error: Kolom 'stress_level' tidak ditemukan")
        return  # Tangani kesalahan ini lebih baik di sini

    # Melakukan analisis tingkat stres berdasarkan 'stress_level'
    stress_stats = data['stress_level'].value_counts()
    average_stress = data.groupby('stress_level')['total_stress'].mean()

    print("Distribusi Tingkat Stres:")
    print(stress_stats)

    print("\nRata-rata Skor Berdasarkan Tingkat Stres:")
    print(average_stress)

def load_data(**kwargs):
    ti = kwargs['ti']
    # Get the transformed data from XCom
    olap_data = ti.xcom_pull(task_ids='transform_data', key='transformed_data')

    # Menyimpan data yang telah diproses ke dalam OLAP.csv
    olap_data.to_csv("/home/abiyasa/airflow/dags/OLAP.csv", index=False)
    print("Data telah disimpan ke:OLAP.csv")

with DAG(
    'etl_mental_health_stress_analysis',
    description='ETL untuk Data Mental Health Survey dengan Analisis Tingkat Stres',
    schedule='@daily',
    start_date=datetime(2025, 5, 21),
    catchup=False,
) as dag:

    # Menarik data
    extract = PythonOperator(
        task_id='extract_data',
        python_callable=extract_data,
    )

    # Transformasi data
    transform = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data,
    )

    # Analisis tingkat stres
    analyze = PythonOperator(
        task_id='analyze_stress',
        python_callable=analyze_stress,
    )

    # Memuat data ke dalam OLAP.csv
    load = PythonOperator(
        task_id='load_data',
        python_callable=load_data,
    )

    # Menyusun urutan tugas
    extract >> transform >> analyze >> load
