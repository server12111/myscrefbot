import logging

import aiohttp

from config import GRAMADS_TOKEN

logger = logging.getLogger(__name__)

GRAMADS_URL = 'https://api.gramads.net/ad/SendPost'


async def show_advert(user_id: int) -> None:
    if not GRAMADS_TOKEN:
        return
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                GRAMADS_URL,
                headers={
                    'Authorization': f'Bearer {GRAMADS_TOKEN}',
                    'Content-Type': 'application/json',
                },
                json={'SendToChatId': user_id},
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                if not resp.ok:
                    logger.error('Gramads error for user %s: status %s', user_id, resp.status)
    except Exception as exc:
        logger.warning('Gramads error for user %s: %s', user_id, exc)
