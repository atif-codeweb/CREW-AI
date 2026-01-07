from  crewai import LLM
import os
import streamlit as st
from crewai import Agent,Task,Crew
os.environ["GOOGLE_API_KEY"]="AIzaSyDLZuWUjaYQuoY9mypkA8brwUMVl0b2pWM"

GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY")
llm=LLM(model="gemini/gemini-2.0-flash",api_key=GOOGLE_API_KEY)

bug_detector=Agent(
    role="Bug Detector",
    goal="Identify coding mistakes and potential logical error in student submission",
    backstory="former compiler spirit,now dedicated to spotting errors before they frustrate learners",
    llm=llm,
    verbose=True
)
hint_generator=Agent(
    role="Hine Generator",
    goal="provide hints to the student so that they can fix the errors in their code",
    backstory="once a patient tutor,now reborn as AI whispherer of subtle guidance",
    llm=llm,
    verbose=True
)
code_optimizer=Agent(
    role="Code Optimizer",
    goal="suggest efficient algorithm and cleaner code to increase the complexity",
    backstory=" Ex-performance engineer turned mentor, obsessed with making every line faster and smarter.",
    llm=llm,
    verbose=True
)
teaching_agent=Agent(
    role="Teaching Agent",
    goal="Explains the reason behind the bug in your code in simple terms ",
    backstory="a retired professor who live as an AI story teller of coding wisdom",
    llm=llm,
    verbose=True
)
evaluator_agent=Agent(
    role="Performance Evaluator",
    goal="Assess student performance and suggest improvements",
    backstory="An insightful mentor who helps student grow",
    llm=llm,
    verbose=True
)
motivation_agent=Agent(
    role="Motivation Agent",
    goal="keep the student motivated and engaged",
    backstory="a supportive mentor who believes in the power of posiitve reinforcement",
    llm=llm,
    verbose=True
)
st.title("Debugging Mentor System")
st.write("Enter your coding problem below and let the AI agent  help you debug your code")
problem_statement=st.text_area("Problem Statement","")
student_code=st.text_area("Your code",height=200)
student_level=st.selectbox("your level",["beginner","Intermediate","Advance"])
if st.button("Run Debugger"):
  if problem_statement.strip()=="" or student_code.strip()=="":
    st.warning("Please enter both problem statement and student code")
  else:
    task1=Task(
        description=(
            f"debug the following student submission.\n\n"
            f"Problem Statement:{problem_statement}\n\n"
            f"Student Code:{student_code}\n\n"
            f"Student Level:{student_level}"
            f"identify bugs in the code"
        ),
        agent=bug_detector,
        expected_output="Detailed debugging feedback of bugs in the code"
        )
    task2=Task(
        description=(
            f"provide hints to guide student in debugging the code step-by-step\n\n"
            f"problem statement:{problem_statement}\n\n"
            f"student code:{student_code}\n\n"
            f"student level:{student_level}\n\n"
            f"provide hints instead of direct answer,adaptive to student level"
        ),
        agent=hint_generator,
        expected_output="hints to guide the student in debugging the code"
    )
    task3=Task(
        description=(
            f"optimize the code for better efficiency\n\n"
            f"problem statement:{problem_statement}\n\n"
            f"student code:{student_code}\n\n"
            f"student level:{student_level}\n\n"
            f"suggest ways to make the code optimal interms of efficiency/complexity"
        ),
        agent=code_optimizer,
        expected_output="optimized code with clear explanation of improvements"
    )
    task4=Task(
        description=(
            f"explain the reason behind the bug in the code\n\n"
            f"problem statement:{problem_statement}\n\n"
            f"student code:{student_code}\n\n"
            f"student level:{student_level}\n\n"
            f"act as a mentor and explain why the bug occurred and how to avoid the bug"
        ),
        agent=teaching_agent,
        expected_output="detailed explanation of why the bug occurred and how to avoid it"
    )
    task5=Task(
        description=(
            f"evaluate the student performance and provide a detailed feedback\n\n"
        ),
        agent=evaluator_agent,
        expected_output="detailed output on student performance"
    )
    task6 = Task(
        description="Motivate the student and encourage them to keep learning.",
        agent=motivation_agent,
        expected_output="A short motivational message tailored to the student's level and progress."
    )
    crew=Crew(
        agents=[bug_detector,hint_generator,code_optimizer,teaching_agent,evaluator_agent,motivation_agent],
        tasks=[task1,task2,task3,task4,task5,task6],
        verbose=True
    )
    with st.spinner("The AI debugger is analyzing the code"):
      result=crew.kickoff(
          inputs={
              "problem_statement":problem_statement,
              "student_code":student_code,
              "student_level":student_level
          }
      )
    st.subheader("DEBUGGER REPORT: ")
    st.write(result)