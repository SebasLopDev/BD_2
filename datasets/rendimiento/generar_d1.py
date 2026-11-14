import csv
from pathlib import Path

#cantidades de registros
cantidades=[100_000,500_000,1_000_000]

#carpeta donde guardaremos los csv
carpeta_salida=Path(__file__).resolve().parent / "datos_generados"

#crear la carpeta si todavia no existe
carpeta_salida.mkdir(parents=True,exist_ok=True)

#recorrer cada cantidad de registros
for cantidad in cantidades:
    #construir el nombre del archivo
    if cantidad ==1_000_000:
        nombre_archivo="d1_1m.csv"
    else:
        nombre_archivo=f"d1_{cantidad//1000}k.csv"   
    
    #Ruta completa del archivo
    ruta_archivo=carpeta_salida/nombre_archivo     

    #abrimos o creamos el archivo csv
    with open(ruta_archivo,"w",newline="",encoding="utf-8") as archivo:
        
        #creamos el escritor csv
        escritor=csv.writer(archivo)
        #escribimos los encabezados
        escritor.writerow(["clave","nombre"])

        #generamos los registros
        for i in range(1,cantidad+1):
            clave=i
            nombre="Persona_"+str(i)
            #escribimos una fila en el csv
            escritor.writerow([clave,nombre])
            
    print(f"Generado: {nombre_archivo} ({cantidad} registros)")  
    
print("Todos los datasets D1 fueron generados correctamente")          
        
    