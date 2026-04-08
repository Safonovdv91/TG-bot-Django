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
        """Тест что метод пишет в логгер уведомление о ошибке и уведомляет администратора о возникшей ошибке"""
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = {"test": "test_data"}

        mock_get.return_value = mock_response

        result = self.api._make_request("some_http.ru", {"key": "test_key"})

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
    """Тесты для класса APIGetter. Получение данных о определенном чампионате"""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.api = APIGetter()
        self.mock_response_data = {
            "id": 23,  # ID чемпионата
            "title": "champ test",  #  Название чемпионата
            "year": 2026,  # Год проведения чемпионата
            "description": "<html>Some html code</html>",  # Описание чемпионата
            "stages": [  # //Инфомация об этапах
                {
                    "id": 12,  # ID этапа
                    "status": "string",  # Статус этапа. Возможные значения: Предстоящий этап, Приём результатов, Подведение итогов, Прошедший этап, Этап отменён
                    "title": "string",  # Название этапа
                    "description": "html",  # Описание этапа
                    "usersCount": 24,  # Количество активных участников
                    "class": "string",  # Класс этапа. Возможные значения: A, B, C1, C2, C3, D1, D2, D3, D4, N
                    "trackUrl": "http://test_url.com",  # Ссылка на фото трассы
                    "dateStart": 12231123,  # Дата начала этапа в формате unixtime
                    "dateEnd": 42131231,  # Дата начала этапа в формате unixtime
                    "referenceTimeSeconds": 123012,  # Эталонное время в миллисекундах
                    "referenceTime": "string",  # Эталонное время в формате "мин:сек.мсек"
                    "bestTimeSeconds": 421312,  #  Лучшее время в миллисекундах
                    "bestTime": "string",  #  Лучшее время в формате "мин:сек.мсек"
                    "bestUserId": "int",  # ID спортсмена, показавшего лучший результат
                    "bestUserFirstName": "John",  # Имя спортсмена, показавшего лучший результат
                    "bestUserLastname": "Salivan",  # Фамилия спортсмена, показавшего лучший результат
                    "bestUserFullName": "John Salivan",  # Полное имя спортсмена, показавшего лучший результат
                    "bestUserCity": "Smolensk",  # Город спортсмена, показавшего лучший результат
                }
            ],
        }

    @patch("g_cup_site.utils.httpx.get")
    def test_get_data_championships_by_id_success(self, mock_get):
        """Тест успешного получения данных о чемпионате по ID."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_response_data
        mock_get.return_value = mock_response

        result = self.api.get_data_championships_by_id(1, "gp")

        assert result == self.mock_response_data
        mock_get.assert_called_once()

    @pytest.mark.parametrize("error_code", [400, 401, 403, 404])
    @patch("g_cup_site.utils.logger")
    @patch("g_cup_site.utils.httpx.get")
    def test_get_data_championships_40x_error(self, mock_get, mock_logger, error_code):
        mock_response = MagicMock()
        mock_response.status_code = error_code
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        result = self.api.get_data_championships(champ_type=TypeChampionship.GGP)

        mock_logger.error.assert_called_once()
        assert result == {}


@pytest.mark.django_db
class TestAPIGetterGetDataStageGGP:
    """Тесты для класса APIGetter. Получение данных о данных этапа GGP"""

    def test_data_stage_success(self):
        """Тест успешного получения данных об этапе."""
        mock_response_data = {
            "id": 1,
            "title": "Тестовый этап",
            "type": "gp",
            "results": [],
        }

        with patch("g_cup_site.utils.httpx.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_get.return_value = mock_response

            result = self.api.data_stage(1, "gp")

            assert result == mock_response_data
            mock_get.assert_called_once()

    def test_get_figure_data_success(self):
        """Тест успешного получения данных о фигуре."""
        mock_response_data = {
            "id": 1,
            "title": "Тестовая фигура",
            "description": "Описание фигуры",
            "track": "Трек",
            "withIncClass": True,
        }

        with patch("g_cup_site.utils.httpx.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_get.return_value = mock_response

            result = self.api.get_figure_data(1)

            assert result == mock_response_data
            mock_get.assert_called_once()

    def test_get_athlete_data_success(self):
        """Тест успешного получения данных о спортсмене."""
        mock_response_data = {
            "id": 1,
            "firstName": "Иван",
            "lastName": "Иванов",
            "userCity": "Москва",
            "userCountry": "Россия",
            "class": "N",
        }

        with patch("g_cup_site.utils.httpx.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_get.return_value = mock_response

            result = self.api.get_athlete_data(1)

            assert result == mock_response_data
            mock_get.assert_called_once()
