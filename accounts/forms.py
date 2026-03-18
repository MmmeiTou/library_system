from django import forms
from django.contrib.auth import get_user_model
from .models import Student,Librarian

User = get_user_model()

class StudentRegistrationForm(forms.ModelForm):
    student_id = forms.CharField(max_length=20, label='学号')
    password1 = forms.CharField(
        label='密码',
        widget=forms.PasswordInput,
        help_text=''
    )
    password2 = forms.CharField(
        label='确认密码',
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ['username', 'email']  # 只需基础字段，密码字段我们自定义

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if not password1:
            raise forms.ValidationError('请输入密码')
        if len(password1) < 4:
            raise forms.ValidationError('密码长度不能少于4位')
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('两次输入的密码不一致')
        return password2

    def save(self, commit=True):
        # 创建用户对象（但尚未保存）
        user = super().save(commit=False)
        # 使用 set_password 正确哈希密码
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        # 创建关联的学生资料
        Student.objects.create(
            user=user,
            student_id=self.cleaned_data['student_id']
        )
        return user

class LibrarianRegistrationForm(forms.ModelForm):
    employee_id = forms.CharField(max_length=20, label='工号')
    password1 = forms.CharField(
        label='密码',
        widget=forms.PasswordInput,
        help_text=''
    )
    password2 = forms.CharField(
        label='确认密码',
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if not password1:
            raise forms.ValidationError('请输入密码')
        if len(password1) < 4:
            raise forms.ValidationError('密码长度不能少于4位')
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('两次输入的密码不一致')
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
    username_or_email = forms.CharField(label='用户名或邮箱', max_length=254)

    def clean_username_or_email(self):
        data = self.cleaned_data['username_or_email']
        # 尝试通过用户名或邮箱查找用户
        try:
            user = User.objects.get(username=data)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=data)
            except User.DoesNotExist:
                raise forms.ValidationError('该用户名或邮箱不存在')
        self.user = user  # 将用户对象存储在表单中，供视图使用
        return data

class SetPasswordForm(forms.Form):
    new_password1 = forms.CharField(label='新密码', widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='确认新密码', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password1')
        p2 = cleaned_data.get('new_password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('两次密码输入不一致')
        return cleaned_data


class UserEditForm(forms.ModelForm):
    """编辑用户基本信息（用户名、邮箱）"""
    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_username(self):
        username = self.cleaned_data['username']
        # 排除当前用户，检查用户名是否已被其他用户使用
        if User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise forms.ValidationError('该用户名已被使用')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError('该邮箱已被注册')
        return email

class StudentProfileForm(forms.ModelForm):
    """学生资料编辑表单"""
    class Meta:
        model = Student
        fields = ['student_id']

    def clean_student_id(self):
        student_id = self.cleaned_data['student_id']
        if Student.objects.exclude(pk=self.instance.pk).filter(student_id=student_id).exists():
            raise forms.ValidationError('该学号已存在')
        return student_id

class LibrarianProfileForm(forms.ModelForm):
    """管理员资料编辑表单"""
    class Meta:
        model = Librarian
        fields = ['employee_id']

    def clean_employee_id(self):
        employee_id = self.cleaned_data['employee_id']
        if Librarian.objects.exclude(pk=self.instance.pk).filter(employee_id=employee_id).exists():
            raise forms.ValidationError('该工号已存在')
        return employee_id
    


class CustomPasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        label='旧密码',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        label='新密码',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text=''  # 如果需要帮助文本，可以填写；否则留空
    )
    new_password2 = forms.CharField(
        label='确认新密码',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text=''
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        """验证旧密码是否正确"""
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError('旧密码不正确')
        return old_password

    def clean_new_password1(self):
        """自定义新密码规则：长度 >= 4 位"""
        new_password1 = self.cleaned_data.get('new_password1')
        if not new_password1:
            raise forms.ValidationError('请输入新密码')
        if len(new_password1) < 4:
            raise forms.ValidationError('新密码长度不能少于4位')
        return new_password1

    def clean_new_password2(self):
        """验证两次新密码是否一致"""
        new_password1 = self.cleaned_data.get('new_password1')
        new_password2 = self.cleaned_data.get('new_password2')
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError('两次输入的新密码不一致')
        return new_password2

    def save(self, commit=True):
        """保存新密码到用户对象"""
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user