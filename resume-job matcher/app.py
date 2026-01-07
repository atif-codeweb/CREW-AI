from crewai import LLM
import os
import streamlit as st
from crewai import Agent,Task,Crew
import PyPDF2
from PyPDF2 import PdfReader
import re
from crewai.tools import tool

os.environ["GOOGLE_API_KEY"]=""##enter your google api key here
GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY")
llm=LLM(model="gemini/gemini-1.5-flash",api_key=GOOGLE_API_KEY)

def extract_from_pdf(uploaded_file):
  text=""
  reader=PdfReader(uploaded_file)
  for page in reader.pages:
    if page.extract_text():
      
      text+=page.extract_text()+"\n"
  return text


def clean_skill(skill:str)->str:
  """Normalize skill for better matching"""
  skill=skill.lower().strip()
  skill=re.sub(r"[^a-z0-9+\s]", "", skill)
  return skill
def compare_skills(resume_skills,job_skills):
  """return match,missing ,% overlap"""
  resume_set=set([clean_skill(s) for s in resume_skills])
  job_set=set([clean_skill(s) for s in job_skills])

  matched=list(resume_set & job_set)
  missed=list(job_set-resume_set)
  percent=(len(matched)/len(job_set)*100) if job_set else 0

  return{
    "match":matched,
    "missing":missed,
    "matched%":round(percent,2)
  }

@tool("compare_skills_tool")
def compare_skills_tool(resume_skills:list,job_skills:list)->dict:
  """deterministic tool for comparing job skills with resume skills"""
  return compare_skills(resume_skills,job_skills)



skill_extraction_agent=Agent(
    role="Skill Extractor",
    goal="Extract only clean list of skills from text",
    backstory="you are excellent at identifying skills from job descriptions and resume",
    llm=llm,
    verbose=True
)
matcher_agent=Agent(
    role="Matcher Agent",
    goal="compare job skills against resume skills and decide which are matching/missing",
    backstory="you are excellent at matching skills from job descriptions and resume",
    llm=llm,
    verbose=True,
    tools=[compare_skills_tool]
)
reporter_agent=Agent(
    role="Reporting Agent",
    goal="Summarize the matched and missed skill in clear way to the end user",
    backstory="you are excellent at summarizing skills from job descriptions and resume",
    llm=llm,
    verbose=True
)

st.set_page_config(page_title="Resume VS Job Skill Matcher",layout="wide")
st.title("RESUME VS JOB SKILL MATCHER")

upload_resume=st.file_uploader("Upload your resume(PDF): ",type=["pdf"])
job_desc=st.text_area("Write the job description")
if upload_resume and job_desc and st.button("Analyze Match"):
  with st.spinner("Extracting and analyzing...."):
    resume_text=extract_from_pdf(upload_resume)
    st.write("Resume Text Extracted:", resume_text[:500])  # first 500 chars
    st.write("Job Description Entered:", job_desc[:500])
    extract_job_skill = Task(
    description="Read the following job description text carefully. "
        "Return ONLY the exact skills explicitly written in the text. "
        "Do NOT infer or add extra skills. . Return ONLY a JSON array of strings, e.g. [\"Python\", \"Machine Learning\"].",
    agent=skill_extraction_agent,
    expected_output="JSON array of skills",
    output_key="job_skills"
)

    extract_resume_skill = Task(
        description="Read the following resume text carefully. "
        "Return ONLY the exact skills explicitly written in the text. "
        "Do NOT add extra skills, only return those actually present. Return ONLY a JSON array of strings, e.g. [\"Python\", \"Machine Learning\"].",
        agent=skill_extraction_agent,
        expected_output="JSON array of skills",
        output_key="resume_skills"
    )

    match_skill = Task(
    description="Use compare_skills_tool to compare resume_skills and job_skills. Return JSON with match, missing, and matched%.",
    agent=matcher_agent,
    expected_output="JSON with match, missing and matched%",
    output_key="comparison",
    inputs={"resume_skills": "{{resume_skills}}", "job_skills": "{{job_skills}}"}
)

    report_result = Task(
    description="Present the comparison results in a clear, user-friendly way.",
    agent=reporter_agent,
    expected_output="JSON with match, missing and matched%",
    inputs={"comparison": "{{comparison}}"}
)

    crew=Crew(
        agents=[skill_extraction_agent,matcher_agent,reporter_agent],
        tasks=[extract_job_skill,extract_resume_skill,match_skill,report_result]
    )

    result = crew.kickoff(inputs={
            "resume_text": resume_text,
            "job_description": job_desc
        })
    st.subheader("RESULT: ")
    st.json(result)