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
import numpy
import pandas

fp = "C:\\WORK_2021\\MEISE\\SALVATOR_2\\geotif_elevation_couleur\\couleur_elevation_burundi_agrandi.tif"
bdi="C:\\WORK_2021\\MEISE\\SALVATOR\BDI_adm\\BDI_adm0.gpkg"
lakes="C:\\WORK_2021\\MEISE\\SALVATOR_2\\osm_lakes\\osm_lakes_dissolved.gpkg"
rivers="C:\\WORK_2021\\MEISE\\SALVATOR_2\\rivers\\group_bdi_akagera_ruvubu_ruzizi_malagarasi_simple.gpkg"

fichier_dist="C:\\WORK_2021\\MEISE\\2021_dec\\12\\ArticleB_Checklist_Burundi_Dataset_Salvator_20211003.txt"
fichier_taxo="C:\\WORK_2021\\MEISE\\2021_dec\\12\\Artib_latex_taxo_20211010_indeterminataft1bis.txt"

output_map="C:/PROJECTS_R/SALVATOR/maps/"





def go_plot(p_bbox, p_raster_data, p_raster_data_extent, p_boundary, p_rivers, p_dict_rivs, p_lakes, family, species, points, p_xticks, p_jticks, p_xlabels, p_ylabels):     
    f, ax = plt.subplots(figsize=(7,7))
    ep.plot_rgb(p_raster_data.values,
                rgb=[0, 1, 2],
                ax=ax,
                title="test Burundi",
                extent=p_raster_data_extent)    
    p_rivers.plot(ax=ax, linewidth=0.2, color="blue", zorder=2)
    for name_riv, params in p_dict_rivs.items():
        plt.annotate(text=name_riv, xy=params[0], horizontalalignment='center', fontsize=7, rotation=params[1])    
    p_boundary.boundary.plot(ax=ax,color="black", linewidth=0.3, zorder=10)
    p_lakes.plot(ax=ax, zorder=3)
    p_lakes.boundary.plot(ax=ax, color="blue", linewidth=0.1, zorder=4)
    
    p_points=geopandas.GeoDataFrame(geometry=points)
    p_points.set_crs(epsg=3857, inplace=True)
    p_points.plot(ax=ax, zorder=20, color="black")
    
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
    #plt.show()
    #plt.savefig(output_map)
    ax.set_title(family+ " - "+ species)
    plt.savefig(output_map+family+"_"+species+".png")
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


rivers_shp=geopandas.read_file(rivers)
rivers_shp.set_crs(epsg=4326, inplace=True)
rivers_shp['coords'] = rivers_shp['geometry'].apply(lambda x: x.representative_point().coords[:])
rivers_shp['coords'] = [coords[0] for coords in rivers_shp['coords']]
dict_rivs={}
for idx, row in rivers_shp.iterrows():
    geom=row.geometry
    if row["name"] is not None:
        if len(row["name"])>0:
            bbox=geom.bounds
            p_start=(bbox[0], bbox[1])
            p_end=(bbox[2], bbox[3])
            near=shapely.ops.nearest_points(geom,shapely.geometry.Point(p_start))
            near2=shapely.ops.nearest_points(geom,shapely.geometry.Point(p_end))
            pt1=near[0].coords[0]
            pt2=near2[0].coords[0]
            slope=(pt2[1]-pt1[1])/(pt2[0]-pt1[0])
            deg=numpy.degrees(numpy.arctan(slope))
            anno_coord=transformer.transform(row['coords'][0],row['coords'][1])
            dict_rivs[row['name']]=[anno_coord,deg ]
            #plt.annotate(text=row['name'], xy=anno_coord, horizontalalignment='center', fontsize=7, rotation=deg)
print(dict_rivs)
rivers_shp=rivers_shp.to_crs('epsg:3857')


prov_shp=geopandas.read_file(bdi)
prov_shp.set_crs(epsg=4326, inplace=True)
prov_shp=prov_shp.to_crs('epsg:3857')

lakes_shp=geopandas.read_file(lakes)
lakes_shp.set_crs(epsg=4326, inplace=True)
lakes_shp=lakes_shp.to_crs('epsg:3857')

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

df_dist=pandas.read_csv(fichier_dist, sep='\t', encoding='ISO-8859–1')
df_taxo=pandas.read_csv(fichier_taxo, sep='\t', encoding='ISO-8859–1')
df_dist["Species_Trim"]=df_dist["Species_Trim"].str.strip()
df_taxo["NOM_ACTUEL_A_UTILISER"]=df_taxo["NOM_ACTUEL_A_UTILISER"].str.strip()
list_species=df_taxo["NOM_ACTUEL_A_UTILISER"].unique()
i=1
for species in list_species:
    #print(i)
    #print(species)
    distribution=df_dist.loc[df_dist["Species_Trim"]==species]
    if(len(distribution)>0):
        joint_species=distribution.iloc[0]["Species_Trim"]
        family=df_taxo.loc[df_taxo["NOM_ACTUEL_A_UTILISER"]==species].iloc[0]["family"]
        print(i)
        print(joint_species)
        list_points=[]
        for index, row in distribution.iterrows():
            #print(row)
            list_points.append(shapely.geometry.Point(transformer.transform(row["Longitude"], row["Latitude"])))
        #print(list_points)
        #print( df_taxo["family"])
        print(family)
        print(species)
        go_plot(bbox_conv, raster_data, raster_data_extent, prov_shp, rivers_shp, dict_rivs, lakes_shp, family, species,list_points,xticks, jticks, xlabels, jlabels)
        i=i+1