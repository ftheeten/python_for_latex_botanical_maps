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

#print(os.environ['PROJ_LIB'])
#print("--------------------")
#del os.environ['PROJ_LIB']
#print(os.environ['PROJ_LIB'])
#print("--------------------")
os.environ["PROJ_LIB"]="C:\\OSGeo4W\\share\\proj"
fp = "C:\\DEV\GIS\\burundi\\bdi_export.tif"
fichier_buffer   ="C:\\Users\\ftheeten\\OneDrive - Africamuseum\\Documents\\salvator\\gis\\bdi_utm35S_buffer10km.gpkg"
fichier_dist="C:\\DEV\\salvator\\novembre\\6_nov_dist.txt"
fichier_taxo="C:\\DEV\\salvator\\novembre\\6_nov_taxo.txt"
output_map="C:\\DEV\\salvator\\maps\\"



buff_shp=geopandas.read_file(fichier_buffer)
buff_shp.set_crs(epsg=32735, inplace=True)
buff_shp.to_crs(epsg=3857, inplace=True)
def isfloat(num):
    num=num.replace(",",".")
    try:
        float(num)
        return True
    except ValueError:
        return False
        
def format_filename(name):
    name_array=name.replace("&","").replace(" ex ","").split(" ")
    new_name=[]
    i=0
    for tmp in name_array:
        if not (("(" in tmp) or (")" in tmp) or tmp.isnumeric() or (tmp.lower()!=tmp and i>1)):
            new_name.append(tmp.replace(".",""))
            i=i+1
    returned= "_".join(new_name).replace(" ","_")
    returned = re.sub(' +', ' ', returned)
    return returned

def detect_distribution(row):
    distribution_acceptee=None
    if 'NOM_ACTUEL_A_UTILISER' in  row:
        current_name=row["NOM_ACTUEL_A_UTILISER"]
        distribution_acceptee=df_dist.loc[df_dist["cle_taxo"].str.lower().replace("\\&","&")==current_name.lower().replace("\\&","&")]
        
    return distribution_acceptee

def go_plot(p_bbox, p_raster_data, p_raster_data_extent,  clade, family, species, points, p_xticks, p_jticks, p_xlabels, p_ylabels):     
    f, ax = plt.subplots(figsize=(7,7))
    ep.plot_rgb(p_raster_data.values,
                rgb=[0, 1, 2],
                ax=ax,
                #title="test Burundi",                
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
    print(family)
    print(species)
    #ax.set_title(species)
    #name_file=(output_map+family+"_"+species).replace("&", "and").replace(" ", "_").replace(".", "_").strip("_")
    #plt.subplots(figsize=(1800,1700))
    normspecies=format_filename(species)
    name_file=clade+"_"+family+"_"+normspecies+".png"
    print(name_file)
    plt.savefig(output_map+name_file, dpi=600, bbox_inches='tight')
    plt.close('all') 
    
# main    
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
    
####


#attention encoding
df_dist=pandas.read_csv(fichier_dist, sep='\t', encoding='ISO-8859-1')
df_taxo=pandas.read_csv(fichier_taxo, sep='\t', encoding='ISO-8859-1')
df_dist["Species_Trim"]=df_dist["Species_Trim"].str.strip()
df_taxo['NOM_ACTUEL_A_UTILISER'] = df_taxo['NOM_ACTUEL_A_UTILISER'].str.strip()
df_taxo["NOM_ACTUEL_A_UTILISER"] = df_taxo["NOM_ACTUEL_A_UTILISER"].replace(np.nan,"")
df_taxo["NOM_ACTUEL_A_UTILISER"] = df_taxo["NOM_ACTUEL_A_UTILISER"].fillna('')
df_dist['NOM_JOINTURE'] = df_dist['NOM_JOINTURE'].str.strip()

list_species=df_taxo["NOM_ACTUEL_A_UTILISER"].unique()
i=1
def_species=df_taxo[(df_taxo['rank']=="Species_or_higher") ]

for index, row in def_species.iterrows():
    #current_name=row["NOM_ACTUEL_A_UTILISER"] 
    #print(current_name)
    
    dist=detect_distribution(row)
    #print(dist)
    list_points=[]
    for index2, row2 in dist.iterrows():
        #print(row2)
        #print(row2["Longitude"])
        #print(row2["Latitude"])
        #list_points.append(shapely.geometry.Point(transformer.transform(row2["Longitude"], row2["Latitude"])))
        if len(str(row2["Longitude"]))>0 and len(str(row2["Latitude"]))>0 :
            '''
            print(row2["Longitude"])
            print(row2["Latitude"])
            '''
            if isfloat(str(row2["Longitude"])) and isfloat(str(row2["Latitude"])):
                pt=shapely.geometry.Point(transformer.transform(float(str(row2["Longitude"]).replace(",",".")), float(str(row2["Latitude"]).replace(",","."))))
                inter=buff_shp.intersects(pt)
                flag=any(x == True for x in inter)
                if flag:
                    list_points.append(pt)
        #print(pt)
    
    species=row["NOM_ACTUEL_A_UTILISER"].strip()
    family=df_taxo.loc[df_taxo["NOM_ACTUEL_A_UTILISER"]==species].iloc[0]["family"].upper().replace("ACEAE","").strip()  
    clade=df_taxo.loc[df_taxo["NOM_ACTUEL_A_UTILISER"]==species].iloc[0]["clade"].upper().strip()[0:5]      
    if len(list_points)>0:
        go_plot(bbox_conv, raster_data, raster_data_extent, clade, family, species,list_points,xticks, jticks, xlabels, jlabels)