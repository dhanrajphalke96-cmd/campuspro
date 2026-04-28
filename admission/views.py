from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from core.decorators import role_required
from .models import AdmissionApplication, AdmissionDocument, MeritList
from .forms import AdmissionApplicationForm, AdmissionDocumentForm


@login_required
@role_required('admin', 'principal')
def admission_list(request):
    apps = AdmissionApplication.objects.select_related('course', 'academic_year')
    status = request.GET.get('status')
    search = request.GET.get('search')
    if status:
        apps = apps.filter(status=status)
    if search:
        apps = apps.filter(
            Q(first_name__icontains=search) | Q(last_name__icontains=search) |
            Q(application_id__icontains=search) | Q(email__icontains=search)
        )
    stats = {
        'total': AdmissionApplication.objects.count(),
        'pending': AdmissionApplication.objects.filter(status='pending').count(),
        'approved': AdmissionApplication.objects.filter(status='approved').count(),
        'rejected': AdmissionApplication.objects.filter(status='rejected').count(),
    }
    return render(request, 'admission/list.html', {'applications': apps, 'stats': stats})


@login_required
@role_required('admin', 'principal')
def admission_create(request):
    if request.method == 'POST':
        form = AdmissionApplicationForm(request.POST)
        if form.is_valid():
            app = form.save()
            messages.success(request, f'Application {app.application_id} submitted successfully!')
            return redirect('admission_detail', pk=app.pk)
    else:
        form = AdmissionApplicationForm()
    return render(request, 'admission/create.html', {'form': form})


@login_required
@role_required('admin', 'principal')
def admission_detail(request, pk):
    app = get_object_or_404(AdmissionApplication.objects.select_related('course', 'academic_year'), pk=pk)
    documents = app.documents.all()
    doc_form = AdmissionDocumentForm()
    if request.method == 'POST':
        if 'upload_doc' in request.POST:
            doc_form = AdmissionDocumentForm(request.POST, request.FILES)
            if doc_form.is_valid():
                doc = doc_form.save(commit=False)
                doc.application = app
                doc.save()
                messages.success(request, 'Document uploaded.')
                return redirect('admission_detail', pk=pk)
        elif 'update_status' in request.POST:
            new_status = request.POST.get('new_status')
            if new_status in dict(AdmissionApplication.STATUS_CHOICES):
                app.status = new_status
                app.remarks = request.POST.get('remarks', '')
                app.save()
                messages.success(request, f'Status updated to {app.get_status_display()}.')
                return redirect('admission_detail', pk=pk)
    return render(request, 'admission/detail.html', {
        'application': app, 'documents': documents, 'doc_form': doc_form
    })


@login_required
@role_required('admin', 'principal', 'hod', 'student')
def merit_list_view(request):
    merit_lists = MeritList.objects.select_related('course', 'academic_year').order_by('-generated_at')
    return render(request, 'admission/merit_list.html', {'merit_lists': merit_lists})
