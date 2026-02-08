const bcrypt = require('bcryptjs');
const Student = require('../models/Student');

/**
 * Handle user signup - create or update student profile
 */
exports.signup = async (req, res) => {
  try {
    const payload = req.body;
    const { email, password } = payload;

    if (!email || !password) {
      return res.status(400).json({ 
        ok: false, 
        message: "Email and password are required." 
      });
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
    console.error("Error in signup:", err);
    if (err.code === 11000) {
      return res.status(400).json({ 
        ok: false, 
        message: "Email already exists." 
      });
    }
    res.status(500).json({ 
      ok: false, 
      message: "Internal server error." 
    });
  }
};

/**
 * Handle user login - verify credentials and track login timestamp
 */
exports.login = async (req, res) => {
  try {
    const { email, password } = req.body || {};
    
    if (!email || !password) {
      return res.status(400).json({ 
        ok: false, 
        message: "Email and password are required." 
      });
    }

    // Find student by email
    const student = await Student.findByEmail(email);
    if (!student || !student.passwordHash) {
      return res.status(401).json({ 
        ok: false, 
        message: "Invalid email or password." 
      });
    }

    // Verify password
    const isValid = await bcrypt.compare(password, student.passwordHash);
    if (!isValid) {
      return res.status(401).json({ 
        ok: false, 
        message: "Invalid email or password." 
      });
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
    console.error("Error in login:", err);
    res.status(500).json({ 
      ok: false, 
      message: "Internal server error." 
    });
  }
};
