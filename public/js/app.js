// Simple front-end auth backed by small Node/Express API
// Keys
const USER_KEY = "careerAdvisor_studentProfile";
const SESSION_KEY = "careerAdvisor_sessionEmail";
const API_BASE = "http://localhost:3000/api";

// Elements
const authModal = document.getElementById("auth-modal");
const authTitle = document.getElementById("auth-title");
const authSubtitle = document.getElementById("auth-subtitle");
const authCloseBtn = document.getElementById("auth-close");

const aptitudeSection = document.getElementById("aptitude-section");
const authStatus = document.getElementById("auth-status");
const authMessage = document.getElementById("auth-message");
const logoutBtn = document.getElementById("logout-btn");

const navLogin = document.getElementById("nav-login");
const navSignup = document.getElementById("nav-signup");
const navAptitude = document.getElementById("nav-aptitude");
const navContact = document.getElementById("nav-contact");
const navUser = document.getElementById("nav-user");
const navUserName = document.getElementById("nav-user-name");
const navLogoutBtn = document.getElementById("nav-logout");

const heroAptitudeBtn = document.getElementById("hero-aptitude-btn");
const heroLoginBtn = document.getElementById("hero-login-btn");

const loginForm = document.getElementById("login-form");
const signupForm = document.getElementById("signup-form");
const editProfileBtn = document.getElementById("edit-profile-btn");

const studentSummary = document.getElementById("student-summary");
const loginPasswordToggle = document.getElementById("login-password-toggle");

const startAptitudeBtn = document.getElementById("start-aptitude-btn");
const quantitativeScoreEl = document.getElementById("quant-score");
const logicalScoreEl = document.getElementById("logic-score");
const verbalScoreEl = document.getElementById("verbal-score");

const aptitudeTestScreen = document.getElementById("aptitude-test-screen");
const aptitudeResultsScreen = document.getElementById("aptitude-results-screen");
const aptitudeQuestionsContainer = document.getElementById(
  "aptitude-questions-container"
);
const testSectionTitle = document.getElementById("test-section-title");
const testSectionSubtitle = document.getElementById("test-section-subtitle");
const testProgressText = document.getElementById("test-progress-text");
const testProgressFill = document.getElementById("test-progress-fill");
const prevQuestionBtn = document.getElementById("prev-question-btn");
const nextQuestionBtn = document.getElementById("next-question-btn");
const submitSectionBtn = document.getElementById("submit-section-btn");
const closeResultsBtn = document.getElementById("close-results-btn");
const resultsContent = document.getElementById("results-content");

// Recommendations elements
const recommendationsScreen = document.getElementById("recommendations-screen");
const recommendationsContent = document.getElementById("recommendations-content");
const recommendationsLoading = document.getElementById("recommendations-loading");
const viewRecommendationsBtn = document.getElementById("view-recommendations-btn");
const closeRecommendationsBtn = document.getElementById("close-recommendations-btn");

const APTITUDE_SCORES_KEY = "careerAdvisor_aptitudeScores";

// Test state
let currentAptitudeQuestions = null;
let currentSectionIndex = 0; // 0: quantitative, 1: logical, 2: verbal
let currentQuestionIndex = 0;
let answers = {}; // { "quantitative-0": 1, "logical-3": 2, ... }
const sections = [
  { key: "quantitative", title: "Section 1: Quantitative Aptitude", subtitle: "Answer all 10 questions. Each question is worth 1 mark." },
  { key: "logical", title: "Section 2: Logical Reasoning", subtitle: "Answer all 10 questions. Each question is worth 1 mark." },
  { key: "verbal", title: "Section 3: Verbal & Communication", subtitle: "Answer all 10 questions. Each question is worth 1 mark." },
];

