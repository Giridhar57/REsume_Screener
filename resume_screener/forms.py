from django.forms import ModelForm
from django import forms
from .models import jobDescription

class JobDescription(ModelForm):
	required_skills=forms.TextInput()
	min_cgpa=forms.TextInput()
	exp_required=forms.TextInput()
	required_cand_count=forms.TextInput()
	class Meta:
		model=jobDescription
		fields=['required_skills','min_cgpa','exp_required','required_cand_count']