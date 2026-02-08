const fetch = require('node-fetch');

const GEMINI_API_KEY = process.env.GEMINI_API_KEY;

/**
 * Fallback questions if Gemini API is unavailable
 */
const fallbackQuestions = {
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

/**
 * Generate aptitude questions using Gemini AI
 * @param {string} classLevel - Student's class level
 * @returns {Promise<Object>} Questions object with three sections
 */
exports.generateAptitudeQuestions = async (classLevel) => {
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

  if (!GEMINI_API_KEY) {
    console.log('⚠️ Gemini API key not found, using fallback questions');
    return fallbackQuestions;
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
            temperature: 1.0,
            topP: 0.95,
            topK: 64,
          },
        }),
      }
    );

    if (!res.ok) {
      console.error("Gemini API error status", res.status);
      return fallbackQuestions;
    }

    const data = await res.json();
    const text =
      data?.candidates?.[0]?.content?.parts?.[0]?.text ||
      data?.candidates?.[0]?.output_text;

    if (!text) {
      return fallbackQuestions;
    }

    // Strip markdown code blocks if present
    const cleaned = text.replace(/```json|```/g, "").trim();
    const parsed = JSON.parse(cleaned);

    if (!parsed.quantitative || !parsed.logical || !parsed.verbal) {
      return fallbackQuestions;
    }

    return parsed;
  } catch (err) {
    console.error("Error calling Gemini API", err);
    return fallbackQuestions;
  }
};
