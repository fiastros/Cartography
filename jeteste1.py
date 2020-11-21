from flask import Flask, jsonify, request, render_template , redirect, url_for
import bddconnection as bdd
import sqlite3 as sl
from requests import session

import numpy as np
import pandas as pd
import shapefile as shp
import matplotlib.pyplot as plt
import seaborn as sns
import requests as rq
import json
from PIL import Image
from pyproj import Proj, transform
from io import BytesIO
from datetime import datetime as dt


def read_shapefile(sf):

    fields = [x[0] for x in sf.fields][1:]
    data=sf.records()
    records=[]
    for i in range(0,len(data)):
        records.append(data[i][0:6])
        
    shps = [s.points for s in sf.shapes()]
    df = pd.DataFrame(columns=fields, data=records)
    df = df.assign(coords=shps)
    
    return df

#preparer fond de carte
sns.set(style="whitegrid", palette="pastel", color_codes=True)
sns.mpl.rc("figure", figsize=(10,6))

#Import SHP
shp_path =  "PARCELLES_GRAPHIQUES.shp"
sf = shp.Reader(shp_path)

df = read_shapefile(sf)
df.shape
def post_polygon(df,comuna):
    if (comuna in df.ID_PARCEL.values):
        com_id = df[df.ID_PARCEL == comuna].index.get_values()[0]
        test=df.loc[com_id,'coords']
        test=json.dumps(test)
        test.replace('(','[')
        test.replace(')',']')
        test=json.loads(test)
    
        inProj = Proj(init='epsg:2154')
        outProj = Proj(init='epsg:4326')
    
    
        for i in range(0,len(test)):
            x1=test[i][0]
            y1=test[i][1]
            x2,y2 = transform(inProj,outProj,x1,y1)
            test[i][0]=x2
            test[i][1]=y2
    
        name= "Polygon "+comuna
        data={"name":name,
           "geo_json":{
              "type":"Feature",
              "properties":{
        
              },
              "geometry":{
                 "type":"Polygon",
                 "coordinates":[
                   test
                 ]
              }
           }
        }
            
        data_formate=json.dumps(data)
        url="http://api.agromonitoring.com/agro/1.0/polygons?appid=d3e4c13c5b4df74d21dc4bb57b6f6930"
        headers={"Content-Type": "application/json"}
        
        r = rq.post(url=url,data=data_formate,headers=headers)
        id_polygon=json.loads(r.text)
        return id_polygon
    else:
        return "erreur"

def post_polygon_coord(coord,name):
    try:
        data={"name":name,
           "geo_json":{
              "type":"Feature",
              "properties":{
        
              },
              "geometry":{
                 "type":"Polygon",
                 "coordinates":[
                   coord
                 ]
              }
           }
        }
        data_formate=json.dumps(data)
        url="http://api.agromonitoring.com/agro/1.0/polygons?appid=d3e4c13c5b4df74d21dc4bb57b6f6930"
        headers={"Content-Type": "application/json"}   
        r = rq.post(url=url,data=data_formate,headers=headers)
        id_polygon=json.loads(r.text)
        print(id_polygon)
        return id_polygon
    except:
        return "erreur"
              
def log_out():
  db = sl.connect("identifiant.db")
  cur = db.cursor()
  bdd.del_current_user(db,cur)
  db.close()
  


app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0



        
@app.route('/', methods= ['GET','POST'])
def index():  
  erreur = " "
  db = sl.connect("identifiant.db")
  cur = db.cursor()
  bdd.create_one_table(cur)
  if request.method == 'POST':
    details = request.form
    username = details['user_name']
    password = details['user_pw']
    try:    
        #verfication des donnees dans la base de données
        for _i in range(len(bdd.verification(db,cur))):
          if (str(username), str(password)) == bdd.verification(db,cur)[_i] :
            state="connected"
            bdd.store_current_user(db,cur,username)
            #print(bdd.fetch_current_user(db,cur))
            return   redirect("/index")
            break
          else:
            state="not connected"
        if state=="not connected":
          erreur="username et password incompatibles"
    except:
        erreur="veuillez créer un compte"
  db.close()
  return render_template('sign_in1.html',erreur = erreur)


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    erreur=""
    if request.method == "POST":
        # recupération elements inscription
        details = request.form
        username = details['user_name']
        password = details['user_pw']
        verif_pw=details['user_pw_verif']
        age = details['user_age']
        telephone = details['user_tel']
        
        #test
        if verif_pw==password:
            #sauvegarde dans la bdd
            db = sl.connect("identifiant.db")
            cur = db.cursor()
            bdd.create_one_table(cur)
            list_user=bdd.read_users(db,cur)
            if (username,) in list_user:
                erreur="Identifiant deja utilise"
            else:
              try:
                if request.form['remember_me'] == 'accepted':
                  if request.form['submit_button'] == 'Subscription':
                    bdd.fill_id_polygon(db, cur,username,password,age,telephone)
                    bdd.read_all_table(db,cur)
                    return redirect("/")               
              except:
                erreur = "veuillez accepter les conditions"
            db.close()
        else:
            erreur="second mot de passe incorrect"   
    return render_template('sign_up1.html',erreur=erreur)

