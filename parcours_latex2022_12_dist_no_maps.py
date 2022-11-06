import pandas as pnd
import numpy as np
import sys
import traceback
import geopandas
from shapely.geometry import Point
from os.path import exists
import re
import collections
import shutil
from os import unlink



fichier_syno="C:\\DEV\\salvator\\mar\\20\\export_list_syno_fusionne_no_rank.txt"
fichier_verna="C:\\DEV\\salvator\\aout\\28\\ArticleB_Liste des noms vernaculaires_2022_09_03.txt" 
fichier_taxo="C:\\DEV\\salvator\\novembre\\6_nov_taxo.txt"
fichier_dist="C:\\DEV\\salvator\\novembre\\6_nov_dist_with_provs_2.txt"

image_folder="C:\\DEV\\salvator\\maps\\"



#fichier_excel="C:\\DEV\salvator\\octobre\\23_octobre\\16octobre_fusion_newchecks_bis.xlsx"

image_folder="C:\\DEV\\salvator\\maps\\"


fichier_provinces="C:\\Users\\ftheeten\\OneDrive - Africamuseum\\Documents\\salvator\\gis\\provinces_botaniques_bdi.gpkg"
prov_shp=geopandas.read_file(fichier_provinces)
prov_shp.set_crs(epsg=4326, inplace=True)


output_file="C:\\Users\\ftheeten\\OneDrive - Africamuseum\\Documents\\salvator\\SALVATOR\\latex\\output_pdf.tex" 
output_idx="C:\\Users\\ftheeten\\OneDrive - Africamuseum\\Documents\\salvator\\SALVATOR\\latex\\output_idx.txt" 
index_name={}
global_idx=1
def trim_all_columns(df):
    """
    Trim whitespace from ends of each value across all series in dataframe
    """
    trim_strings = lambda x: x.replace("\r","").replace("\n","").strip() if isinstance(x, str) else x
    return df.applymap(trim_strings)


output_data={}
array_references={}
dict_geo={}
no_distribution=[]
dict_syno={}

#print(fichier_taxo)
df_taxo=pnd.read_csv(fichier_taxo, sep='\t', encoding='ISO-8859–1')
df_syno=pnd.read_csv(fichier_syno, sep='\t', encoding='ISO-8859–1')
df_verna=pnd.read_csv(fichier_verna, sep='\t', encoding='UTF-8')
df_dist=pnd.read_csv(fichier_dist, sep='\t', encoding='ISO-8859–1')

df_taxo=trim_all_columns(df_taxo)
df_syno=trim_all_columns(df_syno)
df_verna=trim_all_columns(df_verna)
df_dist=trim_all_columns(df_dist)

df_taxo["Reference1"]=df_taxo["Reference1"].fillna("")
df_taxo["Reference2"]=df_taxo["Reference2"].fillna("")
df_taxo["Reference3"]=df_taxo["Reference3"].fillna("")
df_taxo["Reference4"]=df_taxo["Reference4"].fillna("")
df_taxo["Reference5"]=df_taxo["Reference5"].fillna("")

df_taxo["Reference1"]=df_taxo["Reference1"].str.replace(").",")", regex=False)
df_taxo["Reference2"]=df_taxo["Reference2"].str.replace(").",")", regex=False)
df_taxo["Reference3"]=df_taxo["Reference3"].str.replace(").",")", regex=False)
df_taxo["Reference4"]=df_taxo["Reference4"].str.replace(").",")", regex=False)
df_taxo["Reference5"]=df_taxo["Reference5"].str.replace(").",")", regex=False)

df_taxo['NOM_ACTUEL_A_UTILISER'] = df_taxo['NOM_ACTUEL_A_UTILISER'].str.strip()
df_taxo["NOM_ACTUEL_A_UTILISER"] = df_taxo["NOM_ACTUEL_A_UTILISER"].replace(np.nan,"")
df_taxo["NOM_ACTUEL_A_UTILISER"] = df_taxo["NOM_ACTUEL_A_UTILISER"].fillna('')
df_dist['cle_taxo'] = df_dist['cle_taxo'].str.strip()

