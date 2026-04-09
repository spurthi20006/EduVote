from django.core.management.base import BaseCommand
from voting.models import Student, Candidate

class Command(BaseCommand):
    help = 'Seeds the database with sample Students and Candidates'

    def handle(self, *args, **kwargs):
        self.stdout.write("Deleting old sample data...")
        Student.objects.all().delete()
        Candidate.objects.all().delete()

        # Candidates
        self.stdout.write("Creating candidates...")
        candidates_data = [
            {'name': 'Alice Smith', 'position': 'President (School)', 'institution_type': 'school', 'manifesto': 'Better school lunches!'},
            {'name': 'Bob Jones', 'position': 'President (School)', 'institution_type': 'school', 'manifesto': 'More sports events.'},
            {'name': 'Charlie Davis', 'position': 'General Secretary (PU)', 'institution_type': 'pu', 'manifesto': 'Extended library hours for PU students.'},
            {'name': 'Diana Prince', 'position': 'General Secretary (PU)', 'institution_type': 'pu', 'manifesto': 'More fests for PU!'},
            {'name': 'Evan Wright', 'position': 'Tech Lead (Engineering)', 'institution_type': 'engineering', 'manifesto': 'Hackathons every month!'},
            {'name': 'Fiona Gallagher', 'position': 'Tech Lead (Engineering)', 'institution_type': 'engineering', 'manifesto': 'Better lab equipments.'},
            {'name': 'George Washington', 'position': 'University Representative', 'institution_type': 'all', 'manifesto': 'Representation for everyone.'},
        ]

        for c_data in candidates_data:
            Candidate.objects.create(**c_data)

        # Students
        self.stdout.write("Creating students...")
        students_data = [
            # School students
            {'institution_type': 'school', 'student_id': 'SCH001', 'name': 'John Doe', 'class_name': '10A'},
            {'institution_type': 'school', 'student_id': 'SCH002', 'name': 'Jane Doe', 'class_name': '10B'},
            # PU students
            {'institution_type': 'pu', 'student_id': 'PU1001', 'name': 'Katy Perry', 'year': '1st Year'},
            {'institution_type': 'pu', 'student_id': 'PU1002', 'name': 'Liam Neeson', 'year': '2nd Year'},
            # Engineering students
            {'institution_type': 'engineering', 'student_id': 'ENG2020CS01', 'name': 'Mark Zuckerberg', 'branch': 'CS', 'year': '4th Year'},
            {'institution_type': 'engineering', 'student_id': 'ENG2021EC02', 'name': 'Elon Musk', 'branch': 'EC', 'year': '3rd Year'},
        ]

        for s_data in students_data:
            Student.objects.create(**s_data)

        self.stdout.write(self.style.SUCCESS("Successfully seeded the database!"))
