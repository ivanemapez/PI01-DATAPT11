import uvicorn
from fastapi import FastAPI 
import pandas as pd
from datetime import datetime

df = pd.read_csv("C:\\Users\ivan\Documents\PI1\movies_completo.csv")

# Crear la aplicación FastAPI
app = FastAPI()


# Transformaciones necesarias (preprocesamiento del dataset)
df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
df['release_year'] = df['release_date'].dt.year
df['month_name'] = df['release_date'].dt.strftime('%B').str.lower()  # Mes en español
df['day_name'] = df['release_date'].dt.strftime('%A').str.lower()  # Día en español

# Endpoint 1: Cantidad de filmaciones por mes
@app.get("/cantidad_filmaciones_mes/{mes}")
def cantidad_filmaciones_mes(mes: int):
    mes = mes.lower()
    cantidad = df[df['month_name'] == mes].shape[0]
    return {"mensaje": f"{cantidad} cantidad de películas fueron estrenadas en el mes de {mes}"}


# Endpoint 2: Cantidad de filmaciones por día
@app.get("/cantidad_filmaciones_dia/{dia}")
def cantidad_filmaciones_dia(dia: str):
    dia = dia.lower()
    cantidad = df[df['day_name'] == dia].shape[0]
    return {"mensaje": f"{cantidad} cantidad de películas fueron estrenadas en los días {dia}"}

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
    actor_films = df[df['cast'].str.contains(nombre_actor, case=False, na=False)]
    if actor_films.empty:
        return {"mensaje": "Actor no encontrado"}
    cantidad_peliculas = actor_films.shape[0]
    retorno_total = actor_films['return'].sum()
    promedio_retorno = retorno_total / cantidad_peliculas
    return {
        "mensaje": f"El actor {nombre_actor} ha participado de {cantidad_peliculas} películas, con un retorno total de {retorno_total} y un promedio de {promedio_retorno} por filmación"
    }

# Endpoint 6: Información del director
@app.get("/get_director/{nombre_director}")
def get_director(nombre_director: str):
    director_films = df[df['director'].str.contains(nombre_director, case=False, na=False)]
    if director_films.empty:
        return {"mensaje": "Director no encontrado"}
    peliculas = []
    for _, film in director_films.iterrows():
        retorno_individual = film['return']
        costo = film['budget']
        ganancia = film['revenue']
        peliculas.append({
            "titulo": film['title'],
            "fecha_estreno": film['release_date'].strftime('%Y-%m-%d'),
            "retorno": retorno_individual,
            "costo": costo,
            "ganancia": ganancia
        })
    return {
        "director": nombre_director,
        "peliculas": peliculas
    }