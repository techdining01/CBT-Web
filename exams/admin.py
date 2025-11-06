from django.contrib import admin
from .models import Class, Subject, Quiz, Question, Choice, StudentQuizAttempt, Answer
from .models import StudentQuizAttempt

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2


class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ('text', 'quiz', 'question_type', 'marks')


class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'is_published')
    list_filter = ('subject', 'is_published')


class AnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'is_pending')


admin.site.register(Class)
admin.site.register(Subject)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Answer, AnswerAdmin)


@admin.register(StudentQuizAttempt)
class StudentQuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("student", "quiz", "is_submitted", "score", "retake_allowed", "retake_count")
    list_filter = ("is_submitted", "retake_allowed")
    actions = ["allow_retake"]

    def allow_retake(self, request, queryset):
        updated = queryset.update(retake_allowed=True)
        self.message_user(request, f"{updated} attempt(s) granted retake")
    allow_retake.short_description = "Grant retake to selected students"
