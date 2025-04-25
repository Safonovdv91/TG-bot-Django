from django import template

register = template.Library()


@register.filter(name="is_subscribed")
def is_subscribed(competition_type, user_subscriptions):
    """
    Проверяет, подписан ли пользователь на данный тип соревнований
    user_subscriptions - множество кортежей (competition_type_id, sportsman_class_id)
    """
    return any(ct_id == competition_type.id for ct_id, _ in user_subscriptions)
