from allauth.socialaccount.models import SocialAccount


def get_telegram_id(user) -> int | None:
    try:
        social_account = SocialAccount.objects.get(user=user, provider="telegram")
        return social_account.extra_data.get("id")
    except SocialAccount.DoesNotExist:
        return None
