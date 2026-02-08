require('dotenv').config();
const express = require("express");
const path = require("path");
const bcrypt = require("bcryptjs");
const cors = require("cors");
const fetch = require("node-fetch");
const connectDB = require('./database');
const Student = require('./models/Student');

const app = express();
const PORT = process.env.PORT || 3000;
const PYTHON_ENGINE_URL = process.env.PYTHON_ENGINE_URL || "http://localhost:5000";
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;

// Connect to MongoDB Atlas
connectDB();

app.use(express.json());
app.use(
  cors({
    origin: "*",
  })
);

// Serve static front-end files
app.use(express.static(path.join(__dirname, "..", "public")));

async function generateAptitudeQuestions(classLevel) {
  // Define difficulty level and topic complexity based on class
  let levelText, difficultyGuide, quantTopics, logicalTopics, verbalTopics;
  
  if (classLevel === "10th") {
    levelText = "class 10 (secondary school) student in India";
    difficultyGuide = `DIFFICULTY LEVEL: INTERMEDIATE
- Mathematics: Basic algebra, linear equations, quadratic equations (simple), geometry (triangles, circles, areas), percentages, ratio & proportion, simple interest, speed-time-distance
- Complexity: Moderate calculations, 2-3 step problems
- Avoid: Advanced trigonometry, calculus, complex word problems`;
    quantTopics = "algebra (linear/quadratic equations), geometry (areas, volumes, Pythagoras), percentages, profit/loss, simple/compound interest, ratio/proportion, speed/time/distance, number systems";
    logicalTopics = "number series, coding-decoding, blood relations, direction sense, rankings, analogies, syllogisms (basic), statement conclusions";
    verbalTopics = "synonyms/antonyms (moderate difficulty), sentence correction, fill in the blanks, one-word substitution, idioms & phrases, active/passive voice, direct/indirect speech";
  } else if (classLevel === "12th") {
    levelText = "class 12 (higher secondary) student in India";
    difficultyGuide = `DIFFICULTY LEVEL: ADVANCED
- Mathematics: Advanced algebra, trigonometry, calculus basics, complex geometry, data interpretation, probability, permutation & combination, logarithms
- Complexity: Multi-step problems requiring analytical thinking, 3-4 step solutions
- Include: Application-based problems, competitive exam level questions`;
    quantTopics = "trigonometry, calculus (differentiation/integration basics), complex numbers, probability, permutation & combination, matrices, logarithms, data interpretation, advanced algebra, coordinate geometry";
    logicalTopics = "complex patterns, data sufficiency, logical deduction, statement & assumptions, critical reasoning, puzzles, seating arrangements, input-output, advanced syllogisms";
    verbalTopics = "advanced vocabulary, reading comprehension, para jumbles, sentence improvement, error spotting, cloze test, idioms & phrases (advanced), inference questions";
  } else {
    levelText = "Indian school student (general level)";
    difficultyGuide = "DIFFICULTY LEVEL: MODERATE - Mix of basic and intermediate questions";
    quantTopics = "basic arithmetic, algebra, geometry, percentages, profit/loss, time & work";
    logicalTopics = "patterns, series, coding-decoding, basic reasoning";
    verbalTopics = "grammar, vocabulary, sentence formation";
  }

  const fallback = {
    quantitative: [
      {
        id: "q1",
        question: "A shopkeeper sells an item at 20% profit. If the cost price is ₹500, what is the selling price?",
        options: ["₹600", "₹550", "₹625", "₹580"],
        answerIndex: 0,
      },
      {
        id: "q2",
        question: "If 3x + 5 = 20, what is the value of x?",
        options: ["3", "4", "5", "6"],
        answerIndex: 2,
      },
      {
        id: "q3",
        question: "A train 150m long passes a pole in 10 seconds. What is the speed of the train in km/h?",
        options: ["45 km/h", "54 km/h", "60 km/h", "72 km/h"],
        answerIndex: 1,
      },
      {
        id: "q4",
        question: "If the area of a circle is 154 cm², what is its radius? (Take π = 22/7)",
        options: ["5 cm", "6 cm", "7 cm", "8 cm"],
        answerIndex: 2,
      },
      {
        id: "q5",
        question: "A number when divided by 7 gives a quotient of 12 and remainder 5. What is the number?",
        options: ["84", "89", "91", "96"],
        answerIndex: 1,
      },
      {
        id: "q6",
        question: "If 25% of a number is 75, what is 40% of that number?",
        options: ["100", "120", "150", "180"],
        answerIndex: 1,
      },
      {
        id: "q7",
        question: "The sum of three consecutive even numbers is 54. What is the largest number?",
        options: ["16", "18", "20", "22"],
        answerIndex: 2,
      },
      {
        id: "q8",
        question: "If a person walks at 6 km/h, how long will it take to cover 4.5 km?",
        options: ["40 minutes", "45 minutes", "50 minutes", "55 minutes"],
        answerIndex: 1,
      },
      {
        id: "q9",
        question: "A rectangle has length 12 cm and width 8 cm. What is the area of a square with the same perimeter?",
        options: ["64 cm²", "81 cm²", "100 cm²", "121 cm²"],
        answerIndex: 2,
      },
      {
        id: "q10",
        question: "If 2^5 × 3^2 = ?",
        options: ["144", "192", "288", "324"],
        answerIndex: 2,
      },
    ],
    logical: [
      {
        id: "l1",
        question: "In a code, CAT is written as 3120. How is DOG written in that code?",
        options: ["4157", "4156", "4158", "4159"],
        answerIndex: 0,
      },
      {
        id: "l2",
        question: "If all roses are flowers and some flowers are red, which statement must be true?",
        options: [
          "All roses are red",
          "Some roses are red",
          "No roses are red",
          "Cannot be determined",
        ],
        answerIndex: 3,
      },
      {
        id: "l3",
        question: "What comes next: 2, 6, 12, 20, 30, ?",
        options: ["40", "42", "44", "46"],
        answerIndex: 1,
      },
      {
        id: "l4",
        question: "If Monday is the first day, what day will it be after 25 days?",
        options: ["Thursday", "Friday", "Saturday", "Sunday"],
        answerIndex: 1,
      },
      {
        id: "l5",
        question: "A is taller than B, C is shorter than A. Who is the tallest?",
        options: ["A", "B", "C", "Cannot be determined"],
        answerIndex: 0,
      },
      {
        id: "l6",
        question: "In a row, Priya is 15th from the left and 20th from the right. How many people are in the row?",
        options: ["33", "34", "35", "36"],
        answerIndex: 1,
      },
      {
        id: "l7",
        question: "If 5 × 3 = 15, 7 × 4 = 28, then 9 × 6 = ?",
        options: ["45", "54", "63", "72"],
        answerIndex: 1,
      },
      {
        id: "l8",
        question: "Complete the series: Z, Y, X, W, V, ?",
        options: ["U", "T", "S", "R"],
        answerIndex: 0,
      },
      {
        id: "l9",
        question: "If all doctors are professionals and some professionals are teachers, which is true?",
        options: [
          "All doctors are teachers",
          "Some doctors are teachers",
          "No doctors are teachers",
          "Cannot be determined",
        ],
        answerIndex: 3,
      },
      {
        id: "l10",
        question: "Find the odd one out: 8, 27, 64, 100, 125",
        options: ["8", "27", "100", "125"],
        answerIndex: 2,
      },
    ],
    verbal: [
      {
        id: "v1",
        question: "Choose the correct synonym for 'Benevolent':",
        options: ["Cruel", "Kind", "Strict", "Lazy"],
        answerIndex: 1,
      },
      {
        id: "v2",
        question: "Fill in the blank: She is the _____ student in the class.",
        options: ["good", "better", "best", "well"],
        answerIndex: 2,
      },
      {
        id: "v3",
        question: "Identify the error: 'Neither of the students were present.'",
        options: [
          "No error",
          "were should be was",
          "students should be student",
          "present should be presence",
        ],
        answerIndex: 1,
      },
      {
        id: "v4",
        question: "Choose the correct meaning of 'Procrastinate':",
        options: [
          "To do immediately",
          "To delay or postpone",
          "To complete quickly",
          "To organize",
        ],
        answerIndex: 1,
      },
      {
        id: "v5",
        question: "Select the correctly spelled word:",
        options: ["Accomodate", "Accommodate", "Acommodate", "Acomodate"],
        answerIndex: 1,
      },
      {
        id: "v6",
        question: "Choose the appropriate preposition: 'She is allergic _____ peanuts.'",
        options: ["to", "for", "with", "at"],
        answerIndex: 0,
      },
      {
        id: "v7",
        question: "What is the antonym of 'Abundant'?",
        options: ["Plentiful", "Scarce", "Many", "Rich"],
        answerIndex: 1,
      },
      {
        id: "v8",
        question: "Identify the figure of speech: 'The wind whispered through the trees.'",
        options: ["Simile", "Metaphor", "Personification", "Alliteration"],
        answerIndex: 2,
      },
      {
        id: "v9",
        question: "Choose the correct form: 'I wish I _____ harder for the exam.'",
        options: ["study", "studied", "had studied", "will study"],
        answerIndex: 2,
      },
      {
        id: "v10",
        question: "What does 'Eloquent' mean?",
        options: [
          "Unable to speak",
          "Fluent and persuasive in speaking",
          "Quiet and shy",
          "Rude and impolite",
        ],
        answerIndex: 1,
      },
    ],
  };

  if (!GEMINI_API_KEY) {
    return fallback;
  }

  try {
    const prompt = `You are an expert aptitude test generator for Indian students preparing for competitive exams and career assessments.

TARGET STUDENT: ${levelText}

${difficultyGuide}

Generate three sections with EXACTLY 10 UNIQUE questions each:

SECTION 1 - QUANTITATIVE APTITUDE (10 questions)
Topics to cover: ${quantTopics}
- Each question MUST test a DIFFERENT concept
- Vary question types: calculations, word problems, data interpretation
- For Class 10: Focus on CBSE/ICSE Class 10 curriculum level
- For Class 12: Include JEE/competitive exam style questions

SECTION 2 - LOGICAL REASONING (10 questions)
Topics to cover: ${logicalTopics}
- Each question MUST be DISTINCT and test different reasoning skills
- Include variety: patterns, verbal reasoning, analytical reasoning
- For Class 10: Basic to moderate difficulty
- For Class 12: Advanced problem-solving, similar to CAT/competitive exams

SECTION 3 - VERBAL & COMMUNICATION (10 questions)
Topics to cover: ${verbalTopics}
- Each question MUST test different language skills
- Mix of grammar, vocabulary, and comprehension
- For Class 10: Based on standard English curriculum
- For Class 12: Advanced English suitable for professional communication

CRITICAL JSON FORMAT REQUIREMENTS:
{
  "quantitative": [
    {"id": "q1", "question": "Question text here?", "options": ["Option A", "Option B", "Option C", "Option D"], "answerIndex": 0}
  ],
  "logical": [...],
  "verbal": [...]
}

STRICT RULES:
✓ Return ONLY valid JSON (no markdown, no explanations, no code blocks)
✓ EXACTLY 10 questions per section (30 total)
✓ Each question ID must be unique (q1-q10, l1-l10, v1-v10)
✓ All 10 questions in EACH section must be COMPLETELY DIFFERENT
✓ 3-5 options per question
✓ answerIndex is 0-based (0 = first option, 1 = second, etc.)
✓ Use Indian context (₹ for currency, Indian names, realistic scenarios)
✓ MAXIMUM RANDOMIZATION - Generate completely new questions every time
✓ NO REPETITION of questions or concepts within the same section

DIFFICULTY CALIBRATION:
- Class 10: Questions should be challenging but solvable with Class 10 knowledge
- Class 12: Questions should prepare students for competitive exams (JEE, NEET, CAT level intro)

Generate NOW:`;

    const res = await fetch(
      "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=" +
        GEMINI_API_KEY,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contents: [
            {
              parts: [{ text: prompt }],
            },
          ],
          generationConfig: {
            temperature: 1.0,  // Increased for more randomization
            topP: 0.95,
            topK: 64,
          },
        }),
      }
    );

    if (!res.ok) {
      console.error("Gemini API error status", res.status);
      return fallback;
    }

    const data = await res.json();
    const text =
      data?.candidates?.[0]?.content?.parts?.[0]?.text ||
      data?.candidates?.[0]?.output_text;

    if (!text) {
      return fallback;
    }

    // In case model wraps JSON in markdown, strip fences
    const cleaned = text.replace(/```json|```/g, "").trim();
    const parsed = JSON.parse(cleaned);

    if (!parsed.quantitative || !parsed.logical || !parsed.verbal) {
      return fallback;
    }

    return parsed;
  } catch (err) {
    console.error("Error calling Gemini API", err);
    return fallback;
  }
}

