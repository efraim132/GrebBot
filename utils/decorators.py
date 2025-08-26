import time
import os
import inspect
import functools

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


def _is_dev_mode_enabled() -> bool:
    """Return True if DEBUG_MODE is truthy in the environment."""
    debugMode = os.getenv("DEBUG_MODE", "False")
    return str(debugMode).lower() in ("1", "true", "yes", "on")

#TODO Implement Dev mode only decorator
async def devModeOnly(func):
    async def wrapper(func):
        if _is_dev_mode_enabled():
            value = func()
            return value
        raise Exception("[ERROR] Currently not in dev mode.")

    return wrapper

