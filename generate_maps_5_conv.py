import os
import matplotlib.pyplot as plt
import matplotlib as mpl
import geopandas
import rioxarray as rxr
from rasterio.plot import plotting_extent
import earthpy as et
import earthpy.spatial as es
import earthpy.plot as ep
import shapely
from matplotlib_scalebar.scalebar import ScaleBar
from pyproj import Proj, transform, CRS, Transformer
from shapely.ops import nearest_points
import numpy as np
import pandas
import rasterio
import re

os.environ["PROJ_LIB"]="C:\\OSGeo4W\\share\\proj"
fp = "C:\\DEV\GIS\\burundi\\bdi_export.tif"
fichier_buffer   ="C:\\Users\\ftheeten\\OneDrive - Africamuseum\\Documents\\salvator\\gis\\bdi_utm35S_buffer10km.gpkg"
fichier_dist="C:\\DEV\\salvator\\dec\\dist_20_12_correction.txt"
fichier_taxo="C:\\DEV\\salvator\\dec\\taxo_20_12_correction.txt"
output_map="C:\\DEV\\salvator\\maps\\"

buff_shp=geopandas.read_file(fichier_buffer)
buff_shp.set_crs(epsg=32735, inplace=True)
buff_shp.to_crs(epsg=3857, inplace=True)

transformer = Transformer.from_crs("epsg:4326", "epsg:3857", always_xy=True)
bbox_all=[28.9, 31, -4.7, -2.2]
raster_data = rxr.open_rasterio(fp, masked=True).rio.reproject("epsg:3857")

raster_data_extent = plotting_extent(raster_data[0], 
                                   raster_data.rio.transform())


bbox_1=transformer.transform(bbox_all[0], bbox_all[2])
bbox_2=transformer.transform(bbox_all[0], bbox_all[3])
bbox_3=transformer.transform( bbox_all[1], bbox_all[3])
bbox_4=transformer.transform(bbox_all[1], bbox_all[2])

bbox_conv=[bbox_1[0],bbox_4[0],bbox_1[1], bbox_3[1]]



xticks=[]
jticks=[]
xlabels=[]
jlabels=[]
i=bbox_all[0]
while i <= bbox_all[1] :
    #print(i)
    if (i % 0.5) ==0:
        pt_coord=transformer.transform(i,bbox_all[2])
        xticks.append(pt_coord[0])
        xlabels.append(i)
    i=round(i+0.1,2)
j=bbox_all[2]
while j <= bbox_all[3] :
    if (j % 0.5) ==0:
        pt_coord=transformer.transform(bbox_all[0],j)
        jticks.append(pt_coord[1])
        jlabels.append(j)
    j=round(j+0.1,2)

def isfloat(num):
    num=num.replace(",",".")
    try:
        float(num)
        return True
    except ValueError:
        return False
        
def format_family(family):
    return family.upper().replace("ACEAE","").strip()

def format_clade(clade):
    return clade.upper().strip()[0:5]

def format_filename(name):
    name_array=str(name).replace("&","").replace(" ex ","").split(" ")
    new_name=[]
    i=0
    for tmp in name_array:
        if not (("(" in tmp) or (")" in tmp) or tmp.isnumeric() or (tmp.lower()!=tmp and i>1)):
            new_name.append(tmp.replace(".",""))
            i=i+1
    returned= "_".join(new_name).replace(" ","_")
    returned = re.sub(' +', ' ', returned)
    if  returned is not None:
        returned=returned.replace("_f","")
        returned=returned.strip("_")
    returned=returned.strip("_")
    returned=returned.strip("_de")
    return returned

def go_plot(p_bbox, p_raster_data, p_raster_data_extent,  name_map, points, p_xticks, p_jticks, p_xlabels, p_ylabels):     
    f, ax = plt.subplots(figsize=(7,7))
    ep.plot_rgb(p_raster_data.values,
                rgb=[0, 1, 2],
                ax=ax,               
                extent=p_raster_data_extent)
    
    p_points=geopandas.GeoDataFrame(geometry=points)
    p_points.set_crs(epsg=3857, inplace=True)
    p_points.plot(ax=ax,  color="black", markersize=140, edgecolor="white" )    
    ax.set_xticks(p_xticks)
    ax.set_yticks(p_jticks)
    ax.set_xticklabels(p_xlabels)
    ax.set_yticklabels(p_ylabels)
    ax.set_xlim(p_bbox[0], p_bbox[1])
    ax.set_ylim(p_bbox[2], p_bbox[3])
    ax.add_artist(ScaleBar(
        dx=1,
        box_alpha=0.1,
        location='lower left'
    ))    
    name_file=name_map+".svg"
    print(name_file)
    plt.savefig(output_map+name_file, dpi=600, bbox_inches='tight')
    plt.close('all') 
    