@app.route("/about", methods=['GET', 'POST'])  
def about():
  db = sl.connect("identifiant.db")
  cur = db.cursor()
  try:
      usera= bdd.fetch_current_user(db,cur)
  except:
      usera='Bienvenue'
  #pour chque page, je dois me conneccter a la base de donnée puis fecch le current user et changer les lien en bouton par form. 
  db.close()
  if request.method == "POST":
      if request.form["logouts"] == "logg_out":
          log_out()
          return redirect("/")
  return render_template('about.html',usera=usera)

@app.route("/contact", methods=['GET', 'POST'])  
def contact():
  db = sl.connect("identifiant.db")
  cur = db.cursor()
  try:
      usera= bdd.fetch_current_user(db,cur)
  except:
      usera='Bienvenue'
  db.close()
  if request.method == "POST":
      if request.form["logouts"] == "logg_out":
          log_out()
          return redirect("/")
  return render_template('contact.html',usera=usera)

@app.route("/index", methods=['GET', 'POST'])  
def indexe():
  db = sl.connect("identifiant.db")
  cur = db.cursor()
  try:
      usera= bdd.fetch_current_user(db,cur)
  except:
      usera='Bienvenue'
  db.close()
  if request.method == "POST":
      if request.form["logouts"] == "logg_out":
          log_out()
          return redirect("/")
  return render_template('index.html',usera=usera)

@app.route('/liste/<user>', methods= ['GET','POST'])
def listing(user):
  db = sl.connect("identifiant.db")
  cur = db.cursor()
  try:
        user= bdd.fetch_current_user(db,cur)
        mes_erreur=""
        db = sl.connect("identifiant.db")
        cur = db.cursor()
        bdd.create_table_poly(cur)
        res=bdd.read_all_poly_user(db,cur,user)
        info=[]
        for i in range(0,len(res)):
            info.append([res[i][0],res[i][1],res[i][3]])
        #print(info)
        if request.method == "POST":
            for inf in info:
                if request.form['submit_button'] == inf[0]:
                    id_poly=inf[0]
                    return redirect("/liste/"+user+"/"+id_poly)
                elif request.form['submit_button'] == ("delete"+inf[0]):
                    bdd.del_poly(db,cur,user,inf[0])
                    #print("yes")
            if request.form['submit_button'] == 'ajout':
                #collecte saisie:
                details = request.form
                id_poly = details['id_poly']
                name = details['parc_name']
                
                #collecte donénes api
                id_pol=post_polygon(df,id_poly)
            
                if id_pol=="erreur":
                    mes_erreur="Cette parcelle n'est pas referencee dans le RPG Normandie 2017"
                else:
                    mes_erreur=""
                    size=id_pol["area"]
                    center=id_pol["center"]
                    poly_key=id_pol["id"]
                    coord=str(id_pol["geo_json"]["geometry"]["coordinates"][0])
                
                    #Ajout à la bdd
                    bdd.add_poly(db,cur,id_poly,name,user,size,coord,"RPG")
                    #suppression du polygon
                    rq.delete("http://api.agromonitoring.com/agro/1.0/polygons/"+poly_key+"?appid=d3e4c13c5b4df74d21dc4bb57b6f6930")
            if request.form['submit_button'] == 'ajout_coord':
                details = request.form
                coord=[]
                name=details["parc_name_coord"]
                coord_sup_gauche=[float(details["lon_s_g"]),float(details["lat_s_g"])]
                coord_sup_droit=[float(details["lon_s_d"]),float(details["lat_s_d"])]
                coord_inf_droit=[float(details["lon_i_d"]),float(details["lat_i_d"])]
                coord_inf_gauche=[float(details["lon_i_g"]),float(details["lat_i_g"])]
                coord.append(coord_sup_gauche)
                coord.append(coord_sup_droit)
                coord.append(coord_inf_droit)
                coord.append(coord_inf_gauche)
                coord.append(coord_sup_gauche)
                print(coord)
                id_pol=post_polygon_coord(coord,name)
                if id_pol=="erreur":
                    mes_erreur="Les coordonnees saisies ne fonctionnent pas"
                else:
                    mes_erreur=""
                    size=id_pol["area"]
                    center=id_pol["center"]
                    poly_key=id_pol["id"]
                    id_poly=id_pol["id"]
                    coord=str(id_pol["geo_json"]["geometry"]["coordinates"][0])
                
                    #Ajout à la bdd
                    bdd.add_poly(db,cur,id_poly,name,user,size,coord,"Perso")
                    #suppression du polygon
                    rq.delete("http://api.agromonitoring.com/agro/1.0/polygons/"+poly_key+"?appid=d3e4c13c5b4df74d21dc4bb57b6f6930")
            if request.form['submit_button'] == "logg_out":
                log_out()
                return redirect("/")
        res=bdd.read_all_poly_user(db,cur,user)
        #fermeture de la bdd
        db.close()
        info=[]
        for i in range(0,len(res)):
            info.append([res[i][0],res[i][1],res[i][3]])
            
        return render_template('parcelle.html',info=info,usera = user ,error=mes_erreur)
  except:
        return redirect("/")

