from django.contrib.auth.models import User


def user_slots(request):
    hay_normales = User.objects.filter(is_staff=False, is_superuser=False).exists()
    hay_admins = User.objects.filter(is_staff=True).exists()
    return {
        'hay_normales': hay_normales,
        'hay_admins': hay_admins,
        'registro_disponible': not (hay_normales and hay_admins),
    }
