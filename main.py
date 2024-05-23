
## hacemos la importacion de librerias a utilizar

from fastapi import FastAPI
import pandas as pd
from fastapi.responses import HTMLResponse

## cargamos los archivos que vamos a utilizar

tabla_developer = pd.read_parquet("./Datasets_endpoints/endpoint_Developer.parquet")


app = FastAPI()

#hacemos un testeo de funcionamiento de la api
@app.get("/")
def mensaje():
    return "Testeo Primera Api"

@app.get("/developer/{desarrollador}",response_class=HTMLResponse)
def developer(desarrollador: str):
        #primer paso normalizamos str ingresado a minuscula, para evitar conflictos
        desarrolador_normalizado = desarrollador.lower()
        
        #hacemos el filtrado por developer
        developer_filtrado = tabla_developer[tabla_developer["developer"] == desarrolador_normalizado]
        
        # establecemos la condicion de que si el developer que se ingresó tiene la tabla vacia, significa que no existe ese developer
        if developer_filtrado.empty:
            return "No existe ese Developer"
        else:
            # ahora procedemos a hacer la agrupacion de los developer por año y calculamos la cantidad de items por año y la cantidad de productos gratis por año
            Developer_muestra = tabla_developer[tabla_developer["developer"] == desarrolador_normalizado].groupby(["año"]).agg(
            Cantidad_de_Items=("item_id" ,"count"),
            Contenido_Free=("price",lambda x: (x=='free').sum())
            ).reset_index()
            
            # posteriormente calculamos el porcentaje de juegos gratis por año, lo convertimos en entero para redondearlo mejor y finalmente lo convertimos en string para agregarle
            # el signo de porcentaje
            Developer_muestra["Contenido_Free"] = round((Developer_muestra["Contenido_Free"] / Developer_muestra["Cantidad_de_Items"]* 100)).astype(int)
            Developer_muestra["Contenido_Free"] = Developer_muestra["Contenido_Free"].astype(str) + '%'
            
            #Finalmente convertimos el dataframe en un HTML
            Developer_muestra = Developer_muestra.to_html(index=False)
            return Developer_muestra