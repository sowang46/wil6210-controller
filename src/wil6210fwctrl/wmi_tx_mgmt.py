from wmi_basic import *

class WmiTxMgmt(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### WMI_SW_TX_REQ_CMDID
    WMI_CMDID = 0x82B
    WMI_EVENTID = 0x182B
    cmd_args = [('dst_mac', 6),
        ('len', 2),
        ('payload', -1)
    ]
    event_args = [('status', 1),
        ('reserved', 0)
    ]
    
    @classmethod
    def cmdDefault(self):
        cmd = self.wmi_get_cmd(self.cmd_args)
        cmd['dst_mac'] = '04CE14073F5A3A'
        cmd['len'] = 32
        cmd['payload'] = '0000000000000000000000000000000000000000000000000000000000000000'
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