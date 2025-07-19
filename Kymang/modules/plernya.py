from Kymang.modules.data import add_seller, cek_seller


async def plernya():
    if 2028665763 not in await cek_seller():
        await add_seller(2028665763)
