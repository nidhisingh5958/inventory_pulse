import aioredis

redis_client = aioredis.from_url("redis://localhost", decode_responses=True) 
