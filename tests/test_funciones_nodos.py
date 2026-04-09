import unittest
from unittest.mock import MagicMock, patch

from tests.utils import load_main_module


main_module = load_main_module()
Neo4jManager = main_module.Neo4jManager


class TestFuncionesNodos(unittest.TestCase):
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
    def test_create_user_uses_merge_with_expected_params(
        self,
        _mock_load_dotenv: MagicMock,
        mock_driver_factory: MagicMock,
    ) -> None:
        mock_driver_factory.return_value = MagicMock()
        manager = Neo4jManager()

        with patch.object(manager, "_run_write_query") as mock_run_write_query:
            manager.create_user(name="Alice", user_id="u1")

        query = mock_run_write_query.call_args.args[0]
        self.assertIn("MERGE (user:User {userId: $user_id})", query)
        self.assertEqual(
            mock_run_write_query.call_args.kwargs,
            {"name": "Alice", "user_id": "u1"},
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
    def test_create_movie_merges_by_movie_id_and_sets_properties(
        self,
        _mock_load_dotenv: MagicMock,
        mock_driver_factory: MagicMock,
    ) -> None:
        mock_driver_factory.return_value = MagicMock()
        manager = Neo4jManager()

        with patch.object(manager, "_run_write_query") as mock_run_write_query:
            manager.create_movie(
                title="The Matrix",
                movie_id="m1",
                year=1999,
                plot="Sci-fi",
                extra="Test",
            )

        query = mock_run_write_query.call_args.args[0]
        self.assertIn("MERGE (movie:Movie {movieId: $movie_id})", query)
        self.assertEqual(
            mock_run_write_query.call_args.kwargs,
            {
                "movie_id": "m1",
                "properties": {
                    "title": "The Matrix",
                    "movieId": "m1",
                    "year": 1999,
                    "plot": "Sci-fi",
                    "extra": "Test",
                },
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
    def test_create_genre_uses_merge_with_name(
        self,
        _mock_load_dotenv: MagicMock,
        mock_driver_factory: MagicMock,
    ) -> None:
        mock_driver_factory.return_value = MagicMock()
        manager = Neo4jManager()

        with patch.object(manager, "_run_write_query") as mock_run_write_query:
            manager.create_genre(name="Action")

        query = mock_run_write_query.call_args.args[0]
        self.assertIn("MERGE (genre:Genre {name: $name})", query)
        self.assertEqual(mock_run_write_query.call_args.kwargs, {"name": "Action"})

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
    def test_create_person_merges_by_tmdb_id_and_includes_born(
        self,
        _mock_load_dotenv: MagicMock,
        mock_driver_factory: MagicMock,
    ) -> None:
        mock_driver_factory.return_value = MagicMock()
        manager = Neo4jManager()

        with patch.object(manager, "_run_write_query") as mock_run_write_query:
            manager.create_person(
                name="Keanu Reeves",
                tmdb_id="p1",
                born=1964,
                nationality="Canadian",
            )

        query = mock_run_write_query.call_args.args[0]
        self.assertIn("MERGE (person:Person {tmdbId: $tmdb_id})", query)
        self.assertEqual(
            mock_run_write_query.call_args.kwargs,
            {
                "tmdb_id": "p1",
                "properties": {
                    "name": "Keanu Reeves",
                    "tmdbId": "p1",
                    "born": 1964,
                    "nationality": "Canadian",
                },
            },
        )


if __name__ == "__main__":
    unittest.main()
