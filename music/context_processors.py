from django.core.exceptions import ObjectDoesNotExist

def auth_display(request):
    """
    Добавляет в каждый шаблон:
      - auth_display_name
      - auth_image
    Чтобы base.html не ломался на страницах, где view не передаёт эти переменные.
    """
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {"auth_display_name": "", "auth_image": ""}

    display_name = user.username
    image = ""

    try:
        profile = user.spotifyprofile
    except ObjectDoesNotExist:
        return {"auth_display_name": display_name, "auth_image": image}

    if getattr(profile, "display_name", ""):
        display_name = profile.display_name
    if getattr(profile, "image", ""):
        image = profile.image

    return {"auth_display_name": display_name, "auth_image": image}