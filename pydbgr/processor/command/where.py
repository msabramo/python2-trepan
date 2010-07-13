# -*- coding: utf-8 -*-
#  Copyright (C) 2009 Rocky Bernstein
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os
from import_relative import import_relative

# Our local modules
Mbase_cmd = import_relative('base_cmd', top_name='pydbgr')
Mstack    = import_relative('stack',  '...lib', 'pydbgr')
Mcmdfns   = import_relative('cmdfns', '..',     'pydbgr')

class WhereCommand(Mbase_cmd.DebuggerCommand):
    """where [count]

Print a stack trace, with the most recent frame at the top.  With a
positive number, print at most many entries.  With a negative number
print the top entries minus that number.

An arrow indicates the 'current frame'. The current frame determines
the context used for many debugger commands such as expression
evaluation or source-line listing.

Examples:
   where    # Print a full stack trace
   where 2  # Print only the top two entries
   where -1 # Print a stack trace except the initial (least recent) call.
"""


    aliases       = ('bt', 'backtrace')
    category      = 'stack'
    min_args      = 0
    max_args      = 1
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = True
    short_help   = 'Print backtrace of stack frames'

    def run(self, args):
        if len(args) > 1:
            at_most = len(self.proc.stack)
            if at_most == 0:
                self.errmsg("Stack is empty.")
                return False
            min_value = - at_most + 1
            count = self.proc.get_int(args[1], min_value = min_value,
                                      cmdname = 'where',
                                      default=0, at_most = at_most)
            if count is None: return False
            if count < 0:
                count =  at_most - count
                pass
            elif 0 == count: count = None
        else:
            count = None
            pass

        if not self.proc.curframe:
            self.errmsg("No stack.")
            return False
        Mstack.print_stack_trace(self.proc, count)
        return False

    pass

if __name__ == '__main__':
    cmdproc      = import_relative('cmdproc', '..')
    debugger     = import_relative('debugger', '...')
    d            = debugger.Debugger()
    cp           = d.core.processor
    command      = WhereCommand(cp)
    command.run(['where', 'wrong', 'number', 'of', 'args'])

    def nest_me(cp, command, i):
        import inspect
        if i > 1:
            cp.curframe = inspect.currentframe()
            cp.stack, cp.curindex = cmdproc.get_stack(cp.curframe, None, None,
                                                      cp)
            print '-' * 10
            command.run(['where'])
            print '-' * 10
            command.run(['where', '1'])
        else:
            nest_me(cp, command, i+1)
        return
    def ignore_me(cp, command, i):
        print '=' * 10
        nest_me(cp, command, 1)
        print '=' * 10
        cp.core.add_ignore(ignore_me)
        nest_me(cp, command, 1)
        return
    cp.forget()
    command.run(['where'])
    print '-' * 10
    ignore_me(cp, command, 1)
    command.run(['where', '1'])
    print '-' * 10
    command.run(['where', '-1'])
    print '-' * 10
    command.run(['where', '3'])
    print '-' * 10
    command.run(['where', '-2'])
    print '-' * 10
    pass

