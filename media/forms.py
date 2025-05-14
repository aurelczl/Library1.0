from django import forms
from .models import Book, Series, Movie, Genre

class BookForm(forms.ModelForm):
    raw_genres = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )

    class Meta:
        model = Book
        fields = ['title', 'author', 'read', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_raw_genres(self):
        raw = self.cleaned_data.get('raw_genres', '')
        names = [name.strip() for name in raw.split(',') if name.strip()]
        genres = []
        for name in names:
            genre, _ = Genre.objects.get_or_create(name=name)
            genres.append(genre)
        return genres

    def save(self, user, commit=True):
        book = super().save(commit=False)
        book.user = user
        if commit:
            book.save()

        # genres = self.cleaned_data.get('genres') ne marche plus
        genres = self.cleaned_data.get('raw_genres', [])
        book.genres.set(genres)
        return book


class SeriesForm(forms.ModelForm):
    raw_genres = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )

    class Meta:
        model = Series
        fields = ['title', 'seasons', 'completed', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_raw_genres(self):
        raw = self.cleaned_data.get('raw_genres', '')
        names = [name.strip() for name in raw.split(',') if name.strip()]
        genres = []
        for name in names:
            genre, _ = Genre.objects.get_or_create(name=name)
            genres.append(genre)
        return genres

    def save(self, user, commit=True):
        serie = super().save(commit=False)
        serie.user = user
        if commit:
            serie.save()
            serie.genres.set(self.cleaned_data.get('raw_genres', []))
        return serie

    
class MovieForm(forms.ModelForm):
    raw_genres = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Movie
        fields = ['title', 'director', 'watched', 'image', 'raw_genres']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            existing = ','.join([g.name for g in self.instance.genres.all()])
            self.fields['raw_genres'].initial = existing

    def clean_raw_genres(self):
        raw = self.cleaned_data.get('raw_genres', '')
        names = [name.strip() for name in raw.split(',') if name.strip()]
        genres = []
        for name in names:
            genre, _ = Genre.objects.get_or_create(name=name)
            genres.append(genre)
        return genres

    def save(self, user, commit=True):
        movie = super().save(commit=False)
        movie.user = user
        if commit:
            movie.save()
            self.save_m2m()

        # assign genres
        genres = self.cleaned_data.get('raw_genres', [])
        if genres:
            movie.genres.set(genres)
        else:
            movie.genres.clear()

        return movie
