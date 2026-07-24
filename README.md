# ♻️ AI-Enabled Smart City Waste Management System

## 📌 Project Overview

The **AI-Enabled Smart City Waste Management System** is a web-based application developed to improve waste collection and monitoring in smart cities. The system monitors waste bin fill levels, predicts future fill levels using Artificial Intelligence (AI), simulates IoT sensor data, displays waste bins on an interactive map, and provides a complaint management system for citizens.

This project demonstrates how AI, IoT, and web technologies can work together to create a cleaner and smarter city.

---

## 🎯 Objectives

- Monitor waste bin fill levels.
- Predict future waste levels using AI.
- Simulate IoT sensor data.
- Display waste bins with GPS locations.
- Enable citizens to submit complaints.
- Assist authorities in identifying bins that require collection.

---

## ✨ Features

- 📊 Interactive Dashboard
- 🤖 AI-Based Waste Fill Level Prediction
- 📡 IoT Sensor Simulation
- 🗺️ Interactive GPS Map
- 🗑️ Waste Bin Monitoring
- 🔍 Waste Bin Search
- 🚨 Alert Panel for Full Bins
- 📈 Charts and Analytics
- 📝 Customer Complaint Management
- 💾 SQLite Database

---

## 🛠️ Technologies Used

### Backend

- Python
- FastAPI
- SQLAlchemy
- SQLite

### Frontend

- HTML
- CSS
- JavaScript
- Jinja2 Templates

### AI & Visualization

- Scikit-learn
- Joblib
- Chart.js
- Leaflet.js

---

## 📂 Project Structure

```text
AI-Enabled Smart City Waste Management System
│
├── ai/
│   ├── prediction.py
│   ├── training.py
│   └── waste_prediction_model.pkl
│
├── iot/
│
├── static/
│   ├── style.css
│   └── images/
│
├── templates/
│   └── dashboard.html
│
├── database.py
├── models.py
├── main.py
├── requirements.txt
├── waste_management.db
└── README.md
```

---

## ⚙️ Installation

### Clone the Repository

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/AI-Enabled-Smart-City-Waste-Management-System.git
```

### Open the Project

```bash
cd AI-Enabled-Smart-City-Waste-Management-System
```

### Create Virtual Environment

```bash
python -m venv .venv
```

### Activate Virtual Environment (Windows)

```bash
.venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Application

```bash
uvicorn main:app --reload
```

### Open in Browser

```
http://127.0.0.1:8000/dashboard
```

---

## 📸 Modules

- Dashboard
- Waste Bin Management
- AI Prediction
- IoT Simulation
- Interactive Map
- Complaint Management
- Analytics

---

## 🔮 Future Enhancements

- Real IoT Sensor Integration
- Live GPS Tracking
- QR Code for Waste Bins
- Mobile Application
- Email Notifications
- Garbage Truck Route Optimization
- Camera-Based Waste Detection
- Admin Login System

---

## 📷 Screenshots

You can add screenshots of your dashboard here after uploading the project.

---

## 👨‍💻 Developed By

**Vinathi Kaithi**

AI & Data Science Student

GitHub: https://github.com/vinathireddy08-bit

---

## 📄 License

This project is developed for educational and academic purposes.