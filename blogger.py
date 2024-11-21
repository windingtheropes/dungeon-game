# logging library
from datetime import datetime
class blogger():
    def __init__(self, file=f"log"):
        ds = datetime.now().strftime("%m_%d_%Y__%H_%M_%S")
        self.file = f"{file}_{ds}"
    def _log(self, p,m):
        ts = datetime.now().strftime("%H:%M.%S")
        msg = f"[{ts}][{p}] {m}"
        print(msg)
        buf = open(self.file, "+a")
        buf.write(f"{msg}\n")
        buf.close()
    def warn(self, m):
        self._log("warn", m)
    def error(self, m):
        self._log("error", m)
        raise Exception(m)
    def info(self, m):
        self._log("info", m)

# blogger init function to be used globally, all log to one file
b: blogger = None
def blog():
    return b
def init(file):
    global b
    b = blogger(file)