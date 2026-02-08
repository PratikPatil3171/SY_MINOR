# Career Advisor - Backend Architecture

## 📁 Project Structure

```
Personalized/
├── src/                                # Backend source code
│   ├── config/                         # Configuration files
│   │   ├── database.js                 # MongoDB Atlas connection
│   │   └── index.js                    # App configuration
│   │
│   ├── controllers/                    # Request handlers (business logic)
│   │   ├── authController.js           # Signup, Login
│   │   ├── profileController.js        # Get student profile
│   │   ├── aptitudeController.js       # Generate questions, reset pool
│   │   └── recommendationController.js # Career recommendations
│   │
│   ├── models/                         # Database schemas
│   │   └── Student.js                  # Student model with timestamps
│   │
│   ├── routes/                         # API route definitions
│   │   ├── authRoutes.js               # /api/signup, /api/login
│   │   ├── profileRoutes.js            # /api/profile/:email
│   │   ├── aptitudeRoutes.js           # /api/aptitude-questions
│   │   └── recommendationRoutes.js     # /api/recommendations
│   │
│   ├── services/                       # External service integration
│   │   ├── geminiService.js            # Gemini AI for questions
│   │   └── pythonEngineService.js      # Python ML recommendations
│   │
│   ├── middlewares/                    # Express middlewares
│   │   └── errorHandler.js             # Global error handler
│   │
│   ├── utils/                          # Utility functions
│   │   └── helpers.js                  # Common helper functions
│   │
│   └── server.js                       # Main application entry point
│
├── public/                             # Frontend static files
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── images/
│
├── python_engine/                      # ML recommendation engine
│   ├── app.py                          # Flask API
│   ├── recommendation_engine.py        # ML logic
│   └── models/                         # Trained ML models
│
├── data/                               # Data files
│   ├── careers.csv
│   └── FakeStudents.csv
│
├── scripts/                            # Utility scripts
│   └── migrate.js                      # JSON to MongoDB migration
│
├── .env                                # Environment variables (MongoDB URI)
├── .env.example                        # Environment template
├── package.json                        # Node.js dependencies
└── README.md                           # This file

```

## 🏗️ Architecture Pattern: MVC (Model-View-Controller)

### Models (`models/`)
- Define database schema and data structure
- Handle data validation
- Database operations (CRUD)

### Controllers (`controllers/`)
- Handle incoming HTTP requests
- Process request data
- Call services and models
- Return HTTP responses

### Routes (`routes/`)
- Define API endpoints
- Map URLs to controller functions
- Group related endpoints

### Services (`services/`)
- Business logic layer
- External API integration (Gemini, Python)
- Reusable business operations

### Middlewares (`middlewares/`)
- Request/response processing
- Error handling
- Authentication (future)
- Logging (future)

## 🔄 Request Flow

```
Client Request
    ↓
Express Router (routes/)
    ↓
Controller (controllers/)
    ↓
Service (services/) ← → External APIs
    ↓
Model (models/) ← → MongoDB Atlas
    ↓
Controller Response
    ↓
Client Response
```

## 📡 API Endpoints

### Authentication
- `POST /api/signup` - Register or update user profile
- `POST /api/login` - Authenticate user and track login

### Profile
- `GET /api/profile/:email` - Get student profile by email

### Aptitude Test
- `POST /api/aptitude-questions` - Generate personalized questions
- `POST /api/reset-question-pool` - Reset user's question history

### Recommendations
- `POST /api/recommendations` - Get ML-based career recommendations

## 🗄️ Database (MongoDB Atlas)

### Student Schema
```javascript
{
  fullName: String,
  email: String (unique),
  passwordHash: String,
  class: String,
  stream: String,
  ratings: { ... },
  skills: [String],
  careerDomains: [String],
  
  // Auto-generated timestamps
  createdAt: Date,        // Signup time
  updatedAt: Date,        // Last profile update
  lastLoginAt: Date,      // Last login time
  loginCount: Number      // Total login count
}
```

## 🚀 Running the Application

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment
```bash
# Copy template
cp .env.example .env

# Edit .env with your MongoDB Atlas connection string
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/career_advisor
```

### 3. Start Node.js Server
```bash
npm start
```

### 4. Start Python Engine (separate terminal)
```bash
cd python_engine
python app.py
```

## 🧪 Development

### Project Files Removed
- ✅ Deleted 27 unnecessary markdown documentation files (IMPL/)
- ✅ Removed redundant setup guides
- ✅ Cleaned up test files
- ✅ Moved migration script to scripts/

### Code Improvements
- ✅ Modular architecture (separation of concerns)
- ✅ Consistent error handling
- ✅ Better code organization
- ✅ Reusable services and utilities
- ✅ Clean server.js (from 700+ to 60 lines)

## 📝 Future Enhancements

- [ ] Add JWT authentication middleware
- [ ] Implement request validation middleware
- [ ] Add request logging
- [ ] Create admin routes
- [ ] Add rate limiting
- [ ] Implement caching layer
- [ ] Add API documentation (Swagger)
- [ ] Unit and integration tests

## 🤝 Contributing

When adding new features:
1. Create model in `models/` if needed
2. Create controller in `controllers/`
3. Create route in `routes/`
4. Import route in `server.js`
5. Add services in `services/` for external integrations

## 📄 License
MIT
