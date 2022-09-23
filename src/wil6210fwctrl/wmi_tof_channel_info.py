from wmi_basic import *

class WmiTofChannelInfo(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### WMI_TOF_CHANNEL_INFO_CMDID
    WMI_CMDID = 0x995
    cmd_args = [('channel_info_report_request', 4),
    ]
    WMI_EVENTID = 0x1996
    event_args = [('session_id', 4),
        ('dst_mac', 6),
        ('type', 1),
        ('len', 1),
        ('report', 0),
    ]
    
    @classmethod
    def cmdDefault(self):
        cmd = self.wmi_get_cmd(self.cmd_args)
        cmd['channel_info_report_request'] = 0x2
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