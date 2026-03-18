from django.urls import path
from . import views

urlpatterns = [
    path('my-loans/', views.StudentLoanListView.as_view(), name='student_loan_list'),
    path('admin-loans/', views.AdminLoanListView.as_view(), name='admin_loan_list'),
    path('borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('return/<str:loan_id>/', views.return_book, name='return_book'),
    path('delete/<str:loan_id>/', views.delete_loan, name='delete_loan'),
]