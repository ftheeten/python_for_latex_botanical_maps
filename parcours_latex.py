import pandas as pnd
import numpy as np

fichier_taxo="C:\\WORK_2021\\MEISE\\2021_nov\\14\\Artib_latex_taxo_20211114_indeterminataft.txt"
fichier_syno="C:\\WORK_2021\\MEISE\\2021_nov\\7\\export_list_syno_fusionne.txt"
fichier_verna="C:\\WORK_2021\\MEISE\\2021_nov\\7\\ArticleB_Liste des noms vernaculaires.txt" 
output_file="C:\\PROJECTS_R\\SALVATOR\\latex\\main2.tex" 

output_data={}


df_taxo=pnd.read_csv(fichier_taxo, sep='\t', encoding='ISO-8859–1')
df_syno=pnd.read_csv(fichier_syno, sep='\t', encoding='ISO-8859–1')
df_verna=pnd.read_csv(fichier_verna, sep='\t', encoding='UTF-8')

def replace_latex(text):
    text=text.replace('#','')
    #text=text.replace('&','\&')
    text=text.replace('_',' ')
    return text
    
def split_and_format_latex(text, pos, style,term, delim=" "):
    tmp_arr=str(text).split(delim)
    nominal=tmp_arr[0:pos]
    auth=tmp_arr[pos:]
    return style+" ".join(nominal)+term+" "+" ".join(auth)
    
def writeline(text, file):
    file.write(text)
    file.write("\n")
    
def parse_row(row):
    global df_syno
    global df_verna
    returned={}
    genus=row["genus"]
    rank=row["rank"]
    #print(genus)
    #genus=genus.replace("&", "\&")    
    returned["genus"]=genus
    returned["rank"]=rank
    current_name=row["NOM_ACTUEL_A_UTILISER"]
    #print("CURRENT : "+current_name)
    current_name=current_name.replace("&", "\&")    
    returned["current_name"]=current_name
    references=[]
    if(len(str(row["Reference1"]).strip())>0):
        references.append(str(row["Reference1"]).strip())
    if(len(str(row["Reference2"]).strip())>0):
        references.append(str(row["Reference2"]).strip())
    if(len(str(row["Reference3"]).strip())>0):
        references.append(str(row["Reference3"]).strip())
    if(len(str(row["Reference4"]).strip())>0):
        references.append(str(row["Reference4"]).strip())
    if(len(str(row["Reference5"]).strip())>0):
        references.append(str(row["Reference5"]).strip())
    #references=sorted(references)
    references_txt=""
    if(len(references)>0):
        references_txt='~; '.join(references)
    returned["references"]=references_txt.replace("&", "\&")
    df_syno_2=df_syno.loc[df_syno['nom_actuel_a_utiliser'] == current_name]
    returned["synonyms"]=[]
    for index2, row2 in df_syno_2.iterrows():
        syno=str(row2["synonym"])
        if len(syno)>0:
            #print(current_name+ " SYNO " + str(syno))
            returned["synonyms"].append(str(syno).replace("&", "\&")  )
    tmp_arr=str(current_name).split(" ")
    name_no_auth=' '.join(tmp_arr[0:2]).strip()
    df_verna_filter=df_verna.loc[df_verna['Scientific names without author'] == name_no_auth]
    returned["vernacular_names"]=[]
    for index3, row3 in df_verna_filter.iterrows():
        verna=row3["Vernacular name1"]
        #print("VERNA")
        #print(verna)
        returned["vernacular_names"].append(str(verna).replace("&", "\&")  )
    return returned
    
    
