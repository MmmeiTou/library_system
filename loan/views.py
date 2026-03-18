from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
import uuid
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from books.models import Book
from .models import LoanRecord
from books.views import LibrarianRequiredMixin   # Assumed defined, if not please implement
from django.db.models import Q


# ---------- List Views ----------
class StudentLoanListView(LoginRequiredMixin, ListView):
    model = LoanRecord
    template_name = 'loan/student_loan_list.html'
    context_object_name = 'loans'
    paginate_by = 10

    def get_queryset(self):
        # Base queryset: only show current student's records
        queryset = LoanRecord.objects.filter(student_username=self.request.user.username)
        # If parameter overdue=1, show only overdue records (borrowing and due_date < today)
        if self.request.GET.get('overdue') == '1':
            today = timezone.now().date()
            queryset = queryset.filter(
                status='borrowing',
                due_date__lt=today
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass current filter status to template for button highlighting
        context['overdue_filter'] = self.request.GET.get('overdue') == '1'
        return context


class AdminLoanListView(LibrarianRequiredMixin, ListView):
    model = LoanRecord
    template_name = 'loan/admin_loan_list.html'
    context_object_name = 'loans'
    paginate_by = 20

    '''Filter overdue'''
    def get_queryset(self):
        queryset = super().get_queryset()
        # If parameter overdue=1, show only overdue records (borrowing and due_date < today)
        if self.request.GET.get('overdue') == '1':
            today = timezone.now().date()
            queryset = queryset.filter(
                status='borrowing',
                due_date__lt=today
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass whether overdue filter is active to template for button highlighting
        context['overdue_filter'] = self.request.GET.get('overdue') == '1'
        return context

# ---------- Borrow Book ----------
@login_required
@transaction.atomic
def borrow_book(request, book_id):
    # Only students are allowed to borrow
    if not hasattr(request.user, 'student_profile'):
        messages.error(request, 'Only students can borrow books')
        return redirect('book_list')

    book = get_object_or_404(Book, pk=book_id)
    if book.available_copies < 1:
        messages.error(request, 'This book is currently out of stock')
        return redirect('book_list')

    # Generate unique loan ID
    loan_id = uuid.uuid4().hex[:12].upper()
    due = timezone.now().date() + timedelta(days=7)   # Due in 7 days

    loan = LoanRecord.objects.create(
        loan_id=loan_id,
        student_username=request.user.username,
        student_id=request.user.student_profile.student_id,
        book_id=book.book_id,
        book_name=book.title,
        due_date=due,
        status='borrowing'
    )
    book.available_copies -= 1
    book.save()

    messages.success(request, f'Successfully borrowed "{book.title}". Please return it by {due}')
    return redirect('book_list')

# ---------- Return Book ----------
@login_required
@transaction.atomic
def return_book(request, loan_id):
    loan = get_object_or_404(LoanRecord, loan_id=loan_id)

    # Check permissions: must be the record's owner and status is borrowing
    if request.user.username != loan.student_username:
        messages.error(request, 'Permission denied')
        return redirect('student_loan_list')
    if loan.status != 'borrowing':
        messages.error(request, 'This book has already been returned or has an abnormal status')
        return redirect('student_loan_list')

    # Update status to returned
    loan.status = 'returned'
    loan.save()

    # Increase book stock
    try:
        book = Book.objects.get(book_id=loan.book_id)
        book.available_copies += 1
        book.save()
    except Book.DoesNotExist:
        messages.warning(request, 'Original book does not exist, cannot update stock')

    messages.success(request, 'Book returned successfully')
    return redirect('student_loan_list')

# ---------- Admin Delete Returned Record ----------
@login_required
def delete_loan(request, loan_id):
    # Only librarians allowed to delete
    if not hasattr(request.user, 'librarian_profile'):
        messages.error(request, 'Permission denied')
        return redirect('admin_loan_list')

    loan = get_object_or_404(LoanRecord, loan_id=loan_id)
    if loan.status != 'returned':
        messages.error(request, 'Only returned records can be deleted')
        return redirect('admin_loan_list')

    loan.delete()
    messages.success(request, 'Record deleted')
    return redirect('admin_loan_list')