from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Class, Subject, Quiz, Question, Choice
from accounts.models import TeacherProfile
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Load sample quiz questions for all classes and subjects'

    def handle(self, *args, **kwargs):
        classes = ['JSS1', 'JSS2', 'JSS3', 'SSS1', 'SSS2', 'SSS3']
        subjects_per_class = ['Mathematics', 'English', 'Basic Science', 'Social Studies', 'Civic Education', 'Computer', 'Agriculture']
        teacher = User.objects.filter(role='teacher').first() or User.objects.filter(role='admin').first()

        if not teacher:
            self.stdout.write(self.style.ERROR("No teacher or admin user found. Please create one first."))
            return

        for class_name in classes:
            class_obj, _ = Class.objects.get_or_create(name=class_name)

            for subject_name in subjects_per_class:
                subject, _ = Subject.objects.get_or_create(name=subject_name, class_assigned=class_obj)

                quiz = Quiz.objects.create(
                    subject=subject_name,
                    class_assigned=class_obj,
                    created_by=teacher,
                    description=f"{subject_name} quiz for {class_name}",
                    duration=30,
                )

                for i in range(1, 6):
                    q_type = random.choice(['objective', 'subjective', 'multiple_choice'])
                    question = Question.objects.create(
                        quiz=quiz,
                        question_text=f"{q_type.title()} Question {i} for {subject_name} ({class_name})",
                        question_type=q_type,
                        max_score=5,
                    )

                    if q_type in ['objective', 'multiple_choice']:
                        for j in range(1, 5):
                            Choice.objects.create(
                                question=question,
                                choice_text=f"Option {j}",
                                is_correct=(j == 1 if q_type == 'objective' else random.choice([True, False]))
                            )

        self.stdout.write(self.style.SUCCESS("✅ Sample quizzes and questions loaded successfully."))
