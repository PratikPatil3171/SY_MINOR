"""
Preprocessing Pipeline
Converts form data into clean, normalized student profiles
"""
import re


class StudentPreprocessor:
    """Handles student data preprocessing and normalization"""
    
    def __init__(self):
        pass
    
    def clean_text(self, text):
        """Clean free-text input"""
        if not text:
            return ""
        # Convert to lowercase
        text = text.lower()
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        return text.strip()
    
    def normalize_score(self, score, max_value=10):
        """Normalize scores to 0-10 scale"""
        if score is None:
            return 0
        try:
            score = float(score)
            if score > max_value:
                # If score is out of 100, convert to 10
                if max_value == 10 and score > 10:
                    score = (score / 100) * 10
            return min(max(score, 0), 10)  # Clamp between 0-10
        except (ValueError, TypeError):
            return 0
    
    def process_form_data(self, form_data):
        """
        Convert raw form data into standardized student profile
        
        Expected form_data structure:
        {
            "email": "student@example.com",
            "name": "John Doe",
            "stream": "Science",
            "classLevel": "12th",
            "marks10th": 85,
            "marks12th": 88,  # optional for 10th students
            "mathsPercent": 90,
            "sciencePercent": 88,
            "commercePercent": None,
            "englishPercent": 82,
            "csItPercent": 85,
            "interests": {
                "coding": 4,
                "design": 2,
                "math": 5,
                "science": 4,
                "business": 2,
                "people": 3,
                "creative": 3
            },
            "aptitude": {
                "quantitative": 8,
                "logical": 7,
                "verbal": 6,
                "creative": 5,
                "technical": 8,
                "commerce": 3
            },
            "dreamText": "I want to build software that helps people..."
        }
        """
        
        # Extract and clean text
        dream_text = self.clean_text(form_data.get("dreamText", ""))
        
        # Calculate overall CGPA/average
        marks_10th = self.normalize_score(form_data.get("marks10th", 0), 100)
        marks_12th = self.normalize_score(form_data.get("marks12th", 0), 100)
        cgpa = (marks_10th + marks_12th) / 2 if marks_12th > 0 else marks_10th
        
        # Extract interests (1-5 scale, normalize to 0-10)
        interests = form_data.get("interests", {})
        coding_interest = self.normalize_score(interests.get("coding", 0), 5) * 2
        design_interest = self.normalize_score(interests.get("design", 0), 5) * 2
        math_interest = self.normalize_score(interests.get("math", 0), 5) * 2
        science_interest = self.normalize_score(interests.get("science", 0), 5) * 2
        business_interest = self.normalize_score(interests.get("business", 0), 5) * 2
        people_interest = self.normalize_score(interests.get("people", 0), 5) * 2
        creative_interest = self.normalize_score(interests.get("creative", 0), 5) * 2
        
        # Extract aptitude scores (assume 0-10 scale)
        aptitude = form_data.get("aptitude", {})
        apt_quant = self.normalize_score(aptitude.get("quantitative", 0))
        apt_logical = self.normalize_score(aptitude.get("logical", 0))
        apt_verbal = self.normalize_score(aptitude.get("verbal", 0))
        apt_creative = self.normalize_score(aptitude.get("creative", 0))
        apt_technical = self.normalize_score(aptitude.get("technical", 0))
        apt_commerce = self.normalize_score(aptitude.get("commerce", 0))
        
        # Extract subject percentages
        maths_pct = self.normalize_score(form_data.get("mathsPercent", 0), 100)
        science_pct = self.normalize_score(form_data.get("sciencePercent", 0), 100)
        commerce_pct = self.normalize_score(form_data.get("commercePercent", 0), 100)
        english_pct = self.normalize_score(form_data.get("englishPercent", 0), 100)
        cs_it_pct = self.normalize_score(form_data.get("csItPercent", 0), 100)
        
        # Build student profile
        student_profile = {
            # Metadata
            "email": form_data.get("email", ""),
            "name": form_data.get("name", ""),
            "stream": form_data.get("stream", ""),
            "class_level": form_data.get("classLevel", ""),
            
            # Academic performance
            "cgpa": cgpa,
            "marks_10th": marks_10th,
            "marks_12th": marks_12th,
            "maths_pct": maths_pct,
            "science_pct": science_pct,
            "commerce_pct": commerce_pct,
            "english_pct": english_pct,
            "cs_it_pct": cs_it_pct,
            
            # Interests (0-10 scale)
            "coding_interest": coding_interest,
            "design_interest": design_interest,
            "math_interest": math_interest,
            "science_interest": science_interest,
            "business_interest": business_interest,
            "people_interest": people_interest,
            "creative_interest": creative_interest,
            
            # Aptitude scores (0-10 scale)
            "apt_quant": apt_quant,
            "apt_logical": apt_logical,
            "apt_verbal": apt_verbal,
            "apt_creative": apt_creative,
            "apt_technical": apt_technical,
            "apt_commerce": apt_commerce,
            
            # Free text
            "goal_text": dream_text
        }
        
        return student_profile
    
    def build_student_query_text(self, student_profile):
        """
        Build a comprehensive text query from student profile for embedding
        """
        parts = []
        
        # Add goal text (most important)
        if student_profile.get("goal_text"):
            parts.append(student_profile["goal_text"])
        
        # Add stream and class info
        parts.append(f"I am a {student_profile.get('stream', '')} student in {student_profile.get('class_level', '')}")
        
        # Add strong interests (threshold: >= 6/10)
        interests_map = {
            "coding": student_profile.get("coding_interest", 0),
            "design": student_profile.get("design_interest", 0),
            "mathematics": student_profile.get("math_interest", 0),
            "science": student_profile.get("science_interest", 0),
            "business": student_profile.get("business_interest", 0),
            "working with people": student_profile.get("people_interest", 0),
            "creative work": student_profile.get("creative_interest", 0)
        }
        
        strong_interests = [name for name, score in interests_map.items() if score >= 6]
        if strong_interests:
            parts.append(f"I am interested in {', '.join(strong_interests)}")
        
        # Add strong aptitudes
        aptitude_map = {
            "quantitative reasoning": student_profile.get("apt_quant", 0),
            "logical thinking": student_profile.get("apt_logical", 0),
            "verbal communication": student_profile.get("apt_verbal", 0),
            "creative thinking": student_profile.get("apt_creative", 0),
            "technical skills": student_profile.get("apt_technical", 0)
        }
        
        strong_aptitudes = [name for name, score in aptitude_map.items() if score >= 7]
        if strong_aptitudes:
            parts.append(f"I am good at {', '.join(strong_aptitudes)}")
        
        return ". ".join(parts) + "."
