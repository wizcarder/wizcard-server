from django.conf import settings


REDIRECT_FALLBACK_TO_PROFILE = getattr(settings,
                                       'CARDS_REDIRECT_FALLBACK_TO_PROFILE',
                                       False)
