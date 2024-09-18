from starlette.middleware.base import BaseHTTPMiddleware

class AddPermissionsPolicyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Permissions-Policy"] = "browsing-topics, private-state-token-redemption, private-state-token-issuance"
        return response
