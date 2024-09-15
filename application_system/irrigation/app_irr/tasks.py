from celery import shared_task
from .forms import statistique_form
from .models import Terrain
from celery import shared_task




@shared_task
def save_statistique_data(terid, post_data):#on a utiliser post_data car on ne peut pas utiliser request n'est pas défini car vous ne pouvez pas passer un objet request en tant que paramètre dans une tâche Celery.
    terassocier = Terrain.objects.get(id=terid)
    form = statistique_form(post_data or None)
    if form.is_valid():
        terassocier=form.save(commit=False)
        terassocier.Nterrain_id = terid
        terassocier.save()