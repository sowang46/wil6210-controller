from wmi_basic import *

class WmiBeaconSend(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### Send beacons
    
    WMI_SET_SSID_CMDID = 0x827
    cmd_set_ssid_args = [('ssid_len', 4),
        ('ssid', 32), # max 32
    ]
    
    WMI_SET_APPIE_CMDID = 0x3F
    cmd_set_appie_args = [('mgmt_frm_type', 1),
        ('reserved', 1),
        ('ie_len', 2),
    ]
    
    WMI_CFG_RX_CHAIN_CMDID = 0x820
    WMI_CFG_RX_CHAIN_DONE_EVENTID = 0x1820
    cmd_cfg_rx_chain_args = [('misc', 54),
    ]
    event_cfg_rx_chain_args = [('rx_ring_tail_ptr', 4),
        ('status', 4),
    ]
    
    WMI_PCP_START_CMDID = 0x918
    WMI_PCP_STARTED_EVENTID = 0x1918
    cmd_args = [('bcon_interval', 2),
        ('pcp_max_assoc_sta', 1),
        ('hidden_ssid', 1),
        ('is_go', 1),
        ('reserved', 5),
        ('abft_len', 1),
        ('disable_ap_sme', 1),
        ('network_type', 1),
        ('channel', 1),
        ('disable_sec_offload', 1),
        ('disable_sec', 1),
    ]
    event_args = [('status', 1),
        ('reserved', 0),
    ]
    
    FAST_BI_ADDR = 0x0093eb00
    
    @classmethod
    def cmdDefault(self):
        cmd = self.wmi_get_cmd(self.cmd_args)
        cmd['bcon_interval'] = 100
        cmd['pcp_max_assoc_sta'] = 8
        cmd['hidden_ssid'] = 0
        cmd['is_go'] = 0
        cmd['reserved'] = '0000000000'
        cmd['abft_len'] = 0
        cmd['disable_ap_sme'] = 0
        cmd['network_type'] = 0x10
        cmd['channel'] = 1
        cmd['disable_sec_offload'] = 1
        cmd['disable_sec'] = 0
        cmd['beacon_number_of_sectors'] = 1
        return cmd
    
    @classmethod
    def call(self, fw, cmd=None):
        if cmd is None:
            cmd = self.cmdDefault()
        
        ## Config RF Chain
        if fw.get_fw_ver() == "4.1.0.55":
            cfg_rx_chain_cmd = self.wmi_get_cmd(self.cmd_cfg_rx_chain_args)
            cfg_rx_chain_cmd['misc'] = '00000000000001350000000000040008'+\
                                      '00000000000002000000000000000000'+\
                                      '80000100000000000000000000000000'+\
                                      '000000000000'
            cfg_rx_chain_cmd_data = fw.wmi_encode_cmd(cfg_rx_chain_cmd, self.cmd_cfg_rx_chain_args)
            WMI_EVENT_DATA = fw.wmi_call(self.WMI_CFG_RX_CHAIN_CMDID, 
                                         cfg_rx_chain_cmd_data,
                                         self.WMI_CFG_RX_CHAIN_DONE_EVENTID, TIME_OUT=5)
            # print WMI_EVENT_DATA
            fw.usleep(1000)
        
        ## Write BI
        print 'Set BI to:', cmd['bcon_interval']
        fw.mem_write(self.FAST_BI_ADDR, cmd['bcon_interval']*1024)
        
        ## Set SSID
        set_ssid_cmd = self.wmi_get_cmd(self.cmd_set_ssid_args)
        set_ssid_cmd['ssid_len'] = 6
        set_ssid_cmd['ssid'] = '717765717765'
        set_ssid_cmd_data = fw.wmi_encode_cmd(set_ssid_cmd, self.cmd_set_ssid_args)
        
        fw.send_wmi(self.WMI_SET_SSID_CMDID, set_ssid_cmd_data)
        fw.usleep(200000)
        
        ## Set APPID
        set_appie_cmd = self.wmi_get_cmd(self.cmd_set_appie_args)
        set_appie_cmd['mgmt_frm_type'] = 0x00
        set_appie_cmd['reserved'] = 0
        set_appie_cmd['ie_len'] = 0
        set_appie_cmd_data = fw.wmi_encode_cmd(set_appie_cmd, self.cmd_set_appie_args)
        
        fw.send_wmi(self.WMI_SET_APPIE_CMDID, set_appie_cmd_data)
        fw.usleep(200000)
        
        ## Set beacon number
        try:
            from wmi_set_sector_number import WmiSetSectorNumber
            fw.caller(WmiSetSectorNumber, 
                      WmiSetSectorNumber.setCmdArgs({'beacon_number_of_sectors':cmd['beacon_number_of_sectors']}))
        except:
            pass
        fw.usleep(200000)
        
        ## Start PCP
        cmd_data = fw.wmi_encode_cmd(cmd, self.cmd_args)
        WMI_EVENT_DATA = fw.wmi_call(self.WMI_PCP_START_CMDID, 
                                     cmd_data,
                                     self.WMI_PCP_STARTED_EVENTID, 15)
                                            
        # print WMI_EVENT_DATA
        wmi_evt = fw.wmi_decode_event(self.event_args, WMI_EVENT_DATA)
        print 'wmi_evt', wmi_evt
        return wmi_evt