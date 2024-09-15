from django.db import models
from django.contrib.auth.models import User
# Create your models here.





class Adresse(models.Model):
    numero=models.IntegerField(default=2)
    quartier=models.CharField(max_length=200)
    voie=models.CharField(max_length=200)
    code_postale=models.IntegerField(default=150)
    ville=models.CharField(max_length=200)
    pays=models.CharField(max_length=200)
    
class Proprietaire_terrain(models.Model):
    cin=models.CharField(max_length=200,null=True)
    nom=models.CharField(max_length=200,null=True)
    prenom=models.CharField(max_length=200,null=True)
    tel=models.IntegerField(default=144)
    email=models.CharField(max_length=200,null=True)


    
    
class Terrain(models.Model):
    proprietaire=models.ForeignKey(User,on_delete=models.CASCADE)
    id_adresse=models.OneToOneField(Adresse,on_delete=models.CASCADE,null=True)
    arrosage=models.BooleanField()
    fk_prop=models.ForeignKey(Proprietaire_terrain,on_delete=models.CASCADE,null=True)
    
    



class Statistique(models.Model):
    Nterrain=models.ForeignKey(Terrain,on_delete=models.CASCADE)
    temperature = models.FloatField(default=10)
    date=models.DateField()
    heure=models.TimeField()
    humidite = models.FloatField()#%
    HS=models.FloatField()
    FV=models.IntegerField()
    RS=models.FloatField()
    debit=models.FloatField(default=100)
    consommation_eau=models.FloatField(default=100)

   