from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Song)
class SongModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
admin.site.register(Playlist)
admin.site.register(Favourite)
admin.site.register(Recent)   
# admin.site.register(Music)