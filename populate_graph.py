import time
from main import Neo4jManager

def populate_custom_graph(manager: Neo4jManager) -> None:
    print("Iniciando creación del grafo personalizado con todas las propiedades...")

    # 1. Crear el nodo Movie con todas las propiedades
    # title: string, tmdbId: integer, released: datetime, imdbRating: decimal (0-10), movieId: integer
    # year: integer, imdbId: integer, runtime: integer, countries: list of strings, imdbVotes: integer
    # url: string, revenue: integer, plot: string, poster: string, budget: integer, languages: list of strings
    manager.create_movie(
        title="Inception",
        movie_id="1",  # en create_movie se llama movieId y en nuestro manager espera string
        year=2010,
        plot="A thief who steals corporate secrets through the use of dream-sharing technology...",
        tmdbId=27205,
        released="2010-07-16T00:00:00",
        imdbRating=8.8,
        imdbId=1375666,
        runtime=148,
        countries=["USA", "UK"],
        imdbVotes=2500000,
        url="https://www.imdb.com/title/tt1375666/",
        revenue=839000000,
        poster="https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvmHnTcr79.jpg",
        budget=160000000,
        languages=["English", "Japanese", "French"]
    )
    print("Nodo Movie creado exitosamente.")

    # 2. Crear las 3 personas
    # Person 1 (Actor/Director)
    # name: string, tmdbId: integer, born: datetime, died: datetime, bornIn: string
    # url: string, imdbId: integer, bio: string, poster: string
    manager.create_person(
        name="Christopher Nolan",
        tmdb_id="1", # El manager actual espera tmdbId como primary en string O integer, dependiendo de lo que reciba
        born="1970-07-30T00:00:00", # String con formato datetime Neo4j friendly
        died="N/A",                 # String o None
        bornIn="London, England, UK",
        url="https://www.imdb.com/name/nm0634240/",
        imdbId=634240,
        bio="Christopher Edward Nolan is a British-American film director, producer, and screenwriter.",
        poster="https://image.tmdb.org/t/p/w500/xuAIuYSsl1jrWO0WNCjYvED4Gnt.jpg"
    )

    # Person 2 (Actor)
    manager.create_person(
        name="Leonardo DiCaprio",
        tmdb_id="2",
        born="1974-11-11T00:00:00",
        died="N/A",
        bornIn="Los Angeles, California, USA",
        url="https://www.imdb.com/name/nm0000138/",
        imdbId=138,
        bio="Leonardo Wilhelm DiCaprio is an American actor and film producer.",
        poster="https://image.tmdb.org/t/p/w500/wo2hJpn04vbtmh0B9utCFdsQhxM.jpg"
    )

    # Person 3 (Director)
    manager.create_person(
        name="Emma Thomas",
        tmdb_id="3",
        born="1971-12-09T00:00:00",
        died="N/A",
        bornIn="London, England, UK",
        url="https://www.imdb.com/name/nm0858784/",
        imdbId=858784,
        bio="Dame Emma Thomas Nolan is an English film producer.",
        poster="https://image.tmdb.org/t/p/w500/someposter.jpg"
    )
    print("Nodos Person (Actor/Director) creados exitosamente.")

    # Añadir extra labels explícitamente en Cypher, ya que requiren múltiples labels.
    # El API Manager de create_person solo genera (Person). Las especificaciones dicen "Person Actor", etc.
    session = manager.open_session()
    try:
        session.run("MATCH (p:Person {tmdbId: '1'}) SET p:Actor:Director")
        session.run("MATCH (p:Person {tmdbId: '2'}) SET p:Actor")
        session.run("MATCH (p:Person {tmdbId: '3'}) SET p:Director")
    finally:
        session.close()
    
    print("Labels extra Actor/Director asignados.")

    # 3. Crear nodo Genre
    manager.create_genre(name="Sci-Fi")
    print("Nodo Genre creado exitosamente.")

    # 4. Crear nodo User
    manager.create_user(name="Felipe", user_id="101")
    print("Nodo User creado exitosamente.")

    # 5. Crear relaciones
    # Person 1 (Actor/Director) -> ACTED_IN (role) & DIRECTED (role)
    manager.create_acted_in_relationship(person_id="1", movie_id="1", role="Extra/Himself")
    manager.create_directed_relationship(person_id="1", movie_id="1", role="Lead Director")

    # Person 2 (Actor) -> ACTED_IN (role)
    manager.create_acted_in_relationship(person_id="2", movie_id="1", role="Cobb")

    # Person 3 (Director) -> DIRECTED (role)
    manager.create_directed_relationship(person_id="3", movie_id="1", role="Co-Director / Producer")

    # Movie -> IN_GENRE -> Genre
    manager.create_in_genre_relationship(movie_id="1", genre_name="Sci-Fi")

    # User -> RATED (rating, timestamp) -> Movie
    timestamp_actual = int(time.time())
    manager.create_rated_relationship(user_id="101", movie_id="1", rating=5.0, timestamp=timestamp_actual)

    print("Todas las relaciones creadas exitosamente. Grafo construido de acuerdo al inciso!")

if __name__ == "__main__":
    manager = Neo4jManager(suffix="2")
    try:
        populate_custom_graph(manager)
    except Exception as e:
        print(f"Error durante el poblado: {e}")
    finally:
        manager.close_driver()
