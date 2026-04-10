import os
from typing import Any

from dotenv import load_dotenv
from neo4j import GraphDatabase


class Neo4jManager:
    def __init__(self, suffix: str = "") -> None:
        load_dotenv()
        self.uri = self._get_env_var(f"NEO4J_URI{suffix}")
        self.username = self._get_env_var(f"NEO4J_USERNAME{suffix}")
        self.password = self._get_env_var(f"NEO4J_PASSWORD{suffix}")
        self.database = self._get_env_var(f"NEO4J_DATABASE{suffix}")
        self.driver = self.create_driver()

    def _get_env_var(self, key: str) -> str:
        value = os.getenv(key)
        if not value:
            raise ValueError(f"La variable de entorno {key} no está definida.")
        return value

    def create_driver(self) -> Any:
        return GraphDatabase.driver(
            self.uri,
            auth=(self.username, self.password),
        )

    def open_session(self) -> Any:
        return self.driver.session(database=self.database)

    def execute_test_query(self, session: Any) -> dict[str, str | int]:
        query = """
        RETURN
            1 AS number,
            'Conexion exitosa con Neo4j' AS message
        """
        record = session.run(query).single()

        if record is None:
            raise RuntimeError("La query de prueba no devolvió resultados.")

        return {
            "number": record["number"],
            "message": record["message"],
        }

    def _run_write_query(self, query: str, **parameters: Any) -> None:
        session = self.open_session()
        try:
            session.run(query, **parameters)
        finally:
            session.close()

    def _node_exists(self, label: str, property_name: str, property_value: Any) -> bool:
        session = self.open_session()
        query = (
            f"MATCH (node:{label} {{{property_name}: $property_value}}) "
            "RETURN COUNT(node) > 0 AS exists"
        )

        try:
            record = session.run(query, property_value=property_value).single()
        finally:
            session.close()

        return bool(record and record["exists"])

    def _require_node(self, label: str, property_name: str, property_value: Any) -> None:
        if not self._node_exists(label, property_name, property_value):
            raise ValueError(
                f"No existe un nodo {label} con {property_name}={property_value}."
            )

    def create_user(self, name: str, user_id: str) -> None:
        query = """
        MERGE (user:User {userId: $user_id})
        SET user.name = $name
        """
        self._run_write_query(query, name=name, user_id=user_id)

    def create_movie(
        self,
        title: str,
        movie_id: str,
        year: int,
        plot: str,
        **extra_properties: Any,
    ) -> None:
        properties = {
            "title": title,
            "movieId": movie_id,
            "year": year,
            "plot": plot,
            **extra_properties,
        }
        query = """
        MERGE (movie:Movie {movieId: $movie_id})
        SET movie += $properties
        """
        self._run_write_query(query, movie_id=movie_id, properties=properties)

    def create_genre(self, name: str) -> None:
        query = """
        MERGE (genre:Genre {name: $name})
        """
        self._run_write_query(query, name=name)

    def create_person(
        self,
        name: str,
        tmdb_id: str,
        born: int | None = None,
        **extra_properties: Any,
    ) -> None:
        properties = {
            "name": name,
            "tmdbId": tmdb_id,
            **extra_properties,
        }
        if born is not None:
            properties["born"] = born

        query = """
        MERGE (person:Person {tmdbId: $tmdb_id})
        SET person += $properties
        """
        self._run_write_query(query, tmdb_id=tmdb_id, properties=properties)

    def create_rated_relationship(
        self,
        user_id: str,
        movie_id: str,
        rating: float,
        timestamp: int,
    ) -> None:
        self._require_node("User", "userId", user_id)
        self._require_node("Movie", "movieId", movie_id)

        query = """
        MATCH (user:User {userId: $user_id})
        MATCH (movie:Movie {movieId: $movie_id})
        MERGE (user)-[rated:RATED]->(movie)
        SET rated.rating = $rating,
            rated.timestamp = $timestamp
        """
        self._run_write_query(
            query,
            user_id=user_id,
            movie_id=movie_id,
            rating=rating,
            timestamp=timestamp,
        )

    def create_acted_in_relationship(
        self,
        person_id: str,
        movie_id: str,
        role: str,
    ) -> None:
        self._require_node("Person", "tmdbId", person_id)
        self._require_node("Movie", "movieId", movie_id)

        query = """
        MATCH (person:Person {tmdbId: $person_id})
        MATCH (movie:Movie {movieId: $movie_id})
        MERGE (person)-[acted_in:ACTED_IN]->(movie)
        SET acted_in.role = $role
        """
        self._run_write_query(
            query,
            person_id=person_id,
            movie_id=movie_id,
            role=role,
        )

    def create_directed_relationship(self, person_id: str, movie_id: str, role: str = None) -> None:
        self._require_node("Person", "tmdbId", person_id)
        self._require_node("Movie", "movieId", movie_id)

        query = """
        MATCH (person:Person {tmdbId: $person_id})
        MATCH (movie:Movie {movieId: $movie_id})
        MERGE (person)-[directed:DIRECTED]->(movie)
        """
        if role is None:
            query = """
        MATCH (person:Person {tmdbId: $person_id})
        MATCH (movie:Movie {movieId: $movie_id})
        MERGE (person)-[:DIRECTED]->(movie)
        """
            
        parameters = {"person_id": person_id, "movie_id": movie_id}
        
        if role is not None:
            query += "SET directed.role = $role"
            parameters["role"] = role
            
        self._run_write_query(query, **parameters)

    def create_in_genre_relationship(self, movie_id: str, genre_name: str) -> None:
        self._require_node("Movie", "movieId", movie_id)
        self._require_node("Genre", "name", genre_name)

        query = """
        MATCH (movie:Movie {movieId: $movie_id})
        MATCH (genre:Genre {name: $genre_name})
        MERGE (movie)-[:IN_GENRE]->(genre)
        """
        self._run_write_query(query, movie_id=movie_id, genre_name=genre_name)

    def print_result(self, result: dict[str, str | int]) -> None:
        print(f"Numero: {result['number']}")
        print(f"Mensaje: {result['message']}")

    def close_driver(self) -> None:
        if self.driver is not None:
            self.driver.close()

    def find_all_users(self) -> list[dict[str, Any]]:
        query = "MATCH (u:User) RETURN u"
        session = self.open_session()
        try:
            records = session.run(query)
            return [dict(record["u"]) for record in records]
        finally:
            session.close()

    def find_all_movies(self) -> list[dict[str, Any]]:
        query = "MATCH (m:Movie) RETURN m"
        session = self.open_session()
        try:
            records = session.run(query)
            return [dict(record["m"]) for record in records]
        finally:
            session.close()

    def find_user(self, name: str) -> dict[str, Any] | None:
        query = "MATCH (u:User {name: $name}) RETURN u"
        session = self.open_session()
        try:
            record = session.run(query, name=name).single()
            if record:
                return dict(record["u"])
            return None
        finally:
            session.close()
            
    def find_movie(self, title: str) -> dict[str, Any] | None:
        query = "MATCH (m:Movie {title: $title}) RETURN m"
        session = self.open_session()
        try:
            record = session.run(query, title=title).single()
            if record:
                return dict(record["m"])
            return None
        finally:
            session.close()

    def find_user_movie_rating(self, user_name: str, movie_title: str) -> dict[str, Any] | None:
        query = """
        MATCH (u:User {name: $user_name})-[r:RATED]->(m:Movie {title: $movie_title})
        RETURN u, r, m
        """
        session = self.open_session()
        try:
            record = session.run(query, user_name=user_name, movie_title=movie_title).single()
            if record:
                return {
                    "user": dict(record["u"]),
                    "rating": dict(record["r"]),
                    "movie": dict(record["m"])
                }
            return None
        finally:
            session.close()

    def print_user(self, user: dict[str, Any] | None) -> None:
        if user:
            print(f"User: {user.get('name', 'N/A')} (ID: {user.get('userId', 'N/A')})")
        else:
            print("Usuario no encontrado.")

    def print_movie(self, movie: dict[str, Any] | None) -> None:
        if movie:
            print(f"Movie: {movie.get('title', 'N/A')} ({movie.get('year', 'N/A')}) - ID {movie.get('movieId', 'N/A')}")
        else:
            print("Película no encontrada.")

    def print_user_movie_rating(self, result: dict[str, Any] | None) -> None:
        if result:
            user = result["user"].get("name", "N/A")
            movie = result["movie"].get("title", "N/A")
            rating = result["rating"].get("rating", "N/A")
            timestamp = result["rating"].get("timestamp", "N/A")
            print(f"{user} calificó '{movie}' con {rating} (Timestamp: {timestamp})")
        else:
            print("No se encontró una relación de calificación para esos parámetros.")

    def close_driver(self) -> None:
        self.driver.close()


    #Funciones de Busqueda
    def find_movie(self, title: str) -> dict | None:
        session = self.open_session()
        query = """
        MATCH (movie:Movie {title: $title})
        RETURN movie.title AS title,
               movie.movieId AS movieId,
               movie.year AS year,
               movie.plot AS plot
        """
        try:
            record = session.run(query, title=title).single()
        finally:
            session.close()

        if record is None:
            return None

        return {
            "title": record["title"],
            "movieId": record["movieId"],
            "year": record["year"],
            "plot": record["plot"],
        }
    
    def find_user(self, user_name: str) -> dict | None:
        session = self.open_session()
        query = """
        MATCH (user:User {name: $user_name})
        RETURN user.name AS name,
               user.userId AS userId
        """
        try:
            record = session.run(query, user_name=user_name).single()
        finally:
            session.close()

        if record is None:
            return None

        return {
            "name": record["name"],
            "userId": record["userId"],
        }
    
    def find_user_movie_rating(self, user_name: str, movie_title: str) -> dict | None:
        session = self.open_session()
        query = """
        MATCH (user:User {name: $user_name})-[rated:RATED]->(movie:Movie {title: $movie_title})
        RETURN user.name AS user_name,
            user.userId AS user_id,
            movie.title AS movie_title,
            movie.movieId AS movie_id,
            rated.rating AS rating,
            rated.timestamp AS timestamp
        """
        try:
            record = session.run(query, user_name=user_name, movie_title=movie_title).single()
        finally:
            session.close()

        if record is None:
            return None

        return {
            "user_name": record["user_name"],
            "user_id": record["user_id"],
            "movie_title": record["movie_title"],
            "movie_id": record["movie_id"],
            "rating": record["rating"],
            "timestamp": record["timestamp"],
        }
    # Prints de busqueda 
    def print_movie(self, movie):
        if movie is None:
            print("No se encontró la película.")
            return
        print("Se encontro la peli:")
        print(f"Titulo: {movie['title']}")
        print(f"ID: {movie['movieId']}")
        print(f"Año: {movie['year']}")
        print(f"Plot: {movie['plot']}")

    def print_user(self, user):
        if user is None:
            print("No se encontró el usuario.")
            return
        print("Se encontro el usuario:")
        print(f"Nombre: {user['name']}")
        print(f"ID: {user['userId']}")

    def print_user_movie_rating(self, result):
        if result is None:
            print("No se encontro la relacion entre el usuario y la pelicula")
            return
        print("Relacion RATED Encontrada:")
        print(f"Usuario: {result['user_name']} (ID: {result['user_id']})")
        print(f"Pelicula: {result['movie_title']} (ID: {result['movie_id']})")
        print(f"Rating: {result['rating']}")
        print(f"Timestamp: {result['timestamp']}")

    def find_all_users(self) -> list[dict]:
        session = self.open_session()
        query = """
        MATCH (user:User)
        RETURN user.name AS name,
               user.userId AS userId
        """
        try:
            records = session.run(query).values()
        finally:
            session.close()

        return [{"name": record[0], "userId": record[1]} for record in records]
    
    def find_all_movies(self) -> list[dict]:
        session = self.open_session()
        query = """
        MATCH (movie:Movie)
        RETURN movie.title AS title,
               movie.movieId AS movieId,
                movie.year AS year,
                movie.plot AS plot
        """
        try:
            records = session.run(query).values()
        finally:
            session.close()

        return [
            {
                "title": record[0],
                "movieId": record[1],
                "year": record[2],
                "plot": record[3],
            }
            for record in records
        ]
    
    def clear_database(self) -> None:
        session = self.open_session()
        query = "MATCH (n) DETACH DELETE n"
        try:
            session.run(query)
        finally:
            session.close()


def main() -> None:
    manager = Neo4jManager()
    session = manager.open_session()

    try:
        result = manager.execute_test_query(session)
        manager.print_result(result)

        manager.create_user(name="Alice", user_id="1")
        manager.create_movie(
            title="The Matrix",
            movie_id="100",
            year=1999,
            plot="A computer hacker learns from mysterious rebels about the true nature of his reality...",
        )
        manager.create_genre(name="Action")
        manager.create_person(name="Keanu Reeves", tmdb_id="200", born=1964)

        manager.create_rated_relationship(
            user_id="1",
            movie_id="100",
            rating=5.0,
            timestamp=1712534400,
        )
        manager.create_acted_in_relationship(
            person_id="200",
            movie_id="100",
            role="Neo",
        )
        manager.create_directed_relationship(person_id="200", movie_id="100")
        manager.create_in_genre_relationship(movie_id="100", genre_name="Action")
    finally:
        session.close()
        manager.close_driver()


if __name__ == "__main__":
    main()
