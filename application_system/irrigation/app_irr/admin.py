from django.contrib import admin
from .models import Terrain,Statistique
from .models import Proprietaire_terrain,Adresse

# Register your models here.
#admin.site.register(terre)
admin.site.register(Proprietaire_terrain)
admin.site.register(Terrain)
admin.site.register(Adresse)
admin.site.register(Statistique)
# admin.site.register(Group)