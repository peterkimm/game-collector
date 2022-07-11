from django.db import models
from django.urls import reverse
from datetime import date
from django.contrib.auth.models import User

TIMES = (
    ('M', 'Morning'),
    ('A', 'Afternoon'),
    ('E', 'Evening')
)

# Create your models here.

class Tag(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return f'{self.name}'

    def get_absolute_url(self):
        return reverse('tags_detail', kwargs={'pk': self.id})


class Game(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=250)
    console = models.CharField(max_length=100)
    year = models.IntegerField()
    tags = models.ManyToManyField(Tag)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def play_for_today(self):
        return self.playing_set.filter(date=date.today()).count() >= len(TIMES)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('detail', kwargs={'game_id': self.id})

class Playing(models.Model):
    date = models.DateField('playing date')
    time = models.CharField(
        max_length=1,
        choices = TIMES,
        default = TIMES[0][0]
        )

    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.get_time_display()} on {self.date}"

    class Meta:
        ordering = ['-date']

class Photo(models.Model):
    url = models.CharField(max_length=200)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    def __str__(self):
        return f"Photo for game_id: {self.game_id} @{self.url}"