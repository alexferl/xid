# xid [![codecov](https://codecov.io/gh/alexferl/xid/branch/master/graph/badge.svg)](https://codecov.io/gh/alexferl/xid)

A Python 3.8+ port of [https://github.com/rs/xid](https://github.com/rs/xid).

# Install

```shell script
pip install py-xid
```

# Usage
```python
from xid import XID

guid = XID()

print(guid.string())
# Output: bsqo1inf38q5alkk85a0

print(guid.machine())
# Output:  b'\xef\x1a4'

print(guid.pid())
# Output: 21846

print(guid.time())
# Output: 1597341898

print(guid.counter())
# Output: 9716052

print(guid.bytes())
# Output: b'_5\x80\xca\xef\x1a4UV\x94AT'

print(XID("bsqo1inf38q5alkk85a0"))
# Output: XID('bsqo1inf38q5alkk85a0')

print(XID(b"_5\x80\xca\xef\x1a4UV\x94AT"))
# Output: XID('bsqo1inf38q5alkk85a0')
```