df_taxo = df_taxo.fillna('')
df_syno = df_syno.fillna('')
df_verna = df_verna.fillna('')
df_dist = df_dist.fillna('')
df_syno['nom_actuel_a_utiliser']=df_syno['nom_actuel_a_utiliser'].str.strip()
df_syno['synonym']=df_syno['synonym'].str.strip()


def replace_latex(text):
    text=text.replace('#','')
    #text=text.replace('&','\&')
    text=text.replace('_',' ')
    return text

def ldb_convert_to_string(x):
    x=re.sub("[^0-9]", "", x)
    if len(x)==0:
       return 0
    else:
        return int(x)
           
def split_and_format_latex(text, pos, style,term, delim=" "):
    tmp_arr=str(text).split(delim)
    nominal=tmp_arr[0:pos]
    auth=tmp_arr[pos:]
    return style+" ".join(nominal)+term+" "+" ".join(auth)
    
def format_scientific_name(name, rank, default_species=False, bold=True, is_syn=False):
    global global_idx
    if " var " in name or " subsp " in name :
        print("==>"+name)
    if bold:
        bold_begin="\\textbf{"
        bold_end="}"
    else:
        bold_begin=""
        bold_end=""
    if " var. " in name:        
        tmp_name=split_and_format_latex(name, 2,"\\emph{"+bold_begin, bold_end+"}" )
        split_name= tmp_name.split(" ")
        tmp_name_arr=[]
        subsp_found=False
        for tmp in split_name:
            if subsp_found:
                tmp="\\emph{"+bold_begin+tmp+bold_end+"}"
                subsp_found=False
            if tmp=="var.":
                subsp_found=True
            tmp_name_arr.append(tmp)
        tmp_name=" ".join(tmp_name_arr)
    elif "subspecies" in name or " subsp. "  in name:
        tmp_name=split_and_format_latex(name, 2,"\\emph{"+bold_begin, bold_end+ "}" )
        split_name= tmp_name.split(" ")
        tmp_name_arr=[]
        subsp_found=False
        for tmp in split_name:
            if subsp_found:
                tmp="\\emph{"+bold_begin+tmp+bold_end+"}"
                subsp_found=False
            if tmp=="subsp.":
                subsp_found=True
            tmp_name_arr.append(tmp)
        tmp_name=" ".join(tmp_name_arr)
    elif rank=="Species_or_higher" or default_species==True:
        tmp_name=split_and_format_latex(name, 2,"\\emph{"+bold_begin, bold_end+"}" )
    else:
        print("=>")
        print(name)
        tmp_name=name
    if is_syn :
        genus=name.strip( ).split(" ")[0]
        index="\\index{"+genus+"!synonym}"
        if not genus+" (syn.)" in index_name:
            index_name[genus+" (syn.)"]=[]
        index_name[genus+" (syn.)"].append(str(global_idx))        
    else:
        genus=name.strip( ).split(" ")[0]
        index="\\index{"+genus+"}"
        if not genus in index_name:
            index_name[genus]=[]
        index_name[genus].append(str(global_idx))
    global_idx=global_idx+1
    return index+tmp_name
    
def writeline(text, file, condition=True):
    if condition:
        file.write(text)
        file.write("\n")
    
