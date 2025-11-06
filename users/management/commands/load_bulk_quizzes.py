from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from exams.models import Quiz, Question, Choice, Class, Subject
import random

User = get_user_model()

class Command(BaseCommand):
    help = "Load bulk quizzes for Math, Physics, Civic, Computer (JSS1-3) with objectives, subjectives, and multiple choice."

    def handle(self, *args, **kwargs):
        # Ensure admin user exists
        admin, _ = User.objects.get_or_create(username="superadmin", defaults={"id": User.objects.first().id})
        
        # Classes
        classes = {}
        for level in ["JSS1", "JSS2", "JSS3"]:
            classes[level], _ = Class.objects.get_or_create(name=level)

        # Subjects
        subjects = {}
        subject_names = ["Mathematics", "Physics", "Civic", "Computer"]
        for level, classx in classes.items():
            for subj in subject_names:
                subjects[(level, subj)], _ = Subject.objects.get_or_create(name=subj, class_assigned=classx)

        # Bulk Quizzes
        for (level, subj), subject in subjects.items():
            quiz, _ = Quiz.objects.get_or_create(
                title=f"{subj} Quiz - {level}",
                subject=subject,
                created_by=admin,
                defaults={"description": f"Auto-generated {subj} quiz for {level}"}
            )

            # Add Objective Questions
            for i in range(1, 4):
                q = Question.objects.create(
                    quiz=quiz,
                    question_text=f"{subj} Objective Q{i} ({level})",
                    question_type="objective",
                    marks=0,
                )
                # 4 choices
                correct = random.randint(1, 4)
                for j in range(1, 5):
                    Choice.objects.create(
                        question=q,
                        choice_text=f"Option {j}",
                        is_correct=(j == correct)
                    )

            # Add Subjective Questions
            for i in range(1, 3):
                Question.objects.create(
                    quiz=quiz,
                    question_text=f"{subj} Subjective Q{i} ({level}) - Explain briefly.",
                    question_type="subjective"
                )

            # Add Multiple Choice Questions
            for i in range(1, 3):
                q = Question.objects.create(
                    quiz=quiz,
                    question_text=f"{subj} Multi-Choice Q{i} ({level})",
                    question_type="multiple_choice"
                )
                # 4 choices, 2 correct
                corrects = random.sample([1, 2, 3, 4], 2)
                for j in range(1, 5):
                    Choice.objects.create(
                        question=q,
                        choice_text=f"Option {j}",
                        is_correct=(j in corrects)
                    )

        self.stdout.write(self.style.SUCCESS("✅ Bulk quizzes created for Math, Physics, Civic, Computer (JSS1-3)"))
