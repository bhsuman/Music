import warnings
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Song, Playlist, Favourite, Recent, Document
from .forms import DocumentForm
from .Metadata import getmetadata
from .predict import predict_gen

warnings.simplefilter('ignore')


def get_last_played_song(user=None):
    if user and user.is_authenticated:
        recent = Recent.objects.filter(user=user).order_by('-id').first()
        if recent and recent.song:
            return recent.song
    recent = Recent.objects.order_by('-id').first()
    if recent and recent.song:
        return recent.song
    return Song.objects.first()


def index(request):
    recent_songs = None
    if request.user.is_authenticated:
        recent_ids = list(Recent.objects.filter(user=request.user).order_by('-id').values_list('song_id', flat=True))
        seen = set()
        ordered_ids = [x for x in recent_ids if not (x in seen or seen.add(x))][:5]
        song_map = {s.id: s for s in Song.objects.filter(id__in=ordered_ids)}
        recent_songs = [song_map[i] for i in ordered_ids if i in song_map]

    first_time = not (request.user.is_authenticated and Recent.objects.filter(user=request.user).exists())
    last_played_song = get_last_played_song(request.user)

    songs = Song.objects.all()
    songs_by_language = {}
    for song in songs:
        lang = song.language or 'Unknown'
        if lang in songs_by_language:
            songs_by_language[lang].append(song)
        else:
            songs_by_language[lang] = [song]

    songs_all = list(Song.objects.all().values_list('id', flat=True).order_by('?'))
    sliced_ids = songs_all[:5]
    indexpage_songs = Song.objects.filter(id__in=sliced_ids)

    songs_hindi = list(Song.objects.filter(language__iexact='Hindi').values_list('id', flat=True))
    indexpage_hindi_songs = Song.objects.filter(id__in=songs_hindi[:5])

    songs_english = list(Song.objects.filter(language__iexact='English').values_list('id', flat=True))
    indexpage_english_songs = Song.objects.filter(id__in=songs_english[:5])

    search_query = request.GET.get('q')
    if search_query:
        filtered_songs = songs.filter(Q(name__icontains=search_query)).distinct()
        context = {'all_songs': filtered_songs, 'last_played': last_played_song, 'query_search': True}
        return render(request, 'musicapp/index.html', context)

    context = {
        'all_songs': indexpage_songs,
        'recent_songs': recent_songs,
        'hindi_songs': indexpage_hindi_songs,
        'english_songs': indexpage_english_songs,
        'last_played': last_played_song,
        'first_time': first_time,
        'query_search': False,
        'songs_by_language': songs_by_language
    }
    return render(request, 'musicapp/index.html', context=context)


def hindi_songs(request):
    hindi_songs = Song.objects.filter(language__iexact='Hindi')
    last_played_song = get_last_played_song(request.user)

    query = request.GET.get('q')
    if query:
        hindi_songs = hindi_songs.filter(Q(name__icontains=query)).distinct()
        context = {'hindi_songs': hindi_songs, 'last_played': last_played_song, 'query_search': True}
        return render(request, 'musicapp/hindi_songs.html', context)

    context = {'hindi_songs': hindi_songs, 'last_played': last_played_song}
    return render(request, 'musicapp/hindi_songs.html', context=context)


def english_songs(request):
    english_songs = Song.objects.filter(language__iexact='English')
    last_played_song = get_last_played_song(request.user)

    query = request.GET.get('q')
    if query:
        english_songs = english_songs.filter(Q(name__icontains=query)).distinct()
        context = {'english_songs': english_songs, 'last_played': last_played_song, 'query_search': True}
        return render(request, 'musicapp/english_songs.html', context)

    context = {'english_songs': english_songs, 'last_played': last_played_song}
    return render(request, 'musicapp/english_songs.html', context=context)


@login_required(login_url='login')
def play_song(request, song_id):
    song = Song.objects.filter(id=song_id).first()
    if song:
        Recent.objects.filter(song=song, user=request.user).delete()
        Recent.objects.create(song=song, user=request.user)
    return redirect('all_songs')


@login_required(login_url='login')
def play_song_index(request, song_id):
    song = Song.objects.filter(id=song_id).first()
    if song:
        Recent.objects.filter(song=song, user=request.user).delete()
        Recent.objects.create(song=song, user=request.user)
    return redirect('index')


@login_required(login_url='login')
def play_recent_song(request, song_id):
    song = Song.objects.filter(id=song_id).first()
    if song:
        Recent.objects.filter(song=song, user=request.user).delete()
        Recent.objects.create(song=song, user=request.user)
    return redirect('recent')


def all_songs(request):
    songs = Song.objects.all()
    first_time = not (request.user.is_authenticated and Recent.objects.filter(user=request.user).exists())
    last_played_song = get_last_played_song(request.user)

    qs_singers = Song.objects.values_list('singer', flat=True)
    all_singers = sorted(list(set([s.strip() for singer in qs_singers if singer for s in singer.split(',') if s.strip()])))

    qs_languages = Song.objects.values_list('language', flat=True)
    all_languages = sorted(list(set([l.strip() for lang in qs_languages if lang for l in lang.split(',') if l.strip()])))

    if len(request.GET) > 0:
        search_query = request.GET.get('q') or ''
        search_singer = request.GET.get('singers') or ''
        search_language = request.GET.get('languages') or ''
        filtered_songs = songs
        if search_query:
            filtered_songs = filtered_songs.filter(name__icontains=search_query)
        if search_singer:
            filtered_songs = filtered_songs.filter(singer__icontains=search_singer)
        if search_language:
            filtered_songs = filtered_songs.filter(language__icontains=search_language)
        filtered_songs = filtered_songs.distinct()
        context = {
            'songs': filtered_songs,
            'last_played': last_played_song,
            'all_singers': all_singers,
            'all_languages': all_languages,
            'query_search': True,
        }
        return render(request, 'musicapp/all_songs.html', context)

    context = {
        'songs': songs,
        'last_played': last_played_song,
        'first_time': first_time,
        'all_singers': all_singers,
        'all_languages': all_languages,
        'query_search': False,
    }
    return render(request, 'musicapp/all_songs.html', context=context)


