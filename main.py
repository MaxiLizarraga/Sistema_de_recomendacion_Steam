
#------------------------------ Importacion de librerias a utilizar ----------------------------------------

from fastapi import FastAPI
import pandas as pd
import numpy as np
from fastapi.responses import HTMLResponse
from sklearn.metrics.pairwise import cosine_similarity
import random as r

#----------------------------------- Carga de archivos------------------------------------------------------

# Tabla consulta 2
tabla_userdata = pd.read_parquet("./Datasets_endpoints/endpoint_userdata.parquet")

# tabla modelo item-item
tabla_modelo_usuarios = pd.read_parquet("./Datasets_endpoints/recommend_usuario_item.parquet")

# tabla modelo usuario-item
tabla_modelo_item = pd.read_parquet("./Datasets_endpoints/recommend_item_item.parquet")

#----------------------------------- Mensaje de Bienvenida -------------------------------------------------
app = FastAPI()

#hacemos un testeo de funcionamiento de la api
@app.get("/")
def mensaje():
    return "Testeo Primera Api"

# ------------------------------------- Funciones Extras ---------------------------------------------------
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
    """
    * **Parámetros**: Recibe el nombre del desarrollador y devuelve una tabla HTML por año donde contiene:
    * Total Productos
    * Porcentaje de Productos Gratis
    
    * **ejemplos de parámetros**: Valve,Capcom,Monster Games
    """
    # Tabla consulta 1
    tabla_developer = pd.read_parquet("./Datasets_endpoints/endpoint_Developer.parquet")
    
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
    """
    * **Parámetros**: Recibe el nombre del usuario y devuelve un diccionario donde contiene:
    * Usuario
    * Total de Dinero Gastado en USD
    * Cantidad de Productos
    * Porcentaje de Recomendación
    
    * **ejemplos de parámetros**: --000-- , echoxsilence , i_did_911_just_saying
    """
    
    # hacemos el filtrado de usuario,luego convertimos la columna de price en float y los que son textos o nulos lo convertimos en 0
    user_filtrado = user_id.lower()
    tabla_userdata_filtrado = tabla_userdata[tabla_userdata["user_id"] == user_filtrado]
    
    # hacemos la condicion de que exista ese usuario
    if tabla_userdata_filtrado.empty:
        return "No está el usuario ingresado"
    
    else:
     tabla_userdata_filtrado["price"] = tabla_userdata_filtrado["price"].apply(str_to_float)
    
     # agrupamos por usuario
     # -calculamos la sumatoria del dinero gastado
     # -contamos las buenas recomendaciones 
     # -conteo de los items del usuario
     tabla_userdata_filtrado = tabla_userdata_filtrado.groupby("user_id").agg(
        Dinero_Gastado = ("price","sum"),
        total_recomendaciones_buenas = ("recommend","count"),
        cantidad_de_items = ("item_id","count")
        ).reset_index()
    
     # posteriormente hacemos el calculo de porcentaje de recomendación
     tabla_userdata_filtrado["%_de_recomendacion"] = round(tabla_userdata_filtrado["total_recomendaciones_buenas"] /tabla_userdata_filtrado["cantidad_de_items"] * 100).astype(int)
     tabla_userdata_filtrado["%_de_recomendacion"] = tabla_userdata_filtrado["%_de_recomendacion"].astype(str) + "%"
     tabla_userdata_filtrado["Dinero_Gastado"] = str(tabla_userdata_filtrado.loc[0,"Dinero_Gastado"]) + " USD"
     
     # por ultimo detalles borramos las columnas que no nos sirven, reenombramos el user_id a usuario y lo convertimos en diccionario
     tabla_userdata_filtrado.drop(["total_recomendaciones_buenas"],axis=1,inplace=True)
     tabla_userdata_filtrado.rename(columns={"user_id":"Usuario"},inplace=True)
     tabla_userdata_filtrado = tabla_userdata_filtrado.to_dict(orient="records")[0]
     
     return tabla_userdata_filtrado

# Tercera Consulta

@app.get("/userforgenre/{genero}")

def userforgenre(genero: str):
    """
    * **Parámetros**: Recibe el género y devuelve una lista donde contiene:
    * Usuario con mas horas jugadas en ese género
    * Año
    * Sumatoria de horas jugadas por año
    
    * **ejemplos de parámetros**: Action, Indie, Casual
    """
    # Tabla consulta 3
    tabla_userforgenre = pd.read_parquet("./Datasets_endpoints/enpoint_userforgenre.parquet")
    # Normalizamos a minuscula el genero ingresado
    genre_normalizado = genero.lower()

    # Filtramos por el genero ingresado y agrupamos por usuarios para sacar las horas totales que le dedicó 
    filtroGenre =tabla_userforgenre[(tabla_userforgenre["genre"] == genre_normalizado)].groupby(["user_id"]).agg(
    Horas_Jugadas_Totales = ("playtime_forever","sum")
    ).sort_values(by="Horas_Jugadas_Totales",ascending=False).reset_index()
    if filtroGenre.empty:
        return f"No existe el género {genre_normalizado}"
    else:
     # sacamos al usuario con el mayor de horas dedicadas a el genero filtrado
     usuario_con_mas_horas = filtroGenre.loc[0,"user_id"]

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
    """
    * **Parámetros**: Recibe el año y devuelve el TOP 3 de ese año en una lista donde contiene:
    * puesto
    * desarrollador 
    
    * **ejemplos de parámetros**: 2000, 2017, 2003
    """
    tabla_user_reviews_sentiments = pd.read_parquet("./Datasets_endpoints/endpoint_games_reviews.parquet")
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