// Helpers
function getStoredUser() {
  try {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch (e) {
    console.error("Failed to parse stored user", e);
    return null;
  }
}

function saveUser(user) {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

function setSession(email) {
  localStorage.setItem(SESSION_KEY, email);
}

function clearSession() {
  localStorage.removeItem(SESSION_KEY);
  localStorage.removeItem(USER_KEY);
}

function getSession() {
  return localStorage.getItem(SESSION_KEY);
}

function isLoggedIn() {
  const user = getStoredUser();
  const sessionEmail = getSession();
  return !!user && !!sessionEmail && user.email === sessionEmail;
}

function openAuthModal(mode) {
  if (!authModal) return;
  const isLogin = mode === "login";
  authModal.classList.remove("hidden");
  authModal.classList.add("visible");
  if (isLogin) {
    authTitle.textContent = "Student Login";
    authSubtitle.textContent =
      "Login to access your saved profile, aptitude overview, and personalized career guidance.";
    loginForm.classList.add("active-form");
    signupForm.classList.remove("active-form");
  } else {
    authTitle.textContent = "Create Your Student Profile";
    authSubtitle.textContent =
      "Fill in your academics, interests and preferences so we can personalise aptitude and career suggestions for you.";
    signupForm.classList.add("active-form");
    loginForm.classList.remove("active-form");
  }
}

function closeAuthModal() {
  if (!authModal) return;
  authModal.classList.add("hidden");
  authModal.classList.remove("visible");
}

function showAptitudeSection() {
  aptitudeSection.classList.remove("hidden");
}

function openAptitudeTest() {
  if (!aptitudeTestScreen) return;
  aptitudeTestScreen.classList.remove("hidden");
  document.body.style.overflow = "hidden";
  currentSectionIndex = 0;
  currentQuestionIndex = 0;
  answers = {};
  renderCurrentQuestion();
}

function closeAptitudeTest() {
  if (!aptitudeTestScreen) return;
  aptitudeTestScreen.classList.add("hidden");
  document.body.style.overflow = "";
}

function openResultsScreen() {
  if (!aptitudeResultsScreen) return;
  aptitudeResultsScreen.classList.remove("hidden");
  aptitudeTestScreen.classList.add("hidden");
  renderResults();
}

function closeResultsScreen() {
  if (!aptitudeResultsScreen) return;
  aptitudeResultsScreen.classList.add("hidden");
  document.body.style.overflow = "";
}

function openRecommendationsScreen() {
  if (!recommendationsScreen) return;
  aptitudeResultsScreen.classList.add("hidden");
  recommendationsScreen.classList.remove("hidden");
  document.body.style.overflow = "hidden";
}

function closeRecommendationsScreen() {
  if (!recommendationsScreen) return;
  recommendationsScreen.classList.add("hidden");
  document.body.style.overflow = "";
}

async function fetchRecommendations() {
  const user = getStoredUser();
  const scores = getStoredScores();
  
  if (!user) {
    alert("Please log in first.");
    return;
  }
  
  if (!scores || !scores.testTakenAt) {
    alert("Please complete the aptitude test first to get career recommendations.");
    return;
  }

  // Check if average score is above 4
  const quantScore = scores.quantitative ?? 0;
  const logicScore = scores.logical ?? 0;
  const verbalScore = scores.verbal ?? 0;
  const average = (quantScore + logicScore + verbalScore) / 3;
  
  if (average <= 4) {
    alert("Your average score is " + average.toFixed(2) + ". Please score marks above 4 to view recommendations. You can attempt the test again to improve your score.");
    return;
  }

  // Show loading state
  openRecommendationsScreen();
  if (recommendationsLoading) recommendationsLoading.classList.remove("hidden");
  if (recommendationsContent) recommendationsContent.innerHTML = "";

  try {
    // Prepare student data for recommendation engine
    const studentData = {
      email: user.email,
      name: user.fullName,
      stream: user.stream,
      classLevel: user.currentClass,
      marks10th: parseFloat(user.tenthPercentage) || null,
      marks12th: parseFloat(user.twelfthPercentage) || null,
      cgpaSem: user.cgpaSem || null,
      
      // Subject interests (1-5 ratings)
      interests: {
        coding: user.ratings?.codingInterest || 0,
        design: user.ratings?.designInterest || 0,
        math: user.ratings?.mathsInterest || 0,
        science: user.ratings?.scienceInterest || 0,
        business: user.ratings?.commerceInterest || 0,
        people: user.ratings?.peopleInterest || 0,
      },
      
      // Aptitude test scores (0-10)
      aptitude: {
        quantitative: scores.quantitative || 0,
        logical: scores.logical || 0,
        verbal: scores.verbal || 0,
      },
      
      // Skills and preferences
      skills: user.skills || [],
      careerDomains: user.careerDomains || [],
      higherStudies: user.higherStudies,
      entranceExams: user.entranceExams || [],
      workEnvironment: user.workEnvironment,
      workStyles: user.workStyles || [],
      financialConstraints: user.financialConstraints,
      locationRestrictions: user.locationRestrictions,
      dreamCareer: user.dreamCareer || "",
    };

    console.log("Fetching recommendations with data:", studentData);

    const res = await fetch(`${API_BASE}/recommendations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(studentData),
    });

    const data = await res.json();

    if (recommendationsLoading) recommendationsLoading.classList.add("hidden");

    console.log("Received recommendations response:", data);

    // Check for both 'ok' and 'success' fields (server returns 'ok', Python returns 'success')
    const isSuccess = data.ok || data.success;
    
    if (!isSuccess || !data.recommendations || data.recommendations.length === 0) {
      recommendationsContent.innerHTML = `
        <div class="error-message">
          <h3>⚠️ Unable to Generate Recommendations</h3>
          <p>${data.message || data.error || "The recommendation service is currently unavailable. Please ensure the Python recommendation engine is running on port 5000."}</p>
          <p>To start the recommendation engine:</p>
          <ol>
            <li>Open a terminal in the <code>python_engine</code> folder</li>
            <li>Run: <code>python app.py</code></li>
            <li>Wait for "API Server ready" message</li>
            <li>Try generating recommendations again</li>
          </ol>
        </div>
      `;
      return;
    }

    renderRecommendations(data.recommendations);
  } catch (err) {
    console.error("Error fetching recommendations:", err);
    if (recommendationsLoading) recommendationsLoading.classList.add("hidden");
    
    recommendationsContent.innerHTML = `
      <div class="error-message">
        <h3>⚠️ Connection Error</h3>
        <p>Could not connect to the recommendation service.</p>
        <p>Please make sure:</p>
        <ol>
          <li>The Python recommendation engine is running on port 5000</li>
          <li>Navigate to <code>python_engine</code> folder</li>
          <li>Run: <code>python app.py</code></li>
          <li>Wait for the server to start</li>
        </ol>
      </div>
    `;
  }
}

function renderRecommendations(recommendations) {
  if (!recommendationsContent) return;
  
  if (!recommendations || recommendations.length === 0) {
    recommendationsContent.innerHTML = `
      <div class="no-results">
        <h3>No Recommendations Found</h3>
        <p>We couldn't find suitable career recommendations based on your profile. Please update your profile with more details.</p>
      </div>
    `;
    return;
  }

  let html = '<div class="recommendations-list">';
  
  recommendations.forEach((career, index) => {
    const rank = index + 1;
    // The Python engine returns 'total_score' out of 10
    const matchScore = Math.round((career.total_score || career.score || 0) * 10);
    
    // Get the explanation object
    const explanation = career.explanation || {};
    const matchStrength = explanation.match_strength || 'Good Match';
    const summary = explanation.summary || '';
    const keyReasons = explanation.key_reasons || [];
    
    html += `
      <div class="recommendation-card">
        <div class="recommendation-header">
          <div class="recommendation-rank">#${rank}</div>
          <div class="recommendation-title">
            <h3>${career.title || 'Career Option'}</h3>
            <div class="match-score">
              <div class="match-bar">
                <div class="match-fill" style="width: ${matchScore}%"></div>
              </div>
              <span>${matchScore}% Match - ${matchStrength}</span>
            </div>
          </div>
        </div>
        <div class="recommendation-body">
          ${career.description ? `<p class="career-description">${career.description}</p>` : ''}
          
          ${career.domain ? `<p><strong>Domain:</strong> ${career.domain}</p>` : ''}
          
          ${career.education_path ? `<p><strong>Education Path:</strong> ${career.education_path}</p>` : ''}
          
          ${career.required_skills ? `
            <p><strong>Key Skills:</strong> ${Array.isArray(career.required_skills) ? career.required_skills.join(', ') : career.required_skills}</p>
          ` : ''}
          
          ${career.avg_salary ? `<p><strong>Average Salary:</strong> ${career.avg_salary}</p>` : ''}
          
          ${summary ? `
            <div class="recommendation-explanation">
              <strong>Why this matches you:</strong>
              <p>${summary}</p>
              ${keyReasons.length > 0 ? `
                <ul>
                  ${keyReasons.map(reason => `<li>${reason}</li>`).join('')}
                </ul>
              ` : ''}
            </div>
          ` : ''}
        </div>
      </div>
    `;
  });
  
  html += '</div>';
  recommendationsContent.innerHTML = html;
}

function updateAuthBanner() {
  const user = getStoredUser();
  if (isLoggedIn() && user) {
    authStatus.classList.remove("hidden");
    logoutBtn.classList.remove("hidden");
    authMessage.textContent = `Logged in as ${user.fullName || user.email}. You can access your aptitude and career overview below.`;

    if (navUser && navUserName) {
      navUser.classList.remove("hidden");
      navUserName.textContent = user.fullName || user.email;
    }
    if (navLogin) navLogin.classList.add("hidden");
    if (navSignup) navSignup.classList.add("hidden");
  } else {
    authStatus.classList.remove("hidden");
    logoutBtn.classList.add("hidden");
    authMessage.textContent =
      "You are not logged in. Please login or create your profile to access aptitude and personalized guidance.";

    if (navUser) navUser.classList.add("hidden");
    if (navLogin) navLogin.classList.remove("hidden");
    if (navSignup) navSignup.classList.remove("hidden");
  }
}

async function fetchProfileFromServer(email) {
  try {
    const res = await fetch(`${API_BASE}/profile/${encodeURIComponent(email)}`);
    if (!res.ok) return null;
    const data = await res.json();
    if (data.ok) return data.user;
    return null;
  } catch (e) {
    console.error("Failed to fetch profile", e);
    return null;
  }
}

function collectRatings() {
  const ratingContainers = document.querySelectorAll(".rating-row");
  const ratings = {};
  ratingContainers.forEach((row) => {
    const name = row.dataset.name;
    const active = row.querySelector(".rating-pill.active");
    ratings[name] = active ? Number(active.dataset.value) : null;
  });
  return ratings;
}

function collectCheckedChips(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return [];
  const checked = Array.from(
    container.querySelectorAll('input[type="checkbox"]:checked')
  );
  return checked.map((el) => el.value);
}

function collectMultiSelectValues(selectId) {
  const sel = document.getElementById(selectId);
  if (!sel) return [];
  return Array.from(sel.selectedOptions).map((o) => o.value);
}

function buildStudentSummary(user) {
  const interests = [];
  if (user.ratings) {
    if (user.ratings.codingInterest >= 4) interests.push("Loves coding / IT");
    if (user.ratings.mathsInterest >= 4) interests.push("Strong in Maths");
    if (user.ratings.scienceInterest >= 4)
      interests.push("Science oriented");
    if (user.ratings.commerceInterest >= 4)
      interests.push("Commerce / business interest");
    if (user.ratings.designInterest >= 4)
      interests.push("Creative / design mindset");
    if (user.ratings.peopleInterest >= 4)
      interests.push("People & communication oriented");
  }

  const skillsText =
    user.skills && user.skills.length
      ? user.skills.join(", ")
      : "Not specified yet";

  const domainsText =
    user.careerDomains && user.careerDomains.length
      ? user.careerDomains.join(", ")
      : "Still exploring options";

  const higherStudies = user.higherStudies || "Not sure yet";

  const env = user.workEnvironment || "Not specified";

  studentSummary.innerHTML = `
    <h3>Hi ${user.fullName || ""} 👋</h3>
    <p><strong>Current level:</strong> ${user.class || "Not specified"} ${
    user.stream ? " • Stream: " + user.stream : ""
  }</p>
    <p><strong>Key skills:</strong> ${skillsText}</p>
    <p><strong>Interested domains:</strong> ${domainsText}</p>
    <p><strong>Higher studies plan:</strong> ${higherStudies}</p>
    <p><strong>Preferred work environment:</strong> ${env}</p>
    <div class="tag-row">
      ${
        interests.length
          ? interests.map((t) => `<span class="tag">${t}</span>`).join("")
          : '<span class="tag">We will understand your interests better once you complete the aptitude test.</span>'
      }
    </div>
  `;
}

function getStoredScores() {
  // Get scores from the current user object instead of localStorage
  const user = getStoredUser();
  return user && user.aptitudeScores ? user.aptitudeScores : null;
}

async function saveScores(scores) {
  // Save scores to database via API
  const user = getStoredUser();
  if (!user || !user.email) {
    console.error('No user logged in');
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/submit-scores`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: user.email, scores })
    });

    const data = await res.json();
    if (data.ok) {
      // Update local user object with new scores
      user.aptitudeScores = data.scores;
      saveUser(user);
      console.log('✅ Scores saved to database');
    } else {
      console.error('Failed to save scores:', data.message);
    }
  } catch (error) {
    console.error('Error saving scores:', error);
  }
}

