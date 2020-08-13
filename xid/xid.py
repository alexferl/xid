from __future__ import annotations

import ctypes
import hashlib
import logging
import os
import platform
import threading
import time

logger = logging.getLogger("xid")

ENCODED_LEN = 20  # string encoded len
RAW_LEN = 12  # binary raw len
ENCODING = b"0123456789abcdefghijklmnopqrstuv"  # custom version of the base32 encoding with lower case letters
DECODING_MAP = bytearray(256)
for index, i in enumerate(ENCODING):
    DECODING_MAP[i] = index


def rand_int() -> int:
    b = os.urandom(3)
    return b[0] << 16 | b[1] << 8 | b[2]


def read_machine_id() -> bytes:
    try:
        hostname = platform.node()
        hw = hashlib.md5()
        hw.update(hostname.encode("utf-8"))
        return hw.digest()[:3]
    except Exception as e:  # pragma: no cover
        logger.warning("Unhandled exception reading machine id: '{}'".format(e))
        return os.urandom(3)


def generate_next_id():
    id_ = rand_int()

    while True:
        new_id = id_ + 1
        id_ += 1
        yield new_id


object_id_counter = rand_int()
machine_id = read_machine_id()
pid = os.getpid()
xid_generator = generate_next_id()
lock = threading.Lock()


class InvalidXID(Exception):
    def __init__(self, message="Invalid ID"):
        self.message = message
        super().__init__(self.message)


