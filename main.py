from fastapi import FastAPI, HTTPException
import pandas as pd
from datetime import datetime
import calendar

# ruta
df = pd.read_csv("C:\\Users\ivan\Documents\PI1\movies_completo.csv")

app = FastAPI()

# Transformaciones 
df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
df['release_year'] = df['release_date'].dt.year
df['month_name'] = df['release_date'].dt.month  # extrae el mes de la columna
df['day_number'] = df['release_date'].dt.day #extrae el dia del mes buscado

# Endpoint 1: Cantidad de filmaciones por mes
@app.get("/cantidad_filmaciones_mes/{mes}")
def cantidad_filmaciones_mes(mes: str):
        meses_ing = {
        "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
        "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
        "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12}


        # Convertir el nombre del mes a número
        mes = mes.lower()
        if mes not in meses_ing:
            return {"error": f"El mes '{mes}' no es válido. Asegúrate de ingresar un mes en español correctamente."}
        
        mes_num = meses_ing[mes]
        
        # Extraer el mes de `release_date`
        df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
        df['release_month'] = df['release_date'].dt.month
        
        # Filtrar por el mes consultado
        count = df[df['release_month'] == mes_num].shape[0]
        
        return {"mensaje": f"{count} cantidad de películas fueron estrenadas en el mes de {mes.capitalize()}"}


# Endpoint 2: Cantidad de filmaciones por día
@app.get("/cantidad_filmaciones_dia/{dia}")
def cantidad_filmaciones_dia(dia: str):
        dias_ing = {
        "lunes": 0, "martes": 1, "miércoles": 2, "jueves": 3,
        "viernes": 4, "sábado": 5, "domingo": 6 }
        # Convertir el nombre del día a su índice
        dia = dia.lower()
        if dia not in dias_ing:
            return {"error": f"El día '{dia}' no es válido. Asegúrate de ingresar un día en español correctamente."}
        dia_num = dias_ing[dia]
        
        # Extraer el día de la semana de `release_date`
        df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
        df['release_dayofweek'] = df['release_date'].dt.dayofweek
        
        # Filtrar por el día consultado
        count = df[df['release_dayofweek'] == dia_num].shape[0]
        return {"mensaje": f"{count} cantidad de películas fueron estrenadas en los días {dia.capitalize()}"}
    

# Endpoint 3: Score por título
@app.get("/score_titulo/{titulo}")
def score_titulo(titulo: str):
    filmacion = df[df['title'].str.lower() == titulo.lower()]
    if filmacion.empty:
        return {"mensaje": "Película no encontrada"}
    titulo = filmacion['title'].values[0]
    estreno = filmacion['release_year'].values[0]
    score = filmacion['popularity'].values[0]
    return {"mensaje": f"La película {titulo} fue estrenada en el año {estreno} con un score/popularidad de {score}"}

# Endpoint 4: Votos por título
@app.get("/votos_titulo/{titulo}")
def votos_titulo(titulo: str):
    filmacion = df[df['title'].str.lower() == titulo.lower()]
    if filmacion.empty:
        return {"mensaje": "Película no encontrada"}
    votos = filmacion['vote_count'].values[0]
    promedio_votos = filmacion['vote_average'].values[0]
    if votos < 2000:
        return {"mensaje": "La película no cumple con el mínimo de 2000 valoraciones"}
    return {"mensaje": f"La película {titulo} tiene {votos} valoraciones con un promedio de {promedio_votos}"}

# Endpoint 5: Información del actor
@app.get("/get_actor/{nombre_actor}")
def get_actor(nombre_actor: str):
    try:
        # Verifica que 'cast' esté en formato de lista en el DataFrame
        if isinstance(df['cast'].iloc[0], str):
            import ast
            df['cast'] = df['cast'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

        # Filtrar películas donde el nombre del actor esté en la columna 'cast'
        actor_films = df[df['cast'].apply(lambda cast_list: nombre_actor in cast_list if isinstance(cast_list, list) else False)]
        
        #calcular retornos, promedio y cantidad de peliculas
        cantidad_peliculas = actor_films.shape[0]
        retorno_total = actor_films['return'].sum() if 'return' in actor_films.columns else 0
        promedio_retorno = retorno_total / cantidad_peliculas if cantidad_peliculas > 0 else 0

        return {
            "mensaje": f"El actor {nombre_actor} ha participado en {cantidad_peliculas} películas, con un retorno total de {retorno_total} y un promedio de {promedio_retorno} por filmación."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando la solicitud: {str(e)}")

# Endpoint 6: Información del director
@app.get("/get_director/{nombre_director}")
def get_director(nombre_director: str):
    try:
        # Verifica que 'crew' esté en formato de lista en el DataFrame
        if isinstance(df['crew'].iloc[0], str):
            import ast
            df['crew'] = df['crew'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

        # Filtrar las películas dirigidas por el director ingresado
        director_films = df[df['crew'].apply(lambda cast_list: nombre_director in cast_list if isinstance(cast_list, list) else False)]

        # Calcular el retorno total del director
        retorno_total = director_films['return'].sum() if 'return' in director_films.columns else 0
        
        # Crear una lista con la información detallada de cada película
        peliculas_info = []
        for _, row in director_films.iterrows():
            pelicula = {
                "titulo": row['title'],
                "fecha_lanzamiento": row['release_date'],
                "retorno": row['return'],
                "costo": row['budget'],
                "ganancia": row['revenue'] - row['budget']
            }
            peliculas_info.append(pelicula)
        
        return {
            "mensaje": f"El director {nombre_director} ha conseguido un retorno total de {retorno_total}.",
            "peliculas": peliculas_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando la solicitud: {str(e)}")
