# AssetFlow

AssetFlow is a comprehensive Asset Management System designed to track, manage, and optimize your organization's assets seamlessly. With a robust backend and a highly responsive frontend, AssetFlow provides real-time insights into your inventory, maintenance schedules, and asset lifecycle.

## Features

- **Dashboard Analytics:** Get an overview of all assets, maintenance statuses, and active locations.
- **Asset Tracking:** Detailed registry of all company assets.
- **Maintenance Management:** Schedule and track maintenance tasks for every asset.
- **User Authentication:** Secure access control for administrators and users.
- **Responsive UI:** Modern web application built with React/Vite.
- **Fast Backend:** High-performance API using FastAPI and SQLAlchemy.

## Tech Stack

### Frontend
- **Framework:** React + Vite
- **Styling:** CSS
- **Language:** JavaScript

### Backend
- **Framework:** FastAPI (Python)
- **Database:** SQLite (SQLAlchemy ORM)
- **Migrations:** Alembic

## Getting Started

### Prerequisites
- Node.js
- Python 3.8+

### Running the Backend

1. Navigate to the backend directory:
   ```bash
   cd assetflow-backend
   ```
2. Activate the virtual environment:
   ```bash
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```
3. Run the application:
   ```bash
   python -m uvicorn app.main:app --reload
   # or
   fastapi dev app/main.py
   ```

### Running the Frontend

1. Navigate to the frontend directory:
   ```bash
   cd assetflow-frontend
   ```
2. Install dependencies (if not already installed):
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

## License

This project is licensed under the MIT License.
