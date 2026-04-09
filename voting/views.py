from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Count, Q
from django.views.decorators.http import require_POST
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import openpyxl

from .models import Student, Candidate, VoteBlock, AdminProfile
from .forms import (
    SchoolLoginForm, PULoginForm, EngineeringLoginForm, 
    AdminRegistrationForm, ExcelUploadForm
)
from .blockchain import Block, get_blockchain, hash_user_id


# ─── helpers ────────────────────────────────────────────────────────────────

def _load_chain_from_db():
    """Rebuild the in-memory blockchain from persisted VoteBlocks."""
    bc = get_blockchain()
    # Clear and re-add (simple rebuild on each startup)
    if VoteBlock.objects.exists():
        bc.chain = bc.chain[:1]  # keep genesis
        for vb in VoteBlock.objects.all().order_by('index'):
            block = Block(
                index=vb.index,
                user_id_hash=vb.user_id_hash,
                candidate=vb.candidate,
                timestamp=vb.timestamp,
                previous_hash=vb.previous_hash,
            )
            block.hash = vb.block_hash
            bc.chain.append(block)


def _get_student_from_session(request):
    sid = request.session.get('student_id')
    if not sid:
        return None
    try:
        return Student.objects.get(id=sid)
    except Student.DoesNotExist:
        return None


# ─── home ────────────────────────────────────────────────────────────────────

def home(request):
    """Landing page — chose institution type."""
    return render(request, 'voting/home.html')


# ─── login ───────────────────────────────────────────────────────────────────

def login_view(request, institution):
    """Unified login for school / pu / engineering."""
    form_map = {
        'school': SchoolLoginForm,
        'pu': PULoginForm,
        'engineering': EngineeringLoginForm,
    }
    if institution not in form_map:
        return redirect('home')

    form_class = form_map[institution]

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            student_id = form.cleaned_data['student_id'].strip().upper()

            # Base query
            qs = Student.objects.filter(
                institution_type=institution,
                student_id__iexact=student_id,
            )

            # Extra field checks
            if institution == 'school':
                qs = qs.filter(class_name__iexact=form.cleaned_data['class_name'])
            elif institution == 'pu':
                qs = qs.filter(year=form.cleaned_data['year'])
            elif institution == 'engineering':
                qs = qs.filter(
                    branch__iexact=form.cleaned_data['branch'],
                    year=form.cleaned_data['year'],
                )

            student = qs.first()
            if student:
                request.session['student_id'] = student.id
                request.session['institution'] = institution
                messages.success(request, f'Welcome, {student.name}! 👋')
                return redirect('vote')
            else:
                messages.error(request, '❌ Invalid credentials. Please check your details.')
    else:
        form = form_class()

    context = {
        'form': form,
        'institution': institution,
        'institution_display': dict(Student.INSTITUTION_CHOICES).get(institution, institution),
    }
    return render(request, 'voting/login.html', context)


# ─── vote ─────────────────────────────────────────────────────────────────────

def vote_view(request):
    """Vote casting page."""
    student = _get_student_from_session(request)
    if not student:
        messages.warning(request, 'Please login first.')
        return redirect('home')

    if student.has_voted:
        messages.warning(request, '⚠️ Duplicate voting attempt detected! You have already cast your vote. Your first entry remains recorded on the blockchain.')
        return redirect('vote_success')

    # Candidates valid for this student
    candidates = Candidate.objects.filter(
        is_active=True
    ).filter(
        institution_type__in=[student.institution_type, 'all']
    )

    if request.method == 'POST':
        candidate_id = request.POST.get('candidate_id')
        if not candidate_id:
            messages.error(request, 'Please select a candidate.')
            return render(request, 'voting/vote.html', {'candidates': candidates, 'student': student})

        candidate = get_object_or_404(Candidate, id=candidate_id, is_active=True)

        # Cast vote on the blockchain
        bc = get_blockchain()
        block = bc.add_vote(student.student_id, candidate.name)

        # Persist to DB
        VoteBlock.objects.create(
            index=block.index,
            user_id_hash=block.user_id_hash,
            candidate=block.candidate,
            timestamp=block.timestamp,
            previous_hash=block.previous_hash,
            block_hash=block.hash,
            student=student,
        )

        # Mark student as voted
        student.has_voted = True
        student.save()

        messages.success(request, f'🗳️ Vote cast for <strong>{candidate.name}</strong>! Your vote is secured on the blockchain.')
        return redirect('vote_success')

    return render(request, 'voting/vote.html', {
        'candidates': candidates,
        'student': student,
    })


def vote_success(request):
    student = _get_student_from_session(request)
    return render(request, 'voting/vote_success.html', {'student': student})


# ─── results ─────────────────────────────────────────────────────────────────

@login_required
def results_view(request):
    """Public results with live counts from blockchain."""
    bc = get_blockchain()
    vote_data = bc.get_all_votes()

    # Tally
    tally = {}
    for vote in vote_data:
        c = vote['candidate']
        tally[c] = tally.get(c, 0) + 1

    # Pair with candidate objects
    candidates = Candidate.objects.filter(is_active=True)
    results = []
    total_votes = sum(tally.values()) or 1
    for candidate in candidates:
        count = tally.get(candidate.name, 0)
        results.append({
            'candidate': candidate,
            'votes': count,
            'percentage': round((count / total_votes) * 100, 1),
        })
    results.sort(key=lambda x: x['votes'], reverse=True)

    chain_valid = bc.is_chain_valid()
    context = {
        'results': results,
        'total_votes': sum(tally.values()),
        'chain_valid': chain_valid,
        'blockchain_blocks': vote_data[:10],  # Show last 10 blocks
    }
    return render(request, 'voting/results.html', context)


