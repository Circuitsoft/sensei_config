import yaml
import os
try:
    import pyinotify
except ImportError:
    pyinotify = None

class Config(object):
    def __init__(self, path=None):
        self.config = {}
        if pyinotify:
            self._wm = pyinotify.WatchManager()

        self.reload(path or '~/.sensei.yaml')

    def reload(self, path=None):
        if path:
            path = os.path.expanduser(path)
            if os.path.isfile(path):
                self.path = path
                # Watch config file
                if pyinotify:
                    self._wm.watches.clear()
                    self._wm.watch_transient_file(path, pyinotify.IN_CLOSE_WRITE, lambda x:lambda x:None)
                    self._nm = pyinotify.Notifier(self._wm)

        with open(self.path, 'r') as strm:
            self.config = yaml.load(strm)

    def check_config(self):
        """Check if config has changed - very fast, can do on every access"""
        if not pyinotify:
            return False
        changed = False
        while self._nm.check_events(0):
            self._nm.read_events()
        while self._nm._eventq:
            ev = self._nm._eventq.popleft()
            if ev.name == os.path.basename(self.path) and \
               ev.mask & pyinotify.IN_CLOSE_WRITE:
                changed = True
        if changed:
            self.reload()
        return changed

    def __getitem__(self, n):
        self.check_config()
        return self.config[n]

    def __contains__(self, k):
        self.check_config()
        return k in self.config

    def get(self, k, d=None):
        self.check_config()
        return self.config.get(k, d)
