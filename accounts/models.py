from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    """
    自定义用户模型，继承AbstractUser，可以添加公共字段。
    如果所有用户都有手机号，可以加在这里；否则保持空白，用Profile扩展。
    """
    # 例如：phone = models.CharField(max_length=15, blank=True)
    pass  # 暂时不添加额外字段
    @property
    def is_librarian(self):
        """判断用户是否关联了 Librarian profile"""
        return hasattr(self, 'librarian_profile')

    # 可选：也可以添加 is_student property
    @property
    def is_student(self):
        return hasattr(self, 'student_profile')


class Student(models.Model):
    """学生扩展信息"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True, verbose_name='student_id')
    
    # 其他学生特有字段

    class Meta:
        verbose_name = 'Student'
        

    def __str__(self):
        return f"{self.user.username} - {self.student_id}"

class Librarian(models.Model):
    """图书管理员扩展信息"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='librarian_profile')
    employee_id = models.CharField(max_length=20, unique=True, verbose_name='librarian_id')
    

    class Meta:
        verbose_name = 'Librarian'
        

    def __str__(self):
        return f"{self.user.username} - {self.employee_id}"