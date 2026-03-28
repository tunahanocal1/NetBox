def book_detail(request, olid):
    url = f"https://openlibrary.org/works/{olid}.json"
    book = {}
    thumbnail_url = None # Varsayılan olarak boş

    try:
        response = requests.get(url)
        data = response.json()

        book['title'] = data.get('title', 'No Title')

        # GÖRSEL MANTIĞI: OpenLibrary'den kapak ID'sini alıp URL oluşturuyoruz
        covers = data.get('covers')
        if covers and len(covers) > 0:
            # Covers listesindeki ilk ID'yi kullanıyoruz
            thumbnail_url = f"https://covers.openlibrary.org/b/id/{covers[0]}-L.jpg"

        # description
        desc = data.get('description')
        if isinstance(desc, dict):
            book['description'] = desc.get('value', '')
        else:
            book['description'] = desc

    except Exception as e:
        print(f"Detail error: {e}")
        book['title'] = "Error loading book"
        book['description'] = ""

    # REVIEWS
    reviews = BookReview.objects.filter(olid=olid).order_by('-created_at')

    # Ortalama rating
    avg_rating = None
    if reviews.exists():
        avg_rating = sum(r.rating for r in reviews) / reviews.count()

    # Form gönderme
    if request.method == 'POST':
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
        'thumbnail': thumbnail_url # Şablona bu isimle gönderiyoruz
    })
