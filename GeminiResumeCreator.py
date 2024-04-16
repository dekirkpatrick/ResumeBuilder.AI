import google.generativeai as genai
import os
import time
import re
from datetime import datetime
from MakeResume import makeResume,makeCoverLetter
 

# stepCount = 0
Key = 'AIzaSyDSprxt-5WkB5WCtt0Ie9cbbfkCojVTr5M'
genai.configure(api_key=Key)
model = genai.GenerativeModel('gemini-1.5-pro-latest')
chat = model.start_chat(history=[])

def checkResponse(response):
    if "no" in response.lower():
        raise("GenAI did not understand and glitched. Try again...")
    return 


def generateConversation(chatText):
    # print(chatText)
    # print("")
    # return "Experience"   
    # global stepCount 
    # stepCount += 1 
    # print(stepCount)
    response = chat.send_message(chatText)
    filteredResponse = [line.replace("foster","champion").replace("Foster","Champion").replace("Spearheaded","Pioneered").replace("spearheaded","pioneered").replace("Boosted","Increased").replace("boosted","increased").replace("Cultivated","Developed").replace("cultivated","developed").replace("*","").replace(".  ",". ") for line in (response.text).splitlines() if not line.startswith("@@@")]
    # print(response.text)
    # if stepCount < 9 + len(workExperienceProcessed):
    time.sleep(45)
    return "\n".join(filteredResponse)   
# def generateSingleResponse(chatText):
#     # print(chatText)
#     # print("")
#     # return "Experience"
#     response = model.generate_content(chatText)
#     # print(response.text)
#     time.sleep(5)
#     return response.text

def readFile(filePath):
    lines = []
    with open(filePath, 'r') as file:
        for line in file:
            lines.append(line.strip())
    return lines

def processConfig(readFileArray):
    sections = []
    sublist = []
    for item in readFileArray:
        if item == '':
            if sublist:
                sections.append(sublist)
                sublist = []
        else:
            sublist.append(item)
    if sublist:
        sections.append(sublist)
    return sections

