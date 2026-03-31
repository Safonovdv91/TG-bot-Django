import pytest

from users.utils import get_telegram_id, get_user_by_telegram_id


@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.asyncio
class TestGetTelegramId:
    """
    Тесты для функции get_telegram_id().

    Проверяют корректность получения Telegram ID пользователя
    из связанного SocialAccount.
    """

    async def test_telegram_user_id_success(self, django_user_with_telegram):
        """
        Тест успешного получения Telegram ID.

        Проверяет, что для пользователя с привязанным Telegram аккаунтом
        функция возвращает корректный ID из extra_data.
        """
        # Arrange
        user = django_user_with_telegram

        # Act
        user_id: int | None = get_telegram_id(user)

        # Assert
        assert user_id == 189000981

    @pytest.mark.parametrize(
        "value",
        [
            ("smth_string"),  # Строка вместо объекта User
            ([]),  # Пустой список
            ({122: 23}),  # Словарь
        ],
    )
    async def test_telegram_user_id_bad_value_raises_value_error(self, value):
        """
        Тест передачи некорректного типа данных.

        Проверяет, что функция выбрасывает ValueError при передаче
        объектов, не являющихся экземплярами User модели.

        Параметризовано для проверки различных типов:
        - строка
        - список
        - словарь
        """
        # Act & Assert
        with pytest.raises(ValueError):
            get_telegram_id(value)

    async def test_telegram_user_id_user_has_no_telegram(self, django_user):
        """
        Тест для пользователя без привязанного Telegram аккаунта.

        Проверяет, что функция возвращает None, если у пользователя
        нет связанного SocialAccount с provider="telegram".
        """
        # Arrange
        user = django_user

        # Act
        user_id: int | None = get_telegram_id(user)

        # Assert
        assert user_id is None

    async def test_telegram_user_id_none_input(self):
        """
        Тест передачи None в качестве аргумента.

        Проверяет, что функция корректно обрабатывает None
        и возвращает None без выбрасывания исключений.
        """
        # Act
        user_id: int | None = get_telegram_id(None)

        # Assert
        assert user_id is None


@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.asyncio
class TestGetTelegramUserById:
    """
    Тесты для функции get_user_by_telegram_id().

    Проверяют корректность получения объекта пользователя
    по его Telegram ID через связь с SocialAccount.
    """

    @pytest.mark.parametrize(
        "value",
        [
            189000981,  # Целочисленный Telegram ID
            ("189000981"),  # Строковый Telegram ID
        ],
    )
    async def test_telegram_user_by_id_success(self, value, django_user_with_telegram):
        """
        Тест успешного получения пользователя по Telegram ID.

        Проверяет, что функция корректно находит пользователя
        как по числовому, так и по строковому представлению ID.

        Параметризовано для проверки:
        - int тип (нативный формат Telegram ID)
        - str тип (часто встречается при обработке данных из бота)
        """
        # Arrange
        expected_user = django_user_with_telegram

        # Act
        get_user = get_user_by_telegram_id(value)

        # Assert
        assert get_user == expected_user

    @pytest.mark.parametrize(
        "value",
        [
            None,  # None значение
            "",  # Пустая строка
            666666666,  # Несуществующий ID (больше максимального в БД)
            -1,  # Отрицательное число
            1_000_000_000_000_000_000_000,  # Чрезмерно большое число
        ],
    )
    async def test_telegram_user_by_id_returns_none_for_invalid_or_not_found(
        self, value, django_user_with_telegram
    ):
        """
        Тест возврата None для невалидных или несуществующих ID.

        Проверяет, что функция возвращает None в случаях:
        - Передан None
        - Передана пустая строка (не конвертируется в int)
        - ID не найден в базе данных
        - Отрицательный ID (некорректное значение)
        - Чрезмерно большой ID (выходит за рамки разумного)

        Примечание: django_user_with_telegram используется для создания
        контекста БД, но тест проверяет поиск других/несуществующих ID.
        """
        # Act
        get_user = get_user_by_telegram_id(value)

        # Assert
        assert get_user is None

    async def test_telegram_user_by_id_invalid_type_raises_value_error(self):
        """
        Тест передачи некорректного типа данных.

        Проверяет, что функция выбрасывает ValueError при передаче
        типов, отличных от int, str или None (списки, словари, объекты).
        """
        # Act & Assert
        with pytest.raises(ValueError):
            get_user_by_telegram_id([])

    async def test_telegram_user_by_id_invalid_type_dict_raises_value_error(self):
        """
        Тест передачи словаря в качестве telegram_id.

        Дополнительный тест для проверки обработки словарей.
        """
        # Act & Assert
        with pytest.raises(ValueError):
            get_user_by_telegram_id({"id": 123456})

    async def test_telegram_user_by_id_invalid_type_float_raises_value_error(self):
        """
        Тест передачи float в качестве telegram_id.

        Проверяет, что float значения (даже целочисленные)
        вызывают ValueError, так как ожидаются только int или str.
        """
        # Act & Assert
        with pytest.raises(ValueError):
            get_user_by_telegram_id(123456.0)
