from django.contrib import admin
from .models import Student
from .models import Librarian
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse
from django.utils.html import format_html
from django.urls import NoReverseMatch
from django.contrib.admin.utils import quote

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id','user__email')   # 在列表页显示的字段
    search_fields = ('user__username', 'student_id') # 添加搜索框
  




@admin.register(Librarian)
class Librariantest(admin.ModelAdmin):
    list_display=('user', 'employee_id')
    search_fields = ('user__username', 'employee_id')


