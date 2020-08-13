import pytest

from xid import XID, InvalidXID

XIDs = [
    # taken from https://github.com/rs/xid/blob/master/id_test.go
    {
        "xid": XID(
            bytes(
                [0x4D, 0x88, 0xE1, 0x5B, 0x60, 0xF4, 0x86, 0xE4, 0x28, 0x41, 0x2D, 0xC9]
            )
        ),
        "ts": 1300816219,
        "machine": b"`\xf4\x86",
        "pid": 0xE428,
        "counter": 4271561,
    },
    {
        "xid": XID(
            bytes(
                [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
            )
        ),
        "ts": 0,
        "machine": b"\x00\x00\x00",
        "pid": 0x0000,
        "counter": 0,
    },
    {
        "xid": XID(
            bytes(
                [0x00, 0x00, 0x00, 0x00, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0x00, 0x00, 0x01]
            )
        ),
        "ts": 0,
        "machine": b"\xaa\xbb\xcc",
        "pid": 0xDDEE,
        "counter": 1,
    },
]


def test_xid_parts_extraction():
    for xid in XIDs:
        assert xid["xid"].time() == xid["ts"]
        assert xid["xid"].machine() == xid["machine"]
        assert xid["xid"].pid() == xid["pid"]
        assert xid["xid"].counter() == xid["counter"]


def test_new():
    xids = []
    for _ in range(11):
        xids.append(XID())

    for idx, i in enumerate(xids, 1):
        prev_xid = xids[idx - 1]
        xid = i

        # Test for uniqueness among all other 10 generated ids
        assert len(set(xids)) == len(xids)

        # Check that machine ids are the same
        assert xid.machine() == prev_xid.machine()

        # Check that pids are the same
        assert xid.pid() == prev_xid.pid()


def test_string():
    xid = XID(
        id_=bytes(
            [0x4D, 0x88, 0xE1, 0x5B, 0x60, 0xF4, 0x86, 0xE4, 0x28, 0x41, 0x2D, 0xC9]
        )
    )
    assert xid.string() == "9m4e2mr0ui3e8a215n4g"


def test_encode_from_string():
    xid = XID(id_="9m4e2mr0ui3e8a215n4g")
    e = xid.encode()
    assert e.decode("utf-8") == "9m4e2mr0ui3e8a215n4g"


def test_encode_from_string_invalid():
    with pytest.raises(InvalidXID):
        XID(id_="invalid")


def test_encode_from_bytes():
    with pytest.raises(InvalidXID):
        XID(id_=bytes([0xFF]))


def test_from_bytes_invariant():
    xid1 = XID()
    xid2 = XID(xid1.bytes())

    assert xid1.bytes() == xid2.bytes()


def test_repr():
    xid = XID(
        id_=bytes(
            [0x4D, 0x88, 0xE1, 0x5B, 0x60, 0xF4, 0x86, 0xE4, 0x28, 0x41, 0x2D, 0xC9]
        )
    )
    assert repr(xid) == "XID('9m4e2mr0ui3e8a215n4g')"


def test_pass_timestamp():
    t = 1234567890
    xid = XID(t=1234567890)
    assert xid.time() == t


def test_pass_wrong_type():
    with pytest.raises(TypeError):
        XID(id_=[])


def test_compare():
    xid1 = XID()
    xid2 = XID()

    assert (xid1 == xid2) is False
    assert xid1 != xid2
    assert xid1 < xid2
    assert xid1 <= xid2
    assert xid2 > xid1
    assert xid2 >= xid1
