from wmi_basic import *

class WmiFwVer(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### FW_VER
    WMI_CMDID = 0xF04E
    WMI_EVENTID = 0x9004
    cmd_args = []
    event_args = [('fw_major', 4), 
        ('fw_minor', 4), 
        ('fw_subminor', 4), 
        ('fw_build', 4),
        ('hour', 4), 
        ('minute', 4), 
        ('second', 4), 
        ('day', 4), 
        ('month', 4), 
        ('year', 4), 
        ('bl_major', 4),
        ('bl_minor', 4),
        ('bl_subminor', 4),
        ('bl_build', 4),
        ('fw_capabilities_len', 1),
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