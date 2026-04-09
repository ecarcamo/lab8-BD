import time
from main import Neo4jManager

def poblar_usuarios_y_ratings(manager: Neo4jManager) -> None:
    print("Iniciando inserción de datos (Persona 2)...")
    
    # Creacion 4 películas base para que tengan contenido que calificar
    peliculas = [
        {"id": "m1", "title": "The Matrix", "year": 1999, "plot": "A computer hacker learns about reality..."},
        {"id": "m2", "title": "Inception", "year": 2010, "plot": "A thief who steals corporate secrets through dreams."},
        {"id": "m3", "title": "Interstellar", "year": 2014, "plot": "Explorers travel through a wormhole in space."},
        {"id": "m4", "title": "The Dark Knight", "year": 2008, "plot": "Menace known as the Joker wreaks havoc."}
    ]
    for p in peliculas:
        manager.create_movie(title=p["title"], movie_id=p["id"], year=p["year"], plot=p["plot"])
    print("Películas base creadas.")

    # Creacion 5 usuarios
    usuarios = [
        {"id": "u1", "name": "Alice"},
        {"id": "u2", "name": "Bob"},
        {"id": "u3", "name": "Charlie"},
        {"id": "u4", "name": "Diana"},
        {"id": "u5", "name": "Eve"}
    ]
    for u in usuarios:
        manager.create_user(name=u["name"], user_id=u["id"])
    print("5 Usuarios creados.")

    # Creacion de ratings
    timestamp_actual = int(time.time())
    ratings = [
        # Alice (u1)
        {"user": "u1", "movie": "m1", "rating": 5.0},
        {"user": "u1", "movie": "m2", "rating": 4.5},
        # Bob (u2)
        {"user": "u2", "movie": "m2", "rating": 5.0},
        {"user": "u2", "movie": "m3", "rating": 4.0},
        # Charlie (u3)
        {"user": "u3", "movie": "m3", "rating": 3.5},
        {"user": "u3", "movie": "m4", "rating": 4.5},
        # Diana (u4)
        {"user": "u4", "movie": "m1", "rating": 4.0},
        {"user": "u4", "movie": "m4", "rating": 5.0},
        # Eve (u5)
        {"user": "u5", "movie": "m1", "rating": 3.0},
        {"user": "u5", "movie": "m3", "rating": 5.0},
    ]

    for r in ratings:
        manager.create_rated_relationship(
            user_id=r["user"], 
            movie_id=r["movie"], 
            rating=r["rating"], 
            timestamp=timestamp_actual
        )
    print("Relaciones RATED creadas con éxito.")
    print("¡Poblado de Persona 2 completado exitosamente!")

if __name__ == "__main__":
    manager = Neo4jManager()
    try:
        poblar_usuarios_y_ratings(manager)
    except Exception as e:
        print(f"Error durante el poblado: {e}")
    finally:
        manager.close_driver()
