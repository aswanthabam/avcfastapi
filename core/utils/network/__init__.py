import ipaddress
from fastapi import Request


async def get_client_ip(request: Request):
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        ip = forwarded_for.split(",")[0].strip()
    else:
        ip = request.client.host if request.client else None

    # Normalize to IPv4 if possible
    try:
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj.version == 6 and ip_obj.ipv4_mapped:
            ip = str(ip_obj.ipv4_mapped)
    except ValueError:
        pass  # not a valid IP, just return as-is

    return ip