function renderScores() {
  const scores = getStoredScores();
  if (!scores || !scores.testTakenAt) {
    // No test taken yet - show placeholder
    if (quantitativeScoreEl) {
      quantitativeScoreEl.textContent = '-- / 10';
    }
    if (logicalScoreEl) {
      logicalScoreEl.textContent = '-- / 10';
    }
    if (verbalScoreEl) {
      verbalScoreEl.textContent = '-- / 10';
    }
    return;
  }
  
  // Display actual scores
  if (quantitativeScoreEl) {
    quantitativeScoreEl.textContent = `${scores.quantitative ?? 0} / 10`;
  }
  if (logicalScoreEl) {
    logicalScoreEl.textContent = `${scores.logical ?? 0} / 10`;
  }
  if (verbalScoreEl) {
    verbalScoreEl.textContent = `${scores.verbal ?? 0} / 10`;
  }
}

function syncSignupFormWithStoredUser() {
  const user = getStoredUser();
  if (!user) return;
  document.getElementById("full-name").value = user.fullName || "";
  document.getElementById("email").value = user.email || "";
  document.getElementById("class").value = user.class || "";
  document.getElementById("stream").value = user.stream || "";
  document.getElementById("tenth-perc").value = user.tenthPercentage || "";
  document.getElementById("twelfth-perc").value = user.twelfthPercentage || "";
  document.getElementById("cgpa-sem").value = user.cgpaSem || "";

  // ratings
  if (user.ratings) {
    const ratingContainers = document.querySelectorAll(".rating-row");
    ratingContainers.forEach((row) => {
      const name = row.dataset.name;
      const value = user.ratings[name];
      if (!value) return;
      const pills = row.querySelectorAll(".rating-pill");
      pills.forEach((pill) => {
        if (Number(pill.dataset.value) === value) {
          pill.classList.add("active");
        } else {
          pill.classList.remove("active");
        }
      });
    });
  }

  // skills
  const skillsContainer = document.getElementById("skills");
  if (skillsContainer && user.skills) {
    Array.from(
      skillsContainer.querySelectorAll('input[type="checkbox"]')
    ).forEach((el) => {
      el.checked = user.skills.includes(el.value);
    });
  }

  // career domains
  const domainsContainer = document.getElementById("career-domains");
  if (domainsContainer && user.careerDomains) {
    Array.from(
      domainsContainer.querySelectorAll('input[type="checkbox"]')
    ).forEach((el) => {
      el.checked = user.careerDomains.includes(el.value);
    });
  }

  // select fields
  document.getElementById("higher-studies").value =
    user.higherStudies || "";

  const entranceSel = document.getElementById("entrance-exams");
  if (entranceSel && user.entranceExams) {
    Array.from(entranceSel.options).forEach((opt) => {
      opt.selected = user.entranceExams.includes(opt.value);
    });
  }

  document.getElementById("work-environment").value =
    user.workEnvironment || "";

  const workStyleSel = document.getElementById("work-style");
  if (workStyleSel && user.workStyles) {
    Array.from(workStyleSel.options).forEach((opt) => {
      opt.selected = user.workStyles.includes(opt.value);
    });
  }

  document.getElementById("financial-constraints").value =
    user.financialConstraints || "";
  document.getElementById("location-restrictions").value =
    user.locationRestrictions || "";
  document.getElementById("dream-career").value = user.dreamCareer || "";
  document.getElementById("career-confusion").value =
    user.careerConfusion || "";
}

