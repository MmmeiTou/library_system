from django.test import TestCase

# Create your tests here.
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock

from .models import Student, Librarian
from .forms import StudentRegistrationForm, ForgotPasswordForm, UserEditForm, StudentProfileForm

User = get_user_model()

class ModelTests(TestCase):
    # Core model functionality tests
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_user_properties(self):
        # Test is_librarian and is_student properties
        self.assertFalse(self.user.is_librarian)
        self.assertFalse(self.user.is_student)
        
        Librarian.objects.create(user=self.user, employee_id='L001')
        Student.objects.create(user=self.user, student_id='S001')
        user = User.objects.get(pk=self.user.pk)
        self.assertTrue(user.is_librarian)
        self.assertTrue(user.is_student)

    def test_profile_string_methods(self):
        # Test __str__ methods of Student and Librarian
        student = Student.objects.create(user=self.user, student_id='S123')
        librarian = Librarian.objects.create(user=self.user, employee_id='L456')
        self.assertEqual(str(student), f"{self.user.username} - S123")
        self.assertEqual(str(librarian), f"{self.user.username} - L456")


class FormTests(TestCase):
    # Core form functionality tests
    
    def setUp(self):
        self.user = User.objects.create_user(username='existing', email='old@test.com')

    def test_student_registration_valid(self):
        # Student registration form: valid data should create user and profile
        data = {
            'username': 'newstudent',
            'email': 'new@test.com',
            'password1': 'pass1234',
            'password2': 'pass1234',
            'student_id': 'S001'
        }
        form = StudentRegistrationForm(data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(User.objects.count(), 2)  # Includes the user from setUp
        self.assertTrue(hasattr(user, 'student_profile'))
        self.assertEqual(user.student_profile.student_id, 'S001')

    def test_student_registration_password_mismatch(self):
        # Password mismatch should raise an error
        data = {
            'username': 'newstudent',
            'email': 'new@test.com',
            'password1': 'pass1234',
            'password2': 'different',
            'student_id': 'S001'
        }
        form = StudentRegistrationForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_forgot_password_valid(self):
        # Forgot password form: find user by username
        form = ForgotPasswordForm(data={'username_or_email': 'existing'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.user, self.user)

    def test_forgot_password_invalid(self):
        # Non-existent username should raise an error
        form = ForgotPasswordForm(data={'username_or_email': 'unknown'})
        self.assertFalse(form.is_valid())

    def test_user_edit_form_unique_username(self):
        # When editing a user, username must not conflict with another user
        User.objects.create_user(username='other', email='other@test.com')
        form = UserEditForm(data={'username': 'other', 'email': 'new@test.com'}, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_student_profile_form_unique_student_id(self):
        # Student ID must be unique
        other_user = User.objects.create_user(username='other')
        Student.objects.create(user=other_user, student_id='S001')
        student = Student.objects.create(user=self.user, student_id='S002')
        form = StudentProfileForm(data={'student_id': 'S001'}, instance=student)
        self.assertFalse(form.is_valid())
        self.assertIn('student_id', form.errors)


class ViewTests(TestCase):
    # Core view functionality tests

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.student_user = User.objects.create_user(username='student', password='pass')
        Student.objects.create(user=self.student_user, student_id='S001')

    # ---------- Signup ----------
    def test_student_signup(self):
        # Successful student signup should redirect to home and auto-login
        data = {
            'username': 'newstudent',
            'email': 'new@test.com',
            'password1': 'pass1234',
            'password2': 'pass1234',
            'student_id': 'S100'
        }
        response = self.client.post(reverse('signup_student'), data)
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(User.objects.filter(username='newstudent').exists())
        self.assertIn('_auth_user_id', self.client.session)

    # ---------- Login ----------
    def test_login(self):
        # Correct credentials should log in and redirect to home
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpass'})
        self.assertRedirects(response, reverse('home'))
        self.assertIn('_auth_user_id', self.client.session)

    # ---------- Home view ----------
    def test_home_view(self):
        # After login, home should display correct role and profile
        self.client.login(username='student', password='pass')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['role'], 'student')
        self.assertEqual(response.context['profile'], self.student_user.student_profile)

    # ---------- Forgot password flow ----------
    def test_forgot_password_flow(self):
        # Complete forgot password flow: submit username -> set new password -> success
        # Step 1: Submit username
        response = self.client.post(reverse('forgot_password'), {'username_or_email': 'testuser'})
        self.assertRedirects(response, reverse('set_password'))
        self.assertEqual(self.client.session.get('reset_user_id'), self.user.pk)

        # Step 2: Set new password
        response = self.client.post(reverse('set_password'), {
            'new_password1': 'newpass123',
            'new_password2': 'newpass123'
        })
        self.assertRedirects(response, reverse('password_reset_success'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass123'))
        self.assertNotIn('reset_user_id', self.client.session)