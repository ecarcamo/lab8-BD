import os
from typing import Any

from dotenv import load_dotenv
from neo4j import GraphDatabase


class Neo4jManager:
    def __init__(self) -> None:
        load_dotenv()
        self.uri = self._get_env_var("NEO4J_URI")
        self.username = self._get_env_var("NEO4J_USERNAME")
        self.password = self._get_env_var("NEO4J_PASSWORD")
        self.database = self._get_env_var("NEO4J_DATABASE")
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

    def create_directed_relationship(self, person_id: str, movie_id: str) -> None:
        self._require_node("Person", "tmdbId", person_id)
        self._require_node("Movie", "movieId", movie_id)

        query = """
        MATCH (person:Person {tmdbId: $person_id})
        MATCH (movie:Movie {movieId: $movie_id})
        MERGE (person)-[:DIRECTED]->(movie)
        """
        self._run_write_query(query, person_id=person_id, movie_id=movie_id)

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
        self.driver.close()


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
