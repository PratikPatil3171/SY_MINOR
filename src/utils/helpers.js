/**
 * Helper function to shuffle array
 */
exports.shuffleArray = (array) => {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
};

/**
 * Sanitize user object by removing sensitive fields
 */
exports.sanitizeUser = (user) => {
  const safeUser = user.toObject ? user.toObject() : { ...user };
  delete safeUser.passwordHash;
  delete safeUser.__v;
  delete safeUser.password;
  return safeUser;
};
