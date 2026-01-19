// Configuration settings for the application
module.exports = {
  // Server configuration
  server: {
    port: process.env.PORT || 3000,
    env: process.env.NODE_ENV || 'development'
  },

  // Database configuration
  database: {
    path: './data/database.json'
  },

  // API configuration
  api: {
    geminiApiKey: process.env.GEMINI_API_KEY,
    baseUrl: '/api'
  },

  // CORS configuration
  cors: {
    origin: process.env.CORS_ORIGIN || '*'
  },

  // Authentication configuration
  auth: {
    saltRounds: 10,
    sessionKey: 'careerAdvisor_sessionEmail',
    userKey: 'careerAdvisor_studentProfile'
  }
};
