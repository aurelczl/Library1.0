from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    read = models.BooleanField(default=False)
    genres = models.ManyToManyField(Genre, blank=True)
    image = models.ImageField(upload_to='book_images/', blank=True, null=True)

    def __str__(self):
        return self.title

class Series(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    seasons = models.PositiveIntegerField()
    completed = models.BooleanField(default=False)
    genres = models.ManyToManyField(Genre, blank=True)
    image = models.ImageField(upload_to='series_images/', blank=True, null=True)

    def __str__(self):
        return self.title

class Movie(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    director = models.CharField(max_length=100)
    watched = models.BooleanField(default=False)
    genres = models.ManyToManyField(Genre, blank=True)
    image = models.ImageField(upload_to='movie_images/', blank=True, null=True)

    def __str__(self):
        return self.title
