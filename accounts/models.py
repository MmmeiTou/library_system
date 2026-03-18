from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    
    pass  
    @property
    def is_librarian(self):
        """Check if the user has a Librarian profile"""
        return hasattr(self, 'librarian_profile')

    # Optional: also add is_student property
    @property
    def is_student(self):
        return hasattr(self, 'student_profile')


class Student(models.Model):
    """Student extended information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True, verbose_name='student_id')
    
    # Other student-specific fields

    class Meta:
        verbose_name = 'Student'
        

    def __str__(self):
        return f"{self.user.username} - {self.student_id}"

class Librarian(models.Model):
    """Librarian extended information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='librarian_profile')
    employee_id = models.CharField(max_length=20, unique=True, verbose_name='librarian_id')
    

    class Meta:
        verbose_name = 'Librarian'
        

    def __str__(self):
        return f"{self.user.username} - {self.employee_id}"