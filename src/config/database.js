const mongoose = require('mongoose');

const connectDB = async () => {
  try {
    const mongoURI = process.env.MONGODB_URI;
    
    if (!mongoURI) {
      throw new Error('MONGODB_URI is not defined in environment variables. Please check your .env file.');
    }

    // Basic validation of connection string format
    if (!mongoURI.includes('mongodb')) {
      throw new Error('Invalid MONGODB_URI format. Must start with mongodb:// or mongodb+srv://');
    }

    // Determine if using MongoDB Atlas (cloud) or local
    const isAtlas = mongoURI.includes('mongodb+srv');
    
    console.log(`🔄 Connecting to MongoDB${isAtlas ? ' Atlas (Cloud)' : ' (Local)'}...`);
    
    await mongoose.connect(mongoURI, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });

    console.log('✅ MongoDB Connected Successfully');
    console.log(`📊 Database: ${mongoose.connection.name}`);
    console.log(`🌐 Host: ${isAtlas ? 'MongoDB Atlas (Cloud)' : mongoose.connection.host}`);
    console.log(`💾 All user data and timestamps are saved to ${isAtlas ? 'cloud database' : 'local database'}`);
    
    // Handle connection events
    mongoose.connection.on('error', (err) => {
      console.error('❌ MongoDB connection error:', err);
    });

    mongoose.connection.on('disconnected', () => {
      console.warn('⚠️  MongoDB disconnected');
    });

    // Graceful shutdown
    process.on('SIGINT', async () => {
      await mongoose.connection.close();
      console.log('MongoDB connection closed through app termination');
      process.exit(0);
    });

  } catch (error) {
    console.error('❌ MongoDB connection failed:', error.message);
    
    // Provide specific troubleshooting tips
    if (error.message.includes('MONGODB_URI')) {
      console.error('💡 Please create a .env file with your MongoDB Atlas connection string');
      console.error('💡 See .env.example for the required format');
    } else if (error.message.includes('authentication') || error.message.includes('auth')) {
      console.error('💡 Check your MongoDB Atlas username and password in the connection string');
      console.error('💡 Password with special characters must be URL-encoded:');
      console.error('   < = %3C, > = %3E, @ = %40, : = %3A, / = %2F, ? = %3F, # = %23');
    } else if (error.message.includes('hostname') || error.message.includes('domain name') || error.message.includes('tld')) {
      console.error('💡 Connection string format error. Check your MONGODB_URI in .env file');
      console.error('💡 Should be: mongodb+srv://username:password@cluster.mongodb.net/database?options');
      console.error('💡 Make sure password special characters are URL-encoded');
      console.error('💡 Use only ONE ? in the URL (separate options with &)');
    } else if (error.message.includes('network') || error.message.includes('ENOTFOUND')) {
      console.error('💡 Check your internet connection and MongoDB Atlas network access settings');
      console.error('💡 Make sure your IP address is whitelisted in Atlas (or use 0.0.0.0/0)');
    } else {
      console.error('💡 Check your .env file and MongoDB Atlas configuration');
    }
    
    process.exit(1);
  }
};

module.exports = connectDB;
