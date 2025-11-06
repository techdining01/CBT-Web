from django.core.management.base import BaseCommand
from exams.models import Quiz, Question


class Command(BaseCommand):
    help = "Link unassigned questions to the latest quiz (or create one if missing)."

    def handle(self, *args, **options):
        quiz, created = Quiz.objects.get_or_create(
            title="General Quiz",
            defaults={
                "subject_id": 1,  # ⚠️ replace with an actual Subject ID
                "school_class_id": 1,  # ⚠️ replace with an actual Class ID
                "created_by_id": 1,  # ⚠️ replace with an actual User ID (teacher/admin)
            }
        )

        unassigned = Question.objects.filter(quiz__isnull=True)
        count = unassigned.count()

        for q in unassigned:
            q.quiz = quiz
            q.save()

        self.stdout.write(self.style.SUCCESS(
            f"Linked {count} questions to quiz: {quiz.title}"
        ))