// Signup: create or update full profile (MongoDB)
app.post("/api/signup", async (req, res) => {
  try {
    const payload = req.body;
    const { email, password } = payload;

    if (!email || !password) {
      return res
        .status(400)
        .json({ ok: false, message: "Email and password are required." });
    }

    // Hash the password
    const passwordHash = await bcrypt.hash(password, 10);

    // Check if user already exists
    let student = await Student.findByEmail(email);

    if (student) {
      // Update existing user
      Object.assign(student, payload, { passwordHash });
      delete student.password;
      await student.save();
    } else {
      // Create new user
      const studentData = {
        ...payload,
        passwordHash,
      };
      delete studentData.password;
      student = new Student(studentData);
      await student.save();
    }

    // Convert to plain object and remove sensitive data
    const safeUser = student.toObject();
    delete safeUser.passwordHash;
    delete safeUser.__v;

    res.json({ 
      ok: true, 
      user: safeUser,
      message: `Account ${student.loginCount === 0 ? 'created' : 'updated'} successfully`,
      signupAt: student.createdAt
    });
  } catch (err) {
    console.error("Error in /api/signup", err);
    if (err.code === 11000) {
      return res.status(400).json({ ok: false, message: "Email already exists." });
    }
    res.status(500).json({ ok: false, message: "Internal server error." });
  }
});

