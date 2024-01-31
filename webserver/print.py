import argparse
import socket
from charset import charset

HEADER = b'\x1b\x4e\x0d\x01\x1b\x4e\x04\x0f\x1f\x11\x0a'
'''
  0x1b 0x4e 0x0d  -> Print Speed
  0x05            range: 0x01 (Slow) -  0x05 (Fast)
  0x1b 0x4e 0x04  -> Print Density
  0x0f            range: 01 - 0f
  0x1f  0x11      -> Media Type
  0x0a            Mode: 0a="Label With Gaps" 0b="Continuas" 26="Label With Marks"
'''

BLOCK_MARKER = b'\x1d\x76\x30\x00\x2b\x00\xf0\x00'
'''
  0x1d 0x76 0x30 -> command GS v 0 : print raster bit image
  0x00              mode: 0 (normal), 1 (double width),
                          2 (double-height), 3 (quadruple)
  0x2b 0x00         16bit, little-endian: number of bytes / line (43)
  0xf0 0x00         16bit, little-endian: number of lines in the image (240)
'''

FOOTER = b'\x1f\xf0\x05\x00\x1f\xf0\x03\x00'
'''
  0x1f 0xf0 0x05 0x00
  0x1f 0xf0 0x03 0x00
'''

CHAR_WIDTH = 5
CHAR_HEIGHT = 40
BUF_WIDTH = 43
BUF_HEIGHT = 240

class TextPrinter:
    def open(self, bluetooth_address, channel):
        self.s = socket.socket(
            socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM
        )
        self.s.connect((bluetooth_address, channel))

    def _render_char(self, buffer, pos_x, pos_y, char):
        try:
            char_bitmap = charset[char]
        except KeyError:
            char_bitmap = charset['?']
        for char_x in range(CHAR_WIDTH):
            for char_y in range(CHAR_HEIGHT):
                x = pos_x + char_x
                y = pos_y + char_y
                buffer[(y * BUF_WIDTH) + x] = char_bitmap[char_y][char_x]
        return buffer

    def _render_chars(self, buffer, pos_x, pos_y, text):
        assert(pos_x >= 0)
        assert(pos_y >= 0)
        assert(pos_x <= BUF_WIDTH - CHAR_WIDTH)
        assert(pos_y <= BUF_HEIGHT - CHAR_HEIGHT)
        cur_x = pos_x
        cur_y = pos_y
        for char in text:
            if char == '\r':
                continue
            if char == '\n':
                cur_x = pos_x
                cur_y += CHAR_HEIGHT
                continue
            if cur_x > BUF_WIDTH - CHAR_WIDTH:
                print('forcing line break')
                cur_x = pos_x
                cur_y += CHAR_HEIGHT
            if cur_y > BUF_HEIGHT - CHAR_HEIGHT:
                print('too many lines, skipping text')
                break
            buffer = self._render_char(buffer, cur_x, cur_y, char)
            cur_x += CHAR_WIDTH
        return buffer

    def print(self, text):
        self.s.send(HEADER)
        self.s.send(BLOCK_MARKER)

        bytes_to_send = bytearray(b'\x00' * BUF_WIDTH * BUF_HEIGHT)
        self._render_chars(bytes_to_send, 1*CHAR_WIDTH, 1*CHAR_HEIGHT, text)
        bytes_to_send = bytes(bytes_to_send)

        self.s.send(bytes_to_send)
        self.s.send(FOOTER)

    def close(self):
        self.s.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Print plain text on Phomemo M110 printer via bluetooth')
    parser.add_argument('-t',
                        '--text',
                        type=str,
                        help='Text to print')
    parser.add_argument(
        '-a',
        '--bluetooth_address',
        type=str,
        help='MAC address of your bluetooth device (no need to connect)',
        required=True,
    )
    parser.add_argument(
        '-c',
        '--channel',
        type=int,
        help='Channel to connect to your bluetooth device on',
        required=True,
    )

    args = parser.parse_args()
    tp = TextPrinter()
    tp.open(args.bluetooth_address, args.channel)
    tp.print(args.text)
    tp.close()