def go_map(dist, name_map):
    list_points=[]
    for index2, row2 in dist.iterrows():
        #print(row2)
        #print(row2["Longitude"])
        #print(row2["Latitude"])
        #list_points.append(shapely.geometry.Point(transformer.transform(row2["Longitude"], row2["Latitude"])))
        if len(str(row2["long_merge"]))>0 and len(str(row2["lat_merge"]))>0 :
            
            if isfloat(str(row2["long_merge"])) and isfloat(str(row2["lat_merge"])):
                pt=shapely.geometry.Point(transformer.transform(float(str(row2["long_merge"]).replace(",",".")), float(str(row2["lat_merge"]).replace(",","."))))
                inter=buff_shp.intersects(pt)
                flag=any(x == True for x in inter)
                if flag:
                    list_points.append(pt)
        #print(pt)   
    if len(list_points)>0:
       go_plot(bbox_conv, raster_data, raster_data_extent, name_map,list_points,xticks, jticks, xlabels, jlabels)

def detect_distribution(current_name, p_df_dist):
    distribution_acceptee=p_df_dist.loc[p_df_dist['cle_taxo'].str.lower()==current_name.lower()]              
    return distribution_acceptee  

#print(os.environ['PROJ_LIB'])
#print("--------------------")
#del os.environ['PROJ_LIB']
#print(os.environ['PROJ_LIB'])
#print("--------------------")




df_taxo=pandas.read_csv(fichier_taxo, sep='\t', encoding='ISO-8859-1')
df_taxo['NOM_ACTUEL_A_UTILISER'] = df_taxo['NOM_ACTUEL_A_UTILISER'].astype(str)
df_taxo['NOM_ACTUEL_A_UTILISER'] = df_taxo['NOM_ACTUEL_A_UTILISER'].str.strip()
df_taxo["NOM_ACTUEL_A_UTILISER"] = df_taxo["NOM_ACTUEL_A_UTILISER"].replace(np.nan,"")
df_taxo["NOM_ACTUEL_A_UTILISER"] = df_taxo["NOM_ACTUEL_A_UTILISER"].fillna('')
df_taxo["clade"]=df_taxo["clade"].astype(str)
df_taxo['clade'] = df_taxo['clade'].str.strip()
df_taxo["family"]=df_taxo["family"].astype(str)
df_taxo['family'] = df_taxo['family'].str.strip()


df_taxo_filter=df_taxo[['NOM_ACTUEL_A_UTILISER', 'family', 'clade']]
df_taxo_filter["cle_taxo"]=df_taxo_filter["NOM_ACTUEL_A_UTILISER"]
df_taxo_filter["cle_taxo"]=df_taxo_filter["cle_taxo"].astype(str)
df_taxo_filter["cle_taxo"]=df_taxo_filter["cle_taxo"].str.strip()


df_dist=pandas.read_csv(fichier_dist, sep='\t', encoding='ISO-8859-1')
df_dist["cle_taxo"]=df_dist["cle_taxo"].astype(str)
df_dist["cle_taxo"]=df_dist["cle_taxo"].str.strip()
#df_dist.drop('family', inplace=True, axis=1)
#df_dist.drop('clade', inplace=True, axis=1)

df_dist_filter=pandas.merge(df_dist,df_taxo_filter,on='cle_taxo')

df_dist_filter=df_dist_filter[['cle_taxo', 'family', 'clade']]

df_dist_filter["CLADE_MAP"] = df_dist_filter['clade'].apply(format_clade)
df_dist_filter["FAMILY_MAP"] = df_dist_filter['family'].apply(format_family)
df_dist_filter['SPECIES_MAP'] = df_dist_filter['cle_taxo'].apply(format_filename)
df_dist_filter['FULL_NAME_MAP']=df_dist_filter["CLADE_MAP"] +"_"+df_dist_filter["FAMILY_MAP"]+"_"+df_dist_filter["SPECIES_MAP"]
df_dist_filter['FULL_NAME_MAP']=df_dist_filter['FULL_NAME_MAP'].str.replace('___','_')
df_dist_filter['FULL_NAME_MAP']=df_dist_filter['FULL_NAME_MAP'].str.replace('__','_')
df_dist_filter['FULL_NAME_MAP']=df_dist_filter['FULL_NAME_MAP'].str.replace('-','_')
df_dist_filter=df_dist_filter.drop_duplicates()


species_ref=df_taxo["NOM_ACTUEL_A_UTILISER"].unique()
print(len(species_ref))
species_ref_dist=df_dist["cle_taxo"].unique()
print(len(species_ref_dist))
print(sorted(set(species_ref).difference(set(species_ref_dist))))
print(sorted(set(species_ref_dist).difference(set(species_ref))))


df_dist_filter = df_dist_filter.sort_values(by=['FULL_NAME_MAP'], ascending=True)

i=0
for idx, row in df_dist_filter.iterrows():
    #print(row)
    dist=detect_distribution(row["cle_taxo"], df_dist)
    if len(dist)>0 :
        go_map(dist, row["FULL_NAME_MAP"].strip())
    i=i+1    
print(i)


