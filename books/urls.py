from django.urls import path
from . import views


urlpatterns = [
    path('', views.BookListView.as_view(), name='book_list'),
    path('books/create/', views.BookCreateView.as_view(), name='book_create'),
    path('books/<int:pk>/update/', views.BookUpdateView.as_view(), name='book_update'),
    path('books/<int:pk>/delete/', views.BookDeleteView.as_view(), name='book_delete'),
]