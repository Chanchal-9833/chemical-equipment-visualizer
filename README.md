Chemical Equipment Parameter Visualizer

A hybrid application (Web + Desktop) to visualize and analyze chemical equipment parameters. Users can upload CSV files containing equipment data (flowrate, pressure, temperature, etc.) and get interactive charts and analytics.

This project was part of the Intern Screening Task.

Features

Upload CSV files containing chemical equipment parameters.
Interactive charts (Bar, Scatter) for data visualization.
Works both as a Web application (React.js frontend + Flask/Django backend) and a Desktop app (using Electron/pywebview).
Simple authentication for secure access.
Modular architecture: web-frontend and backend folders.

Project Structure
chemical-equipment-visualizer/
│
├── backend/                 # Backend API and server
│   ├── equipment/           # Equipment module
│   ├── backend/             # Main backend module
│   └── requirements.txt     # Python dependencies
│
├── web-frontend/            # Frontend React app
│   ├── src/
│   └── package.json
│
├── README.md
└── .gitignore

Setup Instructions
Prerequisites

Node.js (v18+ recommended) – for React frontend

Python (v3.10+) – for backend
pip – Python package manager

Git – for version control

Step 1: Clone the repository
git clone https://github.com/Chanchal-9833/chemical-equipment-visualizer.git
cd chemical-equipment-visualizer

Step 2: Setup Backend

Navigate to backend folder:
cd backend


Create a virtual environment (optional but recommended):

python -m venv venv


Activate the virtual environment:

Windows:
venv\Scripts\activate


Linux/Mac:
source venv/bin/activate


Install dependencies:
pip install -r requirements.txt


Run the backend server:
python manage.py runserver   # For Django

Backend will run on http://127.0.0.1:5000 (Flask) or http://127.0.0.1:8000 (Django)

Step 3: Setup Frontend

Open a new terminal and navigate to frontend:

cd web-frontend

Install frontend dependencies:
npm install

Start the React app:
npm start

React app will run on http://localhost:3000. Make sure the backend server is running for API calls.

Step 4: Using the App

Open the frontend in your browser.

Upload your CSV file containing chemical equipment data.
View charts and analysis in the dashboard.

Step 5: for  Desktop App 
run desktop_app.py file 
Notes

Ensure backend server is running before starting the frontend.

CSV files must have proper columns: Equipment Name, Type, Flowrate, Pressure, Temperature