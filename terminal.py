#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Jouko Strömmer, 2018
# Copyright and related rights waived via CC0
# https://creativecommons.org/publicdomain/zero/1.0/legalcode

# As you would expect, use this at your own risk! This code was created
# so you (yes, YOU!) can make it better.
#
# Requires Python 3

import signal
import sys
import struct

class Terminal:
    def __init__(self, settings, vcsa, font, fontsize, noclear, nocursor, cursor, sleep, ttyrows, ttycols, portrait, flipx, flipy,
                spacing, apply_scrub, autofit, attributes, interactive):
        """Display virtual console on an e-Paper display, exit with Ctrl-C."""
        settings.args['font'] = font
        settings.args['fontsize'] = fontsize
        settings.args['spacing'] = spacing

        if cursor != 'legacy' and nocursor:
            print("--cursor and --nocursor can't be used together. To hide the cursor, use --cursor=none")
            sys.exit(1)

        if nocursor:
            print("--nocursor is deprectated. Use --cursor=none instead")
            settings.args['cursor'] = None

        if cursor == 'default' or cursor == 'legacy':
            settings.args['cursor'] = 'default'
        elif cursor == 'none':
            settings.args['cursor'] = None
        else:
            settings.args['cursor'] = cursor

        ptty = settings.get_init_tty()

        if apply_scrub:
            ptty.driver.scrub()
        oldbuff = ''
        oldimage = None
        oldcursor = None
        # dirty - should refactor to make this cleaner
        flags = {'scrub_requested': False, 'show_menu': False, 'clear': False}
        
        # handle SIGINT from `systemctl stop` and Ctrl-C
        def sigint_handler(sig, frame):
            if not interactive:
                print("Exiting (SIGINT)...")
                if not noclear:
                    ptty.showtext(oldbuff, fill=ptty.white, **textargs)
                sys.exit(0)
            else:
                print('Showing menu, please wait ...')
                flags['show_menu'] = True

        # toggle scrub flag when SIGUSR1 received
        def sigusr1_handler(sig, frame):
            print("Scrubbing display (SIGUSR1)...")
            flags['scrub_requested'] = True

        signal.signal(signal.SIGINT, sigint_handler)
        signal.signal(signal.SIGUSR1, sigusr1_handler)

        # group the various params for readability
        textargs = {'portrait': portrait, 'flipx': flipx, 'flipy': flipy}

        if any([ttyrows, ttycols]) and not all([ttyrows, ttycols]):
            ptty.error("You must define both --rows and --cols to change terminal size.")
        if ptty.valid_vcsa(vcsa):
            if all([ttyrows, ttycols]):
                ptty.set_tty_size(ptty.ttydev(vcsa), ttyrows, ttycols)
            else:
                # if size not specified manually, see if autofit was requested
                if autofit:
                    max_dim = ptty.fit(portrait)
                    print("Automatic resize of TTY to {} rows, {} columns".format(max_dim[1], max_dim[0]))
                    ptty.set_tty_size(ptty.ttydev(vcsa), max_dim[1], max_dim[0])
            if interactive:
                print("Started displaying {}, minimum update interval {} s, open menu with Ctrl-C".format(vcsa, sleep))
            else:
                print("Started displaying {}, minimum update interval {} s, exit with Ctrl-C".format(vcsa, sleep))
            character_width, vcsudev = ptty.vcsudev(vcsa)
            while True:
                if flags['show_menu']:
                    flags['show_menu'] = False
                    print()
                    print('Rendering paused. Enter')
                    print('    (f) to change font,')
                    print('    (s) to change spacing,')
                    if ptty.is_truetype:
                        print('    (h) to change font size,')
                    print('    (c) to scrub,')
                    print('    (i) reinitialize display,')
                    print('    (x) to exit,')
                    print('    anything else to continue.')
                    print('Command line arguments for current settings:\n    --font {} --size {} --spacing {}'.format(ptty.fontfile, ptty.fontsize, ptty.spacing))

                    ch = sys.stdin.readline().strip()
                    if ch == 'x':
                        if not noclear:
                            ptty.showtext(oldbuff, fill=ptty.white, **textargs)
                        sys.exit(0)
                    elif ch == 'f':
                        print('Current font: {}'.format(ptty.fontfile))
                        new_font = click.prompt('Enter new font (leave empty to abort)', default='', show_default=False)
                        if new_font:
                            ptty.spacing = spacing
                            ptty.font = ptty.load_font(new_font, keep_if_not_found=True)
                            if autofit:
                                max_dim = ptty.fit(portrait)
                                print("Automatic resize of TTY to {} rows, {} columns".format(max_dim[1], max_dim[0]))
                                ptty.set_tty_size(ptty.ttydev(vcsa), max_dim[1], max_dim[0])
                            oldbuff = None
                        else:
                            print('Font not changed')
                    elif ch == 's':
                        print('Current spacing: {}'.format(ptty.spacing))
                        new_spacing = click.prompt('Enter new spacing (leave empty to abort)', default='empty', type=int, show_default=False)
                        if new_spacing != 'empty':
                            ptty.spacing = new_spacing
                            ptty.recalculate_font()
                            if autofit:
                                max_dim = ptty.fit(portrait)
                                print("Automatic resize of TTY to {} rows, {} columns".format(max_dim[1], max_dim[0]))
                                ptty.set_tty_size(ptty.ttydev(vcsa), max_dim[1], max_dim[0])
                            oldbuff = None
                        else:
                            print('Spacing not changed')
                    elif ch == 'h' and ptty.is_truetype:
                        print('Current font size: {}'.format(ptty.fontsize))
                        new_fontsize = click.prompt('Enter new font size (leave empty to abort)', default='empty', type=int, show_default=False)
                        if new_fontsize != 'empty':
                            ptty.fontsize = new_fontsize
                            ptty.spacing = spacing
                            ptty.font = ptty.load_font(path=None)
                            if autofit:
                                max_dim = ptty.fit(portrait)
                                print("Automatic resize of TTY to {} rows, {} columns".format(max_dim[1], max_dim[0]))
                                ptty.set_tty_size(ptty.ttydev(vcsa), max_dim[1], max_dim[0])
                            oldbuff = None
                        else:
                            print('Font size not changed')
                    elif ch == 'c':
                        flags['scrub_requested'] = True
                    elif ch == 'i':
                        ptty.clear()
                        oldimage = None
                        oldbuff = None

                # if user or SIGUSR1 toggled the scrub flag, scrub display and start with a fresh image
                if flags['scrub_requested']:
                    ptty.driver.scrub()
                    # clear old image and buffer and restore flag
                    oldimage = None
                    oldbuff = ''
                    flags['scrub_requested'] = False
                
                with open(vcsa, 'rb') as f:
                    with open(vcsudev, 'rb') as vcsu:
                        # read the first 4 bytes to get the console attributes
                        attributes = f.read(4)
                        rows, cols, x, y = list(map(ord, struct.unpack('cccc', attributes)))

                        # read from the text buffer 
                        buff = vcsu.read()
                        if character_width == 4:
                            # work around weird bug
                            buff = buff.replace(b'\x20\x20\x20\x20', b'\x20\x00\x00\x00')
                        # find character under cursor (in case using a non-fixed width font)
                        char_under_cursor = buff[character_width * (y * rows + x):character_width * (y * rows + x + 1)]
                        encoding = 'utf_32' if character_width == 4 else ptty.encoding
                        cursor = (x, y, char_under_cursor.decode(encoding, 'ignore'))
                        # add newlines per column count
                        buff = ''.join([r.decode(encoding, 'replace') + '\n' for r in ptty.split(buff, cols * character_width)])
                        # do something only if content has changed or cursor was moved
                        if buff != oldbuff or cursor != oldcursor:
                            # show new content
                            oldimage = ptty.showtext(buff, fill=ptty.black, cursor=cursor if not nocursor else None,
                                                    oldimage=oldimage,
                                                    **textargs)
                            oldbuff = buff
                            oldcursor = cursor
                        else:
                            # delay before next update check
                            time.sleep(float(sleep))
