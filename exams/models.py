from django.db import models
from django.conf import settings
from django.utils import timezone



class Class(models.Model):

    CLASS_NAME_CHOICES = [
        ("JSS1", "Junior Secondary School 1"),
        ("JSS2", "Junior Secondary School 2"),
        ("JSS3", "Junior Secondary School 3"),
        ("SSS1", "Senior Secondary School 1"),  
        ("SSS2", "Senior Secondary School 2"),
        ("SSS3", "Senior Secondary School 3"),
    ]

    name = models.CharField(max_length=50, choices=CLASS_NAME_CHOICES, unique=True)  # e.g. JSS1, JSS2

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=100)
    school_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="subjects")

    def __str__(self):
        return f"{self.name} ({self.school_class})"



class Quiz(models.Model):
    school_class = models.ForeignKey("Class", on_delete=models.CASCADE, related_name="quizzes")
    subject = models.ForeignKey("Subject", on_delete=models.CASCADE, related_name="quizzes")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quizzes")
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(default=30)  # length of quiz in minutes
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)
    allow_retake = models.BooleanField(default=False)  # if true, students can ret
    max_retake_count = models.PositiveIntegerField(default=0)  # 0 = unlimited if allow_retake is True

    def __str__(self):
        return f"{self.title} ({self.subject})"
    
    def total_marks(self):
        return sum(q.marks for q in self.questions.all())



class Question(models.Model):
    QUESTION_TYPES = (
        ("objective", "Objective (single correct)"),
        ("subjective", "Subjective (free text)"),
    )

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    marks = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.text[:50]}  ... ({self.get_question_type_display()})"



class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'Correct' if self.is_correct else 'Wrong'})"


class StudentQuizAttempt(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quiz = models.ForeignKey("Quiz", on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)  # quiz expiry
    is_submitted = models.BooleanField(default=False)  # submitted or not
    submitted_at = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(default=0.0)  # score for the attempt
    graded = models.BooleanField(default=False)
    retake_allowed = models.BooleanField(default=False)  # ✅ admin/superadmin override
    retake_count = models.PositiveIntegerField(default=0)  # how many times student retook
    is_retake_approved = models.BooleanField(default=False)
    retake_requested = models.BooleanField(default=False)
    question_order = models.TextField(blank=True, null=True)  # comma-separated question IDs in order


    def can_resume(self):
        """Allow resume if attempt still within time and not submitted."""
        return not self.is_submitted and (self.end_time is None or timezone.now() < self.end_time)

    def can_retake(self):
        """Allow retake if admin has granted it, or quiz allows retakes globally."""
        return self.retake_allowed 

    def __str__(self):
        return f"{self.student} - {self.quiz} (Retakes: {self.retake_count})"



class Answer(models.Model):
    attempt = models.ForeignKey(StudentQuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.SET_NULL, null=True, blank=True)
    text_answer = models.TextField(blank=True, null=True)
    score = models.FloatField(default=0.0)
    graded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='graded_answers')
    graded_at = models.DateTimeField(auto_now_add=True)
    feedback = models.TextField(blank=True, null=True)
    is_pending = models.BooleanField(default=True)  # True for subjective until graded

    @classmethod
    def objective_score(cls, attempt):
        """Return total objective marks for a given attempt."""
        return cls.objects.filter(
            attempt=attempt,
            question__question_type="objective"
        ).aggregate(total=models.Sum("score"))["total"] or 0

    @classmethod
    def subjective_score(cls, attempt):
        """Return total subjective marks for a given attempt (graded only)."""
        return cls.objects.filter(
            attempt=attempt,
            question__question_type="subjective",
            is_pending=False
        ).aggregate(total=models.Sum("score"))["total"] or 0

    @classmethod
    def total_score(cls, attempt):
        """Return grand total (objective + graded subjective)."""
        return cls.objective_score(attempt) + cls.subjective_score(attempt)


    def __str__(self):
        return f"Answer by {self.attempt.student} for Q{self.question.id}"


class ActionLog(models.Model):
    ACTION_TYPES = (
        ('download', 'Download'),
        ('retake_request', 'Retake Request'),
        ('grade', 'Grade'),
        ('review', 'Review'),
        ('notification', 'Notification'),
        ('pended', 'Pended'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="action_logs")
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    model_name = models.CharField(max_length=100, blank=True, null=True)
    object_id = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(blank=True, null=True)  # optional
    
    def __str__(self):
        return f"{self.user} {self.action} @ {self.timestamp}"


class RetakeRequest(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={"role": "student"})
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=(("pending", "Pending"), ("approved", "Approved"), ("denied", "Denied")),
        default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="retake_reviews")

    def __str__(self):
        return f"{self.student.username} → {self.quiz.title} ({self.status})"


