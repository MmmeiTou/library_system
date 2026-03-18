from django.shortcuts import render
from django.views.generic import ListView
from .models import Book
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

class BookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'books/book_list.html'   # 指定模板文件
    context_object_name = 'books'            # 模板中使用的变量名
    paginate_by = 10                          # 每页显示10条（可选）

    '''搜索功能'''
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
    """仅允许图书管理员访问的 Mixin"""
    def test_func(self):
        return self.request.user.is_librarian
    


from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
class BookCreateView(LibrarianRequiredMixin, CreateView):
    model = Book
    fields = ['book_id','title', 'author', 'available_copies']  # 排除 book_id，可以自动生成
    template_name = 'books/book_form.html'
    success_url = reverse_lazy('book_list')  # 完成后跳转到列表页

    def form_valid(self, form):
        # 自动生成 book_id（示例：基于书名和作者，或使用 UUID）
        form.instance.book_id = self.generate_book_id(form.cleaned_data)
        return super().form_valid(form)

    def generate_book_id(self, cleaned_data):
        # 简单生成逻辑：取书名首字母 + 作者 + 时间戳
        import hashlib, time
        base = f"{cleaned_data['title']}-{cleaned_data['author']}-{time.time()}"
        return hashlib.md5(base.encode()).hexdigest()[:10]

class BookUpdateView(LibrarianRequiredMixin, UpdateView):
    model = Book
    fields = ['book_id','title', 'author', 'available_copies']  # 允许修改 book_id（如果需要）
    template_name = 'books/book_form.html'
    success_url = reverse_lazy('book_list')

class BookDeleteView(LibrarianRequiredMixin, DeleteView):
    model = Book
    template_name = 'books/book_confirm_delete.html'
    success_url = reverse_lazy('book_list')