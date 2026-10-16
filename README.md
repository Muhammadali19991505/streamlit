# 📊 Streamlit Data Analytics Dashboard

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://github.com/Muhammadali19991505/streamlit)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-green)
![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-FF4B4B)

Ushbu repozitoriy **Python** va **Streamlit** freymvorki yordamida yaratilgan interaktiv ma'lumotlar tahlili (Data Analysis) va vizualizatsiya veb-ilovasini o'z ichiga oladi. Ilova foydalanuvchilarga ma'lumotlar to'plamini real vaqt rejimida filtrlash, asosiy statistik ko'rsatkichlarni (KPI) kuzatish va interaktiv grafiklar orqali tahlil qilish imkonini beradi.

---

## ✨ Asosiy Imkoniyatlar

* **🎛 Interaktiv Filtrlar (Sidebar):** Ma'lumotlarni toifalar, hududlar, yosh guruhlari yoki vaqt oralig'i bo'yicha dinamik ravishda saralash.
* **📈 Asosiy Ko'rsatkichlar (KPI Metrics):** Umumiy ko'rsatkichlar, o'rtacha qiymatlar va foiz ulushlarini tezkor kartochkalarda (`st.metric`) ko'rish.
* **📊 Dinamik Vizualizatsiya:** `Plotly`, `Seaborn` va `Matplotlib` yordamida qurilgan interaktiv ustunli, chiziqli va doiraviy diagrammalar.
* **📋 Ma'lumotlar Jadvali:** Tozalangan va saralangan ma'lumotlarni to'g'ridan-to'g'ri brauzerda ko'rish hamda yuklab olish imkoniyati.

---

## 🗂 Loyiha Tuzilmasi (Project Structure)

```text
streamlit/
│
├── app.py                  # Asosiy Streamlit veb-ilovasi kodi
├── TITANIC.xlsx            # Titanic yo'lovchilari ma'lumotlar to'plami (yoki dataset.csv)
├── requirements.txt        # Loyiha uchun kerakli Python kutubxonalar ro'yxati
└── README.md               # Loyiha hujjati va qo'llanmasi
