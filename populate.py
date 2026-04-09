import time
from main import Neo4jManager

def poblar_usuarios_y_ratings(manager: Neo4jManager) -> None:
    print("Iniciando inserción de datos..")
    
    # Creacion 4 películas base para que tengan contenido que calificar
    peliculas = [
        {"id": "1", "title": "The Matrix", "year": 1999, "plot": "A computer hacker learns about reality..."},
        {"id": "2", "title": "Inception", "year": 2010, "plot": "A thief who steals corporate secrets through dreams."},
        {"id": "3", "title": "Interstellar", "year": 2014, "plot": "Explorers travel through a wormhole in space."},
        {"id": "4", "title": "The Dark Knight", "year": 2008, "plot": "Menace known as the Joker wreaks havoc."}
    ]
    for p in peliculas:
        manager.create_movie(title=p["title"], movie_id=p["id"], year=p["year"], plot=p["plot"])
    print("Películas base creadas.")

    # Creacion 5 usuarios
    usuarios = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"},
        {"id": "3", "name": "Charlie"},
        {"id": "4", "name": "Diana"},
        {"id": "5", "name": "Eve"},
        {"id": "6", "name": "Ricardo"},
    ]
    for u in usuarios:
        manager.create_user(name=u["name"], user_id=u["id"])
    print("6 Usuarios creados.")

    # Creacion de ratings
    timestamp_actual = int(time.time())
    ratings = [
        # Alice 
        {"user": "1", "movie": "1", "rating": 5.0},
        {"user": "1", "movie": "2", "rating": 4.5},
        # Bob 
        {"user": "2", "movie": "2", "rating": 5.0},
        {"user": "2", "movie": "3", "rating": 4.0},
        # Charlie 
        {"user": "3", "movie": "3", "rating": 3.5},
        {"user": "3", "movie": "4", "rating": 4.5},
        # Diana 
        {"user": "4", "movie": "1", "rating": 4.0},
        {"user": "4", "movie": "4", "rating": 5.0},
        # Eve 
        {"user": "5", "movie": "1", "rating": 3.0},
        {"user": "5", "movie": "3", "rating": 5.0},
        # Ricardo 
        {"user": "6", "movie": "2", "rating": 4.5},
        {"user": "6", "movie": "4", "rating": 4.0},
    ]

    for r in ratings:
        manager.create_rated_relationship(
            user_id=r["user"], 
            movie_id=r["movie"], 
            rating=r["rating"], 
            timestamp=timestamp_actual
        )
    print("Relaciones RATED creadas con éxito.")
    print("¡Poblado completado exitosamente!")

if __name__ == "__main__":
    manager = Neo4jManager()
    try:
        poblar_usuarios_y_ratings(manager)
    except Exception as e:
        print(f"Error durante el poblado: {e}")
    finally:
        manager.close_driver()
