import aiohttp
from urllib.parse import urlparse
from config import TGRASS_API_KEY, BOTOHUB_API_KEY


async def get_tgrass_offers(user_id: int, is_premium: bool = False, lang: str = "ru") -> list:
    if not TGRASS_API_KEY:
        return []

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://tgrass.space/offers",
                headers={"Auth": TGRASS_API_KEY},
                json={"tg_user_id": user_id, "is_premium": is_premium, "lang": lang},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                data = await resp.json()
                if data.get("status") in ("ok", "no_offers"):
                    return []
                return [o for o in (data.get("offers") or []) if o.get("link")]
    except Exception:
        return []


async def check_tgrass_subscribed(user_id: int, is_premium: bool = False, lang: str = "ru") -> bool:
    if not TGRASS_API_KEY:
        return True

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://tgrass.space/offers",
                headers={"Auth": TGRASS_API_KEY},
                json={"tg_user_id": user_id, "is_premium": is_premium, "lang": lang},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                data = await resp.json()
                return data.get("status") in ("ok", "no_offers")
    except Exception:
        return True


async def get_botohub_tasks(user_id: int) -> tuple:
    if not BOTOHUB_API_KEY:
        return [], True

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://botohub.me/get-tasks",
                headers={"Auth": BOTOHUB_API_KEY},
                json={"chat_id": user_id},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                data = await resp.json()
                tasks = data.get("tasks") or []
                completed = data.get("completed", True)
                return tasks, completed
    except Exception:
        return [], True


async def check_botohub_completed(user_id: int) -> bool:
    if not BOTOHUB_API_KEY:
        return True

    _, completed = await get_botohub_tasks(user_id)
    return completed


def extract_channel_name(url: str) -> str:
    try:
        path = urlparse(url).path.strip("/")
        name = path.split("/")[-1] if path else "Канал"
        return name if name else "Канал"
    except Exception:
        return "Канал"
