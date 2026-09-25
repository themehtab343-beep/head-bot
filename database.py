from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URL

client = AsyncIOMotorClient(MONGO_URL)
db = client['head_bot_db']

keys_col = db['access_keys']
bots_col = db['sub_bots']

async def add_key(key: str):
    await keys_col.insert_one({"key": key, "used": False})

async def is_key_valid(key: str):
    k = await keys_col.find_one({"key": key, "used": False})
    return bool(k)

async def use_key(key: str, user_id: int):
    await keys_col.update_one({"key": key}, {"$set": {"used": True, "used_by": user_id}})

async def register_sub_bot(user_id: int, bot_token: str, welcome_msg: str, buttons: list):
    await bots_col.update_one(
        {"user_id": user_id},
        {"$set": {"bot_token": bot_token, "welcome_msg": welcome_msg, "buttons": buttons}},
        upsert=True
    )