class XID:
    def __init__(self, id_: bytes = None, t: time.time = None):
        if t is None:
            self.t = int(time.time())
        else:
            self.t = t

        if id_ is None:
            self.id = self._generate_new_xid(self.t)
        else:
            self.id = id_

    @staticmethod
    def _generate_new_xid(t: time.time):
        id_ = bytearray(RAW_LEN)

        # Timestamp, 4 bytes, big endian
        id_[0:4] = t.to_bytes(4, byteorder="big")

        # Machine, first 3 bytes of md5(hostname)
        id_[4] = machine_id[0]
        id_[5] = machine_id[1]
        id_[6] = machine_id[2]

        # Pid, 2 bytes, specs don't specify endianness, but we use big endian.
        id_[7] = _uint8(pid >> 8 & 0xFF)
        id_[8] = _uint8(pid & 0xFF)

        # Increment, 3 bytes, big endian
        lock.acquire()
        i = next(xid_generator)
        lock.release()
        id_[9] = _uint8(i >> 16 & 0xFF)
        id_[10] = _uint8(i >> 8 & 0xFF)
        id_[11] = _uint8(i & 0xFF)

        return bytes(id_)

    def string(self) -> str:
        return self._encode(self.id).decode("utf-8")

    def encode(self) -> bytes:
        return self._encode(self.id)

    @staticmethod
    def _encode(id_: bytes) -> bytes:
        dst = bytearray(ENCODED_LEN)

        dst[19] = ENCODING[(id_[11] << 4) & 0x1F]
        dst[18] = ENCODING[(id_[11] >> 1) & 0x1F]
        dst[17] = ENCODING[(id_[11] >> 6) & 0x1F | (id_[10] << 2) & 0x1F]
        dst[16] = ENCODING[id_[10] >> 3]
        dst[15] = ENCODING[id_[9] & 0x1F]
        dst[14] = ENCODING[(id_[9] >> 5) | (id_[8] << 3) & 0x1F]
        dst[13] = ENCODING[(id_[8] >> 2) & 0x1F]
        dst[12] = ENCODING[id_[8] >> 7 | (id_[7] << 1) & 0x1F]
        dst[11] = ENCODING[(id_[7] >> 4) & 0x1F | (id_[6] << 4) & 0x1F]
        dst[10] = ENCODING[(id_[6] >> 1) & 0x1F]
        dst[9] = ENCODING[(id_[6] >> 6) & 0x1F | (id_[5] << 2) & 0x1F]
        dst[8] = ENCODING[id_[5] >> 3]
        dst[7] = ENCODING[id_[4] & 0x1F]
        dst[6] = ENCODING[id_[4] >> 5 | (id_[3] << 3) & 0x1F]
        dst[5] = ENCODING[(id_[3] >> 2) & 0x1F]
        dst[4] = ENCODING[id_[3] >> 7 | (id_[2] << 1) & 0x1F]
        dst[3] = ENCODING[(id_[2] >> 4) & 0x1F | (id_[1] << 4) & 0x1F]
        dst[2] = ENCODING[(id_[1] >> 1) & 0x1F]
        dst[1] = ENCODING[(id_[1] >> 6) & 0x1F | (id_[0] << 2) & 0x1F]
        dst[0] = ENCODING[id_[0] >> 3]

        return bytes(dst)

    @staticmethod
    def _decode(xid: XID, src: bytes, dec=None) -> XID:
        if dec:
            dec = dec
        else:
            dec = DECODING_MAP

        id_ = bytearray(ENCODED_LEN)

        if len(src) != ENCODED_LEN:
            raise InvalidXID()

        for c in src:
            if dec[c] == 255:
                raise InvalidXID()

        id_[11] = (
            _uint8(dec[src[17]] << 6)
            | _uint8(dec[src[18]] << 1)
            | _uint8(dec[src[19]] >> 4)
        )
        id_[10] = _uint8(dec[src[16]] << 3) | _uint8(dec[src[17]] >> 2)
        id_[9] = _uint8(dec[src[14]] << 5) | _uint8(dec[src[15]])
        id_[8] = (
            _uint8(dec[src[12]] << 7)
            | _uint8(dec[src[13]] << 2)
            | _uint8(dec[src[14]] >> 3)
        )
        id_[7] = _uint8(dec[src[11]] << 4) | _uint8(dec[src[12]] >> 1)
        id_[6] = (
            _uint8(dec[src[9]] << 6)
            | _uint8(dec[src[10]] << 1)
            | _uint8(dec[src[11]] >> 4)
        )
        id_[5] = _uint8(dec[src[8]] << 3) | _uint8(dec[src[9]] >> 2)
        id_[4] = _uint8(dec[src[6]] << 5) | _uint8(dec[src[7]])
        id_[3] = (
            _uint8(dec[src[4]] << 7)
            | _uint8(dec[src[5]] << 2)
            | _uint8(dec[src[6]] >> 3)
        )
        id_[2] = _uint8(dec[src[3]] << 4) | _uint8(dec[src[4]] >> 1)
        id_[1] = (
            _uint8(dec[src[1]] << 6)
            | _uint8(dec[src[2]] << 1)
            | _uint8(dec[src[3]] >> 4)
        )
        id_[0] = _uint8(dec[src[0]] << 3) | _uint8(dec[src[1]] >> 2)

        xid.id = bytes(id_)
        return xid

    def time(self) -> int:
        return int.from_bytes(self.id[0:4], byteorder="big")

    def machine(self) -> bytes:
        return self.id[4:7]

    def pid(self) -> int:
        return self.id[7] << 8 | self.id[8]

    def counter(self) -> int:
        b = self.id[9:12]
        return b[0] << 16 | b[1] << 8 | b[2]

    def bytes(self) -> bytes:
        return self.id

    def __repr__(self):
        return "XID('%s')" % self.__str__()

    def __str__(self):
        return self.string()

    def __lt__(self, other: XID) -> bool:
        return self.string() < other.string()

    def __gt__(self, other: XID) -> bool:
        return self.string() > other.string()


def from_string(s: str) -> XID:
    xid = XID()
    return xid._decode(xid, bytes(s.encode("utf-8")))


def from_bytes(b: bytes) -> XID:
    if len(b) != RAW_LEN:
        raise InvalidXID()
    return XID(b)


def _uint8(n: int) -> int:
    return ctypes.c_uint8(n).value
