from wmi_basic import *

class WmiAoaMeas(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### ECHO
    WMI_CMDID = 0x923
    WMI_EVENTID = 0x1923
    cmd_args = [('mac_addr', 6),
        ('channel', 1),
        ('aoa_meas_type', 1),
        ('rfs_mask', 4)
    ]
    event_args = [('mac_addr', 6),
        ('channel', 1),
        ('aoa_meas_type', 1),
        ('rfs_mask', 4),
        ('reserved', 1),
        ('length', 2),
        ('meas_data', 0)
    ]
    
    @classmethod
    def cmdDefault(self):
        cmd = self.wmi_get_cmd(self.cmd_args)
        cmd['mac_addr'] = '4066414F9815'
        cmd['channel'] = 1
        cmd['aoa_meas_type'] = 0x01
        cmd['rfs_mask'] = 1
        return cmd
    
    @classmethod
    def call(self, fw, cmd=None):
        if cmd is None:
            cmd = self.cmdDefault()
        cmd_data = fw.wmi_encode_cmd(cmd, self.cmd_args)
        
        WMI_EVENT_DATA = fw.wmi_call(self.WMI_CMDID, 
                                     cmd_data,
                                     self.WMI_EVENTID, 10)
                                            
        # print WMI_EVENT_DATA
        wmi_evt = fw.wmi_decode_event(self.event_args, WMI_EVENT_DATA)
        print 'wmi_evt', wmi_evt
        return wmi_evt