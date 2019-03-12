import logging
import os
import pickle
import sys
from dataclasses import field
from functools import wraps

import hashlib

from icecream import ic

hasher = hashlib.md5()

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root_logger.addHandler(handler)


# логгирование
def logged(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger()
        logger.info(
            f'Call {func.__name__} '
            f'With arguments {args} {kwargs}'
        )
        func_res = func(*args, **kwargs)
        logger.info(
            f'Exiting {func.__name__} '
            f'Returned {func_res} {kwargs}'
        )
        return func_res

    return wrapper


# кешировать результат функции на диск
def pickle_cached(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        arg_str = f'{args} {kwargs}'.encode()
        arghash = hashlib.md5(arg_str).hexdigest()
        precache_path = f'data/cache/{func.__name__}__{arghash}.pkl'

        if os.path.isfile(precache_path):
            with open(precache_path, 'rb') as precache:
                res = pickle.load(file=precache)
                root_logger.info(f"Used preparsed cache {precache_path}")
                return res
        else:
            root_logger.info(f"No cache file {precache_path}")

        func_res = func(*args, **kwargs)

        with open(precache_path, 'wb') as out:
            root_logger.info(f"Created cache file {precache_path}")
            pickle.dump(func_res, file=out)

        return func_res

    return wrapper


# Статическое поле в dataclass
def static_field(val):
    return field(default=val, init=False, repr=False, compare=False, hash=False)