// Initialize rating pills (1-5)
function initRatingPills() {
  const rows = document.querySelectorAll(".rating-row");
  rows.forEach((row) => {
    // If already populated (e.g., re-init), skip
    if (row.children.length) return;
    for (let i = 1; i <= 5; i++) {
      const pill = document.createElement("button");
      pill.type = "button";
      pill.className = "rating-pill";
      pill.textContent = String(i);
      pill.dataset.value = String(i);
      pill.addEventListener("click", () => {
        Array.from(row.children).forEach((child) =>
          child.classList.remove("active")
        );
        pill.classList.add("active");
      });
      row.appendChild(pill);
    }
  });
}

function renderCurrentQuestion() {
  if (!currentAptitudeQuestions || !aptitudeQuestionsContainer) return;
  
  const section = sections[currentSectionIndex];
  const questions = currentAptitudeQuestions[section.key] || [];
  if (questions.length === 0) return;
  
  const question = questions[currentQuestionIndex];
  if (!question) return;
  
  // Update header
  if (testSectionTitle) testSectionTitle.textContent = section.title;
  if (testSectionSubtitle) testSectionSubtitle.textContent = section.subtitle;
  
  // Update progress
  const totalQuestions = questions.length;
  const progress = ((currentQuestionIndex + 1) / totalQuestions) * 100;
  if (testProgressText) {
    testProgressText.textContent = `Question ${currentQuestionIndex + 1} of ${totalQuestions}`;
  }
  if (testProgressFill) {
    testProgressFill.style.width = `${progress}%`;
  }
  
  // Render question
  aptitudeQuestionsContainer.innerHTML = "";
  const questionCard = document.createElement("div");
  questionCard.className = "question-card";
  
  const questionTitle = document.createElement("h3");
  questionTitle.textContent = question.question;
  questionCard.appendChild(questionTitle);
  
  const optionsDiv = document.createElement("div");
  optionsDiv.className = "question-options";
  
  question.options.forEach((opt, optIdx) => {
    const optionDiv = document.createElement("div");
    optionDiv.className = "question-option";
    
    const input = document.createElement("input");
    input.type = "radio";
    input.name = `question-${currentSectionIndex}-${currentQuestionIndex}`;
    input.value = String(optIdx);
    input.id = `opt-${currentSectionIndex}-${currentQuestionIndex}-${optIdx}`;
    
    const answerKey = `${section.key}-${currentQuestionIndex}`;
    if (answers[answerKey] === optIdx) {
      input.checked = true;
      optionDiv.classList.add("selected");
    }
    
    input.addEventListener("change", () => {
      answers[answerKey] = optIdx;
      document.querySelectorAll(".question-option").forEach((el) => {
        el.classList.remove("selected");
      });
      optionDiv.classList.add("selected");
    });
    
    const label = document.createElement("label");
    label.htmlFor = input.id;
    label.textContent = opt;
    
    optionDiv.appendChild(input);
    optionDiv.appendChild(label);
    optionsDiv.appendChild(optionDiv);
  });
  
  questionCard.appendChild(optionsDiv);
  aptitudeQuestionsContainer.appendChild(questionCard);
  
  // Update navigation buttons
  if (prevQuestionBtn) {
    prevQuestionBtn.classList.toggle("hidden", currentQuestionIndex === 0);
  }
  if (nextQuestionBtn) {
    const isLastQuestion = currentQuestionIndex === totalQuestions - 1;
    nextQuestionBtn.classList.toggle("hidden", isLastQuestion);
  }
  if (submitSectionBtn) {
    const isLastQuestion = currentQuestionIndex === totalQuestions - 1;
    submitSectionBtn.classList.toggle("hidden", !isLastQuestion);
  }
}

