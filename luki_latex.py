import pandas
import openpyxl
import re
import datetime
import calendar
from os import listdir
from os.path import isfile, join

dict_result={}
source_file="D:\\DEV\\WOOD\\Copy of 2022_10_19 metadata_atlasdb.xlsx"
output_file="D:\\DEV\\WOOD\\out2.tex"

dict_floraison={}
folder_floraison="D:\DEV\WOOD\Atlas functional traits_21102022\Atlas functional traits_21102022\Images_Atlas_pheno\\1.Floraison\Figures"

dict_fructification={}
folder_fructification="D:\DEV\WOOD\Atlas functional traits_21102022\Atlas functional traits_21102022\Images_Atlas_pheno\\2.Fructification\Figures"

dict_dissemination={}
folder_dissemination="D:\DEV\WOOD\Atlas functional traits_21102022\Atlas functional traits_21102022\Images_Atlas_pheno\\3.Dissémination\Figures"

dict_defeuillaison={}
folder_defeuillaison="D:\DEV\WOOD\Atlas functional traits_21102022\Atlas functional traits_21102022\Images_Atlas_pheno\\4.Défeuillaison\Figures"

dict_occurences={}
folder_occurences="D:\DEV\WOOD\Atlas functional traits_21102022\Atlas functional traits_21102022\Images_Atlas_pheno\\5.Occurrence_maps"

dict_images={}
folder_images="D:\DEV\WOOD\Atlas functional traits_21102022\Atlas functional traits_21102022\Images_Atlas_pheno\\6.Photos_trees"

CLEANR = re.compile('<.*?>') 

def explore_images(folder, p_dict):
    onlyfiles = [f for f in listdir(folder) if isfile(join(folder, f))]
    for file in onlyfiles:
        print(file)
        if file.endswith(".jpg") or file.endswith(".png"):
            exploded= file.split("_")
            if len(exploded)>=2:
                key=" ".join(exploded[0:2])
                print(key)
                if not key in p_dict:
                    p_dict[key]=[]
                p_dict[key].append(folder+"\\"+file)

def replace_latex(text):
    text=text.replace('\\',"\\\\")
    text=text.replace('%',"\%")
    text=text.replace('#','')
    text=text.replace('&','\&')
    text=text.replace('_',' ')
    
    return text

def cleanhtml(raw_html):
  cleantext = re.sub(CLEANR, '', raw_html)
  return cleantext

def writeline(text, file, condition=True):
    if condition:
        file.write(text)
        file.write("\n")

        
        
