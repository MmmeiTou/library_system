from django.contrib import admin
from . import models
# Register your models here.
class BookAdmin(admin.ModelAdmin):
    list_display = ('book_id', 'title', 'author', 'available_copies')  # 列表页显示的字段
    list_filter = ('author',)                                      # 右侧过滤器
    search_fields = ('title', 'author')                            # 搜索框可搜索的字段
    list_editable = ('available_copies',)                          # 列表页可直接编辑的字段（谨慎使用）
    ordering = ('title',)                                           # 默认排序
    list_per_page = 20                                        
admin.site.register(models.Book,BookAdmin)