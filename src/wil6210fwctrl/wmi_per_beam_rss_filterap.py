from wmi_basic import *
import struct

class WmiSetBeamRssApFilter(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### set the ap filter for rss measurement
    
    cmd_args = [('mac_list', 4),
        ('mem_addr', 4)
    ]
    
    @classmethod
    def cmdDefault(self):
        cmd = self.wmi_get_cmd(self.cmd_args)
        cmd['mac_list'] = []
        cmd['mem_addr'] = 0x93cb00
        return cmd
    
    @classmethod
    def call(self, fw, cmd=None):
        if cmd is None:
            cmd = self.cmdDefault()
            
        ap_num = len(cmd['mac_list'])
        pad_num = 0
        if ap_num:
            mac_val = struct.pack('%dB' % ap_num, *cmd['mac_list'])
            if ap_num % 4:
                pad_num = 4-(ap_num%4)
                mac_val += struct.pack('%dB' % pad_num, *([0]*pad_num))
            
            mem_val = struct.unpack('>%dI' % ((ap_num+pad_num)/4), mac_val)
            
            c = 1
            for val in mem_val:
                fw.mem_write(cmd['mem_addr'] - c * 4, val)
                c += 1
            
        return [1]