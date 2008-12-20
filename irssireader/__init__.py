#!/usr/bin/env python

import sys
from cStringIO import StringIO
import re
import time
import subprocess

spoken_line = re.compile(r'\d\d:\d\d <[ @+]?(?P<name>.*?)> (?P<said>.*)')
bitlbee_line = re.compile(r'\d\d:\d\d -!- ServerMode/&bitlbee \[(?P<notification>.*?)\]')
join_line = re.compile(r'\d\d:\d\d -!- (?P<name>.*?) \[.*?\] has joined (?P<channel>.*?)')
quit_line = re.compile(r'\d\d:\d\d -!- (?P<name>.*?) \[.*?\] has quit \[.*?\]')
link = re.compile(r'https?://[^ ]+')
link2 = re.compile(r'www\.[^ ]+')

def p(s):
    s = s.replace('|', ' ')
    s = link.sub('a link:', s)
    s = link2.sub('a link:', s)
    p1 = subprocess.Popen(['echo', s], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(['festival', '--tts'], stdin=p1.stdout, stdout=subprocess.PIPE)
    sys.stderr.write(s)
    sys.stderr.write('\n')
    p2.wait()

def main():
    data = StringIO()
    prevchannel = ''
    prevnick = ''
    try:
        while True:
            byte = sys.stdin.read(1)
            data.write(byte)
            if byte == '\n':
                line = data.getvalue().strip()
                data.seek(0)
                data.truncate()
                channel = ''
                nick = ''
                if line.startswith('---'):
                    # "--- Log closed ---", etc.
                    pass
                elif line.startswith('==>'):
                    # tail's way of separating logs: "==> path/to/file.log <=="
                    part = line.rsplit('/', 1)[1]
                    channel = part.split('.')[0]
                    continue
                elif bitlbee_line.match(line):
                    m = bitlbee_line.match(line)
                    operation, person = m.group('notification').split()
                    s = "bitlbee: %s " % person
                    if operation == '-v':
                        s+='went away'
                    elif operation == '+v':
                        s+='came back'
                    else:
                        s+='did something I think you should look at'
                    p(s)
                elif spoken_line.match(line):
                    m = spoken_line.match(line)
                    nick = m.group('name')
                    if nick != 'Flexo':
                        s = ''
                        if channel != prevchannel:
                            s += channel + ': '
                        if nick != prevnick:
                            s += "%s said: " % m.group('name')
                        s += m.group('said')
                        p(s)
                elif join_line.match(line):
                    m = join_line.match(line)
                    p("join: %(name)s has joined %(channel)s" % m.groupdict())
                elif quit_line.match(line):
                    m = quit_line.match(line)
                    p(("quit: %(name)s has quit " % m.groupdict()) + channel)
                elif line:
                    p(line)
                prevchannel = channel
                prevnick = nick
            if not byte:
                break
    except Exception:
        print "Error!"
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

