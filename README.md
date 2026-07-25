# ♻️ AI-Enabled Smart City Waste Management System

## 🚀 Live Demo

**Dashboard:**
https://ai-enabled-smart-city-waste-management.onrender.com/dashboard

---

## 📌 Project Overview

The **AI-Enabled Smart City Waste Management System** is a web-based application developed using **FastAPI** to help municipalities monitor and manage waste bins efficiently. The system tracks bin fill levels, displays waste bin locations on an interactive dashboard, manages customer complaints, and provides AI-based waste level prediction for smarter waste collection.

---

## ✨ Features

* ♻️ Real-time Waste Bin Monitoring
* 📍 Interactive Waste Bin Dashboard
* ➕ Add New Waste Bins
* 🗑️ Waste Bin Details and Status Tracking
* 📊 Waste Level Visualization using Chart.js
* 🗺️ Interactive Map using Leaflet
* 🤖 AI-Based Waste Fill Level Prediction
* 📝 Customer Complaint Management
* 💾 SQLite Database Integration
* 🌐 Cloud Deployment using Render

---

## 🛠️ Technologies Used

### Backend

* Python
* FastAPI
* SQLAlchemy
* Pydantic

### Frontend

* HTML5
* CSS3
* JavaScript
* Jinja2 Templates

### Database

* SQLite

### AI & Visualization

* Scikit-learn
* Chart.js
* Leaflet Maps

### Version Control & Deployment

* Git
* GitHub
* Render

---

## 📂 Project Structure

```text
AI-Enabled-Smart-City-Waste-Management-System/
│
├── ai/
│   ├── prediction.py
│   └── training.py
│
├── iot/
│
├── static/
│   ├── style.css
│   ├── images/
│   └── js/
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

### Clone the repository

```bash
git clone https://github.com/vinathireddy08-bit/AI-Enabled-Smart-City-Waste-Management-System.git
```

### Move into the project folder

```bash
cd AI-Enabled-Smart-City-Waste-Management-System
```

### Create a virtual environment

```bash
python -m venv .venv
```

### Activate the virtual environment

#### Windows

```bash
.venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the application

```bash
uvicorn main:app --reload
```

---

## 🌐 Application URLs

### Local Development

```
http://127.0.0.1:8000/dashboard
```

### Live Deployment

```
https://ai-enabled-smart-city-waste-management.onrender.com/dashboard
```

---

## 📊 System Workflow

1. Waste bins are registered with a unique Bin ID.
2. Each Bin ID is linked to its location and GPS coordinates.
3. The system stores all waste bin information in the database.
4. Users can add and monitor waste bins through the dashboard.
5. AI predicts future waste fill levels.
6. Customer complaints are recorded and managed.
7. Interactive charts and maps provide a visual overview of waste collection.

---

## 🎯 Future Enhancements

* IoT Sensor Integration
* User Authentication
* Email/SMS Alerts
* Garbage Truck Route Optimization
* Camera-Based Waste Detection
* Mobile Application
* Real-Time Notifications

---

## 👨‍💻 Author

**Nithin Reddy**

AI & Data Science Student

GitHub: https://github.com/vinathireddy08-bit

---

## 📜 License

This project is developed for educational and portfolio purposes.

This project is developed for educational and academic purposes.
