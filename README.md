#  Online Farmer Marketplace with Crop Price Tracker

An online platform that connects **farmers** directly with **buyers**, allowing them to trade crops fairly and transparently. The system provides a **real-time crop price tracker**, secure user management, and smooth user interaction—all powered by a **Django REST API** and a **React frontend**.

## 🚀 Features

- 👨‍🌾 Farmer and 👤 Buyer authentication system.
- 🌽 Crop listing, searching, and buying.
- 📈 Real-time crop price tracking
- 💬 Messaging system between users
- 🛠️ Admin panel for managing users, crops, and prices

## 🧰 Tech Stack

### Frontend
- HTML, CSS, JavaScript
- **React.js**
  

### Backend
- **Django** with Django REST Framework


### Database
- **MySQL** (via Django ORM)

### Deployment
- **python anywhere
  
### Project Management: 
Trello .

## 📡 API (Django REST)

The backend provides a secure REST API:

- `POST /api/register/` – Register user  
- `POST /api/login/` – Login (returns JWT)  
- `GET /api/crops/` – List all crops  
- `POST /api/crops/` – Add new crop (farmer only)  
- `GET /api/prices/` – Get current crop prices

> 🛡️ Auth: All protected routes require a valid JWT token  
> 📦 Data Format: JSON
