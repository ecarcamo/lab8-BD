from main import Neo4jManager

# prints y busqueda 

from main import Neo4jManager


def main():
    manager = Neo4jManager()

    try:

        print("Mostrar todos los usuarios:")
        users = manager.find_all_users()
        for user in users:
            manager.print_user(user)

        print("\nMostrar todas las películas:")
        movies = manager.find_all_movies()
        for movie in movies:
            manager.print_movie(movie)

        print("\n--- BUSCAR USUARIO ---")
        user_name = input("Ingrese el nombre del usuario: ")
        user = manager.find_user(user_name)
        manager.print_user(user)

        print("\n--- BUSCAR PELÍCULA POR TITULO ---")
        movie_title = input("Ingrese el título de la película: ")
        movie = manager.find_movie(movie_title)
        manager.print_movie(movie)

        print("\n--- BUSCAR RELACIÓN RATED ---")
        user_name = input("Ingrese el nombre del usuario: ")
        movie_title = input("Ingrese el título de la película: ")
        result = manager.find_user_movie_rating(user_name, movie_title)
        manager.print_user_movie_rating(result)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        manager.close_driver()


if __name__ == "__main__":
    main()