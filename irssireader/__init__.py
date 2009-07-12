#!/usr/bin/env python

import sys
from cStringIO import StringIO
import re
import time
import subprocess

link = re.compile(r'https?://[^ ]+')
link2 = re.compile(r'www\.[^ ]+')

def print_to_command(cmd=None):
    def p(s):
        s = s.replace('*', ' star ')
        s = s.replace('|', ' ')
        s = link.sub('a link:', s)
        s = link2.sub('a link:', s)
        sys.stderr.write(s)
        sys.stderr.write('\n')
        if not cmd:
            p1 = subprocess.Popen(['echo', s], stdout=subprocess.PIPE)
            p2 = subprocess.Popen(['festival', '--tts'], stdin=p1.stdout, stdout=subprocess.PIPE)
            p2.wait()
        else:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, stdin=subprocess.PIPE)
            proc.stdin.write(s)
            proc.stdin.close()
            proc.wait()
    return p


class Reader(object):

    def __init__(self, cmd=None):
        self.channel = ''
        self.user = ''
        self.channel_changed = False
        self.time = '00:00'
        self.cmd = cmd
        self.p = print_to_command(cmd)

    def system_message(self, line):
        line = line[4:] # strip '-!- '
        if line.startswith('ServerMode'):
            start = line.find('[') + 1
            end = line.find(']')
            mode, user = line[start:end].split(' ', 1)
            by = line[end + 5:]
            what = ''
            if mode == '+o':
                what = 'was opped'
            elif mode == '-o':
                what = 'was de-opped'
            elif mode == '+v':
                if self.channel.endswith('bitlbee'):
                    what = 'is back'
                else:
                    what = 'was voiced'
            elif mode == '-v':
                if self.channel.endswith('bitlbee'):
                    what = 'went away'
                else:
                    what = 'was de-voiced'
            if self.channel.endswith('bitlbee'):
                say = "%s %s" % (user, what)
            else:
                say = "%s %s by %s" % (user, what, by)
            return user, say
        elif 'has quit' in line:
            user = line.split(' ', 1)[0]
            return user, "%s has quit" % (user,)
        elif 'has joined' in line:
            user = line.split(' ', 1)[0]
            return user, "%s has joined" % (user,)
        elif 'has left' in line:
            user = line.split(' ', 1)[0]
            return user, "%s has left" % (user,)
        return None, "System line ignored."            


    def spoken_line(self, line):
        user, line = line.split('> ', 1)
        user = user.strip('< @+%')
        if user != self.user:
            return user, "%s said: %s" % (user, line)
        else:
            return user, line


    def action_line(self, line):
        line = line.strip(' *')
        user = line.split(' ', 1)[0]
        return user, line


    def __call__(self, line):
        if not line.strip():
            return
        if line.startswith('==>'):
            # get channel:
            # tail's way of separating logs: "==> path/to/file.log <=="
            filename = line.rsplit('/', 1)[1]
            channel = filename.rsplit('.', 1)[0]
            if channel != self.channel:
                self.channel_changed = True
            self.channel = channel
            return
        if line.startswith('---'):
            # --- Log closed ---, etc.
            return

        # All irssi lines start with time:
        self.time, line = line.split(' ', 1)
        resp = None
        user = None
        if line.startswith('-!-'):
            user, resp = self.system_message(line)
        elif line.startswith('<'):
            user, resp = self.spoken_line(line)
        elif line.startswith(' *'):
            user, resp = self.action_line(line)
        else:
            resp = "Line ignored."
            print >> sys.stderr, line
        
        if user:
            self.user = user

        if resp and user != 'Flexo':
            if self.channel_changed:
                self.p(self.channel + '.')
            self.p(resp)

            self.channel_changed = False


def main():
    cmd = None
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
    data = StringIO()
    reader = Reader(cmd)
    try:
        while True:
            byte = sys.stdin.read(1)
            if byte == '\n':
                reader(data.getvalue())
                data.seek(0)
                data.truncate()
            else:
                data.write(byte)
                
    except KeyboardInterrupt:
        sys.exit()
    except Exception:
        print "Error!"
        import traceback
        traceback.print_exc()
    

if __name__ == '__main__':
    main()

