from wmi_basic import *
from wil6210_mbc_platform import *
import binascii

class WmiSetPattern(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### WMI_SET_RF_SECTOR_PARAMS_CMDID
    description = 'Configure the beam pattern (antenna weights) of a given beam index.'
    
    WMI_CMDID = 0x9A1
    WMI_EVENTID = 0x19A1
    cmd_args = [('sector_idx', 2),
        ('sector_type', 1),
        ('rf_modules_vec', 1),
        ('mag', 32),
        ('phase', 32),
        ('amp', 8),
    ]
    wmi_set_rf_sector_params_cmd = [('sector_idx', 2),
        ('sector_type', 1),
        ('rf_modules_vec', 1),
        ('sectors_info', -1),
    ]
    event_args = [('status', 1),
    ]
    
    @classmethod
    def cmdDefault(self):
        cmd = self.wmi_get_cmd(self.cmd_args)
        cmd['sector_idx'] = 0
        cmd['sector_type'] = 0x01
        cmd['rf_modules_vec'] = 0x01
        cmd['mag'] = "00000000000000000000000000000000"
        cmd['phase'] = "00000000000000000000000000000000"
        cmd['amp'] = "00000000"
        return cmd
    
    @classmethod
    def call(self, fw, cmd=None):
        if cmd is None:
            cmd = self.cmdDefault()
        
        rf_sector_params = self.wmi_get_cmd(self.wmi_set_rf_sector_params_cmd)
        rf_sector_params['sector_idx'] = cmd['sector_idx']
        rf_sector_params['sector_type'] = cmd['sector_type']
        rf_sector_params['rf_modules_vec'] = cmd['rf_modules_vec']
        rf_sector_params['sectors_info'] = binascii.hexlify(wil6210_mbc.cfg_verify_convert(cmd['mag']+cmd['phase']+cmd['amp']))
        
        rf_sector_params_data = fw.wmi_encode_cmd(rf_sector_params, self.wmi_set_rf_sector_params_cmd)
        
        WMI_EVENT_DATA = fw.wmi_call(self.WMI_CMDID, 
                                     rf_sector_params_data,
                                     self.WMI_EVENTID, 5, 20)
                                            
        # print WMI_EVENT_DATA
        wmi_evt = fw.wmi_decode_event(self.event_args, WMI_EVENT_DATA)
        print 'wmi_evt', wmi_evt

        return wmi_evt