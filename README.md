# Shopify Store Insights-Fetcher Application

A FastAPI-based backend application to store, manage, and fetch brand insights for Shopify stores. This project leverages **SQLAlchemy** with **MySQL** for database management and provides a structured API to interact with brand data.

---

## Features

- **Add or Update Brand Data**: Save insights for a brand or update existing data.  
- **Fetch All Brands**: Retrieve a list of all stored brands (ID + Brand Name).  
- **Fetch Brand Details by ID**: Retrieve detailed JSON insights for a specific brand.  
- **Environment-based Configuration**: All database credentials and configurations are managed through a `.env` file.  
- **Robust and Secure**: Proper session handling using SQLAlchemy ORM for reliable data operations.

---

## Tech Stack

- **Backend Framework**: FastAPI  
- **Database**: MySQL  
- **ORM**: SQLAlchemy  
- **Database Driver**: PyMySQL  
- **Environment Management**: python-dotenv  
- **API Documentation**: Automatic Swagger docs via FastAPI

---

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/sujan22359/Shopify-store-Insights-Fetcher-Application.git
cd Shopify-Store-Insights-Fetcher
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup `.env` file**
Create a `.env` file in the project root with the following content:
```env
DB_USER=root
DB_PASS=your_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=shopifydb
```
---

## Usage

1. **Initialize the Database**
```bash
python
>>> from db import init_db
>>> init_db()
```

2. **Run the FastAPI Server**
```bash
uvicorn main:app --reload
```

3. **Access API Documentation**
Open your browser and go to:  
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Example Endpoints

- **POST /brands** – Add or update brand insights  
- **GET /brands** – Fetch all brands  
- **GET /brands/{id}** – Fetch brand details by ID


## License

This project is open-sourced under the MIT License.
