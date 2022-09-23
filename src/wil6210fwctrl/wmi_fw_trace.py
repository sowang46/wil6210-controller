from wmi_basic import *
from wil6210_mbc_platform import *
import cPickle as pickle

class WmiFwTrace(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### FW_TRACE
    WMI_CMDID = 0x0
    WMI_EVENTID = 0x0
    cmd_args = [('log_addr', 4),
        ('log_size', 4),
        ('print', 4),
        ('write', 4),
        ('log_name', 0),
    ]
    event_args = [
    ]
    level = ['E', 'W', 'I', 'V']
    
    @classmethod
    def cmdDefault(self):
        cmd = self.wmi_get_cmd(self.cmd_args)
        cmd['log_addr'] = 0x90B900
        cmd['log_size'] = 1024
        cmd['print'] = 1
        cmd['write'] = 0
        cmd['log_name'] = 'fw_trace_log.txt'
        return cmd
    
    @classmethod
    def call(self, fw, cmd=None):
        if cmd is None:
            cmd = self.cmdDefault()
        
        while True:
            log_list = wil6210_mbc.get_fw_trace(cmd['log_addr'], cmd['log_size'], fw.get_off_virt())
            log_to_addr = pickle.load(open("./wil6210fwctrl/data/log_to_addr_fw6_2_0_40.p", "rb"))
            s_all = []
            for lg in log_list:
                s = ''
                if lg[3] in log_to_addr.keys():
                    if log_to_addr[lg[3]][1]:
                        try:
                            if lg[4] == 1:
                                s = ('[%6d] %s: %s: %s' % (lg[0], self.level[lg[2]], log_to_addr[lg[3]][0], log_to_addr[lg[3]][1])) % (lg[5])
                            elif lg[4] == 2:
                                s = ('[%6d] %s: %s: %s' % (lg[0], self.level[lg[2]], log_to_addr[lg[3]][0], log_to_addr[lg[3]][1])) % (lg[5], lg[6])
                            elif lg[4] == 3:
                                s = ('[%6d] %s: %s: %s' % (lg[0], self.level[lg[2]], log_to_addr[lg[3]][0], log_to_addr[lg[3]][1])) % (lg[5], lg[6], lg[7])
                            else:
                                s = '[%6d] %s: %s: %s' % (lg[0], self.level[lg[2]], log_to_addr[lg[3]][0], log_to_addr[lg[3]][1])
                        except Exception as e:
                            s = '[%6d] %s: %s: %s, %d, %d, %d' % (lg[0], self.level[lg[2]], log_to_addr[lg[3]][0], log_to_addr[lg[3]][1], lg[5], lg[6], lg[7])
                    else:
                        s = '[%6d] %s: %s: %d, %d, %d' % (lg[0], self.level[lg[2]], log_to_addr[lg[3]][0], lg[5], lg[6], lg[7])
                else:
                    s = '[%6d] %s: 0x%02x: %d, %d, %d' % (lg[0], self.level[lg[2]], lg[3], lg[5], lg[6], lg[7])
                
                if cmd['print']:
                    print s
                s_all.append(s)
            
            if cmd['write'] and s_all:
                with open(cmd['log_name'], 'a') as f:
                    for s in s_all:
                        f.write(s+'\n')

            fw.usleep(100000)

        return [[]]