@app.route('/liste/<user>/<poly>', methods= ['GET','POST'])
def consult(user,poly):
    db = sl.connect("identifiant.db")
    cur = db.cursor()
    a=bdd.read_poly_user(db,cur,"sdsd","712451")
    name=a[0][0]
    coord=json.loads(a[0][1])
    db.close()
    id_pol=post_polygon_coord(coord,name)
    id_pol=id_pol["id"]
    
    
    # Acquisition surface:
    s=rq.get("http://api.agromonitoring.com/agro/1.0/polygons/"+id_pol+"?appid=d3e4c13c5b4df74d21dc4bb57b6f6930")
    list_s=json.loads(s.text)
    area=round(list_s["area"],2)
    
    # Acquisition des données meteo
    meteo=[]
    current_meteo=json.loads(rq.get("http://api.agromonitoring.com/agro/1.0/weather?polyid="+id_pol+"&appid=d3e4c13c5b4df74d21dc4bb57b6f6930").text)
    meteo.append([str(dt.date(dt.fromtimestamp(current_meteo["dt"]))),str(dt.fromtimestamp(current_meteo["dt"]).hour)+"h",current_meteo["weather"][0]["main"],round(current_meteo["main"]["temp"]-273.15,2),current_meteo["main"]["humidity"],current_meteo["wind"]["speed"]])
    prev_meteo=json.loads(rq.get("http://api.agromonitoring.com/agro/1.0/weather/forecast?polyid="+id_pol+"&appid=d3e4c13c5b4df74d21dc4bb57b6f6930").text)
    for prev in prev_meteo:
        meteo.append([str(dt.date(dt.fromtimestamp(prev["dt"]))),str(dt.fromtimestamp(prev["dt"]).hour)+"h",prev["weather"][0]["main"],round(prev["main"]["temp"]-273.15,2),prev["main"]["humidity"],prev["wind"]["speed"]])
    
    #acquisition ndvi:
    now=int(dt.utcnow().timestamp())
    s=rq.get("http://api.agromonitoring.com/agro/1.0/image/search?start=1483218000&end="+str(now)+"&polyid="+id_pol+"&appid=d3e4c13c5b4df74d21dc4bb57b6f6930")
    list_s=json.loads(s.text)
    api_last=json.loads(json.dumps(list_s[len(list_s)-1]))
    date_ndvi=str(dt.date(dt.fromtimestamp(api_last["dt"])))
    cl=api_last["cl"]
    im_ndvi=rq.get(api_last["image"]["ndvi"])
    i = Image.open(BytesIO(im_ndvi.content))
    i=i.resize((int((800/i.size[0])*i.size[0]),int((800/i.size[0])*i.size[1])))
    i.save("static/ndvi.png")
    
    #acquisition truecolor
    s=rq.get("http://api.agromonitoring.com/agro/1.0/image/search?start=1483218000&end="+str(now)+"&polyid="+id_pol+"&appid=d3e4c13c5b4df74d21dc4bb57b6f6930&clouds_max=30")
    list_s=json.loads(s.text)
    api_last=json.loads(json.dumps(list_s[len(list_s)-1]))
    date_true=str(dt.date(dt.fromtimestamp(api_last["dt"])))
    im_ndvi=rq.get(api_last["image"]["truecolor"])
    i = Image.open(BytesIO(im_ndvi.content))
    i=i.resize((int((800/i.size[0])*i.size[0]),int((800/i.size[0])*i.size[1])))
    i.save("static/truecolor.png")
    
    #acquisition données sol:
    try:
        s=rq.get("http://api.agromonitoring.com/agro/1.0/soil?polyid="+id_pol+"&appid=d3e4c13c5b4df74d21dc4bb57b6f6930")
        list_s=json.loads(s.text)
        T0=round(list_s["t0"]-273.15,2)
        T10=round(list_s["t10"]-273.15,2)
        moist=round(list_s["moisture"]*100,1)
    except: 
        T0="souci technique, veuillez recommencer plutard"
        T10="souci technique, veuillez recommencer plutard"
        moist="souci technique, veuillez recommencer plutard"
    #suppression polygone
    rq.delete("http://api.agromonitoring.com/agro/1.0/polygons/"+id_pol+"?appid=d3e4c13c5b4df74d21dc4bb57b6f6930")
    if request.method == "POST":
        if request.form['back_button'] == 'retour_liste':
            return redirect("/liste/"+user)
        
    return render_template('consulter.html', code_poly=poly,meteo=meteo,date_ndvi=date_ndvi,date_true=date_true,cl=cl,area=area,T0=T0,T10=T10,moist=moist)

if __name__ == '__main__':
    app.run()
    
#debug = True,port = 8080,host = '0.0.0.0'