def parse_row(row):
    global df_syno
    global df_verna
    global array_references
    returned={}
    genus=row["genus"]
    rank=row["rank"] 
    returned["genus"]=genus
    returned["rank"]=rank
    current_name=row["NOM_ACTUEL_A_UTILISER"]
    name_idx=current_name
    current_name=current_name.replace("&", "\&")    
    returned["current_name"]=current_name

    
    references=array_references[name_idx]["ref"]
    references_txt=""
    
    if(len(references)>0):
        references.sort()
        ref_dict={}
        for ref in references:
            #print(ref)
            tmp_ref=ref.split("(")
            #print(tmp_ref)
            if(len(tmp_ref)>1):
                author=tmp_ref[0]
                author=author.replace("&", "\&")
                if not author in ref_dict:
                    ref_dict[author]={}
                tmp_ref[1]=tmp_ref[1].strip(")")
                tmp_ref2=re.split(',|;', tmp_ref[1] )
                for ref2 in tmp_ref2:
                    #print(ref2)
                    tmp_ref3=re.split(":", ref2)
                    year=tmp_ref3[0].strip()
                    #print(year)
                    if not year in ref_dict[author]:
                        ref_dict[author][year]={}
                        ref_dict[author][year]["pages"]=[]
                    if(len(tmp_ref3)>1):
                        page=tmp_ref3[1].strip()
                        #print(page)
                        tmp_page=ref_dict[author][year]["pages"]
                        tmp_page.append(page)
                        ref_dict[author][year]["pages"]=tmp_page
        
        references_txt2='; '.join(references)
        tmp_pubs=[]
        for author, publi in ref_dict.items():
            tmp_txt1=author
            #print(author)
            for year, elems in publi.items():
                pages=elems["pages"]
                if len(pages)==0:
                    year_txt="("+year+")"
                else:
                    year_txt="("+year+": "+", ".join(pages)+")"
            tmp_pubs.append(tmp_txt1+ " "+year_txt)
        references_txt="; ".join(tmp_pubs)
    returned["references"]=references_txt
    df_syno_2=df_syno.loc[df_syno['nom_actuel_a_utiliser'] == current_name]
    returned["synonyms"]=[]
    for index2, row2 in df_syno_2.iterrows():
        syno=str(row2["synonym"])
        if len(syno)>0:            
            returned["synonyms"].append(str(syno).replace("&", "\&")  )
    returned["synonyms"] = list(dict.fromkeys(returned["synonyms"]))
    tmp_arr=str(current_name).split(" ")
    name_no_auth=' '.join(tmp_arr[0:2]).strip()
    df_verna_filter=df_verna.loc[df_verna['Scientific names without author'] == name_no_auth]
    returned["vernacular_names"]=[]
    for index3, row3 in df_verna_filter.iterrows():
        verna=row3["Vernacular name1"]        
        returned["vernacular_names"].append(str(verna).replace("&", "\&")  )
    return returned


def detect_distribution(row):
    global df_dist
    distribution_acceptee=None
    if 'current_name' in  row:
        current_name=row["current_name"]        
        tmp_list=[]
        if current_name.strip() !="":
            tmp_list.append(current_name.lower().strip().replace("\\&","&"))
        if "synonyms" in row:
            for elem in row["synonyms"]:
                if elem.strip() !="":
                    tmp_list.append(elem.lower().strip().replace("\\&","&"))
        if len(tmp_list)>0:
            distribution_acceptee=df_dist[df_dist["cle_taxo"].isin(tmp_list)]      
    return distribution_acceptee
    
def adapt_acronym_by_collector(collector, acronym):
    if "caljon" in collector.lower() and not "gent" in acronym.lower():
        acronym=acronym+", GENT"
    if ("reekmans m."  in collector.lower() or "ndabaneze"  in collector.lower()) and not "lg" in acronym.lower():
        acronym=acronym+", LG"
    return acronym
    
