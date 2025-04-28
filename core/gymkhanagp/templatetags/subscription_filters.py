from django import template

register = template.Library()


@register.filter(name="is_subscribed")
def is_subscribed(competition_type, user_subscriptions):
    "Фильтр проверяющий подписан ли пользователь на данный тип соревнований, усли хоть один тип то True"
    return any(ct_id == competition_type.id for ct_id, _ in user_subscriptions)


@register.filter(name="is_subscribed_class")
def is_subscribed_class(sport_class, user_subscriptions):
    """
    Фильтр проверяющий подписан ли пользователь на данный класс.
    В данный момент проверка проводится для ggp, поэтому в запросе отправляется запрос с параметром competition_type=1

    :param sport_class:
    :param user_subscriptions:
    :return:
    """
    competition_type_id = 1
    for sc_id_, _ in user_subscriptions:
        if sc_id_ == sport_class.id and _ == competition_type_id:
            return True
    return False
