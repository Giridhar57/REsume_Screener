from django.shortcuts import render, redirect
from django.http import HttpResponse
from . import parser
from . import results
from .forms import JobDescription
from .models import jobDescription

from pymongo import MongoClient
client=MongoClient()
client = MongoClient('mongodb://localhost:27017/')
mydatabase = client['resume_screening']
mycollection = mydatabase['info_table']

query=mydatabase.info_table.find()

job_description={}
jd=list(jobDescription.objects.all().values())[-1]
job_description['required_skills']=jd['required_skills'].split(',')
job_description['min_cgpa']=float(jd['min_cgpa'])
job_description['exp_required']=jd['exp_required']
job_description['required_cand_count']=int(jd['required_cand_count'])

def getJobDescription(request):
    if request.POST:
        form=JobDescription(request.POST)
        form.save()
        job_description['required_skills']=form.data['required_skills'].split(',')
        job_description['min_cgpa']=float(form.data['min_cgpa'])
        job_description['exp_required']=form.data['exp_required']
        job_description['required_cand_count']=int(form.data['required_cand_count'])
        print(job_description)
        return redirect(screened)
    return render(request,'jobdesc.html',{'form':JobDescription})

names=[]
ids=[]
res=[]
info={}
temp=1
for i in query:
    info[temp]=i
    temp+=1
for i in info:
    res.append(info[i])

for j in range(len(res)):
    temp5=[]
    if res[j]['linkedin_info']:
            for i in res[j]['linkedin_info']['experience']:
                temp5.append(res[j]['linkedin_info']['experience'][i])
            res[j]['linkedin_info']['experience']=temp5

def home(request):
    for i in range(len(res)):
        res[i]['slno']=i+1
    return render(request,'home.html',context={'data':res})

def screened(request):
    ranks=results.__init__(info,job_description)['ranks']
    scores=results.__init__(info,job_description)['final_scores']
    scores.sort()
    for i in ranks:
        names.append(info[i]['name'])
        ids.append(info[i]['_id'])
    temp=[]
    count=1
    for i in ranks:
        res[i-1]['count']=count
        res[i-1]['score']=scores[::-1][count-1]
        res[i-1]['rank']=i
        count+=1
        temp.append(res[i-1])


    return render(request,'screened.html',context={'temp':temp,'job_description':job_description})

def details(request,id):
    data=res[int(id)-1]
    github_data=[]
    temp3=1
    if(data['github_info']):
        for i in data['github_info']['git_info']:
            temp=[]
            temp.append(f'{temp3}. {i}')
            temp3+=1
            if(data['github_info']['git_info'][i]['lang']):
                temp2=[]
                for j in data['github_info']['git_info'][i]['lang']:
                    temp2.append(' - '.join(j.split('\n')))
                temp.append("Languages Used: "+", ".join(temp2))
                temp.append("Forks: "+data['github_info']['git_info'][i]['forks'])
            github_data.append(temp)

        print("hello")
    name=res[int(id)-1]['name']
    return render(request,'details.html',context={'data':res[int(id)-1],'title':name,'github_data':github_data})