def print_distribution(row, distribution_acceptee, file1):
    geo_dict={}    
    go=False
    if not distribution_acceptee is None:
        for index, row_dist in distribution_acceptee.iterrows():
            province=row_dist["province"]
            if len(province)>0:
                if province not in geo_dict:
                    geo_dict[province]={}
                collector=row_dist["COLLECTOR"].replace("&", "\&").replace("_", " ")
                if collector is not None:
                    if len(collector)>0:
                        if collector not in geo_dict[province]:
                            geo_dict[province][collector]={}
                        coll_num=row_dist["COLL_NUM"].replace("&", "\&").replace("_", " ")
                        barcode_inst=row_dist["BARCODE_FULL"]
                        reg=re.search(r"^([^0-9]+)",barcode_inst )
                        acronym=""
                        if reg is not None:
                            if len(reg.groups())>0:
                                acronym=reg.group(1).strip()
                                acronym=adapt_acronym_by_collector(collector, acronym)
                        barcode_inst2=row_dist["Barcode 2nd"]                        
                        reg=re.search(r"^([^0-9]+)",barcode_inst2 )
                        acronym2=""
                        if reg is not None:
                            if len(reg.groups())>0:
                                acronym2=reg.group(1).strip().replace(".","").strip() 
                                acronym2=adapt_acronym_by_collector(collector, acronym2)
                        if coll_num is not None:
                            if acronym !="":
                                if acronym2!="":
                                    if acronym!=acronym2 :
                                        if acronym2<acronym:
                                            tmp=acronym2
                                            acronym2=acronym
                                            acronym=tmp                                        
                                        acronym=acronym+", "+acronym2
                                        acronym=acronym.replace("LG, LG","LG")
                            if acronym not in  geo_dict[province][collector]:
                                geo_dict[province][collector][acronym]=[]
                            tmp_arr=geo_dict[province][collector][acronym]
                            if coll_num not in tmp_arr:
                                tmp_arr.append(coll_num)
                            tmp_arr.sort()
                            geo_dict[province][collector][acronym] =tmp_arr 
    list_sp=[]
    
    for region, a_region in sorted(geo_dict.items()):
        list_coll=[]    
        for collector, a_collectors in sorted(a_region.items()):
            if len(a_collectors)>0:
                go =True
            list_herbaria=[]
            for herba_code, nums in sorted(a_collectors.items()):
                list_herba=", ".join(sorted(nums, key=ldb_convert_to_string))+ " ("+herba_code+")"
                #print(list_herba)
                list_herbaria.append(list_herba)
            list_nums="; ".join(list_herbaria)
            str_coll=""+ collector+ " "+list_nums +""
            #print(str_coll)
            list_coll.append(str_coll)
        str_prov="\\textbf{\\emph{"+region + "}}" + " - "+"; ".join(list_coll)
        list_sp.append(str_prov)
    str_p="\\item\\footnotesize{Specimens: "+". ".join(list_sp)+"}."
    if go:
        writeline(str_p, file1) 


    
def write_tex(row, file1):
    global dict_syno
    global no_distribution

    
    distribution_acceptee=None
    if 'current_name' in  row: 
        tmp_name=format_scientific_name(row["current_name"], row["rank"])
        
        #print(tmp_name)
        distribution_acceptee=detect_distribution(row)
        writeline_cond=False
        if distribution_acceptee is not None:
            if len(distribution_acceptee)>0:
                writeline_cond=True
        if not writeline_cond:
            no_distribution.append(row["current_name"])
        #genus=row["current_name"].strip(" ").split(" ")[0]
        writeline("\\begin{itemize}", file1, writeline_cond)
        writeline("\\normalsize\\item\\smallskip\\raggedright{"+replace_latex(tmp_name)+"}", file1, writeline_cond)
        writeline("\\begin{itemize}[leftmargin=5pt]", file1, writeline_cond)

        
        if row["current_name"] in dict_syno:
            if(row['current_name']== 'Ypsilopus tricuspis (Bolus) D’haijère & Stévart'):
                print("HAS_SYNO")
            tmp = dict_syno[row["current_name"]]
            tmp.sort()
            tmp[len(tmp)-1]=tmp[len(tmp)-1].strip(".")
            row["synonyms"]=tmp
            #genus=x.trim().split(" ")[0]
            writeline("\\item\\footnotesize{Syn.: "+ replace_latex('; '.join(
                [format_scientific_name(x, 'not_defined',True , False, True) for x in row["synonyms"]]
                
                ))+".}", file1, writeline_cond)
        
        if "vernacular_names" in row:
            if len(row["vernacular_names"])>0:
                tmp = list(dict.fromkeys(row["vernacular_names"]))
                tmp = [each_string.lower() for each_string in tmp]
                tmp.sort()
                row["vernacular_names"]=tmp
                writeline("\\item\\footnotesize{Vern. names: "+ replace_latex(', '.join(row["vernacular_names"]))+".}", file1, writeline_cond)
                
        if "references" in row:
            if len(row["references"])>0:
                tmp=row["references"]
                writeline("\\item\\footnotesize{Lit.: "+replace_latex(tmp)+".}", file1, writeline_cond)

        
        if "subspecies" in row:
            ##print("HAS_SUBSP")
            for subsp_row in row["subspecies"]:
                write_tex(row["subspecies"][subsp_row], file1)
        if "variety" in row:
            for var_row in row["variety"]:
                write_tex(row["variety"][var_row], file1)
        print_distribution(row, distribution_acceptee, file1)
        writeline("\\end{itemize}", file1, writeline_cond)
        writeline("\\end{itemize}", file1, writeline_cond)

