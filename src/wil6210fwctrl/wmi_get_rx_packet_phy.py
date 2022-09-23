from wmi_basic import *

class WmiGetRxPacketPhy(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### get rx packet phy
    WMI_CMDID = 0x0900
    WMI_EVENTID = 0x1900
    cmd_args = [('module_id', 2),
        ('ut_subtype_id', 2),
        ('sta_id', 4),
        ('qid', 4),
        ('is_cp', 4),
        ('mcs', 4),
        ('is_omni', 4),
        ('timeout_usec', 4),
    ]
    event_args = [('module_id', 2),
        ('ut_subtype_id', 2),
        ('res', 4),
        ('tsf', 8),
        ('rssi_locked_adc', 4),
        ('rssi_locked_if', 4),
        ('rssi_locked_antenna', 4),
        ('snr_locked', 4),
        ('pkt_len', 4),
        ('pkt_freq_offset', 4),
        ('rx_sector', 4),
        ('rf_gain', 4),
        ('mcs', 0),
        ('reserved', 0),
    ]
    
    @classmethod
    def cmdDefault(self):
        cmd = self.wmi_get_cmd(self.cmd_args)
        cmd['module_id'] = 0xa
        cmd['ut_subtype_id'] = 0x4
        cmd['sta_id'] = 0
        cmd['qid'] = 0xff
        cmd['is_cp'] = 0xff
        cmd['mcs'] = 0xff
        cmd['is_omni'] = 0xff
        cmd['timeout_usec'] = 500
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
        print wmi_evt
        return wmi_evt