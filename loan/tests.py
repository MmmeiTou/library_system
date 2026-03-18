from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch

from books.models import Book
from accounts.models import Student, Librarian
from .models import LoanRecord

User = get_user_model()

class LoanModelTest(TestCase):
    # Test the LoanRecord model
    def setUp(self):
        self.loan = LoanRecord.objects.create(
            loan_id='L001',
            student_username='student1',
            student_id='S001',
            book_id='B001',
            book_name='Test Book',
            due_date=timezone.now().date() + timedelta(days=7),
            status='borrowing'
        )

    def test_is_overdue_property(self):
        # Test the overdue property
        self.assertFalse(self.loan.is_overdue)
        # Set due_date to yesterday
        self.loan.due_date = timezone.now().date() - timedelta(days=1)
        self.loan.save()
        self.assertTrue(self.loan.is_overdue)

    def test_get_status_display_with_overdue(self):
        # Test status display with overdue indication
        self.assertEqual(self.loan.get_status_display_with_overdue(), 'Borrowing')
        self.loan.due_date = timezone.now().date() - timedelta(days=1)
        self.loan.save()
        self.assertEqual(self.loan.get_status_display_with_overdue(), 'Overdue')


class LoanViewTest(TestCase):
    def setUp(self):
        # Create a student user and profile
        self.student_user = User.objects.create_user(username='student', password='pass')
        self.student = Student.objects.create(user=self.student_user, student_id='S001')
        # Create a librarian user and profile
        self.lib_user = User.objects.create_user(username='librarian', password='pass')
        self.librarian = Librarian.objects.create(user=self.lib_user, employee_id='L001')
        # Create a book
        self.book = Book.objects.create(
            book_id='B001',
            title='Test Book',
            author='Author',
            available_copies=5
        )
        # Create a loan record
        self.loan = LoanRecord.objects.create(
            loan_id='L001',
            student_username='student',
            student_id='S001',
            book_id='B001',
            book_name='Test Book',
            due_date=timezone.now().date() + timedelta(days=7),
            status='borrowing'
        )

    # ---------- Student loan list ----------
    def test_student_loan_list_requires_login(self):
        response = self.client.get(reverse('student_loan_list'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('student_loan_list')}")

    def test_student_loan_list_shows_only_own_records(self):
        # Create another student's record
        other_user = User.objects.create_user(username='other', password='pass')
        Student.objects.create(user=other_user, student_id='S002')
        LoanRecord.objects.create(
            loan_id='L002',
            student_username='other',
            student_id='S002',
            book_id='B002',
            book_name='Other Book',
            due_date=timezone.now().date() + timedelta(days=7),
            status='borrowing'
        )
        self.client.login(username='student', password='pass')
        response = self.client.get(reverse('student_loan_list'))
        self.assertEqual(len(response.context['loans']), 1)  # Only sees their own
        self.assertEqual(response.context['loans'][0].loan_id, 'L001')

    
    # ---------- Admin loan list ----------
    def test_admin_loan_list_requires_librarian(self):
        url = reverse('admin_loan_list')
        # Unauthenticated redirect
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('login')}?next={url}")
        # Student login should get 403 or redirect (depending on LibrarianRequiredMixin)
        self.client.login(username='student', password='pass')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        # Librarian login succeeds
        self.client.login(username='librarian', password='pass')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


    # ---------- Borrow book ----------
    def test_borrow_book_no_stock(self):
        self.book.available_copies = 0
        self.book.save()
        self.client.login(username='student', password='pass')
        url = reverse('borrow_book', args=[self.book.pk])
        response = self.client.post(url)
        self.assertRedirects(response, reverse('book_list'))
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any('out of stock' in str(m) for m in messages))

    # ---------- Return book ----------
    def test_return_book_requires_login(self):
        url = reverse('return_book', args=[self.loan.loan_id])
        response = self.client.post(url)
        self.assertRedirects(response, f"{reverse('login')}?next={url}")


    def test_return_book_success(self):
        self.client.login(username='student', password='pass')
        url = reverse('return_book', args=[self.loan.loan_id])
        response = self.client.post(url)
        self.assertRedirects(response, reverse('student_loan_list'))
        # Verify record status and book stock
        self.loan.refresh_from_db()
        self.assertEqual(self.loan.status, 'returned')
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 6)  # Originally 5, +1 after return

    # ---------- Admin delete record ----------
    def test_delete_loan_only_returned(self):
        self.client.login(username='librarian', password='pass')
        url = reverse('delete_loan', args=[self.loan.loan_id])  # Current status is borrowing
        response = self.client.post(url)
        self.assertRedirects(response, reverse('admin_loan_list'))
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any('Only returned records' in str(m) for m in messages))

    def test_delete_loan_success(self):
        # First set the record as returned
        self.loan.status = 'returned'
        self.loan.save()
        self.client.login(username='librarian', password='pass')
        url = reverse('delete_loan', args=[self.loan.loan_id])
        response = self.client.post(url)
        self.assertRedirects(response, reverse('admin_loan_list'))
        self.assertEqual(LoanRecord.objects.count(), 0)