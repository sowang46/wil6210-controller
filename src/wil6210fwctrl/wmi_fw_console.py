from __future__ import print_function

import struct
from wmi_basic import *

class WmiFwConsole(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### fw console
    MY_CONSOLE_MAX_LEN = 8192
    MY_CONSOLE_BASE_PTR_FW = 0x8ffff0
    MY_CONSOLE_BASE_PTR_UC = 0x93fff0
    cmd_args = []
    event_args = []
    
    @classmethod
    def console_msg(self, addr, fw):
        console_ptr = struct.unpack('I', fw.mem_dump(addr, 4))[0]
        my_console_len = struct.unpack('I', fw.mem_dump(addr+4, 4))[0]
        
        if my_console_len < self.MY_CONSOLE_MAX_LEN:
            pass
            # print('console_ptr: %d' % console_ptr)
            # print('my_console_len: %d' % my_console_len)
        else:
            print('console len too big!')
            return None
        
        if console_ptr > 0:
            my_console = fw.mem_dump(console_ptr, my_console_len)
            return my_console
        else:
            print('console_ptr is null')
            return ""
    
    @classmethod
    def call(self, fw, cmd=None):
        fw_msg = self.console_msg(self.MY_CONSOLE_BASE_PTR_FW, fw)
        uc_msg = self.console_msg(self.MY_CONSOLE_BASE_PTR_UC, fw)
        
        print('FW Console: %s' % fw_msg, end='')
        print('UC Console: %s' % uc_msg, end='')
        
        return ['']