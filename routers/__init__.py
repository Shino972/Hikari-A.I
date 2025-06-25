from aiogram import Router
from handlers import start
from handlers import callback
from handlers import lang
from handlers import group_me_join

def get_routers() -> list[Router]:
    return [
        start.router,
        callback.router,
        lang.router,
        group_me_join.router
    ]
