#!/usr/bin/env python
from rtmbot.bin.run_rtmbot import main as rtmbotMain


class FakeArgs:
    def __getattr__(self, item):
        if item == 'config':
            return 'soulbot.conf'

        raise ValueError


if __name__ == "__main__":
    rtmbotMain(FakeArgs())
