from django.contrib import admin
from .models import BookReview, UserBook, Book

@admin.register(BookReview)
class BookReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'olid', 'rating', 'created_at') # Tabloda görünecek sütunlar
    list_filter = ('rating', 'created_at') # Sağ tarafta filtreleme paneli
    search_fields = ('user__username', 'comment', 'olid') # Arama çubuğu özelliği

@admin.register(UserBook)
class UserBookAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'is_read', 'is_liked', 'is_watchlist') # Durum takibi
    list_filter = ('is_read', 'is_liked', 'is_watchlist')
    search_fields = ('user__username', 'title', 'olid')

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)