@app.get("/developer_reviews_analysis/{developer}")
def developer_reviews_analysis (Desarrollador: str):
    """
    * **Parámetros**: Recibe el desarrollador y devuelve un diccionario con una lista de valor donde contiene:
    * desarrollador como Key
    * Cantidad de comentarios positivos y negativos 
    
    * **ejemplos de parámetros**: Capcom, Valve, 
    """
    tabla_user_reviews_sentiments = pd.read_parquet("./Datasets_endpoints/endpoint_games_reviews.parquet")
    # Normalizamos el dato a minuscula para evitar confictos en la busqueda
    dev_normalizado = Desarrollador.lower()
    
    #ahora filtramos por developer y lo agrupamos por el mismo, y hacemos los calculos de la cantidad de comentarios positivos y negativos
    dev_reseñas = tabla_user_reviews_sentiments[tabla_user_reviews_sentiments["developer"] == dev_normalizado].groupby("developer").agg(
    Positivos = ("sentiment_analysis",lambda x: (x == 2).sum()),
    Negativos = ("sentiment_analysis",lambda x: (x == 0).sum())
).reset_index()
    
    #hacemos una condicional de si la tabla está vacia 
    if dev_reseñas.empty:
        return "No existe el developer ingresado"
    else:
        #borramos la columna developer y guardamos el numero de los comentarios y positivos en variables
        tabla_salida = dev_reseñas.drop("developer",axis=1)
        salida_positivo = str(tabla_salida["Positivos"][0])
        salida_negativo = str(tabla_salida["Negativos"][0])
        # finalmente devolvemos un diccionario con la key del developer y como valor una lista de los comentarios positivos y negativos
        salida_final = {f"{developer}":["positivos:"+ salida_positivo , "negativos:" + salida_negativo]}
        return salida_final


#---------------------------------------modelo de machine learning----------------------------------------------------
#modelo de recomendacion ITEM-ITEM

@app.get("/recommend_games/{item_id}")
def recomendacion_juego(item_id:int):
    """
    * **Parámetros**: Recibe el id del item y devuelve una lista de 5 juegos recomendados donde contiene:
    * Nombre del juego
    
    * **ejemplos de parámetros**: 10, 2028056, 2028103
    """
    juego_seleccionado = tabla_modelo_item[tabla_modelo_item["item_id"] == item_id]
    juego_seleccionado
    if juego_seleccionado.empty:
        return "No existe ese item en la lista"
    # limpiamos las columnas que no vamos a usar
    juego_seleccionado = juego_seleccionado.drop(["item_id","app_name","developer","año","juegos_vendidos","Valoración"],axis=1)
    dataframe_para_similitud = tabla_modelo_item.drop(["item_id","app_name","developer","año","juegos_vendidos","Valoración"],axis=1)
    # hacemos el calculo de coseno de similitud
    similitud_score = cosine_similarity(juego_seleccionado,dataframe_para_similitud)

    # limitamos por precision en la similitud y devolvemos una lista random de 5 juegos
    indices_recomendados = np.where(similitud_score == 1.0)
    indices_recomendados = indices_recomendados[1][indices_recomendados[1] != juego_seleccionado.index[0]]
    indices_recomendados_aleatorio = r.sample(list(indices_recomendados),5)

    # ya teniendo los indices aleatorios se llama y muestra
    juegos_recomendados = tabla_modelo_item.loc[indices_recomendados_aleatorio][["app_name"]]
    lista_juegos_recomendados = juegos_recomendados["app_name"].to_list()
    return lista_juegos_recomendados

#modelo de recomendacion USUARIO-ITEM
@app.get("/user_recommend/{user}")
def recomendacion_usuario(usuario:str):
    """
    * **Parámetros**: Recibe el id del usuario y devuelve una lista de 5 juegos recomendados donde contiene:
    * Nombre del juego
    
    * **ejemplos de parámetros**: --000-- , echoxsilence , i_did_911_just_saying
    """
    usuario_seleccionado = usuario.lower()
    usuario_seleccionado = tabla_modelo_usuarios[tabla_modelo_usuarios["user_id"] == usuario_seleccionado]
    if usuario_seleccionado.empty:
        return "No se encontró al usuario"

    usuario_gustos = usuario_seleccionado.drop(["item_id"],axis=1)
    df_para_similitud = tabla_modelo_usuarios.drop(["item_id"],axis=1)

    usuario_gustos = usuario_gustos.groupby("user_id").max().reset_index()
    df_para_similitud = df_para_similitud.groupby("user_id").max().reset_index()

    usuario_gustos = usuario_gustos.drop(["user_id"],axis=1)
    df_para_similitud = df_para_similitud.drop(["user_id"],axis=1)

    similitud = cosine_similarity(usuario_gustos,df_para_similitud)

    usuarios_gustos_similares = np.where(similitud > 0.8)
    indices_recomendados = usuarios_gustos_similares[1][usuarios_gustos_similares[1] != usuario_gustos.index[0]]
    indices_recomendados_aleatorio = r.sample(list(indices_recomendados),7)

    juegos_recomendados = tabla_modelo_usuarios.loc[indices_recomendados_aleatorio][["item_id"]].reset_index(drop=True).drop_duplicates()
    juegos_recomendados = pd.merge(juegos_recomendados,tabla_modelo_item,on="item_id")
    juegos_recomendados = juegos_recomendados["app_name"][:5].to_list()

    return juegos_recomendados