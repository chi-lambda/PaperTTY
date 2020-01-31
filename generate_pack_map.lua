#!/usr/bin/env lua5.3

dict = { [0] = 0, [1] = 0xF0, [2] = 0x0F, [3] = 0xFF }

function pack(x)
    first = x // 64
    second = (x // 16) % 4
    third = (x // 4) % 4
    fourth = x % 4

    io.write(string.format('%s, %s, %s, %s', dict[second], dict[first], dict[fourth], dict[third]))
end

print('unsigned char pack_map[256][4] = {')
for i=0,255 do
    io.write('\t{ ')
    pack(i)
    io.write(string.format(' }, // %x\n', i))
end
print('};')