from wmi_basic import *

class WmiGetBfStats(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### get beamforming statistics
    WMI_CMDID = 0x0900
    WMI_EVENTID = 0x1900
    cmd_args = [('module_id', 2),
        ('ut_subtype_id', 2),
        ('station_id', 1),
    ]
    event_args = [('module_id', 2),
        ('ut_subtype_id', 2),
        ('res', 4),
        ('bf_result', 1),
        ('bf_stage', 1),
        ('bf_state', 1),
        ('bf_sub_state', 1),
        ('number_of_received_tx_sectors', 1),
        ('index_of_tx_sector_remote', 1),
        ('index_of_tx_sector_local', 1),
        ('reserved', 1),
        ('snr_of_tx_sector_remote', 4),
        ('snr_of_tx_sector_local', 4),
        ('received_tx_sectors_bitmap_LSB', 8),
        ('received_tx_sectors_bitmap_MSB', 8),
        ('brp_snr', 4),
        ('brp_number_of_antennas', 2),
        ('rx_brp_sector', 2),
        ('bf_done_tsf_low', 4),
    ]
    
    @classmethod
    def cmdDefault(self):
        cmd = self.wmi_get_cmd(self.cmd_args)
        cmd['module_id'] = 0xa
        cmd['ut_subtype_id'] = 0x15
        cmd['station_id'] = 0
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