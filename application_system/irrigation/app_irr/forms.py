from django import forms
from app_irr.models import Terrain,Statistique,Adresse,Proprietaire_terrain

class terrain_form(forms.ModelForm):
    class Meta:
        model=Terrain
        
        fields=["arrosage"]
class adresse_form(forms.ModelForm):
    class Meta:
       
        model=Adresse

 
        fields=["numero","quartier","voie","code_postale","ville","pays"]
class proprietaire_form(forms.ModelForm):
    class Meta:
       
        model=Proprietaire_terrain

 
        fields=["cin","nom","prenom","tel","email"]

        

        
class statistique_form(forms.ModelForm):
    class Meta:
        model=Statistique

        fields=["temperature","humidite","HS","FV","RS","date","heure","debit","consommation_eau"]
        
        
                