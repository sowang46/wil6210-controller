from wmi_basic import *
import struct

class WmiGetRSSI(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### get rssi
    WMI_CMDID = 0x0900
    WMI_EVENTID = 0x1900
    cmd_args = [('module_id', 2),
        ('ut_subtype_id', 2),
    ]
    event_args = [('module_id', 2),
        ('ut_subtype_id', 2),
        ('res', 4),
        ('rssi_adc', 4),
        ('rssi_antenna', 4),
        ('reserved', 0),
    ]
    
    @classmethod
    def cmdDefault(self):
        cmd = self.wmi_get_cmd(self.cmd_args)
        cmd['module_id'] = 0xa
        cmd['ut_subtype_id'] = 0x1
        return cmd
    
    @classmethod
    def call(self, fw, cmd=None):
        if cmd is None:
            cmd = self.cmdDefault()
        cmd_data = fw.wmi_encode_cmd(cmd, self.cmd_args)
        
        WMI_EVENT_DATA = fw.wmi_call(self.WMI_CMDID, 
                                     cmd_data,
                                     self.WMI_EVENTID, 3)
                                            
        # print WMI_EVENT_DATA
        wmi_evt = fw.wmi_decode_event(self.event_args, WMI_EVENT_DATA)
        print wmi_evt['res'], wmi_evt['rssi_adc'], struct.unpack('i', struct.pack('I', wmi_evt['rssi_antenna']))[0]
        return wmi_evt