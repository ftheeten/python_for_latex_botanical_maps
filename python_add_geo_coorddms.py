import pandas as pnd
import numpy as np
import sys
import traceback
import geopandas
from shapely.geometry import Point
import chardet
import re
import traceback
import sys

fichier_dist="C:\\DEV\\salvator\\novembre\\6_nov_dist_no_provs.txt"
fichier_provinces="C:\\Users\\ftheeten\\OneDrive - Africamuseum\\Documents\\salvator\\gis\\provinces_botaniques_bdi.gpkg"
output_file= "C:\\DEV\\salvator\\novembre\\6_nov_dist_with_provs.txt"

def guess_encoding(file):
    with open(file, 'rb') as f:
        tmp=chardet.detect(f.read())
        return tmp['encoding']

prov_shp=geopandas.read_file(fichier_provinces)
prov_shp.set_crs(epsg=4326, inplace=True)

df_dist=pnd.read_csv(fichier_dist, sep='\t', encoding='ISO-8859–1')
df_dist = df_dist.fillna('')

def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False
        
def dms_to_dd(coord):
    coord=coord.replace("''",'"').replace(",",".").upper().strip()
    coord=re.sub(r'\([^()]*\)', '', coord)
    if '"' in coord and not "'" in coord:
        
        if coord.count('"')==1:
            #print("subst"+coord+"=>"+coord.replace('"',"'" ))
            coord=coord.replace('"',"'" )
        else:
            if coord.count('"')==2:
                #print("subst"+coord+"=>"+coord.replace('"',"'",1 ))
                coord=coord.replace('"',"'",1 )
            else:
                print("error"+coord)
    if coord.count("'")==2:
        coord=coord.replace("'",'"').replace('"',"'",1 )
    sign=1
    deg=None
    minute= 0
    second = 0
    returned=None
    try:
        if "S" in coord or "W" in coord :
            sign=-1
        coord=coord.replace("W","").replace("E","").replace("S","").replace("W","").strip()
        tmp=coord.split("°")
        #print(tmp)
        if len(tmp)>=2:
            deg=int(tmp[0].strip())
            rel=tmp[1]
            if '"' in rel and "'" in rel:
                tmp2=rel.split("'")
                if len(tmp2)==2:
                    minute=tmp2[0].replace("'","").strip()
                    second=tmp2[1].replace('"',"").strip()
            elif isfloat(tmp[1].replace("'","").strip()):
                minute=float(tmp[1].replace("'","").strip())
        if deg is not None:            
            returned=float(deg+float(float(minute)/60)+float(float(second)/3600))*sign
    except:
        #print(traceback.format_exc())
        print("exception"+coord)
    return returned
                
def add_prov():
    global df_dist
    global prov_shp
    print("go")
    df_dist["lat_python"]=""
    df_dist["long_python"]=""
    df_dist["province"]=""
    #df_dist['Latitude'] = df_dist['Latitude'].astype(str)
    #df_dist['Longitude'] = df_dist['Longitude'].astype(str)
    for index, row_dist in df_dist.iterrows():
        if index % 1000==0:
            print(index)
        if  len(row_dist["Latitude_DMS"])>0 and len(row_dist["LONGITUDE_DMS"])>0:
            nom_jointure=row_dist["NOM_JOINTURE"].lower()
            collector=row_dist["COLLECTOR"].replace("&", "\&")
            coll_num=row_dist["COLL_NUM"].replace("&", "\&")             
            lat_str=row_dist["Latitude_DMS"].replace(",",".").replace("''",'"')
            long_str=row_dist["LONGITUDE_DMS"].replace(",",".").replace("''",'"')
            '''
            print(row_dist['id'])
            print(row_dist['cle_taxo'])
            print(lat_str)
            
            '''
            lat=dms_to_dd(lat_str)
            
            '''
            print(lat)
            print(long_str)
            '''
            long=dms_to_dd(long_str)
            #print(long)
            
            if long is not None and lat is not None:
                #burundi
                if lat>0:
                    lat=lat*-1
                df_dist.at[index, "lat_python"]=str(lat).replace(".",",")
                df_dist.at[index, "long_python"]=str(long).replace(".",",")
                point=Point(long,lat)
                
                inter=prov_shp.intersects(point)
                flag=any(x == True for x in inter)
                if flag:
                    region=prov_shp.iloc[[i for i, x in enumerate(inter) if x]]
                    if region is not None:
                        tmp_region=region.iloc[0]["layer"]
                        df_dist.at[index, "province"]=tmp_region
                

add_prov()
df_dist.to_csv(output_file, sep ='\t', encoding='ISO-8859–1')