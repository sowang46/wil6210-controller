from wmi_basic import *

class WmiGetSector(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### WMI_GET_SELECTED_RF_SECTOR_INDEX_CMDID
    WMI_CMDID = 0x9A2
    WMI_EVENTID = 0x19A2
    cmd_args = [('cid', 1),
        ('sector_type', 1),
        ('reserved', 2),
    ]
    event_args = [('sector_idx', 2), 
        ('status', 1), 
        ('reserved', 5),
        ('tsf', 8), 
    ]
    
    @classmethod
    def cmdDefault(self):
        cmd = self.wmi_get_cmd(self.cmd_args)
        cmd['cid'] = 0
        cmd['sector_type'] = 1 # wmi_rf_sector_type
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