def run():
    df_data=pandas.read_excel(source_file)
    df_data.fillna("", inplace=True)
    for i, row in df_data.iterrows():
        #print(row)
        family=str(row["Family"])
        name=str(row["ID"])
        if len(family)>0:
            if not family in dict_result:
                dict_result[family]={}
            dict_result[family][name]=row
            
    explore_images(   folder_floraison, dict_floraison)
    explore_images(   folder_fructification, dict_fructification)  
    explore_images(   folder_dissemination, dict_dissemination)
    explore_images(   folder_defeuillaison, dict_defeuillaison)   
    explore_images(   folder_occurences, dict_occurences)     
    file1 = open(output_file,"w", encoding='utf-8') 
    writeline("\\documentclass[12pt]{book}", file1)
    #writeline("\\usepackage{tabto}", file1)
    writeline("\\usepackage[utf8x]{inputenc}", file1)
    writeline("\\usepackage{xcolor}", file1)
    writeline("\\usepackage{float}", file1)
    writeline("\\usepackage{graphicx}", file1)
    writeline("\\usepackage{enumitem}", file1)
    writeline("\\usepackage{graphicx}", file1)
    writeline("\\usepackage{subfig}", file1)
    writeline("\\setlist{nolistsep}", file1)
    writeline("\DeclareUnicodeCharacter{146}{’}", file1)
    writeline("\\begin{document}", file1)
    writeline("\\let\cleardoublepage\\clearpage", file1)
    for key in sorted(dict_result.keys()):
        nested=dict_result[key]
        print(key)
        writeline("\\newpage", file1)
        writeline("\\noindent{\\textbf{\\Huge{"+key+"}}}", file1)
        writeline("\\newline", file1)
        writeline("\\newline", file1)
        writeline("\\begin{itemize}", file1) 
        for key2 in sorted(nested.keys()):
            row2=nested[key2]
            name=replace_latex(cleanhtml(row2["Name"]))
            #print(name)
                       
            writeline("\\normalsize\\item\\raggedright\\emph{{\\textbf{"+ name + "} "+replace_latex(row2["Author"]) +"}}", file1)
            
            strtmp=""
            #flowering_peak=str(row2["Flowering_peak"])
            
            
            if row2["Flowering_peak"] is not None:
                date = row2["Flowering_peak"]
                if isinstance(date, datetime.datetime):
                    #print(date.month)
                    if str(date.month).isnumeric():
                        month=calendar.month_name[date.month]
                        #print(month)
                        strtmp+="\\item\\footnotesize{\\textbf{Flowering peak:} "+ replace_latex(month) +" "+ str(date.day) +"}"            
            if row2["Flowering_rho"] is not None:
                strtmp+="\\item\\footnotesize{\\textbf{Flowering rho:} "+ replace_latex(str(row2["Flowering_rho"])) +"}"
            if row2["Flowering_Seasonality"] is not None:
                strtmp+="\\item\\footnotesize{\\textbf{Flowering seasonality:} "+ replace_latex(str(row2["Flowering_Seasonality"])) +"}"
                
            if row2["Fruiting_peak"] is not None:
                date = row2["Fruiting_peak"]
                if isinstance(date, datetime.datetime):
                    #print(date.month)
                    if str(date.month).isnumeric():
                        month=calendar.month_name[date.month]
                        #print(month)
                        strtmp+="\\item\\footnotesize{\\textbf{Fruiting peak:} "+ replace_latex(month) +" "+ str(date.day) +"}"            
            if row2["Fruiting_rho"] is not None:
                if len(str(row2["Fruiting_rho"]))>0:
                    strtmp+="\\item\\footnotesize{\\textbf{Fruiting rho:} "+ replace_latex(str(row2["Fruiting_rho"])) +"}"
            if row2["Fruiting_Seasonality"] is not None:
                if len(str(row2["Fruiting_Seasonality"]))>0:
                    strtmp+="\\item\\footnotesize{\\textbf{Fruiting seasonality:} "+ replace_latex(str(row2["Fruiting_Seasonality"])) +"}"
                
            if row2["Dissemination_peak"] is not None:
                date = row2["Dissemination_peak"]
                if isinstance(date, datetime.datetime):
                    #print(date.month)
                    if str(date.month).isnumeric():
                        month=calendar.month_name[date.month]                    
                        #print(month)
                        strtmp+="\\item\\footnotesize{\\textbf{Dissemination peak:} "+ replace_latex(month) +" "+ str(date.day) +"}"            
            if row2["Dissemination_rho"] is not None:
                if len(str(row2["Dissemination_rho"]))>0:
                    strtmp+="\\item\\footnotesize{\\textbf{Dissemination rho:} "+ replace_latex(str(row2["Dissemination_rho"])) +"}"
            if row2["Dissemination_Seasonality"] is not None:
                if len(str(row2["Dissemination_Seasonality"]))>0:
                    strtmp+="\\item\\footnotesize{\\textbf{Dissemination seasonality :} "+ replace_latex(str(row2["Dissemination_Seasonality"])) +"}"
                
                
            if row2["Defoliation_peak"] is not None:
                date = row2["Defoliation_peak"]
                if isinstance(date, datetime.datetime):
                    #print(date.month)
                    if str(date.month).isnumeric():
                        month=calendar.month_name[date.month]
                        #print(month)
                        strtmp+="\\item\\footnotesize{\\textbf{Defoliation peak:} "+ replace_latex(month) +" "+ str(date.day) +"}"            
            if row2["Defoliation_rho"] is not None:
                if len(str(row2["Defoliation_rho"]))>0:
                    strtmp+="\\item\\footnotesize{\\textbf{Defoliation rho:} "+ replace_latex(str(row2["Defoliation_rho"])) +"}"
            if row2["Defoliation_Seasonality"] is not None:
                if len(str(row2["Defoliation_Seasonality"]))>0:
                    strtmp+="\\item\\footnotesize{\\textbf{Defoliation seasonality:} "+ replace_latex(str(row2["Defoliation_Seasonality"])) +"}"
            
            
            if len(row2["Description"])>0:
                strtmp+="\\item\\footnotesize{\\textbf{Description:} "+ replace_latex(row2["Description"]) +"}"
            if len(row2["Ecology"])>0:
                strtmp+="\\item\\footnotesize{\\textbf{Ecology:} "+ replace_latex(row2["Ecology"]) +"}"
                
            if len(row2["Source de la description"])>0:
                strtmp+="\\item\\footnotesize{\\textbf{Source:} "+ replace_latex(row2["Source de la description"]) +"}"
            if  len(strtmp)>0: 
                writeline("\\begin{itemize}", file1)
                writeline(strtmp, file1)
                writeline("\\end{itemize}", file1)
                
            
            
            if key2 in dict_floraison and  key2 in dict_fructification and key2 in dict_dissemination and key2 in dict_defeuillaison:
                print("HAS_IMAGE")
                writeline("\\begin{figure}[H]", file1) 
                writeline("\\begin{tabular}{cc}", file1) 
                images_flo=dict_floraison[key2]
                images_flo.sort()
                images_fru=dict_fructification[key2]
                images_fru.sort()
                images_diss=dict_dissemination[key2]
                images_diss.sort()
                images_def=dict_defeuillaison[key2]
                images_def.sort()
                
                writeline("\\includegraphics[width=65mm]{"+images_flo[0].replace("\\","/")+"} & \\includegraphics[width=65mm]{"+images_fru[0].replace("\\","/")+"} ", file1)
                writeline("\\\\ Florishing & Fructification \\\\[6pt]", file1)
                writeline("\\includegraphics[width=65mm]{"+images_diss[0].replace("\\","/")+"} & \\includegraphics[width=65mm]{"+images_def[0].replace("\\","/")+"} ", file1)
                writeline("\\\\ Dissemination & Défeuillaison \\\\[6pt]", file1)
                writeline("\\end{tabular}", file1) 
                writeline("\\end{figure}", file1) 
            if key2 in dict_occurences:
                images_occ=dict_occurences[key2]
                images_occ.sort()
                writeline("\\begin{figure}[H] \\centering \\includegraphics[width=65mm]{"+images_occ[0].replace("\\","/")+"} \\\\ Distribution \\\\[6pt] \\end{figure} ", file1)
                
            
            writeline("\\", file1)                
            writeline("\\", file1)
        writeline("\\end{itemize}", file1)
    writeline("\\end{document}", file1)
            
run()
