from fastapi import HTTPException
import httpx


class GoogleAuthUtils:
    @staticmethod
    async def get_google_user_info(id_token: str) -> dict:
        url = "https://www.googleapis.com/oauth2/v1/userinfo"
        headers = {"Authorization": f"Bearer {id_token}"}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    url, headers=headers, params={"access_token": id_token}
                )
        except httpx.RequestError as exc:
            # Network issues, DNS errors, etc.
            raise HTTPException(
                status_code=503, detail=f"Google API request failed: {exc}"
            ) from exc

        if response.status_code != 200:
            # Google responded, but token invalid or expired
            raise HTTPException(
                status_code=400, detail="Invalid or expired Google token"
            )

        try:
            return response.json()
        except ValueError:
            # Response not JSON
            raise HTTPException(
                status_code=502, detail="Invalid response from Google API"
            )


google_auth = GoogleAuthUtils()
