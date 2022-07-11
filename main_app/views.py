from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .models import Game, Tag, Photo
from .forms import PlayingForm
import uuid
import boto3

S3_BASE_URL = 'https://s3.us-west-1.amazonaws.com/'
BUCKET = 'gamecollector-24'

# Create your views here.
def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')


# class Game:  
#   def __init__(self, name, description, console, year,):
#     self.name = name
#     self.description = description
#     self.console = console
#     self.year = year
  

# games = [
#   Game('Valorant', 'competitive 5v5', 'PC', '2020'),
#   Game('Warzone', 'multiplayer battle royale', 'PS4', '2020'),
#   Game('NBA 2K17', 'basketball simulation game', 'PS4', '2017'),
#   Game('Hearthstone', 'strategy card game', 'PC', '2014'),
# ]

@login_required
def games_index(request):
    games = Game.objects.filter(user=request.user)
    return render(request, 'games/index.html', { 'games': games })

@login_required
def games_detail(request, game_id):
    game = Game.objects.get(id=game_id)
    tags_game_doesnt_have = Tag.objects.exclude(id__in = game.tags.all().values_list('id'))
    playing_form = PlayingForm()
    return render(request, 'games/detail.html', { 'game': game, 'playing_form': playing_form, 'tags': tags_game_doesnt_have })  

@login_required
def add_playing(request, game_id):
    form = PlayingForm(request.POST)
    if form.is_valid():
        new_playing = form.save(commit=False)
        new_playing.game_id = game_id
        new_playing.save()
    return redirect('detail', game_id=game_id) 

@login_required
def assoc_tag(request, game_id, tag_id):
    Game.objects.get(id=game_id).tags.add(tag_id)
    return redirect('detail', game_id=game_id) 

@login_required
def assoc_tag_delete(request, game_id, tag_id):
    Game.objects.get(id=game_id).tags.remove(tag_id)
    return redirect('detail', game_id=game_id)


@login_required
def add_photo(request, game_id):
    photo_file = request.FILES.get('photo-file', None)
    if photo_file:
        s3 = boto3.client('s3')
        key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
        try:
            s3.upload_fileobj(photo_file, BUCKET, key)
            url = f"{S3_BASE_URL}{BUCKET}/{key}"
            photo = Photo(url=url, game_id=game_id)
            photo.save()
        except Exception as error:
            print("Error uploading photo: ", error)
            return redirect('detail', game_id=game_id)
    return redirect('detail', game_id=game_id)


def signup(request):
  error_messages = ''
  if request.method == 'POST':
    form = UserCreationForm(request.POST)
    if form.is_valid():
      user = form.save()
      login(request, user)
      return redirect('index')
    else:
      error_messages = 'Invalid Info - Please Try Again'
  form = UserCreationForm()
  context = {'form': form, 'error_messages': error_messages}
  return render(request, 'registration/signup.html', context)






class GameCreate(LoginRequiredMixin, CreateView):
    model = Game
    fields = '__all__'
    success_url = '/games/'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class GameUpdate(LoginRequiredMixin, UpdateView):
    model = Game
    fields = ['description', 'console', 'year']

class GameDelete(LoginRequiredMixin, DeleteView):
    model = Game
    success_url = '/games/'

class TagList(LoginRequiredMixin, ListView):
    model = Tag
    template_name = 'tags/index.html'

class TagDetail(LoginRequiredMixin, DetailView):
    model = Tag
    template_name = 'tags/detail.html'

class TagCreate(LoginRequiredMixin, CreateView):
    model = Tag
    fields = ['name']

class TagUpdate(LoginRequiredMixin, UpdateView):
    model = Tag
    fields = ['name']

class TagDelete(LoginRequiredMixin, DeleteView):
    model = Tag
    success_url = '/tags/'