@login_required(login_url='login')
def recent(request):
    last_played_song = get_last_played_song(request.user)

    recent_ids = list(Recent.objects.filter(user=request.user).order_by('-id').values_list('song_id', flat=True))
    seen = set()
    ordered_ids = [x for x in recent_ids if not (x in seen or seen.add(x))]
    song_map = {s.id: s for s in Song.objects.filter(id__in=ordered_ids)}
    recent_songs = [song_map[i] for i in ordered_ids if i in song_map]

    query = request.GET.get('q')
    if query:
        filtered_songs = [s for s in recent_songs if query.lower() in s.name.lower()]
        context = {'recent_songs': filtered_songs, 'last_played': last_played_song, 'query_search': True}
        return render(request, 'musicapp/recent.html', context)

    context = {'recent_songs': recent_songs, 'last_played': last_played_song, 'query_search': False}
    return render(request, 'musicapp/recent.html', context=context)


@login_required(login_url='login')
def detail(request, song_id):
    songs = Song.objects.filter(id=song_id).first()
    if not songs:
        return redirect('index')

    Recent.objects.filter(song=songs, user=request.user).delete()
    Recent.objects.create(song=songs, user=request.user)

    last_played_song = get_last_played_song(request.user)
    playlists = Playlist.objects.filter(user=request.user).values('playlist_name').distinct()
    is_favourite = Favourite.objects.filter(user=request.user, song=songs, is_fav=True).exists()

    if request.method == "POST":
        if 'playlist' in request.POST:
            playlist_name = request.POST["playlist"]
            if playlist_name and playlist_name != "Add to Playlist":
                Playlist.objects.create(user=request.user, song=songs, playlist_name=playlist_name)
                messages.success(request, "Song added to playlist!")
        elif 'add-fav' in request.POST:
            Favourite.objects.update_or_create(user=request.user, song=songs, defaults={'is_fav': True})
            messages.success(request, "Added to favorite!")
            return redirect('detail', song_id=song_id)
        elif 'rm-fav' in request.POST:
            Favourite.objects.filter(user=request.user, song=songs).delete()
            messages.success(request, "Removed from favorite!")
            return redirect('detail', song_id=song_id)

    context = {'songs': songs, 'playlists': playlists, 'is_favourite': is_favourite, 'last_played': last_played_song}
    return render(request, 'musicapp/detail.html', context=context)


@login_required(login_url='login')
def mymusic(request):
    return render(request, 'musicapp/mymusic.html')


@login_required(login_url='login')
def playlist(request):
    playlists = Playlist.objects.filter(user=request.user).values('playlist_name').distinct()
    context = {'playlists': playlists}
    return render(request, 'musicapp/playlist.html', context=context)


@login_required(login_url='login')
def playlist_songs(request, playlist_name):
    songs = Song.objects.filter(playlist__playlist_name=playlist_name, playlist__user=request.user).distinct()

    if request.method == "POST":
        post_keys = [k for k in request.POST.keys() if k != 'csrfmiddlewaretoken']
        if post_keys:
            song_id = post_keys[0]
            Playlist.objects.filter(playlist_name=playlist_name, song__id=song_id, user=request.user).delete()
            messages.success(request, "Song removed from playlist!")
            songs = Song.objects.filter(playlist__playlist_name=playlist_name, playlist__user=request.user).distinct()

    context = {'playlist_name': playlist_name, 'songs': songs}
    return render(request, 'musicapp/playlist_songs.html', context=context)


@login_required(login_url='login')
def favourite(request):
    songs = Song.objects.filter(favourite__user=request.user, favourite__is_fav=True).distinct()

    if request.method == "POST":
        post_keys = [k for k in request.POST.keys() if k != 'csrfmiddlewaretoken']
        if post_keys:
            song_id = post_keys[0]
            Favourite.objects.filter(user=request.user, song__id=song_id).delete()
            messages.success(request, "Removed from favourite!")
            songs = Song.objects.filter(favourite__user=request.user, favourite__is_fav=True).distinct()

    context = {'songs': songs}
    return render(request, 'musicapp/favourite.html', context=context)


@login_required(login_url='login')
def upload(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        album = request.POST.get('album')
        song_img = request.FILES.get('song_img')
        year = request.POST.get('year')
        singer = request.POST.get('singer')
        song_file = request.FILES.get('song_file')
        genre = 'Other'
        try:
            meta = getmetadata(song_file)
            genre = predict_gen(meta)
        except Exception:
            genre = 'Other'
        music = Song(
            name=name,
            album=album,
            language=genre,
            song_img=song_img,
            year=year or 2026,
            singer=singer,
            song_file=song_file
        )
        music.save()
        messages.success(request, f"Song '{name}' uploaded successfully with predicted genre '{genre}'!")
        return redirect('index')

    return render(request, 'musicapp/upload.html')
