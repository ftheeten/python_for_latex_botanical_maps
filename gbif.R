library(rgbif)
library(sf)
library(ggplot2)
library(spocc)

shp_parks<-'D:\\DivaGisData\\CongoRDC_parcs_rgc_2019\\Parc.shp'
export_actino<-"C:\\Users\\ftheeten\\Downloads\\actino.csv"

data_parks<-st_read(shp_parks)
selected<-data_parks[which(data_parks$NOM == "Parc National de l'Upemba"),]
var_wkt<-st_as_text(selected$geometry)
print(var_wkt)
var_bbox<-st_bbox(selected$geometry)
print(var_bbox)
var_bbox_wkt<-bbox2wkt(bbox=var_bbox)
tmp_plot<-ggplot(data = selected) +  geom_sf()
key <- name_backbone(name='Actinopterygii')$usageKey
res <- occ_data(geometry = var_bbox_wkt, taxonKey=key)
tmp<-apply(res$data,2,as.character)
#write.table(tmp, file=export_actino, sep="\t")

all_data<-st_as_sf(data.frame(tmp), coords= c("decimalLongitude", "decimalLatitude"))
st_crs(all_data) <- st_crs(selected)
park_limit<-st_intersection(all_data, selected)
tmp_plot<-tmp_plot +  geom_sf(data=park_limit)
st_write(park_limit,export_actino )
