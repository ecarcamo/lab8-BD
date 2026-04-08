import io
import importlib
import sys
import unittest
from contextlib import redirect_stdout
from types import ModuleType
from unittest.mock import MagicMock, patch


def load_main_module():
    dotenv_module = ModuleType("dotenv")
    dotenv_module.load_dotenv = MagicMock()
    sys.modules["dotenv"] = dotenv_module

    neo4j_module = ModuleType("neo4j")
    neo4j_module.GraphDatabase = MagicMock()
    sys.modules["neo4j"] = neo4j_module

    if "main" in sys.modules:
        return importlib.reload(sys.modules["main"])
    return importlib.import_module("main")


main_module = load_main_module()
Neo4jManager = main_module.Neo4jManager
main = main_module.main


class TestNeo4jManager(unittest.TestCase):
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
    def test_create_driver_uses_env_values(
        self,
        mock_load_dotenv: MagicMock,
        mock_driver_factory: MagicMock,
    ) -> None:
        fake_driver = MagicMock()
        mock_driver_factory.return_value = fake_driver

        manager = Neo4jManager()

        mock_load_dotenv.assert_called_once()
        mock_driver_factory.assert_called_once_with(
            "neo4j+s://example.databases.neo4j.io",
            auth=("neo4j", "secret"),
        )
        self.assertIs(manager.driver, fake_driver)

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
    def test_open_session_uses_database_from_env(
        self,
        _mock_load_dotenv: MagicMock,
        mock_driver_factory: MagicMock,
    ) -> None:
        fake_driver = MagicMock()
        fake_session = MagicMock()
        fake_driver.session.return_value = fake_session
        mock_driver_factory.return_value = fake_driver

        manager = Neo4jManager()
        session = manager.open_session()

        fake_driver.session.assert_called_once_with(database="example-db")
        self.assertIs(session, fake_session)

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
    def test_execute_test_query_returns_expected_data(
        self,
        _mock_load_dotenv: MagicMock,
        mock_driver_factory: MagicMock,
    ) -> None:
        mock_driver_factory.return_value = MagicMock()
        manager = Neo4jManager()
        session = MagicMock()
        session.run.return_value.single.return_value = {
            "number": 1,
            "message": "Conexion exitosa con Neo4j",
        }

        result = manager.execute_test_query(session)

        self.assertEqual(
            result,
            {
                "number": 1,
                "message": "Conexion exitosa con Neo4j",
            },
        )
        session.run.assert_called_once()

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
    def test_execute_test_query_raises_when_no_record(
        self,
        _mock_load_dotenv: MagicMock,
        mock_driver_factory: MagicMock,
    ) -> None:
        mock_driver_factory.return_value = MagicMock()
        manager = Neo4jManager()
        session = MagicMock()
        session.run.return_value.single.return_value = None

        with self.assertRaises(RuntimeError):
            manager.execute_test_query(session)

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
    def test_print_result_writes_expected_output(
        self,
        _mock_load_dotenv: MagicMock,
        mock_driver_factory: MagicMock,
    ) -> None:
        mock_driver_factory.return_value = MagicMock()
        manager = Neo4jManager()
        buffer = io.StringIO()

        with redirect_stdout(buffer):
            manager.print_result(
                {
                    "number": 1,
                    "message": "Conexion exitosa con Neo4j",
                }
            )

        self.assertEqual(
            buffer.getvalue(),
            "Numero: 1\nMensaje: Conexion exitosa con Neo4j\n",
        )

    @patch("main.GraphDatabase.driver")
    @patch("main.load_dotenv")
    @patch.dict("os.environ", {}, clear=True)
    def test_init_raises_when_env_var_is_missing(
        self,
        _mock_load_dotenv: MagicMock,
        _mock_driver_factory: MagicMock,
    ) -> None:
        with self.assertRaises(ValueError):
            Neo4jManager()


class TestMainFunction(unittest.TestCase):
    @patch("main.Neo4jManager")
    def test_main_closes_session_and_driver(self, mock_manager_class: MagicMock) -> None:
        fake_manager = MagicMock()
        fake_session = MagicMock()
        fake_manager.open_session.return_value = fake_session
        fake_manager.execute_test_query.return_value = {
            "number": 1,
            "message": "Conexion exitosa con Neo4j",
        }
        mock_manager_class.return_value = fake_manager

        main()

        fake_manager.open_session.assert_called_once()
        fake_manager.execute_test_query.assert_called_once_with(fake_session)
        fake_manager.print_result.assert_called_once_with(
            {
                "number": 1,
                "message": "Conexion exitosa con Neo4j",
            }
        )
        fake_session.close.assert_called_once()
        fake_manager.close_driver.assert_called_once()


if __name__ == "__main__":
    unittest.main()
