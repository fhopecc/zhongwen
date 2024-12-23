class 關閉區塊執行所有輸出(object):
    from types import TracebackType
    from typing import Union
    import sys
    stdout, stderr = sys.__stdout__.fileno(), sys.__stderr__.fileno()
    def __enter__(self) -> None:
        import os
        self.devnull = os.open(os.devnull, os.O_RDWR)
        self.orig_stdout, self.orig_stderr = os.dup(self.stdout), os.dup(self.stderr)
        # point stdout, stderr to /dev/null
        os.dup2(self.devnull, self.stdout)
        os.dup2(self.devnull, self.stderr)

    def __exit__(
        self,
        exc_type: Union[type[BaseException], None],
        exc_val: Union[BaseException, None],
        exc_tb: Union[TracebackType, None],
    ) -> None:
        import os
        print(flush=True)
        # restore stdout, stderr back
        os.dup2(self.orig_stdout, self.stdout)
        os.dup2(self.orig_stderr, self.stderr)
        # close all file descriptors
        # for file in [self.devnull, self.orig_stdout, self.orig_stderr]:
            # os.close(file)
