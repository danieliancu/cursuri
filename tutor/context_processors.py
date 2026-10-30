from django.conf import settings


def pytutor(request):
    return {"allow_signup": settings.PYTUTOR_ALLOW_SIGNUP}
