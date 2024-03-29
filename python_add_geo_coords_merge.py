import pandas as pnd
import numpy as np
import sys
import traceback
import geopandas
from shapely.geometry import Point
import chardet

fichier_dist="C:\\DEV\\salvator\\novembre\\27_novembre_correction_manuelleqgis.txt"
fichier_provinces="C:\\Users\\ftheeten\\OneDrive - Africamuseum\\Documents\\salvator\\gis\\provinces_botaniques_bdi.gpkg"
output_file= "C:\\DEV\\salvator\\novembre\\27_novembre_correction_manuelleqgis_provs.txt"

def guess_encoding(file):
    with open(file, 'rb') as f:
        tmp=chardet.detect(f.read())
        return tmp['encoding']

prov_shp=geopandas.read_file(fichier_provinces)
prov_shp.set_crs(epsg=4326, inplace=True)

df_dist=pnd.read_csv(fichier_dist, sep='\t', encoding='ISO-8859–1')
df_dist = df_dist.fillna('')

def add_prov():
    global df_dist
    global prov_shp
    print("go")
    df_dist["province_recheck"]=""
    df_dist['lat_merge'] = df_dist['lat_merge'].astype(str)
    df_dist['long_merge'] = df_dist['long_merge'].astype(str)
    for index, row_dist in df_dist.iterrows():
        if index % 1000==0:
            print(index)
        if  len(row_dist["lat_merge"])>0 and len(row_dist["long_merge"])>0:
            nom_jointure=row_dist["NOM_JOINTURE"].lower()
            collector=row_dist["COLLECTOR"].replace("&", "\&")
            coll_num=row_dist["COLL_NUM"].replace("&", "\&")             
            lat=row_dist["lat_merge"].replace(",",".")
            long=row_dist["long_merge"].replace(",",".")
            point=Point(float(long), float(lat))
            inter=prov_shp.intersects(point)
            flag=any(x == True for x in inter)
            if flag:
                region=prov_shp.iloc[[i for i, x in enumerate(inter) if x]]
                if region is not None:
                    tmp_region=region.iloc[0]["layer"]
                    df_dist.at[index, "province_recheck"]=tmp_region

add_prov()
df_dist.to_csv(output_file, sep ='\t', encoding='ISO-8859–1')