from wmi_basic import *

class WmiRxMode(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### hw_sysapi_enter_rx_mode
    
    WMI_CMDID = 0x0900
    WMI_EVENTID = 0x1900
    cmd_args = [('module_id', 2),
        ('ut_subtype_id', 2),
        ('enable', 4),
        ('no_detection_mode', 4),
        ('rf_sector_id', 2),
        ('rf_gain_index,', 2),
        ('rx_bb_gain_row_num', 2),
    ]
    event_args = [('module_id', 2),
        ('ut_subtype_id', 2),
        ('res', 4),
    ]
    
    @classmethod
    def cmdDefault(self):
        cmd = self.wmi_get_cmd(self.cmd_args)
        cmd['module_id'] = 0xa
        cmd['ut_subtype_id'] = 0xe
        cmd['enable'] = 1
        cmd['no_detection_mode'] = 1
        cmd['rf_sector_id'] = 63
        cmd['rf_gain_index'] = 1
        cmd['rx_bb_gain_row_num'] = 1
        
        return cmd
    
    @classmethod
    def call(self, fw, cmd=None):
        if cmd is None:
            cmd = self.cmdDefault()
        cmd_data = fw.wmi_encode_cmd(cmd, self.cmd_args)
        
        WMI_EVENT_DATA = fw.wmi_call(self.WMI_CMDID, 
                                     cmd_data,
                                     self.WMI_EVENTID, 5, 20)
                                            
        # print WMI_EVENT_DATA
        wmi_evt = fw.wmi_decode_event(self.event_args, WMI_EVENT_DATA)
        print 'wmi_evt', wmi_evt
        return wmi_evt