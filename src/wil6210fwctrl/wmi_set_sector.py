from wmi_basic import *

class WmiSetSector(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### WMI_SET_SELECTED_RF_SECTOR_INDEX_CMDID
    WMI_CMDID = 0x9A3
    WMI_EVENTID = 0x19A3
    cmd_args = [('cid', 1),
        ('sector_type', 1),
        ('sector_idx', 2),
    ]
    event_args = [('status', 1), 
        ('reserved', 0),
    ]
    
    @classmethod
    def cmdDefault(self):
        cmd = self.wmi_get_cmd(self.cmd_args)
        cmd['cid'] = 0
        cmd['sector_type'] = 1
        cmd['sector_idx'] = 2
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