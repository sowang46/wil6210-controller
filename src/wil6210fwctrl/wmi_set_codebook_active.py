from wmi_basic import *

class WmiSetCodebookActive(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### set codebook active
    WMI_CMDID = 0x0
    WMI_EVENTID = 0x0
    cmd_args = [('codebook_idx', 4),
        ('rf_modules_vec', 1),
        ('store_data', 2),
    ]
    event_args = [
    ]
    
    codebook_start_addr = 0x008fe000
    
    fw_priv_data = 'codebook_data'
    
    @classmethod
    def cmdDefault(self):
        cmd = self.wmi_get_cmd(self.cmd_args)
        cmd['codebook_idx'] = 0
        cmd['rf_modules_vec'] = 0x1
        cmd['store_data'] = 0
        return cmd
    
    @classmethod
    def call(self, fw, cmd=None):
        if cmd is None:
            cmd = self.cmdDefault()

        if not cmd['store_data']:
            try:
                from wmi_set_pattern import WmiSetPattern
                # Reuse set-pattern API to trigger codebook reload
                wmi_evt = fw.caller(WmiSetPattern, 
                                    WmiSetPattern.setCmdArgs({'sector_idx':cmd['codebook_idx'],
                                    }))
            except:
                wmi_evt = [1]
                pass
        else:
            if self.fw_priv_data not in fw.priv_data.keys():
                return ['codebook data not found']
            
            if cmd['codebook_idx'] not in fw.priv_data[self.fw_priv_data].keys():
                return ['codebook index not found']
            
            codebook_data = fw.priv_data[self.fw_priv_data][cmd['codebook_idx']]
            
            data_list = [0] * (128*6 + 1)
            
            data_list[0] = cmd['rf_modules_vec']
            for idx in range(0, len(codebook_data)):
                entry_offset = 6*codebook_data[idx][0]
                data_list[entry_offset + 1] = codebook_data[idx][1]
                data_list[entry_offset + 2] = codebook_data[idx][2]
                data_list[entry_offset + 3] = codebook_data[idx][3]
                data_list[entry_offset + 4] = codebook_data[idx][4]
                data_list[entry_offset + 5] = codebook_data[idx][5]
                data_list[entry_offset + 6] = codebook_data[idx][6]
                
            fw.mem_block_write(self.codebook_start_addr-4, data_list)
            
            try:
                from wmi_set_pattern import WmiSetPattern
                # Reuse set-pattern API to trigger codebook reload
                wmi_evt = fw.caller(WmiSetPattern, 
                                    WmiSetPattern.setCmdArgs({'sector_idx':1,'rf_modules_vec':cmd['rf_modules_vec'],
                                    }))
            except:
                wmi_evt = [1]
                pass

        return wmi_evt
