# -*- coding: UTF-8 -*-
from io import StringIO
import contextlib
import sys



def compilation(code):
    @contextlib.contextmanager
    def stdoutIO(stdout=None):
        old = sys.stdout
        if stdout is None:
            stdout = StringIO()
        sys.stdout = stdout
        yield stdout
        sys.stdout = old
    flag = True
    output = "\n"
    with stdoutIO() as screen:
        try:
            exec(code)
        except Exception as e:
            error = str(e)
            print(error)
            flag = False

    if flag:
        output = output+'>>> Result\n'
        output = output+str(screen.getvalue())
    else:
        output = output+'>>> Error\n'
        output = output+str(screen.getvalue())
    return output

def compilefile(file):
    if type(file) == type("str"):
       return compilation(file)
    else:
        #f = open(file,"r").read()
        return "Unknown Error occured!"




