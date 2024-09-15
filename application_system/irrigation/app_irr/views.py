from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse 
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Proprietaire_terrain,Terrain,Statistique,Adresse
from app_irr.forms import terrain_form,statistique_form,adresse_form,proprietaire_form
from datetime import datetime,timedelta,date
from django.db.models import Sum
from django.db.models.functions import Trunc
import numpy as np
from django.utils import timezone
from .tasks import save_statistique_data
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense, LSTM
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import matplotlib








# Create your views here.


def home(request):
    return render(request,'app_irr/index.html')

def navbar(request):
    return render(request,'app_irr/navbar.html')

def d(request):
  
    terrains = Terrain.objects.filter(proprietaire__id=request.user.id)
    labels = []
    data = []

    for terrain in terrains:
        labels.append(str(terrain.fk_prop.nom))
        data.append(1)  # Vous pouvez modifier cette valeur en fonction de vos besoins

    context = {
        'labels': labels,
        'data': data,
    }
    return render(request,'app_irr/d.html',context)

def register(request):
  
    if request.method=="POST":
        username=request.POST['username']
        firstname=request.POST['firstname']
        lastname=request.POST['lastname']
        Email=request.POST['Email']
        password=request.POST['password']
        password1=request.POST['password1']
        if User.objects.filter(username=username):
            messages.error(request,'Ce nom existe dèja')
            return redirect('register')
        if User.objects.filter(email=Email):
            messages.error(request,'Cette email existe déja ')
            return redirect('register')
        if not username.isalnum():
            messages.error(request,'Le nom doit être alphabétiques')
            return redirect('register')
        if password!=password1:
            messages.error(request,'Les deux mots de passes ne sont pas identiques')
            return redirect('register')
                               

        mon_user=User.objects.create_user(username,Email,password) #Ce code crée un nouvel utilisateur dans une base de données utilisant le modèle User fourni par Django.
        mon_user.first_name=firstname
        mon_user.last_name=lastname
        mon_user.save()
        messages.success(request,'votre compte est créer avec succès')
        return redirect('login')

    return render(request,'app_irr/register.html')  

def logIn(request):
    if request.method=="POST":
       username=request.POST['username']
       password=request.POST['password']
       user=authenticate(username=username,password=password)
       if user is not None:
        login(request,user)
        firstname=user.first_name
        #return render(request,'app_irr/show_address_static.html' ,{'firstname':firstname})
        return redirect('d')
       else:
            messages.error(request,'mauvaise authentification')
            return redirect('login')
        
       
    return render(request,'app_irr/login.html' )



    




def logOut(request):
    logout(request)
    messages.success(request,'vous avez bien déconnecter')
    return redirect('home')

def admin(request):

        return render(request,'app_irr/admin.html')

def admin_update(request):
   context={}
   
   if request.method == 'POST':
       print(request.POST)
       fn = request.POST["fname"]
       ln = request.POST["lname"]
       em = request.POST["email"]     
       usr = User.objects.get(id=request.user.id)
       usr.first_name = fn
       usr.last_name = ln
       usr.email = em
       usr.save()
       
      
      
       
       context["status"] = "votre formulaire a été bien enregistré"
   return render(request,'app_irr/admin_update.html', context)


def terrain(request):
    context={}
    usr=User.objects.filter(id=request.user.id)
    if len(usr)>0:
        data=User.objects.get(id=request.user.id)
        context["data"]=data
    form=terrain_form()
    form1=adresse_form()
    form2=proprietaire_form()
    if request.method=="POST":
        form=terrain_form(request.POST)
        form1=adresse_form(request.POST)
        form2=proprietaire_form(request.POST)
        if form.is_valid():
           
            data=form.save(commit=False)
            login_user = User.objects.get(username=request.user.username)
            data.proprietaire = login_user
            
            #t=Proprietaire_terrain.objects.get(user_id=request.user.id)
           # data.fk_prop_id=t.id
            #data.save()

            context["status"]="{}  votre formulaire a été bien enregistré"
        if form1.is_valid():
            adresse_obj=form1.save(commit=False)
            adresse_obj.save()
            data.id_adresse = adresse_obj
            data.save()
            context["status"]="{} votre formulaire a été bien enregistré"
        if form2.is_valid():
            prp_obj=form2.save(commit=False)
            prp_obj.save()
            data.fk_prop= prp_obj
            data.save()
            context["status"]="{}  votre formulaire a été bien enregistré"   
    context['form']=form
    context['form1']=form1
    context['form2']=form2

    
    return render(request,"app_irr/terrain.html",context)


