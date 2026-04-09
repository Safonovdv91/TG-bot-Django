from unittest.mock import MagicMock, patch

import pytest
from g_cup_site.utils import APIGetter, TypeChampionship
from httpx import NetworkError


@pytest.mark.django_db
class TestAPIGetterMakeRequest:
    """Тесты для класса APIGetter. Получение совершение запроса"""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.api = APIGetter()

    @patch("g_cup_site.utils.httpx.get")
    def test_make_request_success(self, mock_get):
        """Тест что метод работает и возвращает 200"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "test_data"}

        mock_get.return_value = mock_response

        result = self.api._make_request("some_http.ru", {"key": "test_key"})
        mock_get.assert_called_once()
        assert result.get("test") == "test_data"

    @pytest.mark.parametrize("status_code", [400, 401, 404])
    @patch("g_cup_site.utils.AdminNotifier")
    @patch("g_cup_site.utils.logger")
    @patch("g_cup_site.utils.httpx.get")
    def test_make_request_return_4xx_status_code(
        self, mock_get, mock_logger, mock_admin_notifier, status_code
    ):
        """Тест что при 4xx ошибке пишется лог и уведомляется админ"""
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = {"test": "test_data"}

        mock_get.return_value = mock_response

        result = self.api._make_request("/endpoint", {"key": "test_key"})

        mock_get.assert_called_once()
        mock_admin_notifier.notify_admin.assert_called_once()
        mock_logger.error.assert_called_once()

        assert result == {}

    @pytest.mark.parametrize("status_code", [500, 505, 503])
    @patch("g_cup_site.utils.logger")
    @patch("g_cup_site.utils.httpx.get")
    def test_make_request_return_5xx_status_code(
        self, mock_get, mock_logger, status_code
    ):
        """Тест что метод работает и возвращает 500-599"""
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = {"test": "test_data"}

        mock_get.return_value = mock_response

        result = self.api._make_request("some_http.ru", {"key": "test_key"})
        mock_get.assert_called_once()
        mock_logger.warning.assert_called_once()

        assert result == {}

    @pytest.mark.parametrize("httpx_error", [TimeoutError, NetworkError])
    @patch("g_cup_site.utils.logger")
    @patch("g_cup_site.utils.httpx.get")
    def test__make_request_timeout_error(self, mock_get, mock_logger, httpx_error):
        """Тест получения ошибки соединения от httpx."""

        mock_get.side_effect = MagicMock(side_effect=httpx_error)

        result = self.api.get_data_championships(champ_type=TypeChampionship.GGP)

        mock_logger.exception.assert_called_once()
        assert result == {}

    @patch("g_cup_site.utils.logger")
    def test_make_request_url_is_none(self, mock_logger):
        """Тест что при отсутствии URL возвращается пустой dict и пишется ошибка."""
        api = APIGetter()
        api.url = None

        result = api._make_request("/endpoint", {"key": "value"})

        assert result == {}
        mock_logger.error.assert_called_once()

    @patch("g_cup_site.utils.httpx.get")
    def test_make_request_json_parse_error(self, mock_get):
        """Тест что при ошибке парсинга JSON в теле ответа возвращается пустой dict."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = "<html>Error page</html>"

        mock_get.return_value = mock_response

        result = self.api._make_request("/endpoint", {})

        assert result == {}

    @patch("g_cup_site.utils.AdminNotifier")
    @patch("g_cup_site.utils.logger")
    @patch("g_cup_site.utils.httpx.get")
    def test_make_request_5xx_notifies_admin(
        self, mock_get, mock_logger, mock_admin_notifier
    ):
        """Тест что при 5xx ошибке админ получает уведомление."""
        mock_response = MagicMock()
        mock_response.status_code = 502
        mock_response.json.return_value = {"error": "Bad Gateway"}

        mock_get.return_value = mock_response

        result = self.api._make_request("/endpoint", {})

        assert result == {}
        mock_admin_notifier.notify_admin.assert_called_once()
        mock_logger.warning.assert_called_once()

    @patch("g_cup_site.utils.httpx.get")
    def test_make_request_passes_timeout(self, mock_get):
        """Тест что таймаут передаётся в httpx.get."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True}

        mock_get.return_value = mock_response

        self.api._make_request("/endpoint", {})

        _, kwargs = mock_get.call_args
        assert kwargs["timeout"] == 30.0


@pytest.mark.django_db
class TestAPIGetterGetDataChampionship:
    """Тесты для класса APIGetter. Получение данных о чемпионатах"""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.api = APIGetter()

    @patch.object(APIGetter, "_make_request")
    def test_get_data_championships_success(self, mock_make_request):
        """Тест успешного получения данных о чемпионатах."""
        mock_response_data = {
            "championships": [
                {
                    "id": 1,
                    "title": "Тестовый чемпионат",
                    "description": "html",
                    "stagesCount": 3,
                    "type": "gp",
                    "year": 2024,
                }
            ]
        }

        mock_make_request.return_value = mock_response_data

        result = self.api.get_data_championships(TypeChampionship.GGP)

        assert result == mock_response_data
        mock_make_request.assert_called_once_with(
            "/championships/list",
            {"types": TypeChampionship.GGP, "fromYear": None, "toYear": None},
        )

    @patch.object(APIGetter, "_make_request")
    def test_get_data_championships_with_years(self, mock_make_request):
        """Тест получения данных о чемпионатах с указанием годов."""
        mock_make_request.return_value = {"championships": []}

        result = self.api.get_data_championships(
            TypeChampionship.GGP, from_year=2023, to_year=2024
        )

        mock_make_request.assert_called_once_with(
            "/championships/list",
            {"types": TypeChampionship.GGP, "fromYear": 2023, "toYear": 2024},
        )
        assert result == {"championships": []}

    @patch.object(APIGetter, "_make_request")
    def test_get_data_championships_returns_empty_on_error(self, mock_make_request):
        """Тест что при ошибке возвращается пустой dict."""
        mock_make_request.return_value = {}

        result = self.api.get_data_championships(TypeChampionship.GGP)

        assert result == {}


@pytest.mark.django_db
class TestAPIGetterGetDataChampionshipById:
    """Тесты для класса APIGetter. Получение данных о определенном чемпионате"""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.api = APIGetter()
        self.mock_response_data = {
            "id": 23,
            "title": "champ test",
            "year": 2026,
            "description": "<html>Some html code</html>",
            "stages": [
                {
                    "id": 12,
                    "status": "string",
                    "title": "string",
                    "description": "html",
                    "usersCount": 24,
                    "class": "string",
                    "trackUrl": "http://test_url.com",
                    "dateStart": 12231123,
                    "dateEnd": 42131231,
                    "referenceTimeSeconds": 123012,
                    "referenceTime": "string",
                    "bestTimeSeconds": 421312,
                    "bestTime": "string",
                    "bestUserId": "int",
                    "bestUserFirstName": "John",
                    "bestUserLastname": "Salivan",
                    "bestUserFullName": "John Salivan",
                    "bestUserCity": "Smolensk",
                }
            ],
        }

    @patch.object(APIGetter, "_make_request")
    def test_get_data_championships_by_id_success(self, mock_make_request):
        """Тест успешного получения данных о чемпионате по ID."""
        mock_make_request.return_value = self.mock_response_data

        result = self.api.get_data_championships_by_id(23, "gp")

        assert result == self.mock_response_data
        mock_make_request.assert_called_once_with(
            "/championships/get", {"id": 23, "type": "gp"}
        )

    @patch.object(APIGetter, "_make_request")
    def test_get_data_championships_by_id_default_type(self, mock_make_request):
        """Тест что по умолчанию используется тип GGP."""
        mock_make_request.return_value = {"id": 1}

        self.api.get_data_championships_by_id(5)

        mock_make_request.assert_called_once_with(
            "/championships/get", {"id": 5, "type": TypeChampionship.GGP}
        )

    @patch.object(APIGetter, "_make_request")
    def test_get_data_championships_by_id_returns_empty_on_error(
        self, mock_make_request
    ):
        """Тест что при ошибке возвращается пустой dict."""
        mock_make_request.return_value = {}

        result = self.api.get_data_championships_by_id(999)

        assert result == {}


@pytest.mark.django_db
class TestAPIGetterDataStage:
    """Тесты для метода data_stage. Получение данных об этапе"""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.api = APIGetter()

    @patch.object(APIGetter, "_make_request")
    def test_data_stage_success(self, mock_make_request):
        """Тест успешного получения данных об этапе."""
        mock_response_data = {
            "id": 1,
            "title": "Тестовый этап",
            "type": "gp",
            "results": [],
        }
        mock_make_request.return_value = mock_response_data

        result = self.api.data_stage(1, "gp")

        assert result == mock_response_data
        mock_make_request.assert_called_once_with(
            "/stages/get", {"id": 1, "type": "gp"}
        )

    @patch.object(APIGetter, "_make_request")
    def test_data_stage_with_base_type(self, mock_make_request):
        """Тест запроса с типом base."""
        mock_make_request.return_value = {"id": 5, "type": "base"}

        result = self.api.data_stage(5, "base")

        assert result == {"id": 5, "type": "base"}
        mock_make_request.assert_called_once_with(
            "/stages/get", {"id": 5, "type": "base"}
        )

    @patch.object(APIGetter, "_make_request")
    def test_data_stage_with_results(self, mock_make_request):
        """Тест получения данных с результатами."""
        mock_response_data = {
            "id": 10,
            "title": "Этап с результатами",
            "type": "gp",
            "results": [
                {
                    "userId": 1,
                    "userFirstName": "Иван",
                    "userLastName": "Иванов",
                    "motorcycle": "Honda",
                    "resultTimeSeconds": 12345,
                    "resultTime": "0:12.345",
                    "place": 1,
                    "percent": 100,
                }
            ],
        }
        mock_make_request.return_value = mock_response_data

        result = self.api.data_stage(10, "gp")

        assert len(result["results"]) == 1
        assert result["results"][0]["place"] == 1

    @patch.object(APIGetter, "_make_request")
    def test_data_stage_returns_empty_on_4xx_error(self, mock_make_request):
        """Тест что при 4xx ошибке возвращается пустой dict."""
        mock_make_request.return_value = {}

        result = self.api.data_stage(999, "gp")

        assert result == {}

    @patch.object(APIGetter, "_make_request")
    def test_data_stage_returns_empty_on_5xx_error(self, mock_make_request):
        """Тест что при 5xx ошибке возвращается пустой dict."""
        mock_make_request.return_value = {}

        result = self.api.data_stage(999, "gp")

        assert result == {}

    @patch.object(APIGetter, "_make_request")
    def test_data_stage_returns_empty_on_network_error(self, mock_make_request):
        """Тест что при сетевой ошибке возвращается пустой dict."""
        mock_make_request.return_value = {}

        result = self.api.data_stage(1, "gp")

        assert result == {}

    @patch.object(APIGetter, "_make_request")
    def test_data_stage_empty_results(self, mock_make_request):
        """Тест этапа без результатов."""
        mock_make_request.return_value = {"id": 1, "results": []}

        result = self.api.data_stage(1, "gp")

        assert result["results"] == []


@pytest.mark.django_db
class TestAPIGetterGetFigureData:
    """Тесты для метода get_figure_data. Получение данных по фигуре"""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.api = APIGetter()

    @patch.object(APIGetter, "_make_request")
    def test_get_figure_data_success(self, mock_make_request):
        """Тест успешного получения данных о фигуре."""
        mock_response_data = {
            "id": 1,
            "title": "Тестовая фигура",
            "description": "Описание фигуры",
            "track": "Трек",
            "withIncClass": True,
        }
        mock_make_request.return_value = mock_response_data

        result = self.api.get_figure_data(1)

        assert result == mock_response_data
        mock_make_request.assert_called_once_with("/figures/get", {"id": 1})

    @patch.object(APIGetter, "_make_request")
    def test_get_figure_data_with_all_fields(self, mock_make_request):
        """Тест получения фигуры со всеми полями."""
        mock_response_data = {
            "id": 42,
            "title": "Восьмёрка",
            "description": "<p>Фигура типа восьмёрка</p>",
            "track": "http://example.com/track.jpg",
            "withIncClass": False,
        }
        mock_make_request.return_value = mock_response_data

        result = self.api.get_figure_data(42)

        assert result["id"] == 42
        assert result["title"] == "Восьмёрка"
        assert result["withIncClass"] is False

    @patch.object(APIGetter, "_make_request")
    def test_get_figure_data_returns_empty_on_4xx_error(self, mock_make_request):
        """Тест что при 4xx ошибке возвращается пустой dict."""
        mock_make_request.return_value = {}

        result = self.api.get_figure_data(999)

        assert result == {}

    @patch.object(APIGetter, "_make_request")
    def test_get_figure_data_returns_empty_on_5xx_error(self, mock_make_request):
        """Тест что при 5xx ошибке возвращается пустой dict."""
        mock_make_request.return_value = {}

        result = self.api.get_figure_data(1)

        assert result == {}

    @patch.object(APIGetter, "_make_request")
    def test_get_figure_data_returns_empty_on_network_error(self, mock_make_request):
        """Тест что при сетевой ошибке возвращается пустой dict."""
        mock_make_request.return_value = {}

        result = self.api.get_figure_data(1)

        assert result == {}


@pytest.mark.django_db
class TestAPIGetterGetAthleteData:
    """Тесты для метода get_athlete_data. Получение данных по спортсмену"""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.api = APIGetter()

    @patch.object(APIGetter, "_make_request")
    def test_get_athlete_data_success(self, mock_make_request):
        """Тест успешного получения данных о спортсмене."""
        mock_response_data = {
            "id": 1,
            "firstName": "Иван",
            "lastName": "Иванов",
            "userCity": "Москва",
            "userCountry": "Россия",
            "class": "N",
        }
        mock_make_request.return_value = mock_response_data

        result = self.api.get_athlete_data(1)

        assert result == mock_response_data
        mock_make_request.assert_called_once_with("/users/get", {"id": 1})

    @patch.object(APIGetter, "_make_request")
    def test_get_athlete_data_with_full_info(self, mock_make_request):
        """Тест получения спортсмена с полной информацией."""
        mock_response_data = {
            "id": 42,
            "firstName": "Алексей",
            "lastName": "Петров",
            "userCity": "Санкт-Петербург",
            "userCountry": "Россия",
            "class": "A",
            "motorcycle": "KTM",
        }
        mock_make_request.return_value = mock_response_data

        result = self.api.get_athlete_data(42)

        assert result["firstName"] == "Алексей"
        assert result["lastName"] == "Петров"
        assert result["class"] == "A"
        assert result["motorcycle"] == "KTM"

    @patch.object(APIGetter, "_make_request")
    def test_get_athlete_data_minimal_info(self, mock_make_request):
        """Тест получения спортсмена с минимальной информацией."""
        mock_response_data = {
            "id": 7,
            "firstName": "John",
            "lastName": "Doe",
        }
        mock_make_request.return_value = mock_response_data

        result = self.api.get_athlete_data(7)

        assert result["id"] == 7
        assert "userCity" not in result

    @patch.object(APIGetter, "_make_request")
    def test_get_athlete_data_returns_empty_on_4xx_error(self, mock_make_request):
        """Тест что при 4xx ошибке возвращается пустой dict."""
        mock_make_request.return_value = {}

        result = self.api.get_athlete_data(999)

        assert result == {}

    @patch.object(APIGetter, "_make_request")
    def test_get_athlete_data_returns_empty_on_5xx_error(self, mock_make_request):
        """Тест что при 5xx ошибке возвращается пустой dict."""
        mock_make_request.return_value = {}

        result = self.api.get_athlete_data(1)

        assert result == {}

    @patch.object(APIGetter, "_make_request")
    def test_get_athlete_data_returns_empty_on_network_error(self, mock_make_request):
        """Тест что при сетевой ошибке возвращается пустой dict."""
        mock_make_request.return_value = {}

        result = self.api.get_athlete_data(1)

        assert result == {}
