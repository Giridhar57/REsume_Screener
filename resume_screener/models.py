from django.db import models

class jobDescription(models.Model):
    required_skills=models.CharField(max_length=200)
    min_cgpa=models.CharField(max_length=5)
    exp_required=models.CharField(max_length=5)
    required_cand_count=models.CharField(max_length=5)