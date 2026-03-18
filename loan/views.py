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
from books.views import LibrarianRequiredMixin   # 假设已定义，若未定义请自行实现
from django.db.models import Q


# ---------- 列表视图 ----------
class StudentLoanListView(LoginRequiredMixin, ListView):
    model = LoanRecord
    template_name = 'loan/student_loan_list.html'
    context_object_name = 'loans'
    paginate_by = 10

    def get_queryset(self):
        # 基础查询集：只显示当前学生的记录
        queryset = LoanRecord.objects.filter(student_username=self.request.user.username)
        # 如果请求参数 overdue=1，则只显示逾期记录（借阅中且应还日期早于今天）
        if self.request.GET.get('overdue') == '1':
            today = timezone.now().date()
            queryset = queryset.filter(
                status='borrowing',
                due_date__lt=today
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 传递当前筛选状态，用于模板高亮按钮
        context['overdue_filter'] = self.request.GET.get('overdue') == '1'
        return context


class AdminLoanListView(LibrarianRequiredMixin, ListView):
    model = LoanRecord
    template_name = 'loan/admin_loan_list.html'
    context_object_name = 'loans'
    paginate_by = 20

    '''筛选逾期'''
    def get_queryset(self):
        queryset = super().get_queryset()
        # 如果请求参数 overdue=1，则只显示逾期记录（借阅中且应还日期早于今天）
        if self.request.GET.get('overdue') == '1':
            today = timezone.now().date()
            queryset = queryset.filter(
                status='borrowing',
                due_date__lt=today
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 传递当前是否处于逾期筛选状态，用于模板高亮按钮
        context['overdue_filter'] = self.request.GET.get('overdue') == '1'
        return context

# ---------- 借书 ----------
@login_required
@transaction.atomic
def borrow_book(request, book_id):
    # 仅学生允许借书
    if not hasattr(request.user, 'student_profile'):
        messages.error(request, '只有学生才能借书')
        return redirect('book_list')

    book = get_object_or_404(Book, pk=book_id)
    if book.available_copies < 1:
        messages.error(request, '该书暂无库存')
        return redirect('book_list')

    # 生成唯一借阅编号
    loan_id = uuid.uuid4().hex[:12].upper()
    due = timezone.now().date() + timedelta(days=7)   # 7天后应还

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

    messages.success(request, f'成功借阅《{book.title}》，请于 {due} 前归还')
    return redirect('book_list')

# ---------- 还书 ----------
@login_required
@transaction.atomic
def return_book(request, loan_id):
    loan = get_object_or_404(LoanRecord, loan_id=loan_id)

    # 校验权限：必须是记录本人且状态为借阅中
    if request.user.username != loan.student_username:
        messages.error(request, '无权操作')
        return redirect('student_loan_list')
    if loan.status != 'borrowing':
        messages.error(request, '该书已归还或状态异常')
        return redirect('student_loan_list')

    # 更新状态为已归还
    loan.status = 'returned'
    loan.save()

    # 增加图书库存
    try:
        book = Book.objects.get(book_id=loan.book_id)
        book.available_copies += 1
        book.save()
    except Book.DoesNotExist:
        messages.warning(request, '原图书不存在，无法更新库存')

    messages.success(request, '还书成功')
    return redirect('student_loan_list')

# ---------- 管理员删除已归还记录 ----------
@login_required
def delete_loan(request, loan_id):
    # 仅管理员允许删除
    if not hasattr(request.user, 'librarian_profile'):
        messages.error(request, '无权操作')
        return redirect('admin_loan_list')

    loan = get_object_or_404(LoanRecord, loan_id=loan_id)
    if loan.status != 'returned':
        messages.error(request, '只能删除已归还的记录')
        return redirect('admin_loan_list')

    loan.delete()
    messages.success(request, '记录已删除')
    return redirect('admin_loan_list')