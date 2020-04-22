from dataclasses import fields
from enum import IntEnum
from typing import TypeVar, Type

import netstruct

# Helper structs which maps primitive types to the netstruct format string symbols which should be used to serialize
# those types

format_dict = {
    bool: b'B',
    float: b'f',
    int: b'B', # for now all ints are assumed to be unsigned 8-bit values !!
    str: b'i$'
}

T = TypeVar('T')


def unflatten_from_string(data: bytes, cls: Type[T]) -> T:
    """
    Unflatten data following the format of LabView's "Flatten to string" vi into a corresponding dataclass instance

    :param data: the binary representation
    :param cls: type of the dataclass into which data should be deserialized
    :return: dataclass instance
    """

    fmt, names = zip(*[(format_dict[field.type if not issubclass(field.type, IntEnum) else int], field.name) for field in fields(cls)])
    fmt = b''.join(fmt)
    vals = netstruct.unpack(fmt, data)
    res = cls(**{name: (val.decode('utf-8') if isinstance(val, bytes) else val) for name, val in zip(names, vals)})
    return res


def flatten_to_string(obj) -> bytes:
    """
    Flatten a dataclass instance into a binary representation which can be deserialized with LabView's "Unflatten from string" vi.

    :param obj: dataclass instance to flatten
    :return: binary string
    """
    fmt, vals = zip(*[(format_dict[field.type if not isinstance(field.type, IntEnum) else int], getattr(obj, field.name)) for field in fields(obj)])
    fmt = b''.join(fmt)
    vals = [val.encode('utf-8') if isinstance(val, str) else val for val in vals]
    res = netstruct.pack(fmt, *vals)
    return res