def check_duplicates_and_ref():
    global df_syno
    global df_taxo
    global df_verna
    global array_references
    
    check_duplicate={}
    df_syno['nom_actuel_a_utiliser'] = df_syno['nom_actuel_a_utiliser'].str.replace(chr(194),chr(20))
    df_syno['synonym'] = df_syno['synonym'].str.replace(chr(194)," ")
    df_syno['synonym'] = df_syno['synonym'].str.replace('\xc2'," ")
    try:       
        def_check=df_taxo.sort_values(['clade', 'family',"NOM_ACTUEL_A_UTILISER" ], ascending=[True, True, True])
        for index, row in def_check.iterrows():    
            species=str(row["NOM_ACTUEL_A_UTILISER"])
            if(len(species)>0):
                standard=str(row["NOM_STANDARD"])
                if species in check_duplicate:
                    check_duplicate[species]["count"]=check_duplicate[species]["count"]+1
                    standard=str(row["NOM_STANDARD"])
                else:
                    check_duplicate[species]={}
                    check_duplicate[species]["count"]=1
                    #raise Exception('Duplicate problem on '+species)
                if standard != species:
                    check_duplicate[species]["syno"]=standard
                else:
                    check_duplicate[species]["syno"]=""
                    ##print(rank)
                references=[]
                if(len(str(row["Reference1"]).strip())>0):
                    references.append(str(row["Reference1"]).replace("&", "\&").replace("\\&", "\&").strip())
                if(len(str(row["Reference2"]).strip())>0):
                    references.append(str(row["Reference2"]).replace("&", "\&").replace("\\&", "\&").strip())
                if(len(str(row["Reference3"]).strip())>0):
                    references.append(str(row["Reference3"]).replace("&", "\&").replace("\\&", "\&").strip())
                if(len(str(row["Reference4"]).strip())>0):
                    references.append(str(row["Reference4"]).replace("&", "\&").replace("\\&", "\&").strip())
                if(len(str(row["Reference5"]).strip())>0):
                    references.append(str(row["Reference5"]).replace("&", "\&").replace("\\&", "\&").strip())                   
                if species in array_references:
                    tmp_ref=array_references[species]["ref"]
                    for ref in references:
                        if not ref in tmp_ref:
                            tmp_ref.append(ref)
                    array_references[species]["ref"]=tmp_ref
                else:                    
                    array_references[species]={}
                    array_references[species]["ref"]=references
                    
                    
        syno=dict(filter(lambda elem: elem[1]["syno"]!="", check_duplicate.items()))
        
        for key, val in syno.items():
            #print(key+"\t"+str(val["syno"]))
            if val["syno"].strip()!="":
                df_syno_2=df_syno.loc[df_syno['synonym'] == val["syno"]]
                #if len(df_syno_2)>0:
                    #print("found")
                if len(df_syno_2)==0:
                    #print("NOT_FOUND")
                    df_syno=df_syno.append({'rang': 'undefined', 'nom_actuel_a_utiliser':key,'synonym':val["syno"] }, ignore_index=True)
        dups= dict(filter(lambda elem: elem[1]["count"]>1, check_duplicate.items()))
              
    except Exception as e:
        #TODO more efficent exception capture
        print("Issue")
        traceback.print_tb(*sys.exc_info())
  
