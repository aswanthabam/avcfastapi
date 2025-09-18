from fastapi import Request


async def get_client_ip(request: Request):
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        # X-Forwarded-For can be a list of IPs. Take the first one (the original client).
        ip = forwarded_for.split(",")[0].strip()
    else:
        ip = request.client.host if request.client else None
    return ip
