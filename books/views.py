from django.shortcuts import render
from django.views.generic import ListView
from .models import Book
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

class BookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'books/book_list.html'   # Specify template file
    context_object_name = 'books'            # Variable name used in the template
    paginate_by = 10                         # Number of items per page (optional)

    '''Search functionality'''
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(book_id__icontains=search_query) |
                Q(title__icontains=search_query) |
                Q(author__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context



from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class LibrarianRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin that only allows librarian access"""
    def test_func(self):
        return self.request.user.is_librarian



from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView

class BookCreateView(LibrarianRequiredMixin, CreateView):
    model = Book
    fields = ['book_id', 'title', 'author', 'available_copies']  # Include book_id, can be auto-generated
    template_name = 'books/book_form.html'
    success_url = reverse_lazy('book_list')  # Redirect to list page after completion

    def form_valid(self, form):
        # Auto-generate book_id (example: based on title and author, or use UUID)
        form.instance.book_id = self.generate_book_id(form.cleaned_data)
        return super().form_valid(form)

    def generate_book_id(self, cleaned_data):
        # Simple generation logic: take first letters of title + author + timestamp
        import hashlib, time
        base = f"{cleaned_data['title']}-{cleaned_data['author']}-{time.time()}"
        return hashlib.md5(base.encode()).hexdigest()[:10]

class BookUpdateView(LibrarianRequiredMixin, UpdateView):
    model = Book
    fields = ['book_id', 'title', 'author', 'available_copies']  # Allow modifying book_id (if needed)
    template_name = 'books/book_form.html'
    success_url = reverse_lazy('book_list')

class BookDeleteView(LibrarianRequiredMixin, DeleteView):
    model = Book
    template_name = 'books/book_confirm_delete.html'
    success_url = reverse_lazy('book_list')