def terre_data(request):
    context={}
    usr=User.objects.filter(id=request.user.id)
    if len(usr)>0:
        data=User.objects.get(id=request.user.id)
        context["data"]=data
    all=Terrain.objects.filter(proprietaire__id=request.user.id)
    
    all1_ids = [t.id_adresse_id for t in all]
    all1 = Adresse.objects.filter(id__in=all1_ids).distinct()
    
    context["terre"]=all
    context["all1"] = all1
    return render(request,"app_irr/terre_data.html",context)

def terrain_update(request):
    context={}
    terreid=request.GET["terreid"]
    terredonne=get_object_or_404(Terrain,id=terreid)
    context["terredonne"]=terredonne
    if request.method=='POST':
        arg=request.POST["arrosage"]
        nm=request.POST["nom"]
        pn=request.POST["prenom"]
        tl=request.POST["tel"]
        em=request.POST["mail"]
        cin=request.POST["cin"]
        n=request.POST["num"]
        qr=request.POST["qrt"]
        v=request.POST["vo"]
        cp=request.POST["cpo"]
        vil=request.POST["ville"]
        py=request.POST["pays"]

        terredonne.arrosage=arg
        terredonne.fk_prop.cin=cin
        terredonne.fk_prop.nom=nm
        terredonne.fk_prop.prenom=pn
        terredonne.fk_prop.tel=tl
        terredonne.fk_prop.email=em
        terredonne.id_adresse.numero=n
        terredonne.id_adresse.quartier=qr
        terredonne.id_adresse.voie=v
        terredonne.id_adresse.code_postale=cp
        terredonne.id_adresse.ville=vil
        terredonne.id_adresse.pays=py
        terredonne.save()
        terredonne.id_adresse.save()
        terredonne.fk_prop.save()

        context["status"] = "les données ont été bien modifiées"
        context["id"]=terredonne
    return render(request,'app_irr/terrain_update.html', context)



def show_address_static(request):
    context={}
    usr=User.objects.filter(id=request.user.id)
    if len(usr)>0:
        data=User.objects.get(id=request.user.id)
        context["data"]=data
    all=Terrain.objects.filter(proprietaire__id=request.user.id)
    all1_ids = [t.id_adresse_id for t in all]
    all1 = Adresse.objects.filter(id__in=all1_ids)
    context["all1"]=all1
    context["terre"]=all
    return render(request,"app_irr/show_address_static.html",context)
@login_required
 

@login_required
def statistique_create(request):
    context={}
    terid=request.GET["terid"]
    terassocier = get_object_or_404(Terrain, id=terid)#récupérer un objet du modèle Terrain en utilisant le paramètre id égal à terid.
    context["terassocier"]=terassocier
    form=statistique_form()
    if request.method=="POST":
        form=statistique_form(request.POST)
        if form.is_valid():
            save_statistique_data.delay(terid, request.POST)#la tâche sera exécutée de manière asynchrone en arrière-plan par le travailleur Celery.
            terassocier=form.save(commit=False)#changer la valeur de terassocier(form:statistique)
            terassocier.Nterrain_id = terid
            terassocier.save()
            # Planifier l'exécution de la tâche save_statistique_data chaque heure
            schedule, _ = IntervalSchedule.objects.get_or_create(
                every=1,
                period=IntervalSchedule.HOURS,
            )
            task_name = f"votre formulaire a été bien enregistré {terid} - {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
            task = PeriodicTask.objects.create(
            interval=schedule,
            name=task_name,
            task='app_irr.tasks.save_statistique_data',
            args=[terid],
            )
            task.enabled = True
            task.save()
            context["status"]=" votre formulaire a été bien enregistré" 
            
    context['form']=form
   
    return render(request,"app_irr/statistique_create.html",context)



      
def statistique(request):
    terid=request.GET["terid"]

