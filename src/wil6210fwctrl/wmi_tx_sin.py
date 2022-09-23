from wmi_basic import *

class WmiTxSin(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### Transmit sine tone
    
    # <EnumValue publishFW="False" publishLinux="False" publishWin="False" name="UT_MODULE_DRIVERS" value="0xc"/>
    # 	<Enum comment="Drivers Commands" name="WMI_UT_MODULE_DRIVERS_CMD" publishFW="True" publishLinux="True" publishWin="True">
    # 		<EnumValue name="hwd_phy_tx_singen_config" publishFW="True" publishLinux="True" publishWin="True" value="0x409"/>
    # 		<EnumValue name="hwd_phy_tx_singen_transmit" publishFW="True" publishLinux="True" publishWin="True" value="0x40a"/>
    
    # <EnumValue publishFW="False" publishLinux="False" publishWin="False" name="UT_MODULE_SYSTEM_API" value="0xa"/>
    # 	<Enum comment="System API Commands" name="WMI_UT_MODULE_SYSTEM_API_CMD" publishFW="True" publishLinux="True" publishWin="True">
    # 		<EnumValue name="hw_sysapi_enter_tx_mode" publishFW="True" publishLinux="True" publishWin="True" value="0xD"/>
			
    WMI_CMDID = 0x0900
    WMI_EVENTID = 0x1900
    cmd_args = [('freq_a_mhz', 4),
        ('freq_b_mhz', 4),
    ]
    event_args = [
    ]
    
    @classmethod
    def cmdDefault(self):
        cmd = self.wmi_get_cmd(self.cmd_args)
        cmd['freq_a_mhz'] = 200
        cmd['freq_b_mhz'] = 700
        return cmd
    
    @classmethod
    def call(self, fw, cmd=None):
        if cmd is None:
            cmd = self.cmdDefault()
            
        ############# tx mode
        cmd_args_tx_mode = [('module_id', 2),
            ('ut_subtype_id', 2),
            ('enable', 4),
            ('rf_sector_id', 2),
            ('rf_gain_index', 2),
            ('tx_bb_gain_row_num', 2),
            ('mcs', 2),
        ]
        event_args_tx_mode = [('module_id', 2),
            ('ut_subtype_id', 2),
            ('res', 4),
        ]
        
        cmd_tx_mode = self.wmi_get_cmd(cmd_args_tx_mode)
        cmd_tx_mode['module_id'] = 0xa
        cmd_tx_mode['ut_subtype_id'] = 0xd
        cmd_tx_mode['enable'] = 1
        cmd_tx_mode['rf_sector_id'] = 63
        cmd_tx_mode['rf_gain_index'] = 1
        cmd_tx_mode['tx_bb_gain_row_num'] = 1
        cmd_tx_mode['mcs'] = 1
        cmd_data_tx_mode = fw.wmi_encode_cmd(cmd_tx_mode, cmd_args_tx_mode)
        
        WMI_EVENT_DATA = fw.wmi_call(self.WMI_CMDID, 
                                     cmd_data_tx_mode,
                                     self.WMI_EVENTID, 5, 20)
                                            
        wmi_evt = fw.wmi_decode_event(event_args_tx_mode, WMI_EVENT_DATA)
        print 'wmi_evt', wmi_evt
        #############
            
        ############# singen config
        cmd_args_singen_config = [('module_id', 2),
            ('ut_subtype_id', 2),
            ('tx_singen_freq_a_mhz', 4),
            ('tx_singen_freq_b_mhz', 4),
            ('tx_singen_config', 1),
        ]
        event_args_singen_config = [('module_id', 2),
            ('ut_subtype_id', 2),
            ('res', 4),
        ]
        
        cmd_singen_config = self.wmi_get_cmd(cmd_args_singen_config)
        cmd_singen_config['module_id'] = 0xc
        cmd_singen_config['ut_subtype_id'] = 0x409
        cmd_singen_config['tx_singen_freq_a_mhz'] = cmd['freq_a_mhz']
        cmd_singen_config['tx_singen_freq_b_mhz'] = cmd['freq_b_mhz']
        cmd_singen_config['tx_singen_config'] = 7
        cmd_data_singen_config = fw.wmi_encode_cmd(cmd_singen_config, cmd_args_singen_config)
        
        WMI_EVENT_DATA = fw.wmi_call(self.WMI_CMDID, 
                                     cmd_data_singen_config,
                                     self.WMI_EVENTID, 5, 20)
                                            
        wmi_evt = fw.wmi_decode_event(event_args_singen_config, WMI_EVENT_DATA)
        print 'wmi_evt', wmi_evt
        #############
        
        ############# singen transmit
        cmd_args_singen_transmit = [('module_id', 2),
            ('ut_subtype_id', 2),
            ('start_stop_val', 1),
        ]
        event_args_singen_transmit = [('module_id', 2),
            ('ut_subtype_id', 2),
            ('res', 4),
        ]
        
        cmd_singen_transmit = self.wmi_get_cmd(cmd_args_singen_transmit)
        cmd_singen_transmit['module_id'] = 0xc
        cmd_singen_transmit['ut_subtype_id'] = 0x40a
        cmd_singen_transmit['start_stop_val'] = 1
        cmd_data_singen_transmit = fw.wmi_encode_cmd(cmd_singen_transmit, cmd_args_singen_transmit)
        
        WMI_EVENT_DATA = fw.wmi_call(self.WMI_CMDID, 
                                     cmd_data_singen_transmit,
                                     self.WMI_EVENTID, 5, 20)
                                            
        wmi_evt = fw.wmi_decode_event(event_args_singen_transmit, WMI_EVENT_DATA)
        print 'wmi_evt', wmi_evt
        #############
        
        return wmi_evt