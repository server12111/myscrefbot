import logging

import aiohttp

from config import SUBGRAM_KEY

logger = logging.getLogger(__name__)

SUBGRAM_URL = 'https://api.subgram.org/get-sponsors'


async def check_subgram(user_id: int) -> dict:
    if not SUBGRAM_KEY:
        return {'completed': True, 'skip': True, 'tasks': []}

    headers = {'Auth': SUBGRAM_KEY, 'Content-Type': 'application/json'}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                SUBGRAM_URL,
                json={'user_id': user_id, 'chat_id': user_id, 'get_links': 1},
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                if resp.status != 200:
                    logger.warning('Subgram: status %s for user %s', resp.status, user_id)
                    return {'completed': True, 'skip': True, 'tasks': []}
                data = await resp.json()
                if data.get('status') == 'warning':
                    sponsors = data.get('additional', {}).get('sponsors', [])
                    links = [
                        s['link']
                        for s in sponsors
                        if s.get('status') == 'unsubscribed' and s.get('link')
                    ]
                    return {'completed': False, 'skip': False, 'tasks': links}
                return {'completed': True, 'skip': False, 'tasks': []}
    except Exception as exc:
        logger.warning('Subgram error for user %s: %s', user_id, exc)
        return {'completed': True, 'skip': True, 'tasks': []}
