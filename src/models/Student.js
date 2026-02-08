const mongoose = require('mongoose');

const studentSchema = new mongoose.Schema(
  {
    fullName: {
      type: String,
      required: true,
      trim: true
    },
    email: {
      type: String,
      required: true,
      unique: true,
      lowercase: true,
      trim: true,
      index: true
    },
    passwordHash: {
      type: String,
      required: true
    },
    class: {
      type: String,
      required: true,
      enum: ['10th', '12th', 'Graduate', 'Postgraduate']
    },
    stream: {
      type: String,
      enum: ['Science', 'Commerce', 'Arts', null],
      default: null
    },
    tenthPercentage: {
      type: String,
      default: null
    },
    twelfthPercentage: {
      type: String,
      default: null
    },
    cgpaSem: {
      type: String,
      default: null
    },
    ratings: {
      codingInterest: { type: Number, min: 1, max: 5, default: 3 },
      mathsInterest: { type: Number, min: 1, max: 5, default: 3 },
      scienceInterest: { type: Number, min: 1, max: 5, default: 3 },
      commerceInterest: { type: Number, min: 1, max: 5, default: 3 },
      designInterest: { type: Number, min: 1, max: 5, default: 3 },
      peopleInterest: { type: Number, min: 1, max: 5, default: 3 }
    },
    skills: {
      type: [String],
      default: []
    },
    careerDomains: {
      type: [String],
      default: []
    },
    higherStudies: {
      type: String,
      enum: ['Yes', 'No', 'Unsure', null],
      default: null
    },
    entranceExams: {
      type: [String],
      default: []
    },
    workEnvironment: {
      type: String,
      default: null
    },
    workStyles: {
      type: [String],
      default: []
    },
    financialConstraints: {
      type: String,
      enum: ['Yes', 'No', null],
      default: null
    },
    locationRestrictions: {
      type: String,
      default: null
    },
    dreamCareer: {
      type: String,
      default: null
    },
    careerConfusion: {
      type: String,
      default: null
    },
    // Aptitude test scores (0-10 scale)
    aptitudeScores: {
      quantitative: { type: Number, min: 0, max: 10, default: null },
      logical: { type: Number, min: 0, max: 10, default: null },
      verbal: { type: Number, min: 0, max: 10, default: null },
      testTakenAt: { type: Date, default: null }
    },
    // Timestamp fields for tracking login/signup
    lastLoginAt: {
      type: Date,
      default: null
    },
    loginCount: {
      type: Number,
      default: 0
    }
  },
  {
    timestamps: true, // Automatically adds createdAt and updatedAt
    collection: 'students'
  }
);

// Index for faster queries
studentSchema.index({ email: 1 });
studentSchema.index({ createdAt: -1 });
studentSchema.index({ lastLoginAt: -1 });

// Instance method to update login timestamp
studentSchema.methods.recordLogin = async function() {
  this.lastLoginAt = new Date();
  this.loginCount += 1;
  return await this.save();
};

// Static method to find by email
studentSchema.statics.findByEmail = function(email) {
  return this.findOne({ email: email.toLowerCase() });
};

const Student = mongoose.model('Student', studentSchema);

module.exports = Student;
