import pandas

dict_general={}

excel_taxo="C:\\WORK_2021\\MEISE\\2022_jan\\20220116\\salvator\\Artib_latex_taxo_20220116_indeterminataft.txt"
excel_distribution="C:\\WORK_2021\\MEISE\\2022_jan\\20220116\\salvator\\ArticleB_Checklist_Burundi_Dataset_Salvator_2022_1_16nom_jointure.txt"
fichier_output="C:\\WORK_2021\\MEISE\\2022_jan\\20220116\\name_not_found.txt"

excel_distribution_output="C:\\WORK_2021\\MEISE\\2022_jan\\20220116\\salvator\\ArticleB_Checklist_Burundi_Dataset_Salvator_2022_1_16nom_jointure_analyses.xlsx"

df_taxo=pandas.read_csv(excel_taxo, sep='\t', encoding='ISO-8859–1')
print(df_taxo)
df_dist=pandas.read_csv(excel_distribution, sep='\t', encoding='ISO-8859–1')
#print(df_dist)

df_taxo["NOM_ACTUEL_A_UTILISER"]=df_taxo["NOM_ACTUEL_A_UTILISER"].str.strip()
df_taxo["NOM_STANDARD"]=df_taxo["NOM_STANDARD"].str.strip()
df_taxo["NOM_ACTUEL_A_UTILISER_NO_SPACE"]=df_taxo["NOM_ACTUEL_A_UTILISER"].str.replace(" ","")
df_taxo["NOM_ACTUEL_A_UTILISER_NO_SPACE"]=df_taxo["NOM_ACTUEL_A_UTILISER_NO_SPACE"].str.replace(".","")

df_taxo["NOM_STANDARD_NO_SPACE"]=df_taxo["NOM_STANDARD"].str.strip()
df_taxo["NOM_STANDARD_NO_SPACE"]=df_taxo["NOM_STANDARD_NO_SPACE"].str.replace(" ","")
df_taxo["NOM_STANDARD_NO_SPACE"]=df_taxo["NOM_STANDARD_NO_SPACE"].str.replace(".","")

df_dist["Species_Trim"]=df_dist["Species_Trim"].str.strip()
df_dist["Species_Trim_NO_SPACE"]=df_dist["Species_Trim"].str.replace(" ","")
df_dist["Species_Trim_NO_SPACE"]=df_dist["Species_Trim_NO_SPACE"].str.replace(".","")

df_dist["JOINTURE"] = ""

df_dist["MATCH_TYPE"] = ""


list_species=df_taxo["NOM_ACTUEL_A_UTILISER_NO_SPACE"].unique()
for species in list_species:
    taxo_2=df_taxo.loc[df_taxo["NOM_ACTUEL_A_UTILISER_NO_SPACE"]==species]
    #dict_general[species]={}
    if(len(taxo_2)>0):
    
        nom_actuel=taxo_2.iloc[0]["NOM_ACTUEL_A_UTILISER"]
        dict_general[nom_actuel]={}
        
        dict_general[nom_actuel]["nom_actuel"]=nom_actuel
        nom_standard=taxo_2.iloc[0]["NOM_STANDARD"]
        dict_general[nom_actuel]["nom_standard"]=nom_standard
        nom_actuel_indexe=taxo_2.iloc[0]["NOM_ACTUEL_A_UTILISER_NO_SPACE"]
        dict_general[nom_actuel]["nom_actuel_indexe"]=nom_actuel_indexe
        nom_standard_indexe=taxo_2.iloc[0]["NOM_STANDARD_NO_SPACE"]
        dict_general[nom_actuel]["nom_standard_indexe"]=nom_standard_indexe
        #nom_actuel=""
    #
    #nom_standard=taxo_2.iloc[0]["NOM_STANDARD"]
   
    #dict_general[species]["nom_standard"]=nom_standard
    
#print(dict_general)
i_found_accepted=0
i_not_found_accepted=0
i_found_standard=0
i_not_found_standard=0
for key, value in dict_general.items():
    #print(key)
    #print(value)
    distribution_acceptee=df_dist.loc[df_dist["Species_Trim_NO_SPACE"]==value["nom_actuel_indexe"]]
    
    if(len(distribution_acceptee)>0):
        #print(value["nom_actuel_indexe"])
        #print("FOUND BY ACCEPTED")
        i_found_accepted=i_found_accepted+1
        dict_general[key]["FOUND_BY_ACCEPTED"]="yes"
    else:
        i_not_found_accepted=i_not_found_accepted+1
        #print(key)
        #print("NOT FOUND BY ACCEPTED. STANDARD="+ str(value["nom_standard"]))
        dict_general[key]["FOUND_BY_ACCEPTED"]="no"

    distribution_standard=df_dist.loc[df_dist["Species_Trim_NO_SPACE"]==value["nom_standard_indexe"]]
    if(len(distribution_standard)>0):
        #print(value["nom_actuel_indexe"])
        #print("FOUND BY ACCEPTED")
        i_found_standard=i_found_standard+1
        dict_general[key]["FOUND_BY_STANDARD"]="yes"
    else:
        i_not_found_standard=i_not_found_standard+1
        #print(key)
        #print("NOT FOUND BY ACCEPTED")
        dict_general[key]["FOUND_BY_STANDARD"]="no"


        
