from django.db import models
from django.utils import timezone

class LoanRecord(models.Model):
    STATUS_CHOICES = [
        ('borrowing', '借阅中'),
        ('returned', '已归还'),
    ]

    loan_id = models.CharField('借阅编号', max_length=50, unique=True)
    student_username = models.CharField('学生用户名', max_length=150)
    student_id = models.CharField('学号', max_length=20)
    book_id = models.CharField('图书编号', max_length=50)          # 对应 Book 的 book_id
    book_name = models.CharField('书名', max_length=200)
    loan_date = models.DateTimeField('借阅日期', auto_now_add=True)
    due_date = models.DateField('应还日期')
    status = models.CharField('状态', max_length=10, choices=STATUS_CHOICES, default='borrowing')

    class Meta:
        verbose_name = '借阅记录'
        verbose_name_plural = '借阅记录'
        ordering = ['-loan_date']

    def __str__(self):
        return f"{self.loan_id} - {self.book_name} ({self.student_username})"

    @property
    def is_overdue(self):
        """动态判断是否逾期：状态为借阅中且当前日期超过应还日期"""
        if self.status == 'borrowing' and timezone.now().date() > self.due_date:
            return True
        return False

    def get_status_display_with_overdue(self):
        """用于模板显示：如果逾期则返回'已逾期'，否则返回原状态显示"""
        if self.is_overdue:
            return '已逾期'
        return self.get_status_display()