import os
from django.conf import settings  # Tambahkan import settings
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from django.shortcuts import render
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import MentalHealthAssessmentFact, MentalHealthDimension, DemographicsDimension

def load_data():
    # Menentukan path untuk mengakses OLAP.csv
    olap_file_path = '/home/abiyasa/airflow/dags/OLAP.csv'  # Sesuaikan dengan path file yang benar
    olap_data = pd.read_csv(olap_file_path)

    # Menyimpan data ke dalam database
    for index, row in olap_data.iterrows():
        # Simpan data ke tabel MentalHealthAssessmentFact
        MentalHealthAssessmentFact.objects.create(
            survey_id=row['survey_id'],
            student_id=row['student_id'],
            mental_health_id=row['mental_health_id'],
            study_satisfaction=row['study_satisfaction_x'],
            academic_workload=row['academic_workload_x'],
            academic_pressure=row['academic_pressure'],
            financial_concerns=row['financial_concerns']
        )

        # Menghindari duplikasi data dengan memeriksa apakah `mental_health_id` sudah ada
        if not MentalHealthDimension.objects.filter(mental_health_id=row['mental_health_id']).exists():
            # Simpan data ke tabel MentalHealthDimension
            MentalHealthDimension.objects.create(
                mental_health_id=row['mental_health_id'],
                depression_level=row['depression_y'],
                anxiety_level=row['anxiety_y'],
                isolation_level=row['isolation_y'],
                social_relationships_level=row['social_relationships']
            )

        # Menghindari duplikasi data dengan memeriksa apakah `student_id` sudah ada
        if not DemographicsDimension.objects.filter(student_id=row['student_id']).exists():
            # Simpan data ke tabel DemographicsDimension
            DemographicsDimension.objects.create(
                student_id=row['student_id'],
                gender=row['gender'],
                age=row['age'],
                university=row['university'],
                degree_level=row['degree_level']
            )
            
            
def generate_star_schema_plot_1():
    # Ambil data untuk visualisasi
    mental_health = MentalHealthDimension.objects.all()
    demographics = DemographicsDimension.objects.all()

    # Siapkan data untuk plot
    depression_levels = [mh.depression_level for mh in mental_health]
    universities = [demo.university for demo in demographics]  # Bisa diganti dengan 'degree_level'

    # Membuat grafik menggunakan matplotlib
    plt.figure(figsize=(10, 6))
    sns.boxplot(x=universities, y=depression_levels, palette='Set2')  # Boxplot untuk perbandingan
    plt.xlabel('University')  # Bisa diganti dengan 'Degree Level' jika perlu
    plt.ylabel('Depression Level')
    plt.title('Depression Level by University')

    # Tentukan nama file gambar
    file_name = 'star_schema_plot_1.png'
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)  # Simpan di folder media

    # Jika file sudah ada, hapus terlebih dahulu
    if os.path.exists(file_path):
        os.remove(file_path)

    # Simpan gambar ke file
    plt.savefig(file_path)
    plt.close()

    # Kembalikan path gambar yang dapat diakses melalui URL /media/
    return os.path.join(settings.MEDIA_URL, file_name)  # Kembalikan path relatif untuk akses gambar

def generate_star_schema_plot_2():
    # Ambil data untuk visualisasi
    facts = MentalHealthAssessmentFact.objects.all()

    # Siapkan data untuk plot
    study_satisfaction = [fact.study_satisfaction for fact in facts]
    academic_workload = [fact.academic_workload for fact in facts]

    # Membuat grafik menggunakan matplotlib
    plt.figure(figsize=(10, 6))
    
    # Menampilkan titik berdasarkan data
    sns.scatterplot(x=study_satisfaction, y=academic_workload, 
                    hue=academic_workload, size=study_satisfaction, 
                    sizes=(20, 200), palette='coolwarm', legend=None)
    
    plt.xlabel('Study Satisfaction')
    plt.ylabel('Academic Workload')
    plt.title('Study Satisfaction vs Academic Workload')

    # Tentukan nama file gambar
    file_name = 'star_schema_plot_2.png'
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)  # Simpan di folder media

    # Jika file sudah ada, hapus terlebih dahulu
    if os.path.exists(file_path):
        os.remove(file_path)

    # Simpan gambar ke file
    plt.savefig(file_path)
    plt.close()

    # Kembalikan path gambar yang dapat diakses melalui URL /media/
    return os.path.join(settings.MEDIA_URL, file_name)  # Kembalikan path relatif untuk akses gambar


def generate_star_schema_plot_3():
    # Ambil data untuk visualisasi
    demographics = DemographicsDimension.objects.all()

    # Siapkan data untuk plot
    age = [demo.age for demo in demographics]
    university = [demo.university for demo in demographics]

    # Membuat grafik menggunakan matplotlib
    plt.figure(figsize=(10, 6))
    
    # Menampilkan titik berdasarkan data
    sns.scatterplot(x=university, y=age, 
                    hue=age, size=age, 
                    sizes=(20, 200), palette='viridis', legend=None)
    
    plt.xlabel('University')
    plt.ylabel('Age')
    plt.title('Age vs University')

    # Tentukan nama file gambar
    file_name = 'star_schema_plot_3.png'
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)  # Simpan di folder media

    # Jika file sudah ada, hapus terlebih dahulu
    if os.path.exists(file_path):
        os.remove(file_path)

    # Simpan gambar ke file
    plt.savefig(file_path)
    plt.close()

    # Kembalikan path gambar yang dapat diakses melalui URL /media/
    return os.path.join(settings.MEDIA_URL, file_name)  # Kembalikan path relatif untuk akses gambar



def display_star_schema(request):
    # Load data dari CSV ke database jika belum
    load_data()

    # Generate the 3 Star Schema plots and get their file paths
    plot_path_1 = generate_star_schema_plot_1()
    plot_path_2 = generate_star_schema_plot_2()
    plot_path_3 = generate_star_schema_plot_3()

    # Kirim gambar plot ke template untuk ditampilkan
    return render(request, 'display_star_schema_data.html', {
        'plot_path_1': plot_path_1,
        'plot_path_2': plot_path_2,
        'plot_path_3': plot_path_3  # Kirim semua plot
    })
