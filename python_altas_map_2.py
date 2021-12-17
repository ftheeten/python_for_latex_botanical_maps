import geopandas
import fiona
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from shapely.geometry import Point
import pandas
from matplotlib_scalebar.scalebar import ScaleBar
import pyproj
from pyproj import Proj, transform, CRS


fichier_dist="C:\\GIS_DATA\\Africa_adm0\\africa_adm0.shp"
output_map="C:/PROJECTS_R/SALVATOR/maps/_test.png"



fig,ax = plt.subplots(1)
#crs=PROJ()   
prov_shp=geopandas.read_file(fichier_dist )
prov_shp.set_crs(epsg=4326, inplace=True)
print(prov_shp.crs)
crs=CRS("epsg:3857")#.to_proj4()
prov_shp = prov_shp.to_crs(crs)
ax=prov_shp.boundary.plot(color="black", linewidth=0.25)
ax.add_artist(ScaleBar(
    dx=1,
    units="km",
     dimension="si-length",
     length_fraction=0.25,
    scale_formatter=lambda value, unit: f' {value * 1000} km ',
    location='lower left'
))
ax.set_yticks([])
ax.set_xticks([])
plt.savefig(output_map)