print("FOUND_ACCEPTED")
print(i_found_accepted)
print("NOT_FOUND_ACCEPTED")
print(i_not_found_accepted)    
print("FOUND_STANDARD")
print(i_found_standard)
print("NOT_FOUND_STANDARD")
print(i_not_found_standard)

for key, value in dict_general.items():
    found_accepted=value["FOUND_BY_ACCEPTED"]
    found_standard=value["FOUND_BY_STANDARD"]
    if found_accepted=="yes" and found_standard=="yes":
        dict_general[key]["FOUND"]="yes"
        dict_general[key]["FOUND_TYPE"]="ACCEPTED_AND_STANDARD"
    elif found_accepted=="yes" and found_standard=="no":
        dict_general[key]["FOUND"]="yes"
        dict_general[key]["FOUND_TYPE"]="ACCEPTED_ONLY"
    elif found_accepted=="no" and found_standard=="yes":
        dict_general[key]["FOUND"]="yes"
        dict_general[key]["FOUND_TYPE"]="STANDARD_ONLY"
    elif found_accepted=="no" and found_standard=="no":
        dict_general[key]["FOUND"]="no"
        dict_general[key]["FOUND_TYPE"]="NONE"
        
found_both = {k:v for k, v in dict_general.items() if v["FOUND_TYPE"]=="ACCEPTED_AND_STANDARD"}
found_accepted = {k:v for k, v in dict_general.items() if v["FOUND_TYPE"]=="ACCEPTED_ONLY"}
found_standard = {k:v for k, v in dict_general.items() if v["FOUND_TYPE"]=="STANDARD_ONLY"}
not_found = {k:v for k, v in dict_general.items() if v["FOUND_TYPE"]=="NONE"}
print("found_both")
print(len(found_both))

print("found_accepted")
print(len(found_accepted))

print("found_standard")
print(len(found_standard))

print("not_found")
print(len(not_found))

f = open(fichier_output, 'w', encoding="utf-8")
f.write('\n'.join(not_found.keys()) + '\n')
f.close()

for key, value in found_both.items():
    name_1=value["nom_standard_indexe"]
    df_dist.loc[df_dist["Species_Trim_NO_SPACE"]==name_1,"JOINTURE"]=key
    df_dist.loc[df_dist["Species_Trim_NO_SPACE"]==name_1,"MATCH_TYPE"]="FOUND_BOTH"
    name_2=value["nom_actuel_indexe"]
    df_dist.loc[df_dist["Species_Trim_NO_SPACE"]==name_2,"JOINTURE"]=key
    df_dist.loc[df_dist["Species_Trim_NO_SPACE"]==name_2,"MATCH_TYPE"]="FOUND_BOTH"

for key, value in found_accepted.items():
    name_1=value["nom_actuel_indexe"]
    df_dist.loc[df_dist["Species_Trim_NO_SPACE"]==name_1,"JOINTURE"]=key
    df_dist.loc[df_dist["Species_Trim_NO_SPACE"]==name_1,"MATCH_TYPE"]="ACCEPTED_ONLY"

for key, value in found_standard.items():
    name_1=value["nom_standard_indexe"]
    df_dist.loc[df_dist["Species_Trim_NO_SPACE"]==name_1,"JOINTURE"]=key
    df_dist.loc[df_dist["Species_Trim_NO_SPACE"]==name_1,"MATCH_TYPE"]="STANDARD_ONLY"
    
df_dist.loc[df_dist["JOINTURE"]=="","MATCH_TYPE"]="NOT_FOUND"

df_dist.to_excel(excel_distribution_output)  
"""
for species in list_species:
    print(species)
    distribution=df_dist.loc[df_dist["Species_Trim_NO_SPACE"]==species]
    if(len(distribution)>0):
        print("FOUND")
    else:
        print("NOT_FOUND")
        
list_species=df_taxo["NOM_STANDARD_NO_SPACE"].unique()
for species in list_species:
    print(species)
    distribution=df_dist.loc[df_dist["Species_Trim_NO_SPACE"]==species]
    if(len(distribution)>0):
        print("FOUND")
    else:
        print("NOT_FOUND")
"""