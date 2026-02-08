const Student = require('../models/Student');

/**
 * Get student profile by email
 */
exports.getProfile = async (req, res) => {
  try {
    const email = req.params.email;
    const student = await Student.findByEmail(email);
    
    if (!student) {
      return res.status(404).json({ 
        ok: false, 
        message: "Profile not found." 
      });
    }
    
    // Convert to plain object and remove sensitive data
    const safeUser = student.toObject();
    delete safeUser.passwordHash;
    delete safeUser.__v;
    
    res.json({ ok: true, user: safeUser });
  } catch (err) {
    console.error("Error in getProfile:", err);
    res.status(500).json({ 
      ok: false, 
      message: "Internal server error." 
    });
  }
};