// Login: verify credentials (MongoDB with timestamp tracking)
app.post("/api/login", async (req, res) => {
  try {
    const { email, password } = req.body || {};
    if (!email || !password) {
      return res
        .status(400)
        .json({ ok: false, message: "Email and password are required." });
    }

    // Find student by email
    const student = await Student.findByEmail(email);
    if (!student || !student.passwordHash) {
      return res
        .status(401)
        .json({ ok: false, message: "Invalid email or password." });
    }

    // Verify password
    const isValid = await bcrypt.compare(password, student.passwordHash);
    if (!isValid) {
      return res
        .status(401)
        .json({ ok: false, message: "Invalid email or password." });
    }

    // Update login timestamp using the model method
    await student.recordLogin();

    // Convert to plain object and remove sensitive data
    const safeUser = student.toObject();
    delete safeUser.passwordHash;
    delete safeUser.__v;

    res.json({ 
      ok: true, 
      user: safeUser,
      message: "Login successful",
      lastLoginAt: student.lastLoginAt,
      loginCount: student.loginCount
    });
  } catch (err) {
    console.error("Error in /api/login", err);
    res.status(500).json({ ok: false, message: "Internal server error." });
  }
});

// Get profile by email (used to restore session) - MongoDB
app.get("/api/profile/:email", async (req, res) => {
  try {
    const email = req.params.email;
    const student = await Student.findByEmail(email);
    if (!student) {
      return res
        .status(404)
        .json({ ok: false, message: "Profile not found." });
    }
    
    // Convert to plain object and remove sensitive data
    const safeUser = student.toObject();
    delete safeUser.passwordHash;
    delete safeUser.__v;
    
    res.json({ ok: true, user: safeUser });
  } catch (err) {
    console.error("Error in /api/profile", err);
    res.status(500).json({ ok: false, message: "Internal server error." });
  }
});

