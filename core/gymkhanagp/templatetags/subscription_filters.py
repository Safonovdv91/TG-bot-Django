from django import template

register = template.Library()


@register.filter(name="is_subscribed")
def is_subscribed(competition_type, user_subscriptions):
    "Фильтр проверяющий подписан ли пользователь на данный тип соревнований"
    return any(ct_id == competition_type.id for ct_id, _ in user_subscriptions)


@register.filter(name="is_subscribed_class")
def is_subscribed_class(sport_class, user_subscriptions):
    "Фильтр проверяющий подписан ли пользователь на данный класс спортсмена"

    return any(sc_id_ == sport_class.id for _, sc_id_ in user_subscriptions)
