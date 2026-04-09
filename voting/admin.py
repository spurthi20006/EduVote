from django.contrib import admin
from django import forms
from .models import Student, Candidate, VoteBlock, AdminProfile

# Customizing Admin Branding
admin.site.site_header = "EduVote | Election Administration"
admin.site.site_title = "EduVote Admin Portal"
admin.site.index_title = "Welcome to EduVote Multi-Tenant Management"


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']
    list_filter = ['role']


class StudentAdminForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        institution_type = cleaned_data.get('institution_type')
        class_name = cleaned_data.get('class_name')
        year = cleaned_data.get('year')
        branch = cleaned_data.get('branch')
        student_id = cleaned_data.get('student_id')
        name = cleaned_data.get('name')

        if not student_id or not name:
            # Basic required fields
            return cleaned_data

        if institution_type == 'school':
            if not class_name:
                self.add_error('class_name', 'Please fill all the required credentials (Class is required for School).')
            # Clear irrelevant fields
            cleaned_data['year'] = ''
            cleaned_data['branch'] = ''
            cleaned_data['email'] = ''

        elif institution_type == 'pu':
            if not year:
                self.add_error('year', 'Please fill all the required credentials (Year is required for PU College).')
            # Clear irrelevant fields
            cleaned_data['class_name'] = ''
            cleaned_data['branch'] = ''
            cleaned_data['email'] = ''

        elif institution_type == 'engineering':
            if not year or not branch:
                if not year:
                    self.add_error('year', 'Please fill all the required credentials (Year is required for Engineering).')
                if not branch:
                    self.add_error('branch', 'Please fill all the required credentials (Branch is required for Engineering).')
            # Clear irrelevant fields
            cleaned_data['class_name'] = ''

        return cleaned_data


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    form = StudentAdminForm
    list_display = ['student_id', 'name', 'institution_type', 'class_name', 'branch', 'year', 'has_voted']
    list_filter = ['institution_type', 'has_voted']
    search_fields = ['student_id', 'name', 'email']
    readonly_fields = ['has_voted']
    ordering = ['institution_type', 'student_id']

    class Media:
        js = ('js/admin_student.js',)


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'institution_type', 'is_active']
    list_filter = ['institution_type', 'is_active']
    search_fields = ['name', 'position']


@admin.register(VoteBlock)
class VoteBlockAdmin(admin.ModelAdmin):
    list_display = ['index', 'candidate', 'user_id_hash_short', 'timestamp_display', 'block_hash_short']
    ordering = ['index']
    readonly_fields = ['index', 'user_id_hash', 'candidate', 'timestamp', 'previous_hash', 'block_hash', 'student']

    def user_id_hash_short(self, obj):
        return obj.user_id_hash[:12] + '...'
    user_id_hash_short.short_description = 'User ID Hash'

    def block_hash_short(self, obj):
        return obj.block_hash[:16] + '...'
    block_hash_short.short_description = 'Block Hash'

    def timestamp_display(self, obj):
        from datetime import datetime
        return datetime.fromtimestamp(obj.timestamp).strftime('%Y-%m-%d %H:%M:%S')
    timestamp_display.short_description = 'Timestamp'
