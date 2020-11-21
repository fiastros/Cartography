import sqlite3 as sl

def create_one_table(cur):
  cur.execute('''create table if not exists tmasters ("username" text primary key,"password" text,"age" text, "telephone" text)''')

def fill_id_polygon(db, cur,name,pw,age,tel):
  req="insert into tmasters (username, password, age, telephone) values (%a, %a,%a,%a)" %(name,pw,age,tel)
  cur.execute(req)
  db.commit()

def read_all_table(db, cur):
  print("Affichage du contenu de la table tmasters")
  req="select * from tmasters"
  cur.execute(req)
  return cur.fetchall()
  #for _id, _label, _age, _tel in cur:
    #print(_id,_label,_age,_tel)
    
def read_users(db,cur):
    req="select username from tmasters"
    cur.execute(req)
    return cur.fetchall()
    
  
def empty_all_table(db, cur):
  req="delete from tmasters"
  cur.execute(req)
  #for _id, _label, _age, _tel in cur:
    #print(_id, _label, _age, _tel)
  db.commit()
  
def verification(db,cur):
  print("affichage du contenu username et du contenu password")
  req="select username , password from tmasters"
  cur.execute(req)
  contenu = []
  for _id in cur :
    contenu.append(_id)
  return contenu
  
def create_table_poly(cur):
    cur.execute (''' create table if not exists tpoly("id_poly" text,"name" text,"ref_user" text, "size" real,"coord" text,"type_parc" text, foreign key(ref_user) references tmasters(username))''')
    
def add_poly(db,cur,id_poly,name_poly,user,size,coord,type_parc):
    req= "insert into tpoly(id_poly,name,ref_user,size,coord,type_parc) values (%a,%a,%a,%a,%a,%a)" %(id_poly,name_poly,user,size,coord,type_parc)
    cur.execute(req)
    db.commit()
def del_poly(db,cur,user,id_poly):
    t=(id_poly,user)
    cur.execute("delete from tpoly where id_poly=? and ref_user=?",t)
    db.commit()
def read_table_poly(db,cur):
    req="select * from tpoly"
    cur.execute(req)
    return cur.fetchall()
    #for _id_poly, _name, _ref_user, _size in cur:
        #print(_id_poly, _name, _ref_user, _size)

def read_all_poly_user(db,cur,user):
    t = (user,)
    cur.execute("SELECT * FROM tpoly INNER JOIN tmasters ON tmasters.username=tpoly.ref_user WHERE tmasters.username=?",t)
    return cur.fetchall()

def read_poly_user(db,cur,user,poly):
    t = (user,poly)
    cur.execute("SELECT name, coord FROM tpoly INNER JOIN tmasters ON tmasters.username=tpoly.ref_user WHERE tmasters.username=? and tpoly.id_poly=?",t)
    return cur.fetchall()

def store_current_user(db,cur,user):
    cur.execute('''Create table if not exists current_user("username" text)''')
    cur.execute('''DELETE FROM current_user''')
    cur.execute("INSERT INTO current_user(username) values (%a)" %(user))
    db.commit()
    
def del_current_user(db,cur):
    cur.execute('''DELETE FROM current_user''')
    db.commit()
    
def fetch_current_user(db,cur):
    cur.execute("SELECT * FROM current_user")
    return cur.fetchall()[0][0]
"""
db=sl.connect("identifiant.db")
cur = db.cursor()

create_one_table(cur)
create_table_poly(cur)

username=["marc_1","loic_1","aurelie_1"]
password=["111","222","333"]
age=[21,22,22]
telephone=["0659856","65684651","58656168"]
for i in range (0,3):  
    fill_id_polygon(db, cur,username[i],password[i],age[i],telephone[i])

res=read_all_table(db,cur)

id_poly=["poly_1","poly_2","poly_3","poly_4","poly_5"]
name=["parcelle","derriere ferme","ami","toujours","pk pas"]
user=["marc_1","marc_1","loic","aurelie","loic"]
size=[15,18,13.2,21,28]
for i in range(0,5):
    add_poly(db, cur, id_poly[i], name[i],user[i],size[i])
read_table_poly(db,cur)
a=read_poly_user(db,cur,"marc_1")
print(a[0][0])
db.close()
"""