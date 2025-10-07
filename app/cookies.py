from fastapi.responses import JSONResponse

REFRESH_COOKIE_NAME = "refresh_token"
SECURE_COOKIES = False
REFRESH_COOKIE_MAX_AGE = 30 * 24 * 3600  # 30 dni


def set_refresh_cookie(resp: JSONResponse, token: str):
    resp.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=SECURE_COOKIES,
        samesite="lax",
        max_age=REFRESH_COOKIE_MAX_AGE,
        path="/refresh",
    )


def delete_refresh_cookie(resp: JSONResponse):
    resp.delete_cookie(REFRESH_COOKIE_NAME, path="/refresh")
