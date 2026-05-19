from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from .models import FeeStructure, FeePayment, Scholarship
from core.decorators import role_required


@login_required
@role_required('admin', 'principal', 'accountant', 'student')
def fees_dashboard(request):
    if request.user.role == 'student':
        if not hasattr(request.user, 'studentprofile'):
            messages.error(request, "Student profile not found.")
            return redirect('dashboard')
        total_collected = FeePayment.objects.filter(student=request.user.studentprofile, status='paid').aggregate(total=Sum('amount_paid'))['total'] or 0
        pending_count = FeePayment.objects.filter(student=request.user.studentprofile, status='pending').count()
        paid_count = FeePayment.objects.filter(student=request.user.studentprofile, status='paid').count()
        recent_payments = FeePayment.objects.filter(student=request.user.studentprofile).select_related('fee_structure').order_by('-created_at')[:10]
        fee_structures = FeeStructure.objects.none() # Students don't manage structures
    else:
        total_collected = FeePayment.objects.filter(status='paid').aggregate(total=Sum('amount_paid'))['total'] or 0
        pending_count = FeePayment.objects.filter(status='pending').count()
        paid_count = FeePayment.objects.filter(status='paid').count()
        recent_payments = FeePayment.objects.filter(status='paid').select_related('student__user', 'fee_structure').order_by('-paid_at')[:10]
        fee_structures = FeeStructure.objects.filter(is_active=True).select_related('course', 'academic_year')
        
    return render(request, 'fees/dashboard.html', {
        'total_collected': total_collected, 'pending_count': pending_count,
        'paid_count': paid_count, 'recent_payments': recent_payments,
        'fee_structures': fee_structures,
    })


@login_required
@role_required('accountant', 'admin', 'principal')
def fees_pay(request):
    if request.method == 'POST':
        student_id = request.POST.get('student')
        fee_structure_id = request.POST.get('fee_structure')
        amount = request.POST.get('amount')
        payment_mode = request.POST.get('payment_mode')
        transaction_id = request.POST.get('transaction_id', '')

        from students.models import StudentProfile
        student = get_object_or_404(StudentProfile, pk=student_id)
        fee_structure = get_object_or_404(FeeStructure, pk=fee_structure_id)

        payment = FeePayment.objects.create(
            student=student,
            fee_structure=fee_structure,
            amount_paid=amount,
            payment_mode=payment_mode,
            transaction_id=transaction_id,
            status='paid',
            paid_at=timezone.now(),
        )
        messages.success(request, f'Payment recorded. Receipt: {payment.receipt_number}')
        return redirect('fees_dashboard')

    from students.models import StudentProfile
    students = StudentProfile.objects.filter(is_active=True).select_related('user')
    fee_structures = FeeStructure.objects.filter(is_active=True).select_related('course')
    return render(request, 'fees/pay.html', {
        'students': students, 'fee_structures': fee_structures,
    })


@login_required
@role_required('admin', 'principal', 'accountant', 'student')
def fees_history(request):
    payments = FeePayment.objects.select_related('student__user', 'fee_structure__course')
    if request.user.role == 'student':
        payments = payments.filter(student__user=request.user)
        
    search = request.GET.get('search')
    if search and request.user.role != 'student':
        payments = payments.filter(
            Q(student__enrollment_no__icontains=search) |
            Q(receipt_number__icontains=search) |
            Q(student__user__first_name__icontains=search)
        )
    return render(request, 'fees/history.html', {'payments': payments[:50]})


from django.views.decorators.http import require_POST

@login_required
@role_required('admin', 'principal', 'accountant')
def purchase_list(request):
    from .models import PurchaseRecord
    
    role = 'admin' if request.user.is_superuser else request.user.role
    if role == 'accountant':
        purchases = PurchaseRecord.objects.filter(requested_by=request.user)
    else: # Admin, Principal
        purchases = PurchaseRecord.objects.all()
        
    return render(request, 'fees/purchase_list.html', {'purchases': purchases})


@login_required
@role_required('admin', 'accountant')
def purchase_create(request):
    from .models import PurchaseRecord
    if request.method == 'POST':
        item_name = request.POST.get('item_name')
        quantity = request.POST.get('quantity')
        estimated_cost = request.POST.get('estimated_cost')
        description = request.POST.get('description', '')
        
        if item_name and quantity and estimated_cost:
            PurchaseRecord.objects.create(
                item_name=item_name,
                quantity=quantity,
                estimated_cost=estimated_cost,
                description=description,
                requested_by=request.user
            )
            messages.success(request, 'Purchase request submitted successfully.')
            return redirect('purchase_list')
        else:
            messages.error(request, 'Please fill all required fields.')
            
    return render(request, 'fees/purchase_create.html')


@login_required
@role_required('admin', 'principal')
@require_POST
def purchase_approve(request, pk):
    from .models import PurchaseRecord
    purchase = get_object_or_404(PurchaseRecord, pk=pk)
    purchase.status = 'approved'
    purchase.approved_by = request.user
    purchase.approval_remarks = request.POST.get('remarks', '')
    purchase.save()
    messages.success(request, f'Purchase request for "{purchase.item_name}" has been approved.')
    return redirect('purchase_list')


@login_required
@role_required('admin', 'principal')
@require_POST
def purchase_reject(request, pk):
    from .models import PurchaseRecord
    purchase = get_object_or_404(PurchaseRecord, pk=pk)
    purchase.status = 'rejected'
    purchase.approved_by = request.user
    purchase.approval_remarks = request.POST.get('remarks', '')
    purchase.save()
    messages.warning(request, f'Purchase request for "{purchase.item_name}" has been rejected.')
    return redirect('purchase_list')

