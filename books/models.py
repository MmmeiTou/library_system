from django.db import models
from django.core.validators import MinValueValidator

class Book(models.Model):
    book_id = models.CharField('图书编号', max_length=50, unique=True, blank=True)
    title = models.CharField('书名', max_length=200)
    author = models.CharField('作者', max_length=100)
    available_copies = models.PositiveIntegerField(
        '剩余数量',
        validators=[MinValueValidator(0)],
        default=1
    )

    class Meta:
        verbose_name = 'Book'
        

    def __str__(self):
        return f"{self.title} - {self.author}"

