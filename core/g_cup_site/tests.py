from unittest.mock import MagicMock, patch

import pytest
from g_cup_site.utils import APIGetter, TypeChampionship


@pytest.mark.django_db
class TestAPIGetterGetDataChampionship:
    """Тесты для класса APIGetter."""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.api = APIGetter()

    @patch("g_cup_site.utils.httpx.get")
    def test_get_data_championships_success(self, mock_get):
        """Тест успешного получения данных о чемпионатах.
        status:200

            "id": "int", // ID чемпионата
            "title": "string", //Название чемпионата
            "year": "string", //Год проведения чемионата
            "description": "html", //Описание чемпионата
            "stagesCount": "int", //Количество этапов
            "type": "string" //Тип чемпионата, одно из значений: online, offline, gp

        """
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

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_get.return_value = mock_response

        result = self.api.get_data_championships(TypeChampionship.GGP)

        assert result == mock_response_data
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

    @pytest.mark.parametrize("error_code", [500, 501, 502, 505])
    @patch("g_cup_site.utils.logger")
    @patch("g_cup_site.utils.httpx.get")
    def test_get_data_championships_50x_error(self, mock_get, mock_logger, error_code):
        mock_response = MagicMock()
        mock_response.status_code = error_code
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        result = self.api.get_data_championships(champ_type=TypeChampionship.GGP)

        mock_logger.warning.assert_called_once()
        assert result == {}


@pytest.mark.django_db
class TestAPIGetterGetDataChampionshipById:
    """Тесты для класса APIGetter."""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.api = APIGetter()

    def test_get_data_championships_by_id_success(self):
        """Тест успешного получения данных о чемпионате по ID."""
        mock_response_data = {
            "id": 1,
            "title": "Тестовый чемпионат",
            "type": "gp",
            "year": 2024,
            "stages": [],
        }

        with patch("g_cup_site.utils.httpx.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_get.return_value = mock_response

            result = self.api.get_data_championships_by_id(1, "gp")

            assert result == mock_response_data
            mock_get.assert_called_once()

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
