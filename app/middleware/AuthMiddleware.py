from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

from app.schemas.UserSchema import UserResponse
from app.utils import verify_token


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.cookies.get("token")

        if request.url.path in ["/docs", "/redoc", "/openapi.json",

                                "/admins/sign-up",
                                "/admins/sign-in",

                                ] or request.url.path.startswith("/schedula") or request.url.path.startswith("/auth"):

            return await call_next(request)

        # Nếu không có token -> chặn luôn (401)
        if not token:
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication token is missing"}
            )

        # Có token nhưng verify fail -> chặn luôn (401 hoặc 403)
        try:
            payload = verify_token(token)
            request.state.user = payload
        except Exception:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired token"}
            )

        # Kiểm tra quyền admin nếu truy cập /admin/**
        if request.url.path.startswith("/admins/") and payload.get("role") != "admin":
            return JSONResponse(
                status_code=403,
                content={
                    "detail": "You do not have permission to access this resource"}
            )

        # OK -> cho phép vào route
        response = await call_next(request)
        return response
