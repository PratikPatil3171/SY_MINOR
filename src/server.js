require('dotenv').config();
const express = require('express');
const path = require('path');
const cors = require('cors');

// Database connection
const connectDB = require('./config/database');

// Routes
const authRoutes = require('./routes/authRoutes');
const profileRoutes = require('./routes/profileRoutes');
const aptitudeRoutes = require('./routes/aptitudeRoutes');
const recommendationRoutes = require('./routes/recommendationRoutes');

// Middlewares
const { errorHandler, notFoundHandler } = require('./middlewares/errorHandler');

// Initialize Express app
const app = express();
const PORT = process.env.PORT || 3000;
const PYTHON_ENGINE_URL = process.env.PYTHON_ENGINE_URL || 'http://localhost:5000';

// Connect to MongoDB Atlas
connectDB();

// Middleware
app.use(express.json());
app.use(cors({ origin: '*' }));

// Serve static frontend files
app.use(express.static(path.join(__dirname, '..', 'public')));

// API Routes
app.use('/api', authRoutes);           // /api/signup, /api/login
app.use('/api', profileRoutes);        // /api/profile/:email
app.use('/api', aptitudeRoutes);       // /api/aptitude-questions, /api/reset-question-pool
app.use('/api', recommendationRoutes); // /api/recommendations

// 404 Handler
app.use(notFoundHandler);

// Global Error Handler
app.use(errorHandler);

// Start Server
app.listen(PORT, () => {
  console.log('\n🚀 Career Advisor Server Started');
  console.log('================================');
  console.log(`📡 Server running on http://localhost:${PORT}`);
  console.log(`🐍 Python recommendation engine expected at: ${PYTHON_ENGINE_URL}`);
  console.log(`📊 MongoDB Atlas: Connected`);
  console.log('================================\n');
});
