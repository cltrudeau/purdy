#!/usr/bin/env python
import struct

def rtf_encode(text):
    output = []
    data = text.encode("utf-16le")
    length = len(data) // 2

    # Use struct.unpack to turn the pairs of bytes into decimal unicode escape
    # numbers
    parts = struct.unpack(f"<{length}H", data)
    index = 0
    size = len(parts)

    while index < size:
        num = parts[index]

        if num <= 127:
            # Regular ascii
            output.append(chr(num))
        elif num <= 256:
            # Extended ascii, use hex notation
            output.append(f"\\'{num:2x}" )
        elif num < 55296:
            # 0xD800 (55296) is the the boundary for two-word encoding, less
            # than this means it is a single item
            output.append(f"\\uc0\\u{num}")
        else:
            # Greater than 0xD800, means two words
            index += 1
            next_num = parts[index]
            output.append(f"\\uc0\\u{num} \\u{next_num}")

        index += 1

    return "".join(output)

# =============================================================================

text = ["Short string", "до свидáния", ("This is my test string. It has "
"some foreign words in it like café.  There aren't any footnotes in the "
"string, I just like the double dagger symbol ‡. Does anybody like 🐍's?"), ]

for item in text:
    encoded = rtf_encode(item)
    print(encoded)
