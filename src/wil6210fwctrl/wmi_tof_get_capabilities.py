from wmi_basic import *

class WmiTofGetCapabilities(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### WMI_TOF_GET_CAPABILITIES_CMDID
    WMI_CMDID = 0x992
    WMI_EVENTID = 0x1992
    cmd_args = []
    event_args = [('ftm_capability', 1), 
        ('max_num_of_dest', 1), 
        ('max_num_of_meas_per_burst', 1),
        ('reserved', 1), 
        ('max_multi_bursts_sessions', 2), 
        ('max_ftm_burst_duration', 2),
        ('aoa_supported_types', 4), 
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
                                     self.WMI_EVENTID, 3)
        
        # print WMI_EVENT_DATA
        wmi_evt = fw.wmi_decode_event(self.event_args, WMI_EVENT_DATA)
        print wmi_evt
        return wmi_evt