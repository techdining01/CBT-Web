# exams/management/commands/seed_quizzes.py
from django.core.management.base import BaseCommand
from exams.models import Quiz, Question, Choice, Subject, Class
from users.models import User
from django.utils import timezone


class Command(BaseCommand):
    help = "Load quizzes for 7 subjects and 3 classes (SSS1-SSS3) with sample questions (objective + subjective)"

    def handle(self, *args, **kwargs):
        teacher = User.objects.filter(role__in=["superadmin", "admin", "teacher"]).first()
        if not teacher:
            self.stdout.write(self.style.ERROR("❌ No teacher found. Please create a teacher user."))
            return

        subjects = [
            "Computer", "Mathematics", "Economics",
            "Physics", "Biology", "English", "Chemistry"
        ]
        classes = ["SSS1", "SSS2", "SSS3"]

        question_bank = {
            "Computer": {
                "objective": [
                    {"q": "What does CPU stand for?",
                     "opts": ["Central Processing Unit", "Computer Personal Unit", "Control Program Utility", "Central Program Unit"],
                     "ans": "Central Processing Unit"},
                    {"q": "Which is used to input data?",
                     "opts": ["Monitor", "Printer", "Keyboard", "Speaker"],
                     "ans": "Keyboard"},
                ],
                "subjective": [
                    "Explain the role of a motherboard in a computer system."
                ]
            },
            "Mathematics": {
                "objective": [
                    {"q": "Simplify: 2(3x + 4)",
                     "opts": ["6x + 4", "3x + 8", "6x + 8", "5x + 4"],
                     "ans": "6x + 8"},
                    {"q": "Square root of 49?",
                     "opts": ["6", "7", "8", "9"],
                     "ans": "7"},
                ],
                "subjective": [
                    "Solve the quadratic equation: x² - 5x + 6 = 0."
                ]
            },
            "Economics": {
                "objective": [
                    {"q": "What is opportunity cost?",
                     "opts": ["Cost of next best alternative", "Fixed cost", "Variable cost", "Marginal cost"],
                     "ans": "Cost of next best alternative"},
                    {"q": "What is demand?",
                     "opts": ["Desire for a good", "Ability to pay", "Willingness to buy", "Both b and c"],
                     "ans": "Both b and c"},
                ],
                "subjective": [
                    "Describe the basic economic problem of scarcity."
                ]
            },
            "Physics": {
                "objective": [
                    {"q": "What is the SI unit of force?",
                     "opts": ["Joule", "Newton", "Watt", "Pascal"],
                     "ans": "Newton"},
                    {"q": "Speed = ?",
                     "opts": ["Distance/Time", "Force/Time", "Work/Time", "Mass/Time"],
                     "ans": "Distance/Time"},
                ],
                "subjective": [
                    "Explain Newton's First Law of Motion with an example."
                ]
            },
            "Biology": {
                "objective": [
                    {"q": "What is the powerhouse of the cell?",
                     "opts": ["Nucleus", "Ribosome", "Mitochondria", "Chloroplast"],
                     "ans": "Mitochondria"},
                    {"q": "Which organ pumps blood?",
                     "opts": ["Liver", "Brain", "Heart", "Lung"],
                     "ans": "Heart"},
                ],
                "subjective": [
                    "Describe the structure and function of the human heart."
                ]
            },
            "English": {
                "objective": [
                    {"q": "Identify the noun: The cat slept.",
                     "opts": ["The", "cat", "slept", "Identify"],
                     "ans": "cat"},
                    {"q": "What is a synonym for happy?",
                     "opts": ["Sad", "Joyful", "Angry", "Tired"],
                     "ans": "Joyful"},
                ],
                "subjective": [
                    "Write a short essay on the topic: 'My Best Friend'."
                ]
            },
            "Chemistry": {
                "objective": [
                    {"q": "H2O is the chemical formula for?",
                     "opts": ["Oxygen", "Hydrogen", "Salt", "Water"],
                     "ans": "Water"},
                    {"q": "Atomic number is the number of?",
                     "opts": ["Neutrons", "Protons", "Electrons", "Atoms"],
                     "ans": "Protons"},
                ],
                "subjective": [
                    "Explain the difference between elements, compounds, and mixtures."
                ]
            },
        }

        for class_name in classes:
            class_obj, _ = Class.objects.get_or_create(name=class_name)
            for subject_name in subjects:
                subject_obj, _ = Subject.objects.get_or_create(name=subject_name, school_class=class_obj)

                quiz = Quiz.objects.create(
                    school_class=class_obj,
                    subject=subject_obj,
                    created_by=teacher,
                    title=f"A {subject_name} exam for {class_name}",
                    description=f"Auto-generated {subject_name} exam for {class_name}",
                    duration_minutes=30,
                    start_time=timezone.now(),
                    end_time=timezone.now() + timezone.timedelta(minutes=30),
                    is_published=True,
                )

                questions_data = question_bank[subject_name]

                # Objective questions
                for q in questions_data["objective"]:
                    question = quiz.questions.create(
                        text=q["q"],
                        question_type="objective",
                        marks=1,
                    )
                    for opt in q["opts"]:
                        question.choices.create(
                            text=opt,
                            is_correct=(opt == q["ans"])
                        )

                # Subjective questions
                for sq in questions_data["subjective"]:
                    quiz.questions.create(
                        text=sq,
                        question_type="subjective",
                        marks=5,
                    )

        self.stdout.write(self.style.SUCCESS("✅ Quizzes created with objective and subjective questions for all subjects & classes."))