def entry_point():
    global df_syno
    global df_taxo
    global df_verna
    global index_name
    #filtrer acanthacae
    #df_taxo=df_taxo[(df_taxo['family']=="Acanthaceae")| (df_taxo['family']=="Balsaminaceae")|(df_taxo['family']=="Amaranthaceae")]
    check_duplicate={}
    try:
        df_taxo['NOM_ACTUEL_A_UTILISER'] = df_taxo['NOM_ACTUEL_A_UTILISER'].str.strip()
        df_taxo['species_name'] = df_taxo['species_name'].str.strip()

        df_syno['nom_actuel_a_utiliser'] = df_syno['nom_actuel_a_utiliser'].str.replace(chr(194),chr(20))
        df_syno['synonym'] = df_syno['synonym'].str.replace(chr(194)," ")
        df_syno['synonym'] = df_syno['synonym'].str.replace('\xc2'," ")       
        df_taxo["genus"] = df_taxo["genus"].replace(np.nan,"")
        df_taxo["genus"] = df_taxo["genus"].fillna('')        
       
        #MERGE SPECIES VARIETY AND SUBSP IN SORT
        def_species=df_taxo
        def_species=def_species.sort_values(['clade', 'family',"NOM_ACTUEL_A_UTILISER" ], ascending=[True, True, True])
        
        df_dist["cle_taxo"]=df_dist["cle_taxo"].str.lower()
        df_dist["cle_taxo"]=df_dist["cle_taxo"].str.strip()
        df_dist["cle_taxo"]=df_dist["cle_taxo"].str.replace("\\&","&")

        #print("GEO")      
        #print("SPECIES")
        
        #MERGE SYNO
        
        print("go")
        for index, row in def_species.iterrows():
            #print(index)
            species=str(row["NOM_ACTUEL_A_UTILISER"])#.replace("&", "\&").replace("_", " ")
            #print("NOM\t"+species)
            standard=str(row["NOM_STANDARD"])
            if standard != species:
                #print("SYNO = "+standard)
                syno_row= {"nom_actuel_a_utiliser": row["NOM_ACTUEL_A_UTILISER"], "synonym": row["NOM_STANDARD"]}
                df_syno=df_syno.append(syno_row, ignore_index = True)
        df_syno.drop_duplicates()
       
        for index, row in def_species.iterrows():    
            species=str(row["NOM_ACTUEL_A_UTILISER"])#.replace("&", "\&").replace("_", " ")
            if(len(species)>0):
                ##print(species)
                rank=row["rank"]#.replace("&", "\&")
                clade=row["clade"]#.replace("&", "\&")
                family=row["family"]#.replace("&", "\&")
                #synonym=row["SYNONYM"].replace("&", "\&").replace("_", " ")
                if not clade in output_data:
                    output_data[clade]={}
                if not family in output_data[clade]:
                    output_data[clade][family]={}
                tmp=parse_row(row)
                if not species in output_data[clade][family]:
                    output_data[clade][family][species]={}
                tmp["sort"]=clade+"_"+family+"_"+ species 
                output_data[clade][family][species]=tmp              

        file1 = open(output_file,"w", encoding='utf-8') 

        writeline("\\documentclass[12pt]{book}", file1)
        #writeline("\\usepackage{tabto}", file1)
        writeline("\\usepackage[utf8x]{inputenc}", file1)
        writeline("\\usepackage{xcolor}", file1)
        writeline("\\usepackage{graphicx}", file1)
        writeline("\\usepackage{enumitem}", file1)
        writeline("\\usepackage{makeidx}", file1)
        writeline("\\setlist{nolistsep}", file1)
        writeline("\\makeindex", file1)
        writeline("\DeclareUnicodeCharacter{146}{’}", file1)
        writeline("\\begin{document}", file1)
        writeline("\\let\cleardoublepage\\clearpage", file1)
        for clade, nested in output_data.items():           
            writeline("\\newpage", file1)
            #writeline("\\begin{huge}", file1)    
            writeline("\\noindent{\\textbf{\\Huge{"+clade+"}}}", file1)
            writeline("\\newline", file1)
            writeline("\\newline", file1)
            #writeline("\\end{huge}", file1)
            
            for current_family, nested2 in nested.items():
                #if current_family=="Dilleniaceae":
                #    print(current_family)
                writeline("\\colorbox[RGB]{204,255,102}{\\rlap{\\huge{"+current_family.strip()+"}}\\hspace{\\linewidth}\\hspace{-2\\fboxsep}}", file1)
                writeline("\\begin{flushleft}", file1)
                for species, nested3 in nested2.items():
                    #image_file=(image_folder+current_family+"_"+species).replace("&", "and").replace(" ", "_").replace(".", "_").strip("_")+".png"
                    #print(image_file)
                    write_tex(nested3, file1)
                writeline("\\end{flushleft}", file1)
        
        writeline("\\printindex", file1)        
        writeline("\\end{document}", file1)
        file1.close()
        #index file
        file2 = open(output_idx,"w", encoding='utf-8')
        for key in sorted(index_name):
            
            writeline(key+'\t'+'\t'.join(index_name[key]), file2)
        file2.close()
        #print("NO_DISTRIBUTION")
        no_distribution.sort()
        #for line in no_distribution:
        #    print(line)
    except Exception as e:
        #TODO more efficent exception capture
        #print("Issue")
        traceback.print_tb(*sys.exc_info())


