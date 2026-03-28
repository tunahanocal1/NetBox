from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
import requests
from .models import BookReview, UserBook # UserBook modelini ekledik
from .forms import ReviewForm
from django.http import JsonResponse

def home(request):
    if request.user.is_authenticated:
        # Open Library'den fiction kategorisinde kitaplar (search by subject)
        url = "https://openlibrary.org/subjects/fiction.json?limit=10"
        try:
            response = requests.get(url)
            data = response.json()
            books = []

            for item in data.get('works', []):
                books.append({
                    'title': item.get('title', 'No Title'),
                    'authors': [author.get('name', 'Unknown') for author in item.get('authors', [])],
                    'thumbnail': f"https://covers.openlibrary.org/b/id/{item['cover_id']}-M.jpg" if item.get('cover_id') else None
                })

        except Exception as e:
            print(f"Open Library API error: {e}")
            books = []

        return render(request, 'accounts/home_logged_in.html', {'books': books})
    
    else:
        return render(request, 'accounts/landing.html')


def search(request):
    query = request.GET.get('q', '').strip()
    books = []

    if query:
        url = f"https://openlibrary.org/search.json?q={query}&limit=20"
        try:
            response = requests.get(url)
            data = response.json()
            for item in data.get('docs', []):
                books.append({
                    'title': item.get('title', 'No Title'),
                    'authors': item.get('author_name', ['Unknown']),
                    'thumbnail': f"https://covers.openlibrary.org/b/id/{item['cover_i']}-M.jpg" if item.get('cover_i') else None,
                    'olid': item.get('key').split('/')[-1]  # '/works/OL12345W' → 'OL12345W'
                })
        except Exception as e:
            print(f"Open Library search error: {e}")
            books = []

    return render(request, 'accounts/search.html', {
        'books': books,
        'query': query
    })

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')


from .models import BookReview
from .forms import ReviewForm

from .models import BookReview, UserBook # UserBook modelini eklediğinden emin ol

def book_detail(request, olid):
    url = f"https://openlibrary.org/works/{olid}.json"
    book = {}
    thumbnail_url = None 

    try:
        response = requests.get(url)
        data = response.json()
        book['title'] = data.get('title', 'No Title')

        # GÖRSEL MANTIĞI
        covers = data.get('covers')
        if covers and len(covers) > 0:
            thumbnail_url = f"https://covers.openlibrary.org/b/id/{covers[0]}-L.jpg"

        # Description
        desc = data.get('description')
        if isinstance(desc, dict):
            book['description'] = desc.get('value', '')
        else:
            book['description'] = desc

    except Exception as e:
        print(f"Detail error: {e}")
        book['title'] = "Error loading book"
        book['description'] = ""

    # KULLANICI DURUMU (BURASI YENİ)
    # Giriş yapmış kullanıcının bu kitapla etkileşimini kontrol ediyoruz
    user_book_status = None
    if request.user.is_authenticated:
        user_book_status = UserBook.objects.filter(user=request.user, olid=olid).first()

    # REVIEWS
    reviews = BookReview.objects.filter(olid=olid).order_by('-created_at')

    # Ortalama rating
    avg_rating = None
    if reviews.exists():
        avg_rating = sum(r.rating for r in reviews) / reviews.count()

    # Form gönderme (Review/Yorum için)
    if request.method == 'POST' and 'rating' in request.POST:
        form = ReviewForm(request.POST)
        if form.is_valid() and request.user.is_authenticated:
            review = form.save(commit=False)
            review.user = request.user
            review.olid = olid
            review.rating = request.POST.get('rating')
            review.save()
            return redirect('book_detail', olid=olid)
    else:
        form = ReviewForm()

    return render(request, 'accounts/book_detail.html', {
        'book': book,
        'reviews': reviews,
        'form': form,
        'avg_rating': avg_rating,
        'thumbnail': thumbnail_url,
        'olid': olid, # Şablonun butonlar için buna ihtiyacı var
        'user_book_status': user_book_status, # Butonların rengi için buna ihtiyacı var
    })

@login_required
def toggle_book_status(request, olid):
    if request.method == "POST":
        status_type = request.POST.get('status_type') # 'read', 'liked' veya 'watchlist'
        title = request.POST.get('title')
        thumbnail = request.POST.get('thumbnail')

        # Kayıt varsa getir, yoksa oluştur
        user_book, created = UserBook.objects.get_or_create(
            user=request.user, 
            olid=olid,
            defaults={'title': title, 'thumbnail': thumbnail}
        )

        if status_type == 'read':
            user_book.is_read = not user_book.is_read
        elif status_type == 'liked':
            user_book.is_liked = not user_book.is_liked
        elif status_type == 'watchlist':
            user_book.is_watchlist = not user_book.is_watchlist
        
        user_book.save()
        return redirect('book_detail', olid=olid)
    
    return redirect('home')

@login_required
def user_book_list(request, status_type):
    # status_type: 'read', 'liked' veya 'watchlist' olacak
    
    if status_type == 'read':
        books = UserBook.objects.filter(user=request.user, is_read=True)
        title = "Books I've Read"
    elif status_type == 'liked':
        books = UserBook.objects.filter(user=request.user, is_liked=True)
        title = "Favorite Books"
    else:
        books = UserBook.objects.filter(user=request.user, is_watchlist=True)
        title = "Watchlist"

    return render(request, 'accounts/user_book_list.html', {
        'books': books,
        'title': title
    })

@login_required
def profile_view(request):
    # Kullanıcıya özel kitap listelerini veritabanından çekiyoruz
    read_books = UserBook.objects.filter(user=request.user, is_read=True)
    liked_books = UserBook.objects.filter(user=request.user, is_liked=True)
    watchlist_books = UserBook.objects.filter(user=request.user, is_watchlist=True)
    
    return render(request, 'accounts/profile.html', {
        'read_books': read_books,
        'liked_books': liked_books,
        'watchlist_books': watchlist_books,
    })



