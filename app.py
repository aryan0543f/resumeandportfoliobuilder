import streamlit as st
import google.generativeai as genai
import time

# Configure Gemini API
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "AIzaSyC9Mebz2gGOxxnPPgJD6kgzIzhTv-bQQbU")  # Get new key from https://aistudio.google.com/app/apikey

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')  # Using stable version

class StudentProfile:
    def __init__(self, name, education, skills, experience, projects):
        self.name = name
        self.education = education
        self.skills = skills
        self.experience = experience
        self.projects = projects

def create_llm_prompt_from_profile(student_profile):
    prompt_parts = []
    prompt_parts.append(f"Student Name: {student_profile.name}")
    prompt_parts.append(f"Education: {student_profile.education}")
    
    if student_profile.skills:
        prompt_parts.append("Skills:")
        for skill in student_profile.skills:
            prompt_parts.append(f"- {skill}")
    
    if student_profile.experience:
        prompt_parts.append("Experience:")
        for exp in student_profile.experience:
            prompt_parts.append(f"- {exp}")
    
    if student_profile.projects:
        prompt_parts.append("Projects:")
        for project in student_profile.projects:
            prompt_parts.append(f"- {project}")
    
    return "\n".join(prompt_parts)

def mock_llm_generate(prompt):
    """Mock LLM that generates realistic responses"""
    if "professional summary" in prompt.lower() or "resume summary" in prompt.lower():
        return "Highly motivated Data Science professional with strong expertise in machine learning, statistical modeling, and data visualization. Proven track record of developing predictive models and analyzing complex datasets. Proficient in Python, SQL, and cloud platforms with hands-on experience in real-world projects."
    
    elif "accomplishment" in prompt.lower():
        return "• Developed and deployed machine learning models that improved prediction accuracy by 25%\n• Analyzed datasets containing 1M+ records using Python and SQL\n• Collaborated with cross-functional teams to deliver data-driven insights"
    
    elif "cover letter" in prompt.lower():
        return """Dear Hiring Manager,

I am writing to express my strong interest in the Data Scientist position. With a Master's degree in Data Science and hands-on experience in machine learning and statistical modeling, I am confident in my ability to contribute effectively to your team.

During my internship at Tech Innovations Inc., I developed predictive models for customer churn that achieved 85% accuracy, directly impacting customer retention strategies. My academic research involved analyzing large-scale bioinformatics datasets, where I honed my skills in Python, SQL, and data visualization tools.

I am particularly drawn to this opportunity because it aligns perfectly with my expertise in machine learning and cloud computing. My proficiency in AWS and GCP, combined with my strong analytical skills, positions me well to tackle the challenges outlined in your job description.

I am excited about the possibility of bringing my technical skills and passion for data science to your organization. Thank you for considering my application.

Sincerely,
[Your Name]"""
    
    elif "portfolio" in prompt.lower() or "project description" in prompt.lower():
        return """This project demonstrates advanced natural language processing capabilities by implementing a sentiment analysis system for social media data. 

**Key Achievements:**
• Built a deep learning model using TensorFlow achieving 92% accuracy on sentiment classification
• Processed and analyzed over 500,000 social media posts using NLP techniques
• Implemented data preprocessing pipeline including tokenization, lemmatization, and feature extraction
• Deployed the model as a REST API for real-time sentiment prediction

**Technologies Used:** Python, TensorFlow, NLTK, Pandas, Flask

**Impact:** The system successfully classified sentiment with high accuracy, providing valuable insights for brand monitoring and customer feedback analysis."""
    
    return "Generated content based on your profile."

def gemini_generate(prompt):
    """Generate content using Google Gemini AI with retry logic"""
    max_retries = 3
    retry_delay = 7  # Wait 7 seconds between retries
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                if attempt < max_retries - 1:
                    st.warning(f"⏳ Rate limit reached. Waiting {retry_delay} seconds before retry...")
                    time.sleep(retry_delay)
                    continue
                else:
                    return "⚠️ Rate limit exceeded. Please wait a minute and try again. Free tier allows 5 requests per minute."
            else:
                return f"Error generating content: {error_msg}"
    
    return "Failed to generate content after multiple retries."

def generate_ai_summary(student_profile, llm_function):
    base_prompt = create_llm_prompt_from_profile(student_profile)
    summary_instruction = "\n\nGenerate a professional resume summary (2-3 sentences) highlighting key skills and experiences."
    return llm_function(base_prompt + summary_instruction)

def generate_ai_accomplishment_bullet(student_profile, item_description, llm_function):
    base_prompt = create_llm_prompt_from_profile(student_profile)
    bullet_instruction = f"\n\nTransform this into accomplishment-driven bullet points: '{item_description}'"
    return llm_function(base_prompt + bullet_instruction)

def generate_ai_cover_letter(student_profile, llm_function, job_description=None):
    base_prompt = create_llm_prompt_from_profile(student_profile)
    cover_letter_instruction = "\n\nGenerate a professional cover letter (3-5 paragraphs) highlighting relevant skills and experiences."
    
    if job_description:
        cover_letter_instruction += f"\n\nTailor to this job: {job_description}"
    
    return llm_function(base_prompt + cover_letter_instruction)

def generate_ai_portfolio_project_description(student_profile, project_description, llm_function):
    base_prompt = create_llm_prompt_from_profile(student_profile)
    project_instruction = f"\n\nGenerate detailed portfolio description for: '{project_description}'"
    return llm_function(base_prompt + project_instruction)

