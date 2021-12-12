import geopandas
import fiona
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from shapely.geometry import Point
import pandas

fichier_dist="C:\\WORK_2021\\MEISE\\2021_dec\\12\\ArticleB_Checklist_Burundi_Dataset_Salvator_20211003.txt"
output_map="C:/PROJECTS_R/SALVATOR/maps/"

def species_plot(species_name, array_points):
    fig, ax = plt.subplots(figsize=(7,7))
    crs={'init':'epsg:4326'}
    points=geopandas.GeoDataFrame(crs=crs, geometry=array_points)
    prov_shp=geopandas.read_file("C:/WORK_2021/MEISE/2021_sept/new_shape_allprovinces_with_kigwena.gpkg")
    points.plot(ax=ax)
    ax.set_title(species_name)
    prov_shp.boundary.plot(ax=ax,color="black", linewidth=0.25)
    plt.savefig(output_map+species_name+".png")

df_dist=pandas.read_csv(fichier_dist, sep='\t', encoding='ISO-8859–1')
list_species=df_dist["Species_Trim"].unique()
i=1
for species in list_species:
    print(i)
    print(species)
    sub_df=df_dist.loc[df_dist["Species_Trim"]==species]
    list_points=[]
    for index, row in sub_df.iterrows():
        #print(row)
        list_points.append(Point(row["Longitude"], row["Latitude"]))
    #print(list_points)
    species_plot(species, list_points)
    i=i+1

