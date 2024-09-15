import os
from celery import Celery

# Définissez la variable d'environnement DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'irrigation.settings')

# Instanciez l'application Celery
app = Celery('irrigation')

# Chargez la configuration Celery depuis les paramètres Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Chargez les tâches Celery de toutes les applications Django installées
app.autodiscover_tasks()