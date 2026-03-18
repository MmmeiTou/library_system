from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .forms import ForgotPasswordForm, SetPasswordForm
from .forms import StudentRegistrationForm, LibrarianRegistrationForm
from django.contrib.auth.views import PasswordChangeView
from .forms import UserEditForm, StudentProfileForm, LibrarianProfileForm
from django.contrib.auth.decorators import login_required


from django.contrib.auth import get_user_model
User = get_user_model()


def welcomepage(request):
    return render(request, "welcome.html")


class StudentSignUpView(CreateView):
    form_class = StudentRegistrationForm
    template_name = 'accounts/signup_student.html'
    success_url = reverse_lazy('login')  # Redirect to login page after successful registration

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)  # Optional: auto-login after registration
        #super().form_valid(form)
        return redirect('home')  # or redirect to another page

class LibrarianSignUpView(CreateView):
    form_class = LibrarianRegistrationForm
    template_name = 'accounts/signup_librarian.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')

# Use built-in login view, just specify template
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'

# Use built-in logout view
class CustomLogoutView(LogoutView):
    next_page = 'login'  # Redirect after logout


@login_required
def home(request):
    user = request.user
    context = {}
    if hasattr(user, 'student_profile'):
        context['role'] = 'student'
        context['profile'] = user.student_profile
    elif hasattr(user, 'librarian_profile'):
        context['role'] = 'Librarian'
        context['profile'] = user.librarian_profile
    else:
        context['role'] = 'Unknown'
    return render(request, 'home.html', context)




def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            # Store user ID in session for next step
            request.session['reset_user_id'] = form.user.id
            return redirect('set_password')
    else:
        form = ForgotPasswordForm()
    return render(request, 'accounts/forgot_password.html', {'form': form})

def set_password(request):
    # Check if user ID exists in session
    user_id = request.session.get('reset_user_id')
    if not user_id:
        messages.error(request, 'Please verify your identity first')
        return redirect('forgot_password')

    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        form = SetPasswordForm(request.POST)
        if form.is_valid():
            # Set new password
            user.set_password(form.cleaned_data['new_password1'])
            user.save()
            # Keep user logged in (update session hash if current user is logged in)
            if request.user.is_authenticated:
                update_session_auth_hash(request, user)
            # Clear user ID from session
            del request.session['reset_user_id']
            #messages.success(request, 'Password changed successfully, please log in with new password')
            return redirect('password_reset_success')
    else:
        form = SetPasswordForm()
    return render(request, 'accounts/set_password.html', {'form': form}) 


def password_reset_success(request):
    return render(request, 'accounts/password_reset_success.html')



# Profile detail
@login_required
def profile_detail(request):
    user = request.user
    context = {'user_obj': user}
    return render(request, 'accounts/profile_detail.html', context)


from django.db import transaction
from loan.models import LoanRecord  # Import loan record model

# Edit profile
@login_required
@transaction.atomic  # Ensure username and loan records are updated together or not at all
def profile_edit(request):
    user = request.user
    old_username = user.username  # Save old username for later updating loan records

    # Choose the appropriate Profile form based on user type
    if hasattr(user, 'student_profile'):
        profile = user.student_profile
        ProfileForm = StudentProfileForm
    elif hasattr(user, 'librarian_profile'):
        profile = user.librarian_profile
        ProfileForm = LibrarianProfileForm
    else:
        messages.error(request, 'User profile is abnormal, cannot edit')
        return redirect('profile_detail')

    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            saved_user = user_form.save()      # Save user info (may contain new username)
            profile_form.save()

            new_username = saved_user.username
            # If username actually changed, update all related loan records' student_username
            if new_username != old_username:
                updated_count = LoanRecord.objects.filter(student_username=old_username).update(student_username=new_username)
                if updated_count > 0:
                    messages.info(request, f'Synchronized {updated_count} loan record(s) with the new username')

            messages.success(request, 'Profile updated successfully')
            return redirect('profile_detail')
        else:
            messages.error(request, 'Please correct the errors in the form')
    else:
        user_form = UserEditForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/profile_form.html', context)



from .forms import CustomPasswordChangeForm  # Import custom form

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/password_change_form.html'
    success_url = reverse_lazy('profile_detail')
    form_class = CustomPasswordChangeForm  # Specify custom form

    def form_valid(self, form):
        messages.success(self.request, 'Password changed successfully')
        return super().form_valid(form)