from wmi_basic import *

class WmiSetSectorNumber(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### Set sector number
    WMI_PRIO_TX_SECTORS_NUMBER_CMDID = 0x9A6
    WMI_PRIO_TX_SECTORS_NUMBER_EVENTID = 0x19A5
    cmd_sector_number_args = [('beacon_number_of_sectors', 1), # [0-128], 0 = No changes
        ('txss_number_of_sectors', 1), # [0-128], 0 = No changes
        ('cid', 1), # [0-8] needed only for TXSS configuration
    ]
    event_sector_number_args = [('status', 1),
    ]
    
    @classmethod
    def cmdDefault(self):
        cmd = self.wmi_get_cmd(self.cmd_sector_number_args)
        cmd['beacon_number_of_sectors'] = 10
        cmd['txss_number_of_sectors'] = 0
        cmd['cid'] = 0
        return cmd
    
    @classmethod
    def call(self, fw, cmd=None):
        if cmd is None:
            cmd = self.cmdDefault()
        cmd_data = fw.wmi_encode_cmd(cmd, self.cmd_sector_number_args)
        
        WMI_EVENT_DATA = fw.wmi_call(self.WMI_PRIO_TX_SECTORS_NUMBER_CMDID, 
                                     cmd_data,
                                     self.WMI_PRIO_TX_SECTORS_NUMBER_EVENTID, 5, 50)
                                            
        # print WMI_EVENT_DATA
        wmi_evt = fw.wmi_decode_event(self.event_sector_number_args, WMI_EVENT_DATA)
        print 'wmi_evt', wmi_evt
        return wmi_evt