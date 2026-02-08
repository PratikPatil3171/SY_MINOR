const geminiService = require('../services/geminiService');
const { shuffleArray } = require('../utils/helpers');

// In-memory storage for user attempts
const userAttempts = [];

/**
 * Generate aptitude questions for a student
 */
exports.generateQuestions = async (req, res) => {
  try {
    const { classLevel, email } = req.body || {};

    if (!email) {
      return res.status(400).json({
        ok: false,
        message: "User email is required",
      });
    }

    // Get user's recent attempts (last 24 hours)
    const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
    const recentAttempts = userAttempts.filter(
      (attempt) =>
        attempt.userEmail === email && new Date(attempt.timestamp) >= oneDayAgo
    );

    // Collect used question IDs
    let usedQuestionIds = [];
    recentAttempts.forEach((attempt) => {
      if (attempt.questionIds) {
        usedQuestionIds = usedQuestionIds.concat(attempt.questionIds);
      }
    });

    // Generate questions using Gemini service
    const allQuestions = await geminiService.generateAptitudeQuestions(
      classLevel || "other"
    );
    
    console.log(`\n📚 Generating questions for: ${classLevel || "general"} level student`);
    console.log(`👤 User: ${email}`);

    // Function to select and shuffle questions for a section
    function processSection(sectionQuestions, usedIds) {
      // Filter out recently used questions
      let availableQuestions = sectionQuestions.filter(
        (q) => !usedIds.includes(q.id)
      );

      // If not enough new questions, use all questions
      if (availableQuestions.length < 10) {
        availableQuestions = sectionQuestions;
      }

      // Shuffle and take 10
      const shuffled = shuffleArray(availableQuestions).slice(0, 10);

      // Shuffle options for each question
      return shuffled.map((q) => {
        const correctAnswer = q.options[q.answerIndex];
        const shuffledOptions = shuffleArray(q.options);
        return {
          ...q,
          options: shuffledOptions,
          answerIndex: shuffledOptions.indexOf(correctAnswer),
        };
      });
    }

    // Process each section
    const questions = {
      quantitative: processSection(allQuestions.quantitative, usedQuestionIds),
      logical: processSection(allQuestions.logical, usedQuestionIds),
      verbal: processSection(allQuestions.verbal, usedQuestionIds),
    };

    // Store this attempt
    const allQuestionIds = [
      ...questions.quantitative.map((q) => q.id),
      ...questions.logical.map((q) => q.id),
      ...questions.verbal.map((q) => q.id),
    ];

    userAttempts.push({
      userEmail: email,
      classLevel: classLevel,
      questionIds: allQuestionIds,
      timestamp: new Date(),
    });

    // Clean up old attempts (older than 7 days)
    const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
    const validAttempts = userAttempts.filter(
      (attempt) => new Date(attempt.timestamp) >= sevenDaysAgo
    );
    userAttempts.length = 0;
    userAttempts.push(...validAttempts);

    res.json({ ok: true, questions });
  } catch (err) {
    console.error("Error in generateQuestions:", err);
    res.status(500).json({
      ok: false,
      message: "Unable to generate questions at the moment.",
    });
  }
};

/**
 * Reset question pool for a user
 */
exports.resetQuestionPool = (req, res) => {
  try {
    const { email } = req.body;

    if (!email) {
      return res.status(400).json({
        ok: false,
        message: "User email is required",
      });
    }

    // Remove all attempts for this user
    const initialLength = userAttempts.length;
    const filtered = userAttempts.filter(
      (attempt) => attempt.userEmail !== email
    );
    userAttempts.length = 0;
    userAttempts.push(...filtered);

    res.json({
      ok: true,
      message: "Question pool reset successfully",
    });
  } catch (error) {
    console.error("Error resetting question pool:", error);
    res.status(500).json({
      ok: false,
      message: "Failed to reset question pool",
    });
  }
};

/**
 * Submit and save aptitude test scores
 */
exports.submitScores = async (req, res) => {
  try {
    const { email, scores } = req.body;

    if (!email) {
      return res.status(400).json({
        ok: false,
        message: "User email is required",
      });
    }

    if (!scores || typeof scores !== 'object') {
      return res.status(400).json({
        ok: false,
        message: "Scores object is required",
      });
    }

    // Validate scores
    const { quantitative, logical, verbal } = scores;
    
    if (quantitative < 0 || quantitative > 10 ||
        logical < 0 || logical > 10 ||
        verbal < 0 || verbal > 10) {
      return res.status(400).json({
        ok: false,
        message: "Scores must be between 0 and 10",
      });
    }

    // Find student and update scores
    const Student = require('../models/Student');
    const student = await Student.findByEmail(email);

    if (!student) {
      return res.status(404).json({
        ok: false,
        message: "Student not found",
      });
    }

    student.aptitudeScores = {
      quantitative,
      logical,
      verbal,
      testTakenAt: new Date()
    };

    await student.save();

    console.log(`✅ Saved aptitude scores for: ${email}`);

    res.json({
      ok: true,
      message: "Scores saved successfully",
      scores: student.aptitudeScores
    });
  } catch (error) {
    console.error("Error saving scores:", error);
    res.status(500).json({
      ok: false,
      message: "Failed to save scores",
    });
  }
};