# Streamlit App
st.set_page_config(page_title="AI Resume & Portfolio Builder", page_icon="📄", layout="wide")

st.title("🎓 AI Resume & Portfolio Builder")
st.markdown("Generate professional resumes, cover letters, and portfolio content powered by AI")

# Sidebar for input
with st.sidebar:
    st.header("Your Information")
    
    name = st.text_input("Full Name", "Alice Smith")
    education = st.text_area("Education", "Master of Science in Data Science, University of Example (2023)")
    
    st.subheader("Skills")
    skills_input = st.text_area("Enter skills (one per line)", 
                                 "Python\nSQL\nMachine Learning\nDeep Learning\nData Visualization\nCloud Computing (AWS, GCP)")
    skills = [s.strip() for s in skills_input.split("\n") if s.strip()]
    
    st.subheader("Experience")
    exp_input = st.text_area("Enter experience (one per line)",
                              "Data Scientist Intern at Tech Innovations Inc. (Summer 2022): Developed predictive models\nResearch Assistant at University (2021-2023): Analyzed large datasets")
    experience = [e.strip() for e in exp_input.split("\n") if e.strip()]
    
    st.subheader("Projects")
    proj_input = st.text_area("Enter projects (one per line)",
                               "Sentiment Analysis of Social Media Data: Built deep learning model\nE-commerce Recommendation System: Implemented collaborative filtering")
    projects = [p.strip() for p in proj_input.split("\n") if p.strip()]
    
    job_description = st.text_area("Job Description (Optional)", 
                                    "Data Scientist role requiring ML, Python, SQL, and cloud platforms")

# Create profile
profile = StudentProfile(name, education, skills, experience, projects)

# Main content tabs
tab1, tab2, tab3, tab4 = st.tabs(["📝 Resume", "✉️ Cover Letter", "💼 Portfolio", "📄 Full Document"])

with tab1:
    st.header("AI-Generated Resume Sections")
    
    if st.button("Generate Resume Content", key="resume"):
        with st.spinner("Generating with Google Gemini AI..."):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Professional Summary")
                summary = generate_ai_summary(profile, gemini_generate)
                st.info(summary)
                
                st.subheader("Skills")
                st.write(", ".join(skills))
            
            with col2:
                if experience:
                    st.subheader("Enhanced Experience")
                    bullets = generate_ai_accomplishment_bullet(profile, experience[0], gemini_generate)
                    st.success(bullets)
                
                if projects:
                    st.subheader("Enhanced Project")
                    proj_bullets = generate_ai_accomplishment_bullet(profile, projects[0], gemini_generate)
                    st.success(proj_bullets)

with tab2:
    st.header("AI-Generated Cover Letter")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Generate General Cover Letter"):
            with st.spinner("Writing cover letter with Gemini AI..."):
                cover_letter = generate_ai_cover_letter(profile, gemini_generate)
                st.text_area("Cover Letter", cover_letter, height=400)
    
    with col2:
        if job_description and st.button("Generate Tailored Cover Letter"):
            with st.spinner("Tailoring cover letter with Gemini AI..."):
                tailored_letter = generate_ai_cover_letter(profile, gemini_generate, job_description)
                st.text_area("Tailored Cover Letter", tailored_letter, height=400)

with tab3:
    st.header("Portfolio Project Descriptions")
    
    if projects:
        selected_project = st.selectbox("Select a project", projects)
        
        if st.button("Generate Portfolio Description"):
            with st.spinner("Creating portfolio content with Gemini AI..."):
                portfolio_desc = generate_ai_portfolio_project_description(profile, selected_project, gemini_generate)
                st.markdown(portfolio_desc)

with tab4:
    st.header("Complete Professional Document")
    
    st.warning("⚠️ Note: Generating full document makes multiple API calls. Free tier limit: 5 requests/minute. This may take 1-2 minutes.")
    
    if st.button("Generate Full Document", type="primary"):
        with st.spinner("Assembling complete document with Gemini AI..."):
            st.markdown(f"# {name}")
            st.markdown("---")
            
            st.markdown("## Professional Summary")
            summary = generate_ai_summary(profile, gemini_generate)
            st.write(summary)
            time.sleep(7)  # Wait between API calls
            
            st.markdown("## Skills")
            st.write(", ".join(skills))
            
            st.markdown("## Experience")
            for i, exp in enumerate(experience):
                st.markdown(f"**{exp}**")
                bullets = generate_ai_accomplishment_bullet(profile, exp, gemini_generate)
                st.write(bullets)
                if i < len(experience) - 1:
                    time.sleep(7)  # Wait between API calls
            
            st.markdown("## Projects")
            for i, proj in enumerate(projects):
                st.markdown(f"**{proj}**")
                proj_bullets = generate_ai_accomplishment_bullet(profile, proj, gemini_generate)
                st.write(proj_bullets)
                if i < len(projects) - 1:
                    time.sleep(7)  # Wait between API calls
            
            st.markdown("---")
            st.markdown("## Cover Letter")
            time.sleep(7)  # Wait before final API call
            cover = generate_ai_cover_letter(profile, gemini_generate, job_description if job_description else None)
            st.write(cover)

st.sidebar.markdown("---")
st.sidebar.success("🤖 Powered by Google Gemini AI")
st.sidebar.warning("⚠️ Free tier: 5 requests/minute")
st.sidebar.info("💡 Tip: Use individual tabs to avoid rate limits. Wait 1 minute between full document generations.")

