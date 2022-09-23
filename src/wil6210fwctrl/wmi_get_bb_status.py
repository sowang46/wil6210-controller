from wmi_basic import *

class WmiGetBbStatus(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### Get bb status

    # <EnumValue publishFW="False" publishLinux="False" publishWin="False" name="UT_MODULE_SYSTEM_API" value="0xa"/>
    # 	<Enum comment="System API Commands" name="WMI_UT_MODULE_SYSTEM_API_CMD" publishFW="True" publishLinux="True" publishWin="True">
    # 		<EnumValue name="hw_sysapi_get_bb_status_block_1" publishFW="True" publishLinux="True" publishWin="True" value="0x11"/>
    # 		<EnumValue name="hw_sysapi_get_bb_status_block_2" publishFW="True" publishLinux="True" publishWin="True" value="0x12"/>
    
    # <Struct comment="hw_sysapi_get_bb_status_block_2" name="hw_sysapi_get_bb_status_block_2" publishFW="True" publishLinux="True" publishWin="True" type="event" module="UT_MODULE_SYSTEM_API">

    # </Struct>
		
    WMI_CMDID = 0x0900
    WMI_EVENTID = 0x1900
    cmd_args = [
    ]
    event_args = [
    ]
    
    @classmethod
    def cmdDefault(self):
        cmd = self.wmi_get_cmd(self.cmd_args)
        return cmd
    
    @classmethod
    def call(self, fw, cmd=None):
        if cmd is None:
            cmd = self.cmdDefault()
            
        ############# block1
        cmd_args_block1 = [('module_id', 2),
            ('ut_subtype_id', 2),
        ]
        event_args_block1 = [('module_id', 2),
            ('ut_subtype_id', 2),
        	('res', 4),
        	('fw_version_major', 4),
        	('fw_version_minor', 4),
        	('fw_version_sub_minor', 4),
        	('fw_version_build', 4),
        	('bootloader_version', 4),
        	('bb_revision', 2),
        	('rf_revision', 2),
        	('burned_boardfile', 4),
        	('fw_type', 4),
        	('rf_status', 4),
        	('fw_status', 4),
        	('channel', 4),
        	('work_mode', 4),
        	('attached_rf_vector', 1),
        	('enabled_rf_vector', 1),
        	('xif_gc', 1),
        	('gc_ctrl', 1),
        	('stg2_ctrl', 1),
        	('reserved1', 0),
        ]
        
        cmd_block1 = self.wmi_get_cmd(cmd_args_block1)
        cmd_block1['module_id'] = 0xa
        cmd_block1['ut_subtype_id'] = 0x11
        cmd_data_block1 = fw.wmi_encode_cmd(cmd_block1, cmd_args_block1)
        
        WMI_EVENT_DATA = fw.wmi_call(self.WMI_CMDID, 
                                     cmd_data_block1,
                                     self.WMI_EVENTID, 5, 20)
                                            
        wmi_evt = fw.wmi_decode_event(event_args_block1, WMI_EVENT_DATA)
        print 'wmi_evt', wmi_evt
        print ''
        #############
        
        ############# block2
        cmd_args_block2 = [('module_id', 2),
            ('ut_subtype_id', 2),
        ]
        event_args_block2 = [('module_id', 2),
            ('ut_subtype_id', 2),
        	('res', 4),
        	('m_tx_params', 4),
        	('tx_digial_atten_i', 1),
        	('tx_digial_atten_q', 1),
        	('reserved1', 2),
        	('lo_leak_correction', 4),
        	('tx_gain_row', 1),
        	('tx_gain_row_force_enable', 1),
        	('tx_gain_row_force_value', 1),
        	('reserved2', 1),
        	('tx_swap_iq', 4),
        	('debug_packets_active', 1),
        	('reserved3', 1),
        	('num_debug_packets', 2),
        	('debug_packets_mcs', 1),
        	('reserved4_1', 1),
        	('reserved4_2', 2),
        	('debug_packets_length', 4),
        	('silence_between_packets', 4),
        	('tone_transmitted', 1),
        	('tone_mode', 1),
        	('tone_max_value', 1),
        	('reserved5', 1),
        	('tone_frequency_a', 2),
        	('tone_frequency_b', 2),
        	('m_rx_params', 4),
        	('zero_db_row', 1),
        	('agc_start_row', 1),
        	('agc_final_row', 1),
        	('rx_gain_row_force_enable', 1),
        	('rx_gain_row_force_value', 1),
        	('reserved6_1', 1),
        	('reserved6_2', 2),
        	('digital_post_channel_corrections', 4),
        	('digital_iq_correction_w1', 4),
        	('digital_iq_correction_w2', 4),
        ]
        
        cmd_block2 = self.wmi_get_cmd(cmd_args_block2)
        cmd_block2['module_id'] = 0xa
        cmd_block2['ut_subtype_id'] = 0x12
        cmd_data_block2 = fw.wmi_encode_cmd(cmd_block2, cmd_args_block2)
        
        WMI_EVENT_DATA = fw.wmi_call(self.WMI_CMDID, 
                                     cmd_data_block2,
                                     self.WMI_EVENTID, 5, 20)
                                            
        wmi_evt = fw.wmi_decode_event(event_args_block2, WMI_EVENT_DATA)
        print 'wmi_evt', wmi_evt
        print ''
        #############
        
        return wmi_evt