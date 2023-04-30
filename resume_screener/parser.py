from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import time
from webdriver_manager.chrome import ChromeDriverManager

import PyPDF2
import docx2txt
import nltk
from pathlib import Path
from nltk.tokenize import sent_tokenize,word_tokenize
from nltk.corpus import stopwords
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import requests
from bs4 import BeautifulSoup
import pandas
import re
from pymongo import MongoClient

client=MongoClient()
client = MongoClient('mongodb://localhost:27017/')
mydatabase = client['resume_screening']
mycollection = mydatabase['info_table']

def __init__():

    driver = webdriver.Chrome("C:/Users/91913/anaconda3/Lib/site-packages/chromedriver_binary/chromedriver.exe")
    driver.get("https://linkedin.com/uas/login")
    time.sleep(5)
    username = driver.find_element(By.ID,"username")
    username.send_keys("username")
    pword = driver.find_element(By.ID,"password")
    pword.send_keys("password")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    def linkedin_exp(linkedin):
        if linkedin:
            lsr=linkedin[0].split('/')
            if lsr[-1]!='':
                linkedin_usr=lsr[-1]
            else:
                linkedin_usr=lsr[-2]
        else:
            return None

        profile_url = f"https://www.linkedin.com/in/{linkedin_usr}/details/experience/"

        driver.get(profile_url)
        start = time.time()
        initialScroll = 0
        finalScroll = 1000

        while True:
            driver.execute_script(f"window.scrollTo({initialScroll},{finalScroll})")
            initialScroll = finalScroll
            finalScroll += 1000
            time.sleep(3)
            end = time.time()
            if round(end - start) > 20:
                break
        src = driver.page_source
        soup = BeautifulSoup(src, 'lxml')

        exp=soup.find_all("div",{"class":"pvs-entity pvs-entity--padded pvs-list__item--no-padding-when-nested"})
        experience={}
        for i in range(len(exp)):
            x=exp[i].find_all('span',{'class':'visually-hidden'})
            experience[str(i)]=[]
            flag=1
            for j in x:
                if flag:
                    experience[str(i)].append(j.get_text())
                    for k in j.get_text().split():
                        if k in ['mos','yrs','yr','mon']:
                            flag=0

        total_exp=0
        for i in experience:
            x=experience[i][-1].split()
            for i in range(len(x)):
                if x[i] in ['mon','mos']:
                    total_exp+=int(x[i-1])/12
                if x[i] in ['yrs','yr']:
                    total_exp+=int(x[i-1])
        return {'experience':experience,'total_experience':round(total_exp,2)}

    resumes=[]
    resume_data=[]
    sp_char=['!','@','#','$','%','^','&','*','(',')','_','-','+','=','?','<','>','.',',',';',':','/n','',' ',"'"]
    address='C:/Users/91913/Desktop/Final_Year_Project/python_practise/resumes/'
    entries = Path(address)
    for entry in entries.iterdir():
        resumes.append(entry.name)
    #print(resumes)

    for resume in resumes:
        extension=resume.split('.')[-1]
        if(extension=='pdf'):
            x=PyPDF2.PdfReader(address+resume)
            page_numbers = len(x.pages)
            if page_numbers>=2:
                resume_data.append(x.pages[0].extract_text()+x.pages[1].extract_text())
            else:
                resume_data.append(x.pages[0].extract_text())
        elif(extension=='docx'):
            x = docx2txt.process(address+resume)
            resume_data.append(x)

    total_skills=[]
    csvFile1 = pandas.read_csv('C:/Users/91913/Desktop/Final_Year_Project/python_practise/total_skills.csv',encoding='ANSI')
    for i in csvFile1:
        total_skills.append(i)


    stop_words = set(stopwords.words('english'))
    refined_data=[]

    for resume in resume_data:
        words=word_tokenize(resume)
        for i in range(len(words)):
            words[i]=words[i].lower()
        for i in words:
            if(i in stop_words):
                words.remove(i)
        refined_data.append(words)

    def extract_email(data):
        email=re.findall(r'[A-Za-z0-9]*@[A-Za-z]*\.[a-z].{2}',data)
        return email

    def extract_github(data):
        github=re.findall(r'github.com/[A-Za-z0-9-_/&%!@#]*',data)
        return github

    def extract_linkedin(data):
        linkedin=re.findall(r'linkedin.com/[A-Za-z0-9-_/&%!@#]*',data)
        return linkedin

    def extract_phno(data):
        phoneno=re.findall(r'[0-9]{10}',data)
        return phoneno
    def github_user(link):
        usr=''
        str=link.split('?')
        temp=str[0].split('/')
        for i in range(len(temp)):
            if temp[i]=='github.com':
                usr=temp[i+1]
        return usr
    def bigrams(data):
        res=[]
        x=list(nltk.bigrams(data))
        for i in x:
            res.append(i[0]+" "+i[1])
        return res

    def trigrams(data):
        res=[]
        x=list(nltk.ngrams(data,3))
        for i in x:
            res.append(i[0]+" "+i[1]+" "+i[2])
        return res


    def get_skills(data):
        temp=[]
        text=data+bigrams(data)+trigrams(data)
        for skill in text:
            if skill in total_skills:
                temp.append(skill)
        return list(set(temp))

    def get_repo_details(usr,repo):
        URL = f"https://github.com/{usr}/{repo}/"
        r = requests.get(URL)
        soup = BeautifulSoup(r.content, 'html.parser')
    
        details = soup.find_all('li', attrs = {'class':'d-inline'})
        forks=soup.find('a',attrs={'class':'Link--secondary no-underline'})
        lang=[]
        for det in details:
            lang.append(det.get_text().strip())
        data={
            'lang':lang,
            'forks':forks.get_text().strip().split()[::-1][1],
        }
        return data


    def similarity(string):
        vectorizer=CountVectorizer().fit_transform(string)
        vectors=vectorizer.toarray()
        csm=cosine_similarity(vectors)
        def cosine_sim_vectors(v1,v2):
            v1=v1.reshape(1,-1)
            v2=v2.reshape(1,-1)
            return cosine_similarity(v1,v2)[0][0]
        return (cosine_sim_vectors(vectors[0],vectors[1]))

    def get_cgpa(resume):
        final_text=''
        for text in resume:
            if re.search("cgpa",text.lower()) or re.search("%",text.lower()):
                final_text+=text
            elif re.search("percentage",text.lower()) or re.search("gpa",text.lower()):
                final_text+=text
        x=re.findall("[0-9]+[.]?[0-9]+",final_text)
        res=[]
        for i in x:
            if i[:2]=='20' or i[:2]=='19':
                pass
            elif float(i)>=100:
                pass
            else:
                res.append(i)
        if res:
            if float(res[0])>10:
                return round(float(res[0])/9.5,2)
            elif float(res[0])<=4:
                return round(float(res[0])*10/4,2)
            else:
                return float(res[0])

    def has_experience(resume):
        exp_words=['intern','internship','experience','work experience']
        for text in resume:
            for exp in exp_words:
                if re.search(exp,text.lower()):
                    return "Yes"
        return "No"

    def has_certifications(data):
        for i in data:
            if re.search("certificat",i.lower()):
                return "Yes"
        return "No"

    def github_data(data):
        #Here data input is given in the form of resume_data[i]
        
        if extract_github(data):
            username=github_user(extract_github(data)[0])
        else:
            return ''
            
        #username=github_usr('https://github.com/nikki2606/')

        URL = "https://github.com/"+username+"?tab=repositories"
        r = requests.get(URL)
        repos=[]
    
        soup = BeautifulSoup(r.content, 'html.parser')

        repo_names = soup.find_all('a', attrs = {'itemprop':'name codeRepository'})
        for repo in repo_names:
            repos.append(repo.get_text().strip())
        repo_info={}
        for repo in repos:
            repo_info[repo]=get_repo_details(username,repo)
        
        langs=[]
        non_empty_repos=0
        for info in repo_info:
            if repo_info[info]['lang']:
                non_empty_repos+=1
                for i in repo_info[info]['lang']:
                    langs.append(i.split('\n')[0].lower())
        
        return {'git_info':repo_info,'langs_used':list(set(langs)),'valid_repos':non_empty_repos}


    def total_info():
        info={}
        cand_count=1
        for data in resume_data:
            ref_data=word_tokenize(data.lower())
            info[cand_count]={
                "_id":cand_count,
                'name':(" ".join(ref_data[:2])).title(),
                'email':extract_email(data)[0],
                'github':extract_github(data),
                'linkedin':extract_linkedin(data),
                'skills':get_skills(ref_data),
                'cgpa':get_cgpa(data.split('\n')),
                'experience':has_experience(data.split('\n')),
                'certifications':has_certifications(data.split('\n')),
                'linkedin_info':linkedin_exp(extract_linkedin(data)),
                'github_info':github_data(data)
            }
            req=mydatabase.info_table.insert_one(info[cand_count])
            cand_count+=1
    total_info()