# ─── logout ──────────────────────────────────────────────────────────────────

def logout_view(request):
    request.session.flush()
    messages.success(request, 'You have been logged out.')
    return redirect('home')


# ─── admin dashboard ─────────────────────────────────────────────────────────

# ─── admin features ──────────────────────────────────────────────────────────

def admin_signup(request):
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            role = form.cleaned_data['role']
            AdminProfile.objects.create(user=user, role=role)
            login(request, user)
            messages.success(request, f"Welcome {user.username}! Your {role} dashboard is ready.")
            return redirect('admin_dashboard')
    else:
        form = AdminRegistrationForm()
    return render(request, 'voting/admin_signup.html', {'form': form})


@login_required
def admin_dashboard(request):
    """Refined admin dashboard with institutional isolation."""
    try:
        profile = request.user.adminprofile
    except AdminProfile.DoesNotExist:
        # If a superuser exists without a profile (created before signal), create one
        if request.user.is_superuser:
            profile = AdminProfile.objects.create(user=request.user, role='super_admin')
        else:
            messages.error(request, "Access denied. Admin profile not found.")
            return redirect('home')

    bc = get_blockchain()
    inst_type = profile.institution_type
    
    # Isolation logic
    if inst_type == 'all':
        students_qs = Student.objects.all()
        candidates_qs = Candidate.objects.all()
    else:
        students_qs = Student.objects.filter(institution_type=inst_type)
        candidates_qs = Candidate.objects.filter(Q(institution_type=inst_type) | Q(institution_type='all'))

    students_total = students_qs.count()
    students_voted = students_qs.filter(has_voted=True).count()
    
    # Blockchain data filter
    vote_data = bc.get_all_votes()
    if inst_type != 'all':
        # Filter blockchain results for this institution
        # We need to map student_id_hash back or just filter candidate names
        # Simplified: Filter by candidates belonging to this institution
        inst_candidate_names = list(candidates_qs.values_list('name', flat=True))
        vote_data = [v for v in vote_data if v['candidate'] in inst_candidate_names]

    tally = {}
    for vote in vote_data:
        c = vote['candidate']
        tally[c] = tally.get(c, 0) + 1

    results = []
    total_votes = sum(tally.values()) or 1
    for c in candidates_qs.filter(is_active=True):
        count = tally.get(c.name, 0)
        results.append({
            'candidate': c,
            'votes': count,
            'percentage': round((count / total_votes) * 100, 1),
        })
    results.sort(key=lambda x: x['votes'], reverse=True)

    context = {
        'profile': profile,
        'students_total': students_total,
        'students_voted': students_voted,
        'vote_data': vote_data[:20],
        'results': results,
        'chain_valid': bc.is_chain_valid(),
        'chain_length': len(bc.chain),
        'excel_form': ExcelUploadForm(),
    }
    
    if profile.role == 'super_admin':
        context['admin_profiles'] = AdminProfile.objects.exclude(user=request.user)
        context['institution_stats'] = (
            Student.objects.values('institution_type')
            .annotate(total=Count('id'), voted=Count('id', filter=Q(has_voted=True)))
        )

    return render(request, 'voting/admin_dashboard.html', context)


@login_required
@require_POST
def upload_students_excel(request):
    """Extract and store student data from Excel."""
    profile = request.user.adminprofile
    form = ExcelUploadForm(request.POST, request.FILES)
    if form.is_valid():
        excel_file = request.FILES['excel_file']
        try:
            wb = openpyxl.load_data(excel_file)
            sheet = wb.active
            
            created_count = 0
            skipped_rows = []
            
            # Assuming format: StudentID, Name, Extra1, Extra2
            # School: ID, Name, Class
            # PU: ID, Name, Year
            # Engineering: ID, Name, Year, Branch, Email
            
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if not row[0]: continue
                
                sid = str(row[0]).strip().upper()
                name = str(row[1]).strip()
                
                student_data = {
                    'institution_type': profile.institution_type,
                    'student_id': sid,
                    'name': name,
                }
                
                if profile.role == 'school':
                    student_data['class_name'] = str(row[2]) if len(row) > 2 else ''
                elif profile.role == 'pu':
                    student_data['year'] = str(row[2]) if len(row) > 2 else ''
                elif profile.role == 'engineering':
                    student_data['year'] = str(row[2]) if len(row) > 2 else ''
                    student_data['branch'] = str(row[3]) if len(row) > 3 else ''
                    student_data['email'] = str(row[4]) if len(row) > 4 else ''
                
                try:
                    Student.objects.get_or_create(student_id=sid, defaults=student_data)
                    created_count += 1
                except Exception as e:
                    skipped_rows.append(sid)
            
            msg = f"Successfully processed {created_count} students."
            if skipped_rows:
                msg += f" Skipped: {', '.join(skipped_rows)}. Please check data format."
            messages.info(request, msg)
            
        except Exception as e:
            messages.error(request, f"Error processing file: {str(e)}")
            
    return redirect('admin_dashboard')


# ─── API endpoints ────────────────────────────────────────────────────────────

def api_results(request):
    """JSON endpoint for live result chart."""
    bc = get_blockchain()
    vote_data = bc.get_all_votes()
    tally = {}
    for vote in vote_data:
        c = vote['candidate']
        tally[c] = tally.get(c, 0) + 1

    return JsonResponse({
        'tally': tally,
        'total': sum(tally.values()),
        'chain_valid': bc.is_chain_valid(),
        'chain_length': len(bc.chain),
    })
