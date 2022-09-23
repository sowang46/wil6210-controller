from wmi_basic import *

class WmiStartScan(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    
    WMI_SET_SSID_CMDID = 0x827
    cmd_set_ssid_args = [('ssid_len', 4),
        ('ssid', 32), # max 32
    ]
    
    WMI_SET_APPIE_CMDID = 0x3F
    cmd_set_appie_args = [('mgmt_frm_type', 1),
        ('reserved', 1),
        ('ie_len', 2),
    ]

    WMI_CMDID = 0x07
    WMI_EVENTID = 0x100A
    cmd_args = [('mac_addr_h', 4),
                ('mac_addr_l', 2),
                ('discovery_mode', 1),
                ('reserved', 1),
                ('home_dwell_time', 4),
                ('force_scan_interval', 4),
                ('scan_type', 1),
                ('num_channel', 1),
                ('channel_list', 4),
    ]

    event_args = [('status', 4),
    ]
    
    @classmethod
    def cmdDefault(self):
        cmd = self.wmi_get_cmd(self.cmd_args)
        cmd['mac_addr_h'] = 0x0
        cmd['mac_addr_l'] = 0x0
        cmd['discovery_mode'] = 0x0
        cmd['reserved'] = 0x0
        cmd['home_dwell_time'] = 0x20 # ms
        cmd['force_scan_interval'] = 0x10 # ms
        cmd['scan_type'] = 0x00 # Active scan
        cmd['num_channel'] = 0x3
        cmd['channel_list'] = 0x000000010002 # 0-58320MHz  1-60480MHz   2-62640MHz
        return cmd
    
    @classmethod
    def call(self, fw, cmd=None):
        if cmd is None:
            cmd = self.cmdDefault()

        ## Set APPIE
        set_appie_cmd = self.wmi_get_cmd(self.cmd_set_appie_args)
        set_appie_cmd['mgmt_frm_type'] = 0x00
        set_appie_cmd['reserved'] = 0
        set_appie_cmd['ie_len'] = 0
        set_appie_cmd_data = fw.wmi_encode_cmd(set_appie_cmd, self.cmd_set_appie_args)

        fw.send_wmi(self.WMI_SET_APPIE_CMDID, set_appie_cmd_data)

        ## Set SSID
        # set_ssid_cmd = self.wmi_get_cmd(self.cmd_set_ssid_args)
        # set_ssid_cmd['ssid_len'] = 6
        # set_ssid_cmd['ssid'] = '717765717765'
        # set_ssid_cmd_data = fw.wmi_encode_cmd(set_ssid_cmd, self.cmd_set_ssid_args)
        
        # fw.send_wmi(self.WMI_SET_SSID_CMDID, set_ssid_cmd_data)
        # fw.usleep(200000)

        ## Start scan
        cmd_data = fw.wmi_encode_cmd(cmd, self.cmd_args)
        
        WMI_EVENT_DATA = fw.wmi_call(self.WMI_CMDID, 
                                     cmd_data,
                                     self.WMI_EVENTID, 3)
                                            
        # print WMI_EVENT_DATA
        wmi_evt = fw.wmi_decode_event(self.event_args, WMI_EVENT_DATA)
        print wmi_evt
        return wmi_evt