def all_syno():
    global dict_syno
    dict_syno_tmp={}
    for idx, row in df_syno.iterrows():
        dict_syno_tmp[row["synonym"].strip()]=row["nom_actuel_a_utiliser".strip()]
    
    for idx, row in df_taxo.iterrows():
        if row["NOM_ACTUEL_A_UTILISER"] != row["NOM_STANDARD"]:
            if not row["NOM_STANDARD"] in dict_syno_tmp:
                #print("ADD NOM_ACCEPTE : "+row["NOM_ACTUEL_A_UTILISER".strip()] + "\t SYNO_INIT: "+row["NOM_STANDARD".strip()])
                dict_syno_tmp[row["NOM_STANDARD"].strip()]=row["NOM_ACTUEL_A_UTILISER".strip()]
            elif dict_syno_tmp[row["NOM_STANDARD"].strip()] != row["NOM_ACTUEL_A_UTILISER".strip()]:
                print("BIG_PROBLEM SYNO : "+ row["NOM_STANDARD"].strip() + "|ACCEPTE_1 : "+dict_syno_tmp[row["NOM_STANDARD"].strip()]+ "NOM_ACCEPTE_2"+ row["NOM_ACTUEL_A_UTILISER".strip()])
                dict_syno_tmp[row["NOM_STANDARD"].strip()]=row["NOM_ACTUEL_A_UTILISER".strip()]
    
    for key, value in dict_syno_tmp.items():
        value=value.replace("&", "\&")
        if not value in dict_syno:
            dict_syno[value]=[]
        #value=value.replace("&", "\&")
        
        dict_syno[value].append(key.replace("&", "\&"))
    print(dict_syno)
    print("--------------------")
            


#main
all_syno()
check_duplicates_and_ref()
entry_point()

fin = open(output_file, "rt")
#output file to write the result to
fout = open(output_file+"dup", "wt")
#for each line in the input file
for line in fin:
	#read replace the string and write to output file
	fout.write(line.replace('\\\\&', '\\&'))
#close input and output files
fin.close()
fout.close()
shutil.copyfile(output_file+"dup", output_file)
unlink(output_file+"dup")