#les graphes
    context={}
    labels=[]
    dt=[]
    humidite=[]
    HS=[]
    FV=[]
    RS=[]
    debit=[]
 
    queryset=Statistique.objects.filter(Nterrain_id=terid)
    
    for tmp in queryset:
        labels.append(tmp.temperature)
        dt.append(tmp.date.strftime('%Y-%m-%d'))
        humidite.append(tmp.humidite)
        HS.append(tmp.HS)
        FV.append(tmp.FV)
        RS.append(tmp.RS)
        #consomation d'eau sur echelle
    # Données pour les dernières semaines
    semaine = queryset.annotate(date_trunc=Trunc('date', 'week')).values('date_trunc').annotate(consommation=Sum('consommation_eau')).order_by('-date_trunc')[:1]
    semaine_data = [{
        'x': datetime.strftime(item['date_trunc'], '%Y-%m-%d'),
        'y': item['consommation']
        } for item in semaine[::-1]]
        
    mois = queryset.annotate(date_trunc=Trunc('date', 'month')).values('date_trunc').annotate(consommation=Sum('consommation_eau')).order_by('-date_trunc')[:1]
    mois_data = [{
        'x': datetime.strftime(item['date_trunc'], '%Y-%m-%d'),
        'y': item['consommation']
        } for item in mois[::-1]]

        # Données pour le dernier semestre
    semestre = queryset.filter(date__gte=timezone.now() - timezone.timedelta(days=180)).aggregate(total=Sum('consommation_eau'))['total'] or 0
    semestre_data = [{    'x': 'Derniers 6 mois',    'y': semestre}]
        # Données pour la dernière année
    annee = queryset.annotate(date_trunc=Trunc('date', 'year')).values('date_trunc').annotate(consommation=Sum('consommation_eau')).order_by('-date_trunc')[:1]
    annee_data = [{
        'x': datetime.strftime(item['date_trunc'], '%Y-%m-%d'),
        'y': item['consommation']
        } for item in annee[::-1]]

       # Données pour les dernières 5 années
    cinq_ans = queryset.filter(date__gte=timezone.now() - timezone.timedelta(days=365*5)).aggregate(total=Sum('consommation_eau'))['total'] or 0
    annee5_data = [{    'x': '5ans',    'y': cinq_ans}]
          # Graphique Chart.js
    data1 = {
        'semaine': semaine_data,
        'mois': mois_data,
        'semestre': semestre_data,
        'annee': annee_data,
        'cinq_ans': annee5_data
        }

    context["data1"]=data1
        #debit

    context['labels']=labels
    context['dt']=dt
    context['humidite']=humidite
    context['HS']=HS
    context['FV']=FV
    context['RS']=RS
     

     #comparer les dates des statistiques pour chaque terre
    if len(queryset) > 0:
        min_date=queryset[0].date
        max_date=queryset[0].date
        s=0.0
        for st in queryset:
            date_statistique=st.date
            debit_statistique=st.debit
            s+=debit_statistique
            if date_statistique<min_date:
                min_date=date_statistique
            if date_statistique>max_date:
                max_date=date_statistique
        context["min_date"]=min_date
        context["max_date"]=max_date
        context["debit_totale"]=s
        #date_debut=datetime(min_date)
       # date_fin=datetime(max_date)
        duree_irrigation=max_date-min_date
        context["duree_irrigation"]=duree_irrigation.days * 24 + duree_irrigation.seconds
        



        





    else:
        context["erreur"]="Vous n'avez pas de statistiques"    
    all=Terrain.objects.filter(id=terid)#recuperer objet terrain dont id  egale terid de url
    context["terre"]=all#mettre dans context => il ya un seul objet dans le context pour ne pas afficher tout les objet dans for dans le template statistique

    usr=User.objects.filter(id=request.user.id)
    if len(usr)>0:
        data=User.objects.get(id=request.user.id)
        context["data"]=data
    all=Statistique.objects.filter(Nterrain_id=terid)
    context["statistique"]=all
    return render(request,"app_irr/statistique.html",context)

def statistique_update(request):
    context={}

    sid=request.GET["sid"]
    statassoc = get_object_or_404(Statistique, id=sid)#récupérer un objet du modèle Terrain en utilisant le paramètre id égal à terid.
    context["statassoc"]=statassoc

    if request.method=="POST":
        tmp=request.POST["temperature"]
        dt=request.POST["date"]
        hr=request.POST["heure"]
        hd=request.POST["humidite"]
        hs=request.POST["hs"]
        fv=request.POST["fv"]
        rs=request.POST["rs"]
        db=request.POST["debit"]
        cd=request.POST["cde"]

        statassoc.temperature=tmp
        statassoc.date=dt
        statassoc.heure=hr
        statassoc.humidite=hd
        statassoc.HS=hs
        statassoc.FV=fv
        statassoc.RS=rs
        statassoc.debit=db
        statassoc.consommation_eau=cd

        statassoc.save()
        context["status"]="les données ont été bien modifiées"
        context["id"]=sid
    
    return render(request,"app_irr/statistique_update.html",context)




