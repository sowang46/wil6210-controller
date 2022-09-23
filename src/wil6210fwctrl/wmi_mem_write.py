from wmi_basic import *
import binascii
import sys

class WmiMemWrite(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### memory write
    WMI_CMDID = 0x0
    WMI_EVENTID = 0x0
    cmd_args = [('addr', 4),
        ('val', 4),
    ]
    event_args = []
    
    @classmethod
    def cmdDefault(self):
        cmd = self.wmi_get_cmd(self.cmd_args)
        cmd['addr'] = 0
        cmd['val'] = 0
        return cmd
    
    @classmethod
    def call(self, fw, cmd=None):
        if cmd is None:
            cmd = self.cmdDefault()
        if cmd['addr'] > 0:
            if type(cmd['val']) is int:
                wmi_evt = fw.mem_write(cmd['addr'], cmd['val'])
            else:
                wmi_evt = fw.mem_block_write(cmd['addr'], cmd['val'])
            return [0]
        else:
            print 'Address is not specified.'
            return [1]
        