def __init__(info,job_description):
    def cand_scores(job_desc,info):
        scores=[]
        for cand in info:
            res=0
            for skill in job_desc['required_skills']:
                if skill.lower() in info[cand]['skills']:
                    res+=1
            if info[cand]['cgpa']:
                if info[cand]['cgpa']>=job_desc['min_cgpa']:
                    res+=1
            if info[cand]['experience']=='Yes':
                res+=1
            if info[cand]['certifications']=='Yes':
                res+=1
            scores.append(res)
        return scores

    def compare_github(job_desc,n):
        res=0
        for i in info[n]['github_info']['git_info']:
            temp=[]
            langs=info[n]['github_info']['git_info'][i]['lang']
            if langs:
                for j in langs:
                    temp1=j.split('\n')[0].lower()
                    if temp1=='jupyter notebook':
                        temp.append('python')
                    else:
                        temp.append(temp1)
                for skill in job_desc['required_skills']:
                    if skill.lower() in temp:
                        res+=0.1
                        break
                res+=0.01
            res+=int(info[n]['github_info']['git_info'][i]['forks'])/100
        return res

    def refine_scores(info):
        for i in list(set(final_scores))[::-1]:
            if final_scores.count(i)>=2:
                for j in range(1,len(final_scores)+1):
                    if final_scores[j-1]==i:
                        if info[j]['github']:
                            final_scores[j-1]+=compare_github(job_description,j)
                        if info[j]['cgpa']:
                            final_scores[j-1]+=info[j]['cgpa']/100
                        if info[j]['linkedin']:
                            final_scores[j-1]+=info[j]['linkedin_info']['total_experience']/10
                            
    final_scores=cand_scores(job_description,info)
                        
    refine_scores(info)

    score_list=list(set(final_scores))
    score_list.sort()

    rankings=[]
    for i in score_list[::-1]:
        for j in range(1,len(final_scores)+1):
            if i==final_scores[j-1]:
                rankings.append(j)
    return {'ranks':rankings,'final_scores':final_scores}