def statistique_delete(request):
    context = {}
    if "sid" in request.GET:
        sid = request.GET["sid"]
        static = get_object_or_404(Statistique, id=sid)
        context["stati"] = static

        if "action" in request.GET:
            static.delete()
            context["status"] = str(static.Nterrain_id )+" les données ont été supprimées avec succès!!!"
    return render(request,"app_irr/statistique_delete.html",context)

#enregistrer les donnes chaque 1 hour






    
def prediction(request):
   # Récupérer les données de la base de données Django
 data = Statistique.objects.values_list('temperature', 'humidite', 'HS', 'FV', 'RS', 'consommation_eau').order_by('date', 'heure')

# Transformer les données en un tableau NumPy
 data = np.array(data)

# Normaliser les données
 scaler = StandardScaler()
 #scaler = MinMaxScaler(feature_range=(0, 1))
 data = scaler.fit_transform(data)


# Définir la longueur de la séquence temporelle
 seq_length = 10

# Transformer les données en séquences temporelles
 X = []
 y = []
 for i in range(len(data) - seq_length):
    X.append(data[i:i+seq_length])
    y.append(data[i+seq_length])
 X = np.array(X)
 y = np.array(y)

# Diviser les données en ensembles d'entraînement et de test
 split = int(0.8 * len(data))
 X_train, X_test = X[:split], X[split:]
 y_train, y_test = y[:split], y[split:]
 
 
 
 # Définir le modèle LSTM
 model = Sequential()
 model.add(LSTM(64, activation='relu', input_shape=(seq_length, X_train.shape[2])))
 model.add(Dense(6))

# Compiler le modèle
 model.compile(optimizer='adam', loss='mse')

# Entraîner le modèle
 model.fit(X_train, y_train, epochs=100, batch_size=64, validation_data=(X_test, y_test))
 
 # Prédire les valeurs futures
 

 future_data = data[-seq_length:]
 print(future_data.shape)
# Prédire les valeurs futures
 future_data = data[-seq_length:]
 future_data = scaler.inverse_transform(future_data)
 # Normaliser les données futures
 future_data = scaler.transform(future_data)

 
# Remodeler les données futures en un tableau de 3 dimensions
 future_data = future_data.reshape(1, seq_length, X_train.shape[2])
 prediction = model.predict(future_data)[0]
  #denormaliser
 prediction = scaler.inverse_transform(prediction.reshape(1, -1))

 #prediction = scaler.inverse_transform(prediction)

    # Passer la prédiction au template
 # Passer la prédiction au template
 data_past = scaler.inverse_transform(data)
 temperature_past = data_past[:, 0]
 humidite_past = data_past[:, 1]
 HS_past = data_past[:, 2]
 FV_past = data_past[:, 3]
 RS_past = data_past[:, 4]
 consommation_eau_past = data_past[:, 5]

 temperature_pred = prediction[:, 0]
 humidite_pred = prediction[:, 1]
 HS_pred = prediction[:, 2]
 FV_pred = prediction[:, 3]
 RS_pred = prediction[:, 4]
 consommation_eau_pred = prediction[:, 5]
 l=len(temperature_past)
 context = {
    'temperature_past': temperature_past.tolist(),
    'humidite_past': humidite_past.tolist(),
    'HS_past': HS_past.tolist(),
    'FV_past': FV_past.tolist(),
    'RS_past': RS_past.tolist(),
    'consommation_eau_past': consommation_eau_past.tolist(),
    'temperature_pred': temperature_pred,
    'humidite_pred': humidite_pred.tolist(),
    'HS_pred': HS_pred.tolist(),
    'FV_pred': FV_pred.tolist(),
    'RS_pred': RS_pred.tolist(),
    'consommation_eau_pred': consommation_eau_pred.tolist(),
    'l':l
}



 


# Passer la prédiction au template
 print(temperature_pred)
 print(humidite_pred)
 print(HS_pred)
 print(FV_pred)
 print(RS_pred)
 print(consommation_eau_pred)
 
  
 return render(request, "app_irr/prediction.html", context)



               






         
   

    