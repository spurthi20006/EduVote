from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class AdminProfile(models.Model):
    ADMIN_ROLES = [
        ('school', 'School Admin'),
        ('pu', 'PU College Admin'),
        ('engineering', 'Engineering College Admin'),
        ('super_admin', 'Main Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ADMIN_ROLES)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    @property
    def institution_type(self):
        if self.role == 'super_admin':
            return 'all'
        return self.role


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.is_superuser:
        AdminProfile.objects.create(user=instance, role='super_admin')


class Student(models.Model):
    INSTITUTION_CHOICES = [
        ('school', 'School'),
        ('pu', 'PU College'),
        ('engineering', 'Engineering College'),
    ]

    institution_type = models.CharField(max_length=20, choices=INSTITUTION_CHOICES)
    student_id = models.CharField(max_length=50, unique=True, help_text="Roll No / Reg No / USN")
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)

    # School-specific
    class_name = models.CharField(max_length=20, blank=True, null=True, verbose_name="Class")

    # PU / Engineering
    year = models.CharField(max_length=10, blank=True, null=True)

    # Engineering-specific
    branch = models.CharField(max_length=50, blank=True, null=True)

    has_voted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.student_id}) — {self.get_institution_type_display()}"

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
        ordering = ['institution_type', 'student_id']


class Candidate(models.Model):
    INSTITUTION_CHOICES = [
        ('school', 'School'),
        ('pu', 'PU College'),
        ('engineering', 'Engineering College'),
        ('all', 'All Institutions'),
    ]

    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100, default='Student Representative')
    institution_type = models.CharField(max_length=20, choices=INSTITUTION_CHOICES, default='all')
    photo_url = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    manifesto = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.position})"

    class Meta:
        verbose_name = "Candidate"
        verbose_name_plural = "Candidates"
        ordering = ['position', 'name']


class VoteBlock(models.Model):
    """Persistent representation of a blockchain block stored in the DB."""
    index = models.IntegerField(unique=True)
    user_id_hash = models.CharField(max_length=64)
    candidate = models.CharField(max_length=100)
    timestamp = models.FloatField()
    previous_hash = models.CharField(max_length=64)
    block_hash = models.CharField(max_length=64)

    # Metadata (not part of hash computation)
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Block #{self.index} — {self.candidate}"

    class Meta:
        verbose_name = "Vote Block"
        verbose_name_plural = "Vote Blocks"
        ordering = ['index']
