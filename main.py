
## hacemos la importacion de librerias a utilizar

from fastapi import FastAPI
import pandas as pd
from fastapi.responses import HTMLResponse

## cargamos los archivos que vamos a utilizar

# tabla de la primera consulta
tabla_developer = pd.read_parquet("./Datasets_endpoints/endpoint_Developer.parquet")

# tabla de la segunda consulta
tabla_userdata = pd.read_parquet("./Datasets_endpoints/endpoint_userdata.parquet")

# tabla de la tercera consulta
tabla_userforgenre = pd.read_parquet("./Datasets_endpoints/enpoint_userforgenre.parquet")

# tabla de la cuarta y quinta consulta
tabla_user_reviews_sentiments = pd.read_parquet("./Datasets_endpoints/endpoint_games_reviews.parquet")

app = FastAPI()

#hacemos un testeo de funcionamiento de la api
@app.get("/")
def mensaje():
    return "Testeo Primera Api"

# ------------------------------------- Funciones Extras----------------------------------------------------
# funcion para normalizar price
def str_to_float(value):
    try:
        return round(float(value))
    except (TypeError,ValueError):
        return 0

#-------------------------------------------Consultas-------------------------------------------------------


#primera consulta

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
            # lo ordenamos de manera descendiente y reseteamos el index
            Developer_muestra = tabla_developer[tabla_developer["developer"] == desarrolador_normalizado].groupby(["año"]).agg(
            Cantidad_de_Items=("item_id" ,"count"),
            Contenido_Free=("price",lambda x: (x=='free').sum())
            ).sort_values(by="año",ascending=False).reset_index()
            
            # posteriormente calculamos el porcentaje de juegos gratis por año, lo convertimos en entero para redondearlo mejor y finalmente lo convertimos en string para agregarle
            # el signo de porcentaje
            Developer_muestra["Contenido_Free"] = round((Developer_muestra["Contenido_Free"] / Developer_muestra["Cantidad_de_Items"]* 100)).astype(int)
            Developer_muestra["Contenido_Free"] = Developer_muestra["Contenido_Free"].astype(str) + '%'
            
            #Finalmente convertimos el dataframe en un HTML
            Developer_muestra = Developer_muestra.to_html(index=False)
            return Developer_muestra
        

# Segunda Consulta

@app.get("/userdata/{user_id}")
def userdata (user_id:str):
    user_filtrado = tabla_userdata[tabla_userdata["user_id"] == user_id]
    user_filtrado["price"] = user_filtrado["price"].apply(str_to_float)
    user_filtrado = user_filtrado.groupby("user_id").agg(
        Dinero_Gastado = ("price","sum"),
        total_recomendaciones_buenas = ("recommend","sum"),
        total_recomendaciones = ("recommend","count"),
        cantidad_de_items = ("item_id","count")
        ).reset_index()
    user_filtrado["%_de_recomendacion"] = round(user_filtrado["total_recomendaciones_buenas"] /user_filtrado["total_recomendaciones"] * 100).astype(int)
    user_filtrado["%_de_recomendacion"] = user_filtrado["%_de_recomendacion"].astype(str) + "%"

    user_filtrado.drop(["total_recomendaciones_buenas","total_recomendaciones"],axis=1,inplace=True)
    user_filtrado.rename(columns={"user_id":"Usuario"},inplace=True)
    user_filtrado = user_filtrado.to_dict(orient="records")[0]
    
    return user_filtrado