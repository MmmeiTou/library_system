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
    return render(request,"welcome.html")


class StudentSignUpView(CreateView):
    form_class = StudentRegistrationForm
    template_name = 'accounts/signup_student.html'
    success_url = reverse_lazy('login')  # 注册成功后跳转到登录页

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)  # 可选：注册后自动登录
        #super().form_valid(form)
        return redirect('home')  # 或重定向到其他页面

class LibrarianSignUpView(CreateView):
    form_class = LibrarianRegistrationForm
    template_name = 'accounts/signup_librarian.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')

# 使用内置登录视图，只需指定模板
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'

# 使用内置注销视图
class CustomLogoutView(LogoutView):
    next_page = 'login'  # 注销后跳转


@login_required
def home(request):
    user = request.user
    context = {}
    if hasattr(user, 'student_profile'):
        context['role'] = 'student'
        context['profile'] = user.student_profile
    elif hasattr(user, 'librarian_profile'):
        context['role'] = '管理员'
        context['profile'] = user.librarian_profile
    else:
        context['role'] = '未知'
    return render(request, 'home.html', context)




def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            # 将用户ID存入session，供下一步使用
            request.session['reset_user_id'] = form.user.id
            return redirect('set_password')
    else:
        form = ForgotPasswordForm()
    return render(request, 'accounts/forgot_password.html', {'form': form})

def set_password(request):
    # 检查session中是否有用户ID
    user_id = request.session.get('reset_user_id')
    if not user_id:
        messages.error(request, '请先验证身份')
        return redirect('forgot_password')

    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        form = SetPasswordForm(request.POST)
        if form.is_valid():
            # 设置新密码
            user.set_password(form.cleaned_data['new_password1'])
            user.save()
            # 保持用户登录状态（如果当前用户已登录，更新session中的hash）
            if request.user.is_authenticated:
                update_session_auth_hash(request, user)
            # 清除session中的用户ID
            del request.session['reset_user_id']
            #messages.success(request, '密码修改成功，请使用新密码登录')
            return redirect('password_reset_success')
    else:
        form = SetPasswordForm()
    return render(request, 'accounts/set_password.html', {'form': form}) 


def password_reset_success(request):
    return render(request, 'accounts/password_reset_success.html')



# 个人资料详情
@login_required
def profile_detail(request):
    user = request.user
    context = {'user_obj': user}
    return render(request, 'accounts/profile_detail.html', context)

# 编辑个人资料
@login_required
def profile_edit(request):
    user = request.user
    # 根据用户类型选择对应的 Profile 表单
    if hasattr(user, 'student_profile'):
        profile = user.student_profile
        ProfileForm = StudentProfileForm
    elif hasattr(user, 'librarian_profile'):
        profile = user.librarian_profile
        ProfileForm = LibrarianProfileForm
    else:
        messages.error(request, '用户资料异常，无法编辑')
        return redirect('profile_detail')

    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, '个人资料更新成功')
            return redirect('profile_detail')
        else:
            messages.error(request, '请修正表单中的错误')
    else:
        user_form = UserEditForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/profile_form.html', context)

# 自定义密码修改视图（使用内置 PasswordChangeView，仅指定模板和跳转地址）
class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/password_change_form.html'
    success_url = reverse_lazy('profile_detail')

    def form_valid(self, form):
        messages.success(self.request, '密码修改成功')
        return super().form_valid(form)