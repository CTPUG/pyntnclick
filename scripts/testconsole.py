#! /usr/bin/env python
# testconsole.py
# Copyright Simon Cross, Neil Muller, 2009 (see COPYING File)


"""This module launches an interactive console.

   Its purpose is to provide an easy means to
   test the environment created by a py2exe build.
   """

if __name__ == "__main__":
    import code
    # pylint: disable-msg=C0103
    # pylint thinks this should be a constant
    console = code.InteractiveConsole()
    console.interact()
