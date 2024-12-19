import datetime

import django.conf
import django.utils
import django.utils.timesince
import django.utils.timezone
import jwt

__all__ = ()


def make_token(user, expiration_time=False, operation="activate"):
    if not expiration_time:
        expiration_time = django.utils.timezone.now() + datetime.timedelta(
            hours=12,
        )

    payload = {
        "user_id": user.pk,
        "exp": expiration_time,
        "operation": operation,
    }
    return jwt.encode(
        payload,
        django.conf.settings.SECRET_KEY,
        algorithm="HS256",
    )


def check_token(token):
    try:
        decoded = jwt.decode(
            token,
            django.conf.settings.SECRET_KEY,
            algorithms=["HS256"],
        )
        decoded["status"] = "valid"

        return decoded
    except jwt.ExpiredSignatureError:
        payload = jwt.decode(
            token,
            django.conf.settings.SECRET_KEY,
            algorithms=["HS256"],
            options={"verify_exp": False},
        )
        payload["status"] = "expired"
        return payload
    except jwt.InvalidTokenError:
        return False
