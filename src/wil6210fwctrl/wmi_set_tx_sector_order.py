from wmi_basic import *
import struct

class WmiSetTxSectorOrder(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### WMI_PRIO_TX_SECTORS_ORDER
    WMI_CMDID = 0x9A5
    WMI_EVENTID = 0x19A5
    cmd_args = [('tx_sectors_priority_array', 0),
        ('sector_sweep_type', 1),
        ('cid', 1),
        ('reserved', 2)
    ]
    event_args = [('status', 1),
    ]
    
    @classmethod
    def cmdDefault(self):
        cmd = self.wmi_get_cmd(self.cmd_args)
        cmd['tx_sectors_priority_array'] = list(range(0, 64))
        cmd['sector_sweep_type'] = 0x1
        cmd['cid'] = 0
        return cmd
    
    @classmethod
    def call(self, fw, cmd=None):
        if cmd is None:
            cmd = self.cmdDefault()
        
        tx_sectors_priority_array = cmd['tx_sectors_priority_array']
        tx_sectors_priority_array.append(255)
        cmd['tx_sectors_priority_array'] = struct.pack('%dB' % len(tx_sectors_priority_array), 
                                                       *tx_sectors_priority_array)
        
        cmd_data = fw.wmi_encode_cmd(cmd, self.cmd_args)
        
        WMI_EVENT_DATA = fw.wmi_call(self.WMI_CMDID, 
                                     cmd_data,
                                     self.WMI_EVENTID, 5, 20)
                                            
        # print WMI_EVENT_DATA
        wmi_evt = fw.wmi_decode_event(self.event_args, WMI_EVENT_DATA)
        print 'wmi_evt', wmi_evt
        return wmi_evt