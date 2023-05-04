from pathlib import Path

resources = Path(__file__).parent.parent / "resources"


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, email, psw):
        return self._client.post(
            "/api/login", json={"email": email, "psw": psw}
        )

    def logout(self):
        return self._client.post("/api/logout")


class MoviesActions(object):
    def __init__(self, client):
        self._client = client

    def create_movie(
        self, title, director, rate, year, genre_1, genre_2, genre_3
    ):
        return self._client.post(
            "/api/movies/movie_creation",
            query_string={
                "genre_1": genre_1,
                "genre_2": genre_2,
                "genre_3": genre_3,
            },
            json=(
                {
                    "title": title,
                    "director": director,
                    "rate": rate,
                    "year": year,
                }
            ),
        )

    def edit_movie(self, movie_id, query_string, json):
        return self._client.patch(
            f"/api/movies/{movie_id}", query_string=query_string, json=(json)
        )

    def delete_movie(self, movie_id):
        return self._client.delete(f"/api/movies/{movie_id}")

    def upload_poster(self, movie_id, file_part, file_name):
        return self._client.post(
            f"/api/movies/{movie_id}/poster",
            data={
                file_part: (open(resources / "poster.jpeg", "rb"), file_name)
            },
        )

    def delete_poster(self, movie_id):
        return self._client.delete(f"/api/movies/{movie_id}/poster")

    def search_movies(self, query_string):
        return self._client.get("/api/movies", query_string=query_string)

    def get_movie(self, movie_id):
        return self._client.get(f"/api/movies/{movie_id}")