// In-memory storage for user attempts (for simple implementation)
// For production, use MongoDB or another database
const userAttempts = [];

// Helper function to shuffle array
function shuffleArray(array) {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

// Aptitude questions with randomization and user tracking
app.post("/api/aptitude-questions", async (req, res) => {
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

    // Generate questions
    const allQuestions = await generateAptitudeQuestions(classLevel || "other");
    
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
    console.error("Error in /api/aptitude-questions", err);
    res.status(500).json({
      ok: false,
      message: "Unable to generate questions at the moment.",
    });
  }
});

// Reset question pool for a user
app.post("/api/reset-question-pool", (req, res) => {
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
});

// Career Recommendations endpoint - proxies to Python recommendation engine
app.post("/api/recommendations", async (req, res) => {
  try {
    const studentData = req.body;

    if (!studentData.email) {
      return res.status(400).json({
        ok: false,
        message: "Student email is required",
      });
    }

    console.log(`\n🎯 Generating career recommendations for: ${studentData.email}`);

    // Forward request to Python recommendation engine
    const pythonResponse = await fetch(`${PYTHON_ENGINE_URL}/api/recommend`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(studentData),
    });

    if (!pythonResponse.ok) {
      console.error("Python engine error:", pythonResponse.status);
      return res.status(500).json({
        ok: false,
        message: "Recommendation service temporarily unavailable. Please try again later.",
      });
    }

    const recommendations = await pythonResponse.json();
    
    console.log(`✓ Generated ${recommendations.recommendations?.length || 0} recommendations`);
    
    res.json({
      ok: true,
      ...recommendations,
    });
  } catch (err) {
    console.error("Error generating recommendations:", err);
    res.status(500).json({
      ok: false,
      message: "Unable to generate recommendations at this time. Please ensure the Python recommendation engine is running.",
    });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
  console.log(`Python recommendation engine expected at: ${PYTHON_ENGINE_URL}`);
});


