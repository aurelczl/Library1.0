from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Book, Series, Movie, Genre
from .forms import BookForm, SeriesForm, MovieForm
from django.http import Http404

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db.models import Q

# Create your views here.

def home(request):
    return render(request, 'media/home.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Connexion auto après inscription
            return redirect('profile')  # on ira à la page profil ensuite
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def edit_item(request, model_name, item_id):
    # Dictionnaire pour mapper les modèles
    model_mapping = {
        'book': Book,
        'movie': Movie,
        'series': Series
    }
    
    # Récupérer le modèle approprié
    model_class = model_mapping.get(model_name.lower())
    if not model_class:
        return redirect('home')  # Ou une autre page d'erreur si le modèle n'existe pas
    
    # Récupérer l'objet à éditer, vérifiant qu'il appartient à l'utilisateur connecté
    item = get_object_or_404(model_class, id=item_id, user=request.user)

    # Formulaire en fonction du modèle
    if model_class == Book:
        form_class = BookForm
    elif model_class == Movie:
        form_class = MovieForm
    elif model_class == Series:
        form_class = SeriesForm
    else:
        return redirect('home')  # Gestion d'erreur

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=item)
        if form.is_valid():
            item = form.save(user=request.user)
            return redirect('item_detail', model_name=model_name, item_id=item.id)

      # Redirige vers la page de détails après modification

    else:
        form = form_class(instance=item)

    # Extraire les genres sélectionnés pour pré-sélectionner dans le formulaire
    selected_genres = [g.name for g in item.genres.all()]

    return render(request, 'media/edit_item.html', {
        'form': form,
        'instance': item,
        'all_genres': Genre.objects.all(),
        'selected_genres': selected_genres,
        'model_name': model_name  # Passer le nom du modèle pour personnaliser l'affichage si nécessaire
    })

def delete_item(request, model_name, item_id):
    model_mapping = {
        'book': Book,
        'movie': Movie,
        'series': Series
    }

    model_class = model_mapping.get(model_name.lower())
    if not model_class:
        raise Http404("Type inconnu")

    item = get_object_or_404(model_class, id=item_id, user=request.user)
    
    # Supprimer l'élément
    item.delete()
    
    # Rediriger vers la page de profil après suppression
    return redirect('profile')


def add_genre(request):
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            Genre.objects.get_or_create(name=name)
        return redirect('add_book')  # ou une autre vue
    return render(request, 'media/add_genre.html')

def search(request):
    query = request.GET.get('q', '')
    content_type = request.GET.get('type', 'all')

    books = movies = series = []

    if query:
        if content_type == 'book' or content_type == 'all':
            books = Book.objects.filter(
                Q(title__icontains=query) | Q(author__icontains=query),
                user=request.user
            )
        if content_type == 'movie' or content_type == 'all':
            movies = Movie.objects.filter(
                Q(title__icontains=query) | Q(director__icontains=query),
                user=request.user
            )
        if content_type == 'series' or content_type == 'all':
            series = Series.objects.filter(
                Q(title__icontains=query) | Q(director__icontains=query),
                user=request.user
            )

    context = {
        'query': query,
        'books': books,
        'movies': movies,
        'series': series,
    }
    return render(request, 'media/search_results.html', context)

@login_required
def profile(request):
    books = Book.objects.filter(user=request.user)
    series = Series.objects.filter(user=request.user)
    movies = Movie.objects.filter(user=request.user)
    return render(request, 'media/profile.html', {
        'books': books,
        'series': series,
        'movies': movies
    })

@login_required
def home(request):
    books = Book.objects.filter(user=request.user)
    series = Series.objects.filter(user=request.user)
    movies = Movie.objects.filter(user=request.user)
    return render(request, 'media/home.html', {'books': books, 'series': series, 'movies': movies})

MODEL_MAP = {
    'book': Book,
    'movie': Movie,
    'series': Series,
}

def item_detail(request, model_name, item_id):
    model = MODEL_MAP.get(model_name)
    if not model:
        raise Http404("Type inconnu")

    instance = get_object_or_404(model, id=item_id)
    return render(request, 'media/detail_item.html', {
        'instance': instance,
        'model_name': model_name
    })
"""
def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'media/detail_item.html', {
    'instance': book,
    'model_name': 'book'
})

def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    return render(request, 'media/detail_item.html', {
    'instance': movie,
    'model_name': 'movie'
})

def series_detail(request, series_id):
    series = get_object_or_404(Series, id=series_id)
    return render(request, 'media/detail_item.html', {
    'instance': series,
    'model_name': 'series'
})"""

@login_required
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(user=request.user)
            return redirect('profile')
    else:
        form = BookForm()
    
    # Envoie tous les genres pour peupler la liste Select2
    all_genres = Genre.objects.all()

    return render(request, 'media/add_item.html', {
        'form': form,
        'title': 'Ajouter un livre',
        'all_genres': all_genres
    })

@login_required
def add_series(request):
    if request.method == 'POST':
        form = SeriesForm(request.POST, request.FILES)
        if form.is_valid():
            # Passer l'utilisateur connecté à la méthode save
            form.save(user=request.user)
            return redirect('profile') 
    else:
        form = SeriesForm()

    # Envoie tous les genres pour peupler la liste Select2
    all_genres = Genre.objects.all()
    return render(request, 'media/add_item.html', {
        'form': form,
        'title': 'Ajouter une série',
        'all_genres': all_genres
    })

@login_required
def add_movie(request):
    if request.method == 'POST':
        form = MovieForm(request.POST, request.FILES)
        if form.is_valid():
            # Passer l'utilisateur connecté à la méthode save
            form.save(user=request.user)
            return redirect('profile') 
    else:
        form = MovieForm()
    # Envoie tous les genres pour peupler la liste Select2
    all_genres = Genre.objects.all()
    return render(request, 'media/add_item.html', {
        'form': form,
        'title': 'Ajouter un film',
        'all_genres': all_genres
    })
