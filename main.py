import numpy as np 
import pandas as pd 
import os
resume_path = []
base_dir = "/kaggle/input/resume-dataset"


for root , dirs ,  files in os.walk(base_dir):
    for file in files:
        if file.endswith((".pdf" , ".docx" , ".txt")):

          resume_path.append(os.path.join(root , file))

!pip install docx2txt
!pip install pdfplumber
import docx2txt
import pdfplumber

def extract_text_from_pdf(resume_path):
    text = " "
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def clean_text(text):

    text = re.sub(r'\s+' , ' ' , text)

    text = re.sub(r'[^\x00-\x7F]+' , ' ' , text)
    return text.strip()


def preprocess_text(text):

    text = text.lower()

    tokens= text.split()
    return tokens 

import spacy
nlp = spacy.load("en_core_web_sm")

def extract_name(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    first_line = text.strip().split("\n")[0]

    if len(first_line.split()) <= 4:
        return first_line
    return None

def extract_email(text):
    email = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+' , text)
    if email:
        return email[0].lower().strip(";,")
    return None

def extract_phone(text):
    phone = re.findall(r'(\+?\d{1,3}[-\s]?)?\d{10}' , text)
    if phone:
        return phone[0].strip()
    return None

def extract_education(text):
    education_keywords = [ "b.tech", "b.e" , "m.tech" , "m.e" , "b.sc" , "m.sc" , "mba" , "phd" ,"bachelor" , "master" , "university" , "college" , "school"]

    lines = text.lower().split("\n")
    education = [line for line in lines if any(k in line.lower() for k in education_keywords)]
    return education if education else None


skills_db = ["python" , "java" , "c++" , "sql" , "tensorflow" , "keras" , "machinelearning" , "deep leaning"]

import re
def extract_skills(text):
    text_lower = text.lower()
    found = []
    for skill in skills_db:
        if re.search(r'\b' + re.escape(skill) + r'\b' , text_lower):
            found.append(skill)
    return list(set(found)) if found else None

def extract_experience(text):
    lines = text.split("\n")
    exp = [line for line in lines if "experience" in line.lower() or "intern" in line.lower()]
    return exp


def parse_resume(text):
    return {
        "name" : extract_name(text) ,
        "education" : extract_education(text) ,
        "skills": extract_skills(text) ,
        "experience" : extract_experience(text)    
    }

import os , pandas as pd

results = []

for path in resume_path:

    if path.endswith(".pdf"):
        text = extract_text_from_pdf(path)
    else:
        continue

    parsed = parse_resume(text)
    parsed["filename"] = os.path.basename(path)
    results.append(parsed)

df = pd.DataFrame(results)
df.to_csv("parsed_resumes.csv" , index = False)
 

for r in results:
    if not r.get('name'):
        r['name'] = 'Unknown'
    if not r.get('email'):
        r['email'] = 'Not found'



import json
with open("parsed_resumes.json" , "w") as f:
    json.dump(results , f , indent = 4)


print(len(results))










 

!pip install reportlab
import json
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate , Paragraph , Spacer , PageBreak
from reportlab.lib.styles import getSampleStyleSheet

styles = getSampleStyleSheet()
combined_filename = "Combined_Resumes.pdf"

doc = SimpleDocTemplate(combined_filename , pagesize = A4)

story = []

for idx, r in enumerate(results):
    name = r.get("name" , "Unknown")
    email = r.get("email", "Not found")
    education = r.get("education", "Not provided")
    experience  = r.get("experience" , "Not provided")
    skills = r.get("skills" , "Not provided")

    
    if not isinstance(education , list):
      education = [education]
    if not isinstance(experience , list):
      experience = [experience]
    
    story.append(Paragraph(f"<b>Role:</b>{name}" , styles['Title'])) 
    story.append(Spacer(1,12)) 
    story.append(Paragraph(f"<b>Experience:</b>" , styles['Heading2']))
    for exp in experience:
            story.append(Paragraph(f"* {exp}" , styles['Normal']))
    story.append(Spacer(1,12))
    
    story.append(Paragraph(f"<b>Education:</b>" , styles['Heading2']))
    for edu in education:
             story.append(Paragraph(f"* {edu}" , styles['Normal']))
    story.append(Spacer(1,12))

    story.append(Spacer(1,24))
    story.append(PageBreak())

doc.build(story)
print(f"PDF generated: {combined_filename}")
