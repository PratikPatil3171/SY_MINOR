# Personalized Career Advisor

A web application that helps students find the right career path based on their academic performance, interests, and aptitude test results.

## Features

- **User Authentication**: Login and signup system with profile management
- **Aptitude Testing**: Three-section aptitude test (Quantitative, Logical, Verbal)
- **Personalized Career Recommendations**: Based on student profile and test scores
- **Student Dashboard**: View aptitude scores and career guidance

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Node.js, Express.js
- **Database**: JSON file-based storage
- **Authentication**: bcryptjs for password hashing

## Setup Instructions

1. **Install Node.js** (if not already installed)
   - Download from: https://nodejs.org/

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Start the Server**
   ```bash
   npm start
   ```

4. **Open in Browser**
   - Navigate to: http://localhost:3000
   - The application should now be running!

## Usage

1. **Create an Account**: Click "Signup" and fill in your student profile
2. **Login**: Use your email and password to login
3. **Take Aptitude Test**: Click on "Explore Aptitude Guidance" to take the test
4. **View Results**: See your scores and personalized career recommendations

## Project Structure

```
Personalized/
├── public/                 # Frontend static files
│   ├── css/
│   │   └── main.css       # Application styles
│   ├── js/
│   │   └── app.js         # Frontend JavaScript
│   ├── images/            # Image assets
│   └── index.html         # Main application page
├── src/                   # Backend source code
│   └── server.js          # Express server
├── data/                  # Database files
│   └── database.json      # JSON database
├── tests/                 # Test files
│   └── api-test-client.html  # API testing client
├── node_modules/          # Dependencies (auto-generated)
├── .gitignore            # Git ignore rules
├── package.json          # Node dependencies
├── package-lock.json     # Locked dependencies
└── README.md             # This file
```

## API Endpoints

- `POST /api/signup` - Create new student account
- `POST /api/login` - Authenticate user
- `GET /api/profile/:email` - Get user profile
- `POST /api/aptitude/questions` - Generate aptitude questions
- `POST /api/career-recommendations` - Get career recommendations

## Note

This is a student project for learning web development concepts. The database is file-based and not suitable for production use.
