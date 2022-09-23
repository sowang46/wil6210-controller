from wmi_basic import *

class WmiPhyTx(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### hwf_phy_tx_self_transmit_w_mcs_gain
    WMI_CMDID = 0x0900
    WMI_EVENTID = 0x1900
    cmd_args = [('module_id', 2),
        ('ut_subtype_id', 2),
        ('nFrames', 4),
        ('phy_tx_silence_duration', 4),
        ('phy_tx_plcp_mcs,', 4),
        ('phy_tx_plcp_length', 4),
    ]
    event_args = [('module_id', 2),
        ('ut_subtype_id', 2),
        ('res', 4),
        ('reserved', 0),
    ]
    
    @classmethod
    def cmdDefault(self):
        cmd = self.wmi_get_cmd(self.cmd_args)
        cmd['module_id'] = 0x9
        cmd['ut_subtype_id'] = 0x305
        cmd['nFrames'] = 10
        cmd['phy_tx_silence_duration'] = 1
        cmd['phy_tx_plcp_mcs'] = 1
        cmd['phy_tx_plcp_length'] = 1000
        
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