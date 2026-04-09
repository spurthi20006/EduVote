from django.core.management.base import BaseCommand
from voting.models import Student, Candidate

class Command(BaseCommand):
    help = 'Seeds the database with initial dummy data for testing.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database with test data...')

        # Categories mapping to institution
        candidates = [
            {'name': 'Alice Sharma', 'position': 'Head Girl', 'institution_type': 'school', 'bio': 'Let us make our school green!', 'manifesto': 'Free Wi-Fi and better cafeteria.'},
            {'name': 'Bob Patil', 'position': 'Head Boy', 'institution_type': 'school', 'bio': 'Sports and more sports.', 'manifesto': 'Weekly sports events.'},
            {'name': 'Charlie Gupta', 'position': 'President', 'institution_type': 'pu', 'bio': 'Focus on competitive exams.', 'manifesto': 'More mock tests.'},
            {'name': 'Diana Reddy', 'position': 'Vice President', 'institution_type': 'pu', 'bio': 'Better lab facilities.', 'manifesto': 'Upgrade biology lab.'},
            {'name': 'Eve Rao', 'position': 'Cultural Secretary', 'institution_type': 'engineering', 'bio': 'Fest season all year.', 'manifesto': 'More technical Fests.'},
            {'name': 'Frank Singh', 'position': 'Sports Secretary', 'institution_type': 'engineering', 'bio': 'Fitness first.', 'manifesto': 'New gymnasium.'},
            {'name': 'Grace Lee', 'position': 'General Secretary', 'institution_type': 'all', 'bio': 'For all students.', 'manifesto': 'Better transport.'},
        ]

        for cand_data in candidates:
            Candidate.objects.get_or_create(
                name=cand_data['name'],
                defaults=cand_data
            )
            self.stdout.write(f"Created candidate: {cand_data['name']}")

        students = [
            # School
            {'student_id': 'SCH-2024-001', 'name': 'John Doe', 'institution_type': 'school', 'class_name': '10-A'},
            {'student_id': 'SCH-2024-002', 'name': 'Jane Doe', 'institution_type': 'school', 'class_name': '10-A'},
            # PU
            {'student_id': 'PU-2024-001', 'name': 'Mark Smith', 'institution_type': 'pu', 'year': '1'},
            {'student_id': 'PU-2024-002', 'name': 'Mary Smith', 'institution_type': 'pu', 'year': '2'},
            # Engineering
            {'student_id': '1AB21CS001', 'name': 'Tom Jones', 'institution_type': 'engineering', 'branch': 'CSE', 'year': '3'},
            {'student_id': '1AB21CS002', 'name': 'Tony Stark', 'institution_type': 'engineering', 'branch': 'CSE', 'year': '4'},
        ]

        for stu_data in students:
            Student.objects.get_or_create(
                student_id=stu_data['student_id'],
                defaults=stu_data
            )
            self.stdout.write(f"Created student: {stu_data['student_id']}")

        self.stdout.write(self.style.SUCCESS('Successfully seeded database.'))
