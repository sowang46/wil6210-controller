from wmi_basic import *

class WmiGetRfStatus(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### hw_sysapi_get_rf_status command
    WMI_CMDID = 0x0900
    WMI_EVENTID = 0x1900
    cmd_args = [('module_id', 2),
        ('ut_subtype_id', 2),
        ('rfc_id', 1),
    ]
    event_args = [('module_id', 2),
        ('ut_subtype_id', 2),
        ('res', 4),
        ('rfc_id', 4),
        ('rf_revision', 4),
        ('burned_boardfile', 4),
        ('rf_status', 4),
        ('rf_current_status', 4),
        ('current_sector_1', 4),
        ('current_sector_2', 4),
        ('current_sector_3', 4),
        ('current_sector_4', 4),
        ('current_sector_5', 4),
        ('current_sector_6', 4),
        ('lo_current_status_1', 4),
        ('lo_current_status_2', 4),
        ('lo_current_status_3', 4),
    ]
    
    @classmethod
    def cmdDefault(self):
        cmd = self.wmi_get_cmd(self.cmd_args)
        cmd['module_id'] = 0xa
        cmd['ut_subtype_id'] = 0x10
        cmd['rfc_id'] = 1
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
        print 'wmi_evt', wmi_evt
        return wmi_evt