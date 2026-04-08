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
    finally:
        session.close()
        manager.close_driver()


if __name__ == "__main__":
    main()
