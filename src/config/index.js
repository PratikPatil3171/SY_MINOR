
module.exports = {
  // Server configuration
  server: {
    port: process.env.PORT || 3000,
    env: process.env.NODE_ENV || 'development'
  },

  // MongoDB Atlas configuration
  database: {
    uri: process.env.MONGODB_URI || 'mongodb://localhost:27017/career_advisor'
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

  
  auth: {
    saltRounds: 10,
    sessionKey: 'careerAdvisor_sessionEmail',
    userKey: 'careerAdvisor_studentProfile'
  }
};
