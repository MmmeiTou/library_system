from django.db import models
from django.utils import timezone

class LoanRecord(models.Model):
    STATUS_CHOICES = [
        ('borrowing', 'Borrowing'),
        ('returned', 'Returned'),
    ]

    loan_id = models.CharField('Loan ID', max_length=50, unique=True)
    student_username = models.CharField('Student Username', max_length=150)
    student_id = models.CharField('Student ID', max_length=20)
    book_id = models.CharField('Book ID', max_length=50)          # Corresponds to Book.book_id
    book_name = models.CharField('Book Title', max_length=200)
    loan_date = models.DateTimeField('Loan Date', auto_now_add=True)
    due_date = models.DateField('Due Date')
    status = models.CharField('Status', max_length=10, choices=STATUS_CHOICES, default='borrowing')

    class Meta:
        verbose_name = 'Loan Record'
        verbose_name_plural = 'Loan Records'
        ordering = ['-loan_date']

    def __str__(self):
        return f"{self.loan_id} - {self.book_name} ({self.student_username})"

    @property
    def is_overdue(self):
        """Dynamically determine if overdue, borrowing and current date exceeds due date"""
        if self.status == 'borrowing' and timezone.now().date() > self.due_date:
            return True
        return False

    def get_status_display_with_overdue(self):
        """For template display, returns 'Overdue' if overdue, otherwise returns the original status display"""
        if self.is_overdue:
            return 'Overdue'
        return self.get_status_display()