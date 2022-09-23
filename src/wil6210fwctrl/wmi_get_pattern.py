from wmi_basic import *
from wil6210_mbc_platform import *
import binascii
import math

class WmiGetPattern(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### WMI_GET_RF_SECTOR_PARAMS_CMDID
    WMI_CMDID = 0x9A0
    WMI_EVENTID = 0x19A0
    cmd_args = [('sector_idx', 2),
        ('sector_type', 1),
        ('rf_modules_idx', 1),
    ]
    event_args = [('status', 1), 
        ('reserved', 7),
        ('tsf', 8),
        ('sectors_info', 0),
    ]
    wmi_rf_sector_info = [('psh_hi', 4),
        ('psh_lo', 4),
        ('etype0', 4),
        ('etype1', 4),
        ('etype2', 4),
        ('dtype_swch_off', 4),
    ]
    
    @classmethod
    def cmdDefault(self):
        cmd = self.wmi_get_cmd(self.cmd_args)
        cmd['sector_idx'] = 0
        cmd['sector_type'] = 0x01 # wmi_rf_sector_type
        cmd['rf_modules_idx'] = 0
        return cmd
    
    @classmethod
    def call(self, fw, cmd=None):
        if cmd is None:
            cmd = self.cmdDefault()
        
        rf_modules_idx = cmd['rf_modules_idx']
        # convert to rf_modules_vec
        cmd['rf_modules_idx'] = int(math.pow(2, cmd['rf_modules_idx']))
        cmd_data = fw.wmi_encode_cmd(cmd, self.cmd_args)
        
        WMI_EVENT_DATA = fw.wmi_call(self.WMI_CMDID, 
                                     cmd_data,
                                     self.WMI_EVENTID, 3)
        
        # print WMI_EVENT_DATA
        wmi_evt = fw.wmi_decode_event(self.event_args, WMI_EVENT_DATA)
        print 'wmi_evt:', wmi_evt
        sectors_info = fw.wmi_decode_event(self.wmi_rf_sector_info, wmi_evt['sectors_info'][rf_modules_idx*48:])
        print 'sectors_info:', sectors_info
        sector_decode = wil6210_mbc.convert_sector_cfg(binascii.unhexlify(wmi_evt['sectors_info'][rf_modules_idx*48:]))
        sectors_info['mag'] = sector_decode[0:32]
        sectors_info['phase'] = sector_decode[32:64]
        sectors_info['amp'] = sector_decode[64:72]
        return sectors_info