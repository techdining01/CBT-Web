# quizzes/forms.py
from django import forms
from .models import Quiz, Question, Choice, Subject, Class

class QuizCreateForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'subject', 'duration_minutes', 'is_published']

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type', 'marks']

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text', 'is_correct']



class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['name',]

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Create Class'}),
        }


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'school_class']
        
        widgets = {
        'name': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Create Subject'}),
        'school_class': forms.Select(attrs={'class': 'form-control '}),
        }
