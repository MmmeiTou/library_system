from django.contrib import admin
from . import models
# Register your models here.

class BookAdmin(admin.ModelAdmin):
    list_display = ('book_id', 'title', 'author', 'available_copies')  # Fields displayed in the list view
    list_filter = ('author',)                                      # Right sidebar filter
    search_fields = ('title', 'author')                            # Fields searchable in the search box
    list_editable = ('available_copies',)                          # Fields directly editable in the list view (use with caution)
    ordering = ('title',)                                           # Default ordering
    list_per_page = 20

admin.site.register(models.Book, BookAdmin)