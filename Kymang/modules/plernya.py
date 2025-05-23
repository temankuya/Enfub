from Kymang.modules.data import add_seller, cek_seller


async def plernya():
    if 843830036 not in await cek_seller():
        await add_seller(843830036)
