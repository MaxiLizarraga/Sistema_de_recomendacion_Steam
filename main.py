
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
def userdata(user_id:str):
    # hacemos el filtrado de usuario,luego convertimos la columna de price en float y los que son textos o nulos lo convertimos en 0
    user_filtrado = tabla_userdata[tabla_userdata["user_id"] == user_id]
    
    # hacemos la condicion de que exista ese usuario
    if user_filtrado.empty:
        return "El usuario ingresado es incorrecto"
    else:
     user_filtrado["price"] = user_filtrado["price"].apply(str_to_float)
    
     # agrupamos por usuario
     # -calculamos la sumatoria del dinero gastado
     # -la sumatoria de las buenas recomendaciones 
     # -conteo de los items del usuario
     user_filtrado = user_filtrado.groupby("user_id").agg(
        Dinero_Gastado = ("price","sum"),
        total_recomendaciones_buenas = ("recommend","sum"),
        total_recomendaciones = ("recommend","count"),
        cantidad_de_items = ("item_id","count")
        ).reset_index()
    
     # posteriormente hacemos el calculo de porcentaje de recomendación
     user_filtrado["%_de_recomendacion"] = round(user_filtrado["total_recomendaciones_buenas"] /user_filtrado["total_recomendaciones"] * 100).astype(int)
     user_filtrado["%_de_recomendacion"] = user_filtrado["%_de_recomendacion"].astype(str) + "%"

     # por ultimo detalles borramos las columnas que no nos sirven, reenombramos el user_id a usuario y lo convertimos en diccionario
     user_filtrado.drop(["total_recomendaciones_buenas","total_recomendaciones"],axis=1,inplace=True)
     user_filtrado.rename(columns={"user_id":"Usuario"},inplace=True)
     user_filtrado = user_filtrado.to_dict(orient="records")[0]
     return user_filtrado

# Tercera Consulta

@app.get("/userforgenre/{genero}")
def userforgenre(genero: str):
    # Normalizamos a minuscula el genero ingresado
    genre_normalizado = genero.lower()

    # Filtramos por el genero ingresado y agrupamos por usuarios para sacar las horas totales que le dedicó 
    filtroGenre =tabla_userforgenre[(tabla_userforgenre["genre"] == genre_normalizado)].groupby(["user_id"]).agg(
    Horas_Jugadas_Totales = ("playtime_forever","sum")
    ).reset_index()
    if filtroGenre.empty:
        return f"No existe el género {genre_normalizado}"
    else:
     # sacamos al usuario con el mayor de horas dedicadas a el genero filtrado
     usuario_con_mas_horas = filtroGenre.loc[filtroGenre["Horas_Jugadas_Totales"].idxmax(),"user_id"]

     # ahora filtramos por ese usuario y genero, lo agrupamos por año y hacemos que calcule las horas por año, y finalizando convierte las horas en enteros
     Consulta_Final = tabla_userforgenre[(tabla_userforgenre["genre"] == genre_normalizado) & (tabla_userforgenre["user_id"] == usuario_con_mas_horas)].groupby(["año"]).agg(
     Horas = ("playtime_forever","sum")
     ).reset_index()
     Consulta_Final["Horas"] = Consulta_Final["Horas"].astype(int)

     # y por ultimo hacemos el retorno solicitado
     salida_final = {
     "Usuario con mas horas jugadas en el genero action" : usuario_con_mas_horas,
     "Horas Jugadas" : Consulta_Final.to_dict(orient="records")
     }
     return salida_final
 
 # Cuarta Consulta
@app.get("/best_developer_year/{year}")
def best_developer_year(year: int):
    
    # Hacemos el filtrado de año y agrupamos por developer, calculamos el total de comentarios positivos y sentimientos positivos,y lo ordenamos de descendiente
    Filtro_año = tabla_user_reviews_sentiments[tabla_user_reviews_sentiments["año"] == year].groupby("developer").agg(
    comentarios_positivos = ("recommend",'sum'),
    sentimientos_positivos = ("sentiment_analysis",lambda x: (x == 2).count())
    ).sort_values(by=["comentarios_positivos","sentimientos_positivos"],ascending=False).reset_index()
    
    # comprobamos que no esté vacio la tabla, si está vacio significa que no se puso bien el año
    if Filtro_año.empty:
        return "El año ingresado es incorrecto, el rango es de 1989 a 2017"
    
    else:
        # y por ultimo hacemos la salida en forma de diccionario
        salida_best_developer_year = [
            {'Puesto 1': Filtro_año.loc[0,"developer"]},
            {'Puesto 2': Filtro_año.loc[1,"developer"]},
            {'Puesto 3': Filtro_año.loc[2,"developer"]}]
    return salida_best_developer_year

# Quinta Consulta

@app.get("/developer_revires_analysis/{developer}:")
def developer_reviews_analysis (developer: str):
    dev_normalizado = developer.lower()
    dev_reseñas = tabla_user_reviews_sentiments[tabla_user_reviews_sentiments["developer"] == dev_normalizado].groupby("developer").agg(
    Positivos = ("sentiment_analysis",lambda x: (x == 2).sum()),
    negativos = ("sentiment_analysis",lambda x: (x == 0).sum())
).reset_index()
    if dev_reseñas.empty:
        return "No existe el developer ingresado"
    else:
        tabla_salida = dev_reseñas.drop("developer",axis=1)
        tabla_salida = tabla_salida.to_dict(orient="records")

        salida_final = {f"{developer}":tabla_salida}
        return salida_final