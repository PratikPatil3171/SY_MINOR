require('dotenv').config();
const mongoose = require('mongoose');
const fs = require('fs');
const path = require('path');
const Student = require('./src/models/Student');

const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/career_advisor';
const JSON_DB_PATH = path.join(__dirname, 'data', 'database.json');

async function migrateData() {
  try {
    console.log('🚀 Starting data migration from JSON to MongoDB...\n');

    // Connect to MongoDB
    await mongoose.connect(MONGODB_URI, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });
    console.log('✅ Connected to MongoDB\n');

    // Read existing JSON data
    if (!fs.existsSync(JSON_DB_PATH)) {
      console.log('⚠️  No existing database.json found. Starting with empty database.');
      await mongoose.connection.close();
      process.exit(0);
    }

    const rawData = fs.readFileSync(JSON_DB_PATH, 'utf8');
    const jsonDb = JSON.parse(rawData);
    const students = jsonDb.students || [];

    console.log(`📊 Found ${students.length} students in JSON database\n`);

    if (students.length === 0) {
      console.log('ℹ️  No students to migrate.');
      await mongoose.connection.close();
      process.exit(0);
    }

    // Clear existing MongoDB data (optional - comment out if you want to keep existing data)
    const existingCount = await Student.countDocuments();
    if (existingCount > 0) {
      console.log(`⚠️  Found ${existingCount} existing students in MongoDB.`);
      console.log('🗑️  Clearing existing data...');
      await Student.deleteMany({});
      console.log('✅ Existing data cleared\n');
    }

    // Migrate each student
    let successCount = 0;
    let errorCount = 0;

    for (const studentData of students) {
      try {
        // Remove the old 'id' field if it exists
        const { id, password, ...cleanData } = studentData;

        // Create new student document
        const student = new Student({
          ...cleanData,
          // Set createdAt to a past date if you want to preserve signup timing
          // Otherwise, Mongoose will set it to now
          createdAt: new Date(id || Date.now()),
          updatedAt: new Date(id || Date.now()),
        });

        await student.save();
        successCount++;
        console.log(`✅ Migrated: ${student.email}`);
      } catch (err) {
        errorCount++;
        console.error(`❌ Failed to migrate: ${studentData.email}`, err.message);
      }
    }

    console.log('\n📊 Migration Summary:');
    console.log(`   ✅ Successful: ${successCount}`);
    console.log(`   ❌ Failed: ${errorCount}`);
    console.log(`   📈 Total: ${students.length}`);

    // Create a backup of the original JSON file
    const backupPath = path.join(__dirname, 'data', `database_backup_${Date.now()}.json`);
    fs.copyFileSync(JSON_DB_PATH, backupPath);
    console.log(`\n💾 Backup created: ${backupPath}`);

    console.log('\n🎉 Migration completed successfully!');
    console.log('💡 You can now start using MongoDB for your application.\n');

    await mongoose.connection.close();
    process.exit(0);
  } catch (error) {
    console.error('\n❌ Migration failed:', error);
    process.exit(1);
  }
}

// Run migration
migrateData();