def resumeBuilderMain(folder):
    print("Step 1: Prime GenAI as a resume writer")
    checkResponse(generateConversation("""I am re-writing my resume and I need your help. You are going to act as a professional resume writer skilled in presenting information concisely and using niche-appropriate language, while avoiding redundancy and cliché terms. Your task is to position my experience as a solution to my target company’s pain points, tailoring it specifically so that it’s clear that I can manage the primary requirements of the job. I want you to memorize these instructions for the duration of our session. Is that understood? Respond with yes or no only depending on your understanding"""))
    
    print("Step 2: Provide job description to GenAI")
    jobDescription = readFile(f'config/{folder}/job_description.txt')
    checkResponse(generateConversation(f"""First, I am going to provide you with the job description for the role I want to apply for. Can you read it carefully so that when I ask you questions about it later, you will reference the job description and provide me with accurate answers? Respond with yes or no only depending on your understanding: \n{' '.join(jobDescription[3:])}"""))
    
    print("Step 3: Prime company details prompt")
    checkResponse(generateConversation("""Now I am going to provide you with more information on the hiring company, so you can tailor my work experience more effectively to the hiring company’s needs. I want you to memorize this information so that you consider it when helping me rewrite my work experience later. Is that understood? Respond with yes or no only depending on your understanding"""))

    print("Step 4: Provide company details to GenAI")
    checkResponse(generateConversation(f"""Here are some details about the hiring company. The company's name is {jobDescription[1]}. Here is more information about the company: {jobDescription[2]}.\nDoes this make sense? Respond with yes or no only depending on your understanding"""))

    print("Step 5: Prime work experiences prompt")
    checkResponse(generateConversation(f"""I am about to give you my resume which contains detailed information about my past work experiences, a different job per prompt. I want you to thoroughly read and take into account each paragraph separated by a carriage return as a different project and, based on what is most relevant, rewrite and tailor 3 to 5 bullet points specifically for the {jobDescription[0]} job I sent to you previously. By “tailor”, I mean explain each bullet point using similar language to what's written in the job description. Is that understood? Respond with yes or no only depending on your understanding"""))
    
    print("Step 6: Build bulleted work experiences")
    workExperienceProcessed = []
    workExperience = readFile(f'config/user/work_experience.txt')
    sections = processConfig(workExperience[3:])
    for index,section in enumerate(sections):
        print(f"Step 6.{index + 1}: {section[0]} - {section[1]}")
        if len(section) < 3:
            continue
        job_title = section[0]
        company = section[1]
        dates = section[2]
        experiences = section[3:]
        statementCount = 3
        if index == 0:
            statementCount = 5 
        experiencesGenAI = generateConversation(f"""Rewrite this as {statementCount} results-driven achievement statement resume bullet points. Start each bullet with an action verb, followed by the task, and conclude with the result and return each bullet as a separate line. Each statement should be between 25 to 35 words long. Please quantify each statement using numbers, percentages, and dollar amounts or, if better fit, qualify them with results and proven effects instead: \n\n{chr(10).join(experiences)}""")
        workExperienceProcessed.append([company, job_title, dates, experiencesGenAI])
 
    print("Step 7: Produce technical skills")
    skills = readFile(f'config/user/skills.txt')
    sections = processConfig(skills)
    skillsProcessed = {}
    for section in sections:
        if len(section) < 2:
            continue
        skillsProcessed[section[0]] = section[1:] 
    skills_needed = readFile(f'config/{folder}/skills_needed.txt')
    technicalSkills = generateConversation(f"""Provide me with the most important technical skills required for the {jobDescription[0]} job description I sent to you earlier that would give me an advantage? Respond, in bullet points, with the top 3 skills from this list: {", ".join(skills_needed)}\n\nand top 2 skills from this list: {", ".join([skill for skill_list in skillsProcessed.values() for skill in skill_list])}. The response should only be 5 bullet points in total.""")#.strip().replace("\n", "")

    print("Step 8: Produce areas of expertise")
    expertiseAreas = generateConversation(f"""Provide me with 5 bullet points of the most common areas of expertise for a {jobDescription[0]} based on these areas: {", ".join(skills_needed)}. Only respond with the 5 bullet points.""")

    TempResume = f"""\n\nWork Experience: \n{''.join([element + chr(10) + chr(10) for element in [chr(10).join(inner_list) for inner_list in workExperienceProcessed]])} \nTechnical Skills: \n{chr(10).join([f"{skillHeading}: {', '.join(skills)}" for skillHeading, skills in skillsProcessed.items()])} \n\nAreas of Expertise: \n{expertiseAreas}"""
    
    print("Step 9: Produce Summary")
    # careerProfile = readFile(f'config/{folder}/career_profile.txt')
    professionalSummary = generateConversation(f"""Using my resume below and in a concise 2-4 sentence paragraph, summarize my professional experience, including only what's relevant to the {jobDescription[0]} job description I sent you earlier. Start with my role and what I specialize in in the first sentence. Then add my proven experience in the {workExperience[0]} field exceeding {workExperience[1]}. Highlight my achievements through one or two standout successes. List my key skills, focus on those most relevant to the job. Conclude with my overall strengths and what I offer {jobDescription[1]} to solve their unique problems. It should not contain any pronouns or {jobDescription[1]}'s name directly. Just result-driven statements. It should loosely follow this basic pattern:\n[Professional Title] with [Years of Experience] years of experience. Proven track record in [Top Achievement 1] and [Top Achievement 2]. Skilled in [Skill 1], [Skill 2], and [Skill 3]. Known for [Unique Value or Strength].\n\nMy resume: {TempResume}""")

    profile = readFile(f"config/user/profile.txt")    
    print("Step 10: Produce Cover Letter")
    companyAddress = readFile(f'config/{folder}/company_address.txt')
    coverLetterBody = generateConversation(f"""Using my resume below and in 250-350 words, write the body of a cover letter that summarizes my professional experience, including only what's relevant to the {jobDescription[0]} job description I sent you earlier. Showcase how my experience and expertise can address {jobDescription[1]}'s pain points. Write it using resume language, in the first person, making sure to highlight how I can directly help {jobDescription[1]}). This should start with "Dear Hiring Manager", the first sentence should be:"While I was browsing LinkedIn for new career opportunities, I found your listing for a {jobDescription[0]} at {jobDescription[1]} and immediately became excited for the chance to apply.", and end with "Sincerely, {profile[0]}". Do not use phrases like "track record" and "keen" and use only the most relevant experience in my resume to supplement the letter. My resume: {TempResume}""")    
    
    # print("Step 10: Produce Resume Suggestions")
    # resumeSuggestions = generateConversation(f"""Based on the {jobDescription[0]} job description that I sent you previously, what are the most important skills/experiences that I am missing on my resume for the job?""")
    
    
    education = readFile(f"config/user/education.txt")
    
    makeResume(jobDescription,professionalSummary,technicalSkills,skillsProcessed,workExperienceProcessed,expertiseAreas,profile,education)
    makeCoverLetter(profile,companyAddress,jobDescription,coverLetterBody)
    
    
if __name__ == "__main__":
    subdirectories = []
    for item in os.listdir('config'):
        if os.path.isdir(os.path.join('config', item)) and item != "user":
            subdirectories.append(item)
    for directory in subdirectories:
        print("")
        print("")
        print(f"Working on {directory}...")
        for i in range(5):
            print("")
            print(f"Iteration {i + 1}")
            resumeBuilderMain(directory)

    # print('')
    # print('')
    # print(jobDescription)
    # print(professionalSummary)
    # print(workExperienceProcessed)
    # print(skillsProcessed)
    # print(technicalSkills)
    # print(expertiseAreas)


    
    