async function startAptitudeTest() {
  if (!isLoggedIn()) {
    alert("Please login or create your profile before taking the aptitude test.");
    openAuthModal("login");
    return;
  }

  const user = getStoredUser();
  const classLevel = user?.class || "other";
  const email = user?.email; // Get user email for tracking

  try {
    const res = await fetch(`${API_BASE}/aptitude-questions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ classLevel, email }), // Send email to track attempts
    });
    const data = await res.json();
    if (!data.ok) {
      alert(data.message || "Unable to load questions right now.");
      return;
    }
    currentAptitudeQuestions = data.questions;
    currentSectionIndex = 0;
    currentQuestionIndex = 0;
    answers = {};
    openAptitudeTest();
  } catch (err) {
    console.error("Error fetching aptitude questions", err);
    alert("Unable to load questions right now. Please try again later.");
  }
}

// Optional: Reset question pool to see all questions again
async function resetQuestionPool() {
  if (!isLoggedIn()) {
    alert("Please login first.");
    return;
  }
  
  const user = getStoredUser();
  if (!confirm("This will allow you to see questions you've already attempted. Continue?")) {
    return;
  }
  
  try {
    const res = await fetch(`${API_BASE}/reset-question-pool`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: user.email }),
    });
    const data = await res.json();
    if (data.ok) {
      alert("Question pool reset! You can now see all questions again.");
    } else {
      alert(data.message || "Failed to reset question pool.");
    }
  } catch (err) {
    console.error("Error resetting question pool", err);
    alert("Unable to reset right now. Please try again later.");
  }
}

function nextQuestion() {
  const section = sections[currentSectionIndex];
  const questions = currentAptitudeQuestions[section.key] || [];
  if (currentQuestionIndex < questions.length - 1) {
    currentQuestionIndex++;
    renderCurrentQuestion();
  }
}

function prevQuestion() {
  if (currentQuestionIndex > 0) {
    currentQuestionIndex--;
    renderCurrentQuestion();
  }
}

function submitCurrentSection() {
  const section = sections[currentSectionIndex];
  const questions = currentAptitudeQuestions[section.key] || [];
  
  // Check if all questions answered
  let allAnswered = true;
  for (let i = 0; i < questions.length; i++) {
    const answerKey = `${section.key}-${i}`;
    if (answers[answerKey] === undefined) {
      allAnswered = false;
      break;
    }
  }
  
  if (!allAnswered) {
    if (!confirm("You haven't answered all questions. Do you want to submit this section anyway?")) {
      return;
    }
  }
  
  // Move to next section
  if (currentSectionIndex < sections.length - 1) {
    currentSectionIndex++;
    currentQuestionIndex = 0;
    renderCurrentQuestion();
  } else {
    // All sections complete, calculate scores and show results
    calculateAndShowResults();
  }
}

function calculateAndShowResults() {
  const scores = {
    quantitative: 0,
    logical: 0,
    verbal: 0,
  };

  sections.forEach((section) => {
    const questions = currentAptitudeQuestions[section.key] || [];
    let correct = 0;
    questions.forEach((q, index) => {
      const answerKey = `${section.key}-${index}`;
      const chosen = answers[answerKey];
      if (chosen !== undefined && chosen === q.answerIndex) {
        correct += 1;
      }
    });
    scores[section.key] = correct; // 1 mark per question, max 10
  });

  // Update local user object immediately for instant UI update
  const user = getStoredUser();
  if (user) {
    user.aptitudeScores = {
      quantitative: scores.quantitative,
      logical: scores.logical,
      verbal: scores.verbal,
      testTakenAt: new Date().toISOString()
    };
    saveUser(user);
  }

  // Save to database in background
  saveScores(scores);
  
  // Show results immediately with updated local data
  renderScores();
  closeAptitudeTest();
  openResultsScreen();
}

function renderResults() {
  if (!resultsContent) return;
  const scores = getStoredScores();
  
  if (!scores || !scores.testTakenAt) {
    resultsContent.innerHTML = `
      <div class="result-section">
        <h3>No Test Taken</h3>
        <p>You haven't taken the aptitude test yet. Please complete the test first.</p>
      </div>
    `;
    return;
  }
  
  const quantScore = scores.quantitative ?? 0;
  const logicScore = scores.logical ?? 0;
  const verbalScore = scores.verbal ?? 0;
  const average = ((quantScore + logicScore + verbalScore) / 3).toFixed(2);
  
  // Check if average is too low for recommendations
  const lowScore = parseFloat(average) <= 4;
  const warningMessage = lowScore ? `
    <div class="result-warning" style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin-bottom: 20px; border-radius: 5px;">
      <h4 style="color: #856404; margin: 0 0 10px 0;">⚠️ Score Too Low for Recommendations</h4>
      <p style="color: #856404; margin: 0;">Your average score is ${average} out of 10. You need to score above 4 to access career recommendations. Please attempt the test again to improve your score.</p>
    </div>
  ` : '';
  
  resultsContent.innerHTML = `
    ${warningMessage}
    <div class="result-section">
      <h3>Quantitative Aptitude</h3>
      <div class="result-score">${quantScore} / 10</div>
      <p>You scored ${quantScore} out of 10 questions.</p>
    </div>
    <div class="result-section">
      <h3>Logical Reasoning</h3>
      <div class="result-score">${logicScore} / 10</div>
      <p>You scored ${logicScore} out of 10 questions.</p>
    </div>
    <div class="result-section">
      <h3>Verbal & Communication</h3>
      <div class="result-score">${verbalScore} / 10</div>
      <p>You scored ${verbalScore} out of 10 questions.</p>
    </div>
    <div class="result-section result-average">
      <h3>Average Score</h3>
      <div class="result-score">${average} / 10</div>
      <p>Your overall aptitude average across all sections.</p>
      <p class="test-date">Test taken: ${new Date(scores.testTakenAt).toLocaleDateString()}</p>
    </div>
  `;
}

async function handleLoginSubmit(e) {
  e.preventDefault();
  const email = document.getElementById("login-email").value.trim();
  const password = document.getElementById("login-password").value;

  try {
    const res = await fetch(`${API_BASE}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const data = await res.json();
    if (data.ok) {
      const user = data.user;
      // store password locally for offline / fallback login only
      saveUser({ ...user, password });
      setSession(user.email);
      updateAuthBanner();
      buildStudentSummary(user);
      renderScores();
      closeAuthModal();
      showAptitudeSection();
      return;
    }

    // Fallback: try local profile if server auth failed/unavailable
    const localUser = getStoredUser();
    if (
      localUser &&
      localUser.email === email &&
      localUser.password === password
    ) {
      setSession(email);
      updateAuthBanner();
      buildStudentSummary(localUser);
      renderScores();
      closeAuthModal();
      showAptitudeSection();
      return;
    }

    alert(data.message || "Login failed. Please check your details.");
  } catch (err) {
    console.error("Login error", err);
    // Network error fallback
    const localUser = getStoredUser();
    if (
      localUser &&
      localUser.email === email &&
      localUser.password === password
    ) {
      setSession(email);
      updateAuthBanner();
      buildStudentSummary(localUser);
      renderScores();
      closeAuthModal();
      showAptitudeSection();
      return;
    }

    alert("Unable to login right now. Please try again in a moment.");
  }
}

async function handleSignupSubmit(e) {
  e.preventDefault();
  const fullName = document.getElementById("full-name").value.trim();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;
  const currentClass = document.getElementById("class").value;
  const stream = document.getElementById("stream").value;
  const tenthPercentage =
    document.getElementById("tenth-perc").value.trim() || null;
  const twelfthPercentage =
    document.getElementById("twelfth-perc").value.trim() || null;
  const cgpaSem = document.getElementById("cgpa-sem").value.trim() || null;

  if (!fullName || !email || !password || !currentClass) {
    alert("Please fill all required fields (marked with *).");
    return;
  }

  const ratings = collectRatings();
  const skills = collectCheckedChips("skills");
  const careerDomains = collectCheckedChips("career-domains");
  const higherStudies =
    document.getElementById("higher-studies").value || null;
  const entranceExams = collectMultiSelectValues("entrance-exams");
  const workEnvironment =
    document.getElementById("work-environment").value || null;
  const workStyles = collectMultiSelectValues("work-style");
  const financialConstraints =
    document.getElementById("financial-constraints").value || null;
  const locationRestrictions =
    document.getElementById("location-restrictions").value || null;
  const dreamCareer =
    document.getElementById("dream-career").value.trim() || null;
  const careerConfusion =
    document.getElementById("career-confusion").value.trim() || null;

  const userPayload = {
    fullName,
    email,
    password,
    class: currentClass,
    stream,
    tenthPercentage,
    twelfthPercentage,
    cgpaSem,
    ratings,
    skills,
    careerDomains,
    higherStudies,
    entranceExams,
    workEnvironment,
    workStyles,
    financialConstraints,
    locationRestrictions,
    dreamCareer,
    careerConfusion,
  };

  try {
    const res = await fetch(`${API_BASE}/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(userPayload),
    });
    const data = await res.json();
    if (!data.ok) {
      alert(data.message || "Could not save profile. Please try again.");
      return;
    }
    const user = data.user;
    // store password locally for offline / fallback login only
    saveUser({ ...user, password });
    setSession(user.email);
    updateAuthBanner();
    buildStudentSummary(user);
    renderScores();
    alert("Profile saved and account created successfully!");
    closeAuthModal();
    showAptitudeSection();
  } catch (err) {
    console.error("Signup error", err);
    alert("Unable to save profile right now. Please try again later.");
  }
}

function initNavigationGuards() {
  navLogin.addEventListener("click", () => {
    openAuthModal("login");
  });

  if (navSignup) {
    navSignup.addEventListener("click", () => {
      openAuthModal("signup");
    });
  }

  navAptitude.addEventListener("click", () => {
    if (!isLoggedIn()) {
      alert("Please login or create your profile to access aptitude section.");
      openAuthModal("login");
      return;
    }
    showAptitudeSection();
  });

  if (navContact) {
    navContact.addEventListener("click", () => {
      const contactSection = document.getElementById("contact-section");
      if (contactSection) {
        contactSection.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  }

  if (heroAptitudeBtn) {
    heroAptitudeBtn.addEventListener("click", () => {
      if (!isLoggedIn()) {
        alert(
          "Please login or create your profile to explore your aptitude guidance."
        );
        openAuthModal("login");
        return;
      }
      showAptitudeSection();
    });
  }

  if (heroLoginBtn) {
    heroLoginBtn.addEventListener("click", () => {
      openAuthModal("login");
    });
  }
}

function initLogout() {
  logoutBtn.addEventListener("click", () => {
    clearSession();
    clearUserUI();
    updateAuthBanner();
    closeAuthModal();
  });

  if (navLogoutBtn) {
    navLogoutBtn.addEventListener("click", () => {
      clearSession();
      clearUserUI();
      updateAuthBanner();
      closeAuthModal();
    });
  }
}

function clearUserUI() {
  // Clear student summary
  if (studentSummary) {
    studentSummary.innerHTML = '';
  }
  
  // Reset aptitude scores to placeholder
  if (quantitativeScoreEl) {
    quantitativeScoreEl.textContent = '-- / 10';
  }
  if (logicalScoreEl) {
    logicalScoreEl.textContent = '-- / 10';
  }
  if (verbalScoreEl) {
    verbalScoreEl.textContent = '-- / 10';
  }
  
  // Clear login form fields for security
  const loginEmailField = document.getElementById("login-email");
  const loginPasswordField = document.getElementById("login-password");
  if (loginEmailField) {
    loginEmailField.value = '';
  }
  if (loginPasswordField) {
    loginPasswordField.value = '';
  }
}

function initEditProfile() {
  editProfileBtn.addEventListener("click", () => {
    openAuthModal("signup");
    syncSignupFormWithStoredUser();
  });
}

function initForms() {
  loginForm.addEventListener("submit", handleLoginSubmit);
  signupForm.addEventListener("submit", handleSignupSubmit);
}

function initAptitudeTest() {
  if (startAptitudeBtn) {
    startAptitudeBtn.addEventListener("click", () => {
      startAptitudeTest();
    });
  }

  if (nextQuestionBtn) {
    nextQuestionBtn.addEventListener("click", () => {
      nextQuestion();
    });
  }

  if (prevQuestionBtn) {
    prevQuestionBtn.addEventListener("click", () => {
      prevQuestion();
    });
  }

  if (submitSectionBtn) {
    submitSectionBtn.addEventListener("click", () => {
      submitCurrentSection();
    });
  }

  if (closeResultsBtn) {
    closeResultsBtn.addEventListener("click", () => {
      closeResultsScreen();
    });
  }

  if (viewRecommendationsBtn) {
    viewRecommendationsBtn.addEventListener("click", () => {
      fetchRecommendations();
    });
  }

  if (closeRecommendationsBtn) {
    closeRecommendationsBtn.addEventListener("click", () => {
      closeRecommendationsScreen();
    });
  }
}

// Initial boot
document.addEventListener("DOMContentLoaded", () => {
  initRatingPills();
  initNavigationGuards();
  initForms();
  initLogout();
  initEditProfile();
  initAptitudeTest();

  if (authCloseBtn && authModal) {
    authCloseBtn.addEventListener("click", () => {
      closeAuthModal();
    });

    authModal.addEventListener("click", (e) => {
      if (e.target === authModal) {
        closeAuthModal();
      }
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        closeAuthModal();
      }
    });
  }

  if (loginPasswordToggle) {
    loginPasswordToggle.addEventListener("click", () => {
      const input = document.getElementById("login-password");
      if (!input) return;
      const isPassword = input.type === "password";
      input.type = isPassword ? "text" : "password";
    });
  }

  (async () => {
    const sessionEmail = getSession();
    if (sessionEmail) {
      const userFromServer = await fetchProfileFromServer(sessionEmail);
      if (userFromServer) {
        saveUser(userFromServer);
      }
    }
    if (isLoggedIn()) {
      const user = getStoredUser();
      updateAuthBanner();
      if (user) buildStudentSummary(user);
      showAptitudeSection();
      renderScores();
    } else {
      updateAuthBanner();
      renderScores();
      // Keep aptitude visible but empty until login
    }
  })();
});


