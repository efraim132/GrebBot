import time

from discord.ext import commands


def admin_only():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator

    return commands.check(predicate)


def timer(func):
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        result = func(*args, **kwargs)
        dt = time.perf_counter() - t0
        print(f"{func.__name__} call took {dt:.6f}s")
        return result

    return wrapper
