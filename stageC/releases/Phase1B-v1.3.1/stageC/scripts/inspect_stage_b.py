from _bootstrap import *
from stage_c.cli import main
if __name__ == "__main__": raise SystemExit(main(["inspect", *__import__("sys").argv[1:]]))
