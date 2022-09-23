from wmi_basic import *
from wil6210_mbc_platform import *
import binascii
import struct

class WmiSetPattern2(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### hwd_rfc_write_sector
    description = 'Configure the beam pattern (antenna weights) of a given beam index.'
    
    WMI_CMDID = 0x0900
    WMI_EVENTID = 0x1900
    cmd_args = [('sector_idx', 4),
        ('is_tx_sector', 1),
        ('mag', 32),
        ('phase', 32),
        ('amp', 8),
        ('sector_gain_idx', 4),
    ]
    
    rfc_sector_dist_gain_args = [('module_id', 2),
        ('ut_subtype_id', 2),
        ('device_id', 1),
        ('sector_idx', 4),
        ('is_tx_sector', 1),
        ('psh_hi_val', 4),
        ('psh_lo_val', 4),
        ('etype0_val', 4),
        ('etype1_val', 4),
        ('etype2_val', 4),
        ('dtype_swch_off_val', 4),
        ('sector_gain_idx', 4),
    ]
    event_args = [('module_id', 2),
        ('ut_subtype_id', 2),
        ('res', 4)
    ]
    
    @classmethod
    def cmdDefault(self):
        cmd = self.wmi_get_cmd(self.cmd_args)
        cmd['sector_idx'] = 1
        cmd['sector_type'] = 1
        cmd['mag'] = "00000000000000000000000000000000"
        cmd['phase'] = "00000000000000000000000000000000"
        cmd['amp'] = "00000000"
        cmd['sector_gain_idx'] = 0xFF
        return cmd
    
    @classmethod
    def call(self, fw, cmd=None):
        if cmd is None:
            cmd = self.cmdDefault()
        
        rfc_sector_dist_gain_params = self.wmi_get_cmd(self.rfc_sector_dist_gain_args)
        rfc_sector_dist_gain_params['module_id'] = 0xc
        rfc_sector_dist_gain_params['ut_subtype_id'] = 0x514
        rfc_sector_dist_gain_params['device_id'] = 0
        rfc_sector_dist_gain_params['sector_idx'] = cmd['sector_idx']
        rfc_sector_dist_gain_params['is_tx_sector'] = cmd['sector_type']
        sectors_info = wil6210_mbc.cfg_verify_convert(cmd['mag']+cmd['phase']+cmd['amp'])
        sectors_val = struct.unpack('6I', sectors_info)
        rfc_sector_dist_gain_params['psh_hi_val'] = sectors_val[0]
        rfc_sector_dist_gain_params['psh_lo_val'] = sectors_val[1]
        rfc_sector_dist_gain_params['etype0_val'] = sectors_val[2]
        rfc_sector_dist_gain_params['etype1_val'] = sectors_val[3]
        rfc_sector_dist_gain_params['etype2_val'] = sectors_val[4]
        rfc_sector_dist_gain_params['dtype_swch_off_val'] = sectors_val[5]
        rfc_sector_dist_gain_params['sector_gain_idx'] = cmd['sector_gain_idx']
        
        rfc_sector_dist_gain_data = fw.wmi_encode_cmd(rfc_sector_dist_gain_params, 
                                                      self.rfc_sector_dist_gain_args)
        
        WMI_EVENT_DATA = fw.wmi_call(self.WMI_CMDID, 
                                     rfc_sector_dist_gain_data,
                                     self.WMI_EVENTID, 5, 10)
                                            
        # print WMI_EVENT_DATA
        wmi_evt = fw.wmi_decode_event(self.event_args, WMI_EVENT_DATA)
        print 'wmi_evt', wmi_evt

        return wmi_evt