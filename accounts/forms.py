from django import forms
from django.contrib.auth import get_user_model
from .models import Student, Librarian

User = get_user_model()

class StudentRegistrationForm(forms.ModelForm):
    student_id = forms.CharField(max_length=20, label='Student ID')
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput,
        help_text=''
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ['username', 'email']  # Only basic fields, password fields are custom

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if not password1:
            raise forms.ValidationError('Please enter a password')
        if len(password1) < 4:
            raise forms.ValidationError('Password must be at least 4 characters long')
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('The two passwords do not match')
        return password2

    def save(self, commit=True):
        # Create user object (not yet saved)
        user = super().save(commit=False)
        # Use set_password to correctly hash the password
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        # Create associated student profile
        Student.objects.create(
            user=user,
            student_id=self.cleaned_data['student_id']
        )
        return user

class LibrarianRegistrationForm(forms.ModelForm):
    employee_id = forms.CharField(max_length=20, label='Employee ID')
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput,
        help_text=''
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if not password1:
            raise forms.ValidationError('Please enter a password')
        if len(password1) < 4:
            raise forms.ValidationError('Password must be at least 4 characters long')
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('The two passwords do not match')
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        Librarian.objects.create(
            user=user,
            employee_id=self.cleaned_data['employee_id']
        )
        return user


class ForgotPasswordForm(forms.Form):
    username_or_email = forms.CharField(label='Username or Email', max_length=254)

    def clean_username_or_email(self):
        data = self.cleaned_data['username_or_email']
        # Try to find user by username or email
        try:
            user = User.objects.get(username=data)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=data)
            except User.DoesNotExist:
                raise forms.ValidationError('This username or email does not exist')
        self.user = user  # Store the user object in the form for use in views
        return data

class SetPasswordForm(forms.Form):
    new_password1 = forms.CharField(label='New Password', widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='Confirm New Password', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password1')
        p2 = cleaned_data.get('new_password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('The two passwords do not match')
        return cleaned_data


class UserEditForm(forms.ModelForm):
    """Edit basic user information (username, email)"""
    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_username(self):
        username = self.cleaned_data['username']
        # Exclude current user, check if username is already used by another user
        if User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise forms.ValidationError('This username is already taken')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError('This email is already registered')
        return email

class StudentProfileForm(forms.ModelForm):
    """Student profile edit form"""
    class Meta:
        model = Student
        fields = ['student_id']

    def clean_student_id(self):
        student_id = self.cleaned_data['student_id']
        if Student.objects.exclude(pk=self.instance.pk).filter(student_id=student_id).exists():
            raise forms.ValidationError('This student ID already exists')
        return student_id

class LibrarianProfileForm(forms.ModelForm):
    """Librarian profile edit form"""
    class Meta:
        model = Librarian
        fields = ['employee_id']

    def clean_employee_id(self):
        employee_id = self.cleaned_data['employee_id']
        if Librarian.objects.exclude(pk=self.instance.pk).filter(employee_id=employee_id).exists():
            raise forms.ValidationError('This employee ID already exists')
        return employee_id
    

class CustomPasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        label='Old Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text=''  # Add help text if needed, otherwise leave empty
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text=''
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        """Verify old password is correct"""
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError('Old password is incorrect')
        return old_password

    def clean_new_password1(self):
        """Custom new password rule: at least 4 characters long"""
        new_password1 = self.cleaned_data.get('new_password1')
        if not new_password1:
            raise forms.ValidationError('Please enter a new password')
        if len(new_password1) < 4:
            raise forms.ValidationError('New password must be at least 4 characters long')
        return new_password1

    def clean_new_password2(self):
        """Verify the two new passwords match"""
        new_password1 = self.cleaned_data.get('new_password1')
        new_password2 = self.cleaned_data.get('new_password2')
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError('The two new passwords do not match')
        return new_password2

    def save(self, commit=True):
        """Save the new password to the user object"""
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user