def write_tex(row, file1):
    if 'current_name' in  row:
        #writeline("\\begin{block}", file1) 
        if row["rank"]=="Species_or_higher":
            tmp_name=split_and_format_latex(row["current_name"], 2,"\\emph{{\\textbf{", "}}}" )
        elif row["rank"]=="subspecies":
            tmp_name=split_and_format_latex(row["current_name"], 2,"\\emph{{\\textbf{", "}}}" )
            split_name= tmp_name.split(" ")
            tmp_name_arr=[]
            subsp_found=False
            for tmp in split_name:
                if subsp_found:
                   tmp="\\emph{\\textbf{"+tmp+"}}"
                   subsp_found=False
                if tmp=="subsp.":
                    subsp_found=True
                tmp_name_arr.append(tmp)
            tmp_name=" ".join(tmp_name_arr)
        elif row["rank"]=="Variety":      
            tmp_name=split_and_format_latex(row["current_name"], 2,"\\emph{{\\textbf{", "}}}" )
            split_name= tmp_name.split(" ")
            tmp_name_arr=[]
            subsp_found=False
            for tmp in split_name:
                if subsp_found:
                   tmp="\\emph{\\textbf{"+tmp+"}}"
                   subsp_found=False
                if tmp=="var.":
                    subsp_found=True
                tmp_name_arr.append(tmp)
            tmp_name=" ".join(tmp_name_arr)
        else:
            tmp_name=row["current_name"]
        writeline("\\raggedright\\textbullet\\hspace{5mm}\\normalsize{"+replace_latex(tmp_name)+"}", file1)
        writeline("\\linebreak", file1)
        if "remark" in row:
            writeline("\\normalsize{"+replace_latex(row["remark"])+"}", file1)
            writeline("\\linebreak", file1)
        if "synonyms" in row:
            if len(row["synonyms"])>0:
                #tmp_name=split_and_format_latex(row["current_name"], 2,"\\emph{", "}" )
                writeline("\\small{Syn.: "+ replace_latex('~; '.join([split_and_format_latex(x, 2,"\\emph{", "}" ) for x in row["synonyms"]]))+"}", file1)
                writeline("\\linebreak", file1)
        if "references" in row:
            if len(row["references"])>0:
                writeline("\\small{Lit.: "+replace_latex(row["references"])+"}", file1)
                writeline("\\linebreak", file1)
        if "vernacular_names" in row:
            if len(row["vernacular_names"])>0:
                writeline("\\small{Nom\(s\) vern.: "+ replace_latex('~; '.join(row["vernacular_names"]))+"}", file1)
                writeline("\\linebreak", file1)
        #writeline("\\end{block}", file1)        
        writeline("\\linebreak", file1)
        if "subspecies" in row:
            #print("HAS_SUBSP")
            for subsp_row in row["subspecies"]:
                #print(subsp_row)
                #print(row["subspecies"][subsp_row])
                write_tex(row["subspecies"][subsp_row], file1)
        if "variety" in row:
            #print("HAS_VAR")
            for var_row in row["variety"]:
                #print(var_row)
                #print(row["variety"][var_row])
                write_tex(row["variety"][var_row], file1)

df_taxo['NOM_ACTUEL_A_UTILISER'] = df_taxo['NOM_ACTUEL_A_UTILISER'].str.strip()
df_taxo['species_name'] = df_taxo['species_name'].str.strip()

df_syno['nom_actuel_a_utiliser'] = df_syno['nom_actuel_a_utiliser'].str.replace(chr(194),chr(20))
df_syno['synonym'] = df_syno['synonym'].str.replace(chr(194)," ")
df_syno['synonym'] = df_syno['synonym'].str.replace('\xc2'," ")
print(len(df_syno))
df_syno=df_syno.drop_duplicates()
print(len(df_syno))


df_taxo["Reference1"]=df_taxo["Reference1"].fillna("")
df_taxo["Reference2"]=df_taxo["Reference2"].fillna("")
df_taxo["Reference3"]=df_taxo["Reference3"].fillna("")
df_taxo["Reference4"]=df_taxo["Reference4"].fillna("")
df_taxo["Reference5"]=df_taxo["Reference5"].fillna("")
df_taxo["NOM_ACTUEL_A_UTILISER"] = df_taxo["NOM_ACTUEL_A_UTILISER"].replace(np.nan,"")
df_taxo["NOM_ACTUEL_A_UTILISER"] = df_taxo["NOM_ACTUEL_A_UTILISER"].fillna('')
df_taxo["genus"] = df_taxo["genus"].replace(np.nan,"")
df_taxo["genus"] = df_taxo["genus"].fillna('')

def_species=df_taxo[df_taxo['rank']=="Species_or_higher"]
def_species=def_species.sort_values(['clade', 'family',"NOM_ACTUEL_A_UTILISER" ], ascending=[True, True, True])

for index, row in def_species.iterrows():    
    #name_status=row["name_status"].replace("&", "\&")
    species=str(row["species_name"])#.replace("&", "\&").replace("_", " ")
    if(len(species)>0):
        #print(species)
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
        
        #print(rank)
        
def_subspecies=df_taxo[df_taxo['rank']=="subspecies"]
def_subspecies=def_subspecies.sort_values(['clade', 'family',"NOM_ACTUEL_A_UTILISER" ], ascending=[True, True, True])
def_subspecies=def_subspecies.drop_duplicates()
#print("___SUBSP__________\r\n")
for index, row in def_subspecies.iterrows():    
    #name_status=row["name_status"].replace("&", "\&")
    subsp=str(row["NOM_ACTUEL_A_UTILISER"])#.replace("&", "\&").replace("_", " ")
    if(len(subsp)>0):
        #print(subsp)
        rank=row["rank"]#.replace("&", "\&")
        clade=row["clade"]#.replace("&", "\&")
        family=row["family"]#.replace("&", "\&")
        species_name=row["species_name"].replace("&", "\&")
        if not family in output_data[clade]:
            output_data[clade][family]={"remark":"NO_DIRECT_PARENT"}
        if not species_name in output_data[clade][family]:
            output_data[clade][family][species_name]={"remark":"Only identified as subspecies or variety", "current_name":species_name, "rank":"Species_or_higher"}
        else:    
            tmp_array=output_data[clade][family][species_name]
        tmp=parse_row(row)
        if not "subspecies" in output_data[clade][family][species_name]:
            output_data[clade][family][species_name]["subspecies"]={}
        output_data[clade][family][species_name]["subspecies"][subsp]=tmp    

def_variety=df_taxo[df_taxo['rank']=="Variety"]
def_variety=def_variety.sort_values(['clade', 'family',"NOM_ACTUEL_A_UTILISER" ], ascending=[True, True, True])
#print("___VARIETY__________\r\n")
for index, row in def_variety.iterrows():    
    #name_status=row["name_status"].replace("&", "\&")
    variety=str(row["NOM_ACTUEL_A_UTILISER"]).replace("&", "\&").replace("_", " ")
    if(len(variety)>0):
        #print(variety)
        rank=row["rank"]#.replace("&", "\&")
        clade=row["clade"]#.replace("&", "\&")
        family=row["family"]#.replace("&", "\&")
        species_name=row["species_name"].replace("&", "\&")
        if not family in output_data[clade]:
            output_data[clade][family]={"remark":"NO_DIRECT_PARENT"}
        if not species_name in output_data[clade][family]:
            output_data[clade][family][species_name]={"remark":"Only identified as subspecies or variety", "current_name":species_name, "rank":"Species_or_higher"}
        else:    
            tmp_array=output_data[clade][family][species_name]
        tmp=parse_row(row)
        if not "variety" in output_data[clade][family][species_name]:
            output_data[clade][family][species_name]["variety"]={}
        output_data[clade][family][species_name]["variety"][variety]=tmp         

file1 = open(output_file,"w", encoding='utf-8') 
writeline("\\documentclass[12pt]{book}", file1)
writeline("\\usepackage{tabto}", file1)
writeline("\\usepackage[utf8x]{inputenc}", file1)
writeline("\\usepackage{multicol}", file1)
writeline("\DeclareUnicodeCharacter{146}{’}", file1)
writeline("\\begin{document}", file1)
#writeline("\\spaceskip 0.5 em \\relax ", file1)
writeline("\\let\cleardoublepage\\clearpage", file1)
#writeline("\\setlength\\parindent{0pt}", file1)


for clade, nested in output_data.items():
    #writeline("\\newpage", file1)
    #writeline("\\begin{huge}", file1)        
    writeline("\\chapter{"+clade+"}", file1)
    #writeline("\\end{huge}", file1)
    #writeline("\\linebreak", file1)
    for current_family, nested2 in nested.items():
        #writeline("\\begin{large}", file1)
        #writeline("\\begin{center}", file1)
        
        writeline("\\section{"+current_family.strip() +"}", file1)
        writeline("\\begin{multicols*}{2}", file1)
        #writeline("\\end{center}", file1)
        #writeline("\\end{large}", file1)
        for species, nested3 in nested2.items():
            write_tex(nested3, file1)
        writeline("\\end{multicols*}", file1)
writeline("\\end{document}", file1)
file1.close()