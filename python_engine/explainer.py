"""
Explanation Generator
Generates human-readable explanations for career recommendations
"""


class ExplanationGenerator:
    """Generates explanations for why careers were recommended"""
    
    def __init__(self):
        pass
    
    def generate_similarity_reason(self, student_profile, career_data, similarity_score):
        """
        Generate reason based on text similarity
        
        Args:
            student_profile: Dict with student data
            career_data: Dict with career information
            similarity_score: SBERT similarity score (0-10)
        
        Returns:
            str: Explanation text
        """
        goal_text = student_profile.get("goal_text", "").lower()
        career_title = career_data["title"]
        
        # Extract key matching phrases
        matching_phrases = []
        
        # Check for common keywords
        keywords = {
            "coding": ["coding", "programming", "software", "developer"],
            "design": ["design", "ui", "ux", "creative", "visual"],
            "data": ["data", "analytics", "statistics", "analysis"],
            "business": ["business", "entrepreneur", "startup", "company"],
            "engineering": ["engineering", "mechanical", "electrical", "civil"],
            "healthcare": ["medical", "doctor", "healthcare", "patient"],
            "finance": ["finance", "money", "investment", "banking"],
            "math": ["math", "mathematics", "calculations", "numbers"],
            "ai": ["ai", "machine learning", "ml", "artificial intelligence"],
            "cloud": ["cloud", "aws", "azure", "devops"],
            "security": ["security", "cybersecurity", "hacking", "protection"]
        }
        
        for category, words in keywords.items():
            if any(word in goal_text for word in words):
                matching_phrases.append(category)
        
        if similarity_score >= 8:
            strength = "strongly"
        elif similarity_score >= 6:
            strength = "well"
        else:
            strength = "reasonably"
        
        if matching_phrases:
            phrases_str = ", ".join(matching_phrases[:3])
            return f"Your aspirations {strength} align with {career_title}. Key matches: {phrases_str}."
        else:
            return f"Your goals and interests {strength} match the profile of a {career_title}."
    
    def generate_aptitude_reasons(self, student_profile, career_data, aptitude_score):
        """
        Generate reasons based on aptitude scores
        
        Args:
            student_profile: Dict with student data
            career_data: Dict with career information
            aptitude_score: Aptitude match score (0-10)
        
        Returns:
            list: List of aptitude-based reasons
        """
        reasons = []
        
        # Get top aptitudes
        aptitudes = {
            "quantitative reasoning": student_profile.get("apt_quant", 0),
            "logical thinking": student_profile.get("apt_logical", 0),
            "verbal communication": student_profile.get("apt_verbal", 0),
            "creative thinking": student_profile.get("apt_creative", 0),
            "technical skills": student_profile.get("apt_technical", 0),
            "commerce understanding": student_profile.get("apt_commerce", 0)
        }
        
        # Sort by score
        sorted_aptitudes = sorted(aptitudes.items(), key=lambda x: x[1], reverse=True)
        
        # Add top 2-3 aptitudes as reasons
        for apt_name, score in sorted_aptitudes[:3]:
            if score >= 7:
                reasons.append(f"Strong {apt_name} (score: {score}/10)")
            elif score >= 5:
                reasons.append(f"Good {apt_name} (score: {score}/10)")
        
        return reasons
    
    def generate_interest_reasons(self, student_profile, career_data):
        """
        Generate reasons based on interest alignment
        
        Args:
            student_profile: Dict with student data
            career_data: Dict with career information
        
        Returns:
            list: List of interest-based reasons
        """
        reasons = []
        
        # Get student interests
        interests = {
            "coding": student_profile.get("coding_interest", 0),
            "design": student_profile.get("design_interest", 0),
            "mathematics": student_profile.get("math_interest", 0),
            "science": student_profile.get("science_interest", 0),
            "business": student_profile.get("business_interest", 0),
            "working with people": student_profile.get("people_interest", 0),
            "creative work": student_profile.get("creative_interest", 0)
        }
        
        # Check which interests align with career
        career_interests = career_data.get("suitable_interests", "").lower()
        
        for interest_name, score in interests.items():
            if score >= 6:  # Strong interest
                # Check if this interest is relevant to the career
                interest_keywords = interest_name.split()
                if any(keyword in career_interests for keyword in interest_keywords):
                    reasons.append(f"High interest in {interest_name} ({score}/10)")
        
        # If no specific matches, add top interests
        if not reasons:
            sorted_interests = sorted(interests.items(), key=lambda x: x[1], reverse=True)
            for interest_name, score in sorted_interests[:2]:
                if score >= 6:
                    reasons.append(f"Interested in {interest_name} ({score}/10)")
        
        return reasons
    
    def generate_academic_reasons(self, student_profile, career_data):
        """
        Generate reasons based on academic performance
        
        Args:
            student_profile: Dict with student data
            career_data: Dict with career information
        
        Returns:
            list: List of academic-based reasons
        """
        reasons = []
        
        # Check relevant subject performance
        stream = student_profile.get("stream", "")
        career_stream = career_data.get("stream_tag", "")
        
        # STEM performance
        if "Science" in stream or "science" in career_stream.lower():
            math_pct = student_profile.get("maths_pct", 0)
            science_pct = student_profile.get("science_pct", 0)
            cs_pct = student_profile.get("cs_it_pct", 0)
            
            if math_pct >= 8:
                reasons.append(f"Excellent mathematics performance ({math_pct}/10)")
            if science_pct >= 8:
                reasons.append(f"Strong science background ({science_pct}/10)")
            if cs_pct >= 8:
                reasons.append(f"High CS/IT aptitude ({cs_pct}/10)")
        
        # Commerce performance
        if "Commerce" in stream or "commerce" in career_stream.lower():
            commerce_pct = student_profile.get("commerce_pct", 0)
            if commerce_pct >= 8:
                reasons.append(f"Strong commerce foundation ({commerce_pct}/10)")
        
        # Overall academic strength
        cgpa = student_profile.get("cgpa", 0)
        if cgpa >= 8.5:
            reasons.append(f"Outstanding academic performance (CGPA: {cgpa}/10)")
        elif cgpa >= 7.5:
            reasons.append(f"Strong academic record (CGPA: {cgpa}/10)")
        
        return reasons
    
    def generate_full_explanation(self, student_profile, career_data, scores):
        """
        Generate complete explanation for a career recommendation
        
        Args:
            student_profile: Dict with student data
            career_data: Dict with career information and scores
            scores: Dict with component scores
        
        Returns:
            dict: Structured explanation
        """
        explanation = {
            "summary": "",
            "match_strength": "",
            "key_reasons": [],
            "aptitude_match": [],
            "interest_match": [],
            "academic_fit": [],
            "recommendation_score": scores.get("total_score", 0)
        }
        
        # Generate match strength
        total_score = scores.get("total_score", 0)
        if total_score >= 8:
            explanation["match_strength"] = "Excellent Match"
            strength_text = "highly recommended"
        elif total_score >= 7:
            explanation["match_strength"] = "Very Good Match"
            strength_text = "strongly recommended"
        elif total_score >= 6:
            explanation["match_strength"] = "Good Match"
            strength_text = "recommended"
        else:
            explanation["match_strength"] = "Moderate Match"
            strength_text = "worth considering"
        
        # Summary
        career_title = career_data["title"]
        explanation["summary"] = f"{career_title} is {strength_text} based on your profile."
        
        # Key reasons (from similarity)
        similarity_score = scores.get("similarity_score", 0)
        similarity_reason = self.generate_similarity_reason(student_profile, career_data, similarity_score)
        explanation["key_reasons"].append(similarity_reason)
        
        # Aptitude match
        aptitude_score = scores.get("aptitude_score", 0)
        explanation["aptitude_match"] = self.generate_aptitude_reasons(student_profile, career_data, aptitude_score)
        
        # Interest match
        explanation["interest_match"] = self.generate_interest_reasons(student_profile, career_data)
        
        # Academic fit
        explanation["academic_fit"] = self.generate_academic_reasons(student_profile, career_data)
        
        return explanation
    
    def add_explanations_to_recommendations(self, student_profile, recommendations):
        """
        Add explanations to all recommended careers
        
        Args:
            student_profile: Dict with student data
            recommendations: List of career dicts with scores
        
        Returns:
            List of careers with added explanations
        """
        for career in recommendations:
            scores = {
                "total_score": career["total_score"],
                "similarity_score": career["similarity_score"],
                "aptitude_score": career["aptitude_score"],
                "interest_score": career["interest_score"]
            }
            
            explanation = self.generate_full_explanation(student_profile, career, scores)
            career["explanation"] = explanation
        
        return recommendations
