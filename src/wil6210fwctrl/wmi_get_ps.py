from wmi_basic import *

class WmiGetPowerSave(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### WMI_PS_DEV_PROFILE_CFG_READ_CMDID
    WMI_CMDID = 0x942
    WMI_EVENTID = 0x1942
    cmd_args = [('reserved', 4)
    ]
    event_args = [('ps_profile', 1), 
        ('reserved', 3), 
    ]
    
    @classmethod
    def cmdDefault(self):
        cmd = self.wmi_get_cmd(self.cmd_args)
        return cmd
    
    @classmethod
    def call(self, fw, cmd=None):
        if cmd is None:
            cmd = self.cmdDefault()
        cmd_data = fw.wmi_encode_cmd(cmd, self.cmd_args)
        WMI_EVENT_DATA = fw.wmi_call(self.WMI_CMDID, 
                                     cmd_data,
                                     self.WMI_EVENTID, 5)
        
        # print WMI_EVENT_DATA
        wmi_evt = fw.wmi_decode_event(self.event_args, WMI_EVENT_DATA)
        # print wmi_evt
        return wmi_evt