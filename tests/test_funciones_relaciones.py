import unittest
from unittest.mock import MagicMock, call, patch

from tests.utils import load_main_module


main_module = load_main_module()
Neo4jManager = main_module.Neo4jManager


class TestFuncionesRelaciones(unittest.TestCase):
    @patch("main.GraphDatabase.driver")
    @patch("main.load_dotenv")
    @patch.dict(
        "os.environ",
        {
            "NEO4J_URI": "neo4j+s://example.databases.neo4j.io",
            "NEO4J_USERNAME": "neo4j",
            "NEO4J_PASSWORD": "secret",
            "NEO4J_DATABASE": "example-db",
        },
        clear=True,
    )
    def test_create_rated_relationship_validates_nodes_and_merges_relation(
        self,
        _mock_load_dotenv: MagicMock,
        mock_driver_factory: MagicMock,
    ) -> None:
        mock_driver_factory.return_value = MagicMock()
        manager = Neo4jManager()

        with (
            patch.object(manager, "_require_node") as mock_require_node,
            patch.object(manager, "_run_write_query") as mock_run_write_query,
        ):
            manager.create_rated_relationship(
                user_id="u1",
                movie_id="m1",
                rating=4.5,
                timestamp=1712534400,
            )

        self.assertEqual(
            mock_require_node.call_args_list,
            [
                call("User", "userId", "u1"),
                call("Movie", "movieId", "m1"),
            ],
        )
        query = mock_run_write_query.call_args.args[0]
        self.assertIn("MERGE (user)-[rated:RATED]->(movie)", query)
        self.assertEqual(
            mock_run_write_query.call_args.kwargs,
            {
                "user_id": "u1",
                "movie_id": "m1",
                "rating": 4.5,
                "timestamp": 1712534400,
            },
        )

    @patch("main.GraphDatabase.driver")
    @patch("main.load_dotenv")
    @patch.dict(
        "os.environ",
        {
            "NEO4J_URI": "neo4j+s://example.databases.neo4j.io",
            "NEO4J_USERNAME": "neo4j",
            "NEO4J_PASSWORD": "secret",
            "NEO4J_DATABASE": "example-db",
        },
        clear=True,
    )
    def test_create_acted_in_relationship_validates_nodes_and_sets_role(
        self,
        _mock_load_dotenv: MagicMock,
        mock_driver_factory: MagicMock,
    ) -> None:
        mock_driver_factory.return_value = MagicMock()
        manager = Neo4jManager()

        with (
            patch.object(manager, "_require_node") as mock_require_node,
            patch.object(manager, "_run_write_query") as mock_run_write_query,
        ):
            manager.create_acted_in_relationship(
                person_id="p1",
                movie_id="m1",
                role="Neo",
            )

        self.assertEqual(
            mock_require_node.call_args_list,
            [
                call("Person", "tmdbId", "p1"),
                call("Movie", "movieId", "m1"),
            ],
        )
        query = mock_run_write_query.call_args.args[0]
        self.assertIn("MERGE (person)-[acted_in:ACTED_IN]->(movie)", query)
        self.assertEqual(
            mock_run_write_query.call_args.kwargs,
            {
                "person_id": "p1",
                "movie_id": "m1",
                "role": "Neo",
            },
        )

    @patch("main.GraphDatabase.driver")
    @patch("main.load_dotenv")
    @patch.dict(
        "os.environ",
        {
            "NEO4J_URI": "neo4j+s://example.databases.neo4j.io",
            "NEO4J_USERNAME": "neo4j",
            "NEO4J_PASSWORD": "secret",
            "NEO4J_DATABASE": "example-db",
        },
        clear=True,
    )
    def test_create_directed_relationship_validates_nodes_and_merges_relation(
        self,
        _mock_load_dotenv: MagicMock,
        mock_driver_factory: MagicMock,
    ) -> None:
        mock_driver_factory.return_value = MagicMock()
        manager = Neo4jManager()

        with (
            patch.object(manager, "_require_node") as mock_require_node,
            patch.object(manager, "_run_write_query") as mock_run_write_query,
        ):
            manager.create_directed_relationship(person_id="p1", movie_id="m1")

        self.assertEqual(
            mock_require_node.call_args_list,
            [
                call("Person", "tmdbId", "p1"),
                call("Movie", "movieId", "m1"),
            ],
        )
        query = mock_run_write_query.call_args.args[0]
        self.assertIn("MERGE (person)-[:DIRECTED]->(movie)", query)
        self.assertEqual(
            mock_run_write_query.call_args.kwargs,
            {"person_id": "p1", "movie_id": "m1"},
        )

    @patch("main.GraphDatabase.driver")
    @patch("main.load_dotenv")
    @patch.dict(
        "os.environ",
        {
            "NEO4J_URI": "neo4j+s://example.databases.neo4j.io",
            "NEO4J_USERNAME": "neo4j",
            "NEO4J_PASSWORD": "secret",
            "NEO4J_DATABASE": "example-db",
        },
        clear=True,
    )
    def test_create_in_genre_relationship_validates_nodes_and_merges_relation(
        self,
        _mock_load_dotenv: MagicMock,
        mock_driver_factory: MagicMock,
    ) -> None:
        mock_driver_factory.return_value = MagicMock()
        manager = Neo4jManager()

        with (
            patch.object(manager, "_require_node") as mock_require_node,
            patch.object(manager, "_run_write_query") as mock_run_write_query,
        ):
            manager.create_in_genre_relationship(movie_id="m1", genre_name="Action")

        self.assertEqual(
            mock_require_node.call_args_list,
            [
                call("Movie", "movieId", "m1"),
                call("Genre", "name", "Action"),
            ],
        )
        query = mock_run_write_query.call_args.args[0]
        self.assertIn("MERGE (movie)-[:IN_GENRE]->(genre)", query)
        self.assertEqual(
            mock_run_write_query.call_args.kwargs,
            {"movie_id": "m1", "genre_name": "Action"},
        )


if __name__ == "__main__":
    unittest.main()
