from wmi_basic import *
import binascii
import sys

class WmiMemDump(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### memory dump
    WMI_CMDID = 0x0
    WMI_EVENTID = 0x0
    cmd_args = [('addr', 4),
        ('size', 4),
        ('highlight', 1),
        ('dump', 1)
    ]
    event_args = [('data', 4),
    ]
    old_data = ''
    
    @classmethod
    def cmdDefault(self):
        cmd = self.wmi_get_cmd(self.cmd_args)
        cmd['addr'] = 0
        cmd['size'] = 4
        cmd['highlight'] = 0
        cmd['dump'] = 0
        return cmd
    
    @classmethod
    def call(self, fw, cmd=None):
        if cmd is None:
            cmd = self.cmdDefault()
        wmi_evt = fw.mem_dump(cmd['addr'], cmd['size'])
        
        if cmd['dump'] > 0:
            f= open("dump.bin","w")
            f.write(wmi_evt)
            f.close
            return ''
        
        dump_data = binascii.hexlify(wmi_evt)
        g = 0
        l = 0
        for i in range(0, len(dump_data)):
            if i < len(self.old_data) and self.old_data[i] == dump_data[i]:
                sys.stdout.write(dump_data[i]),
            else:
                sys.stdout.write('\x1b[1;31;40m' + dump_data[i] + '\x1b[0m')
            g += 1
            if g >= 8:
                sys.stdout.write('  ')
                g = 0
            l += 1
            if l >= 64:
                print ''
                l = 0
        print ''
        self.old_data = dump_data
        return [dump_data]