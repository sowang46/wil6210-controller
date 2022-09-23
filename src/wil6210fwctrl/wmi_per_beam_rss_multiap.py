import struct
from wmi_basic import *

class WmiGetBeamRssMultiAp(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### get per-beam rss from beacon frame (version 4.2)
    
    rss_mem_addr = {"6.2.0.40":0x008FC000,
                    "4.1.0.55":0x008FC000,
    }
    cmd_args = [('tail_ptr', 4),
        ('rss_mem_addr', 4),
        ('storage_size', 4),
        ('head_ptr_offset', 4),
        ('ap_num', 4),
        ('beam_num', 4),
    ]
    
    @classmethod
    def cmdDefault(self):
        cmd = self.wmi_get_cmd(self.cmd_args)
        cmd['beam_num'] = 64
        cmd['tail_ptr'] = None
        cmd['rss_mem_addr'] = 0x008FC000
        cmd['storage_size'] = 28
        cmd['head_ptr_offset'] = 0
        cmd['ap_num'] = 1
        return cmd
    
    @classmethod
    def load_parse_data(self, base_addr, val, cmd, tail_ptr_all):
        data = []
        for beam_idx in range(0, cmd['beam_num']):
            offset = beam_idx * (cmd['storage_size'] + 4)
            counter = val[offset]
            timestamp = val[offset+1]
            head_ptr = val[offset+2] + cmd['head_ptr_offset']
            mac_addr = val[offset+3]
            tail_ptr = tail_ptr_all[beam_idx]
            
            data_start_addr = base_addr + (offset+4)*4
            data_end_addr = base_addr + (offset+4+cmd['storage_size'])*4
            beam_rss_snr = list(val[offset + 4 : offset + 4 + cmd['storage_size']])
            
            beam_rss = []
            beam_snr = []
            for d in beam_rss_snr:
                beam_rss.append(d & 0xFFFFF)
                beam_snr.append(d >> 20)
            
            if not tail_ptr:
                tail_ptr = data_start_addr
            
            if head_ptr > 0 and tail_ptr < head_ptr:
                new_size = head_ptr-tail_ptr
                data_pos = (tail_ptr - data_start_addr)/4
                new_rss_data = beam_rss[data_pos : data_pos + new_size / 4]
                new_snr_data = beam_snr[data_pos : data_pos + new_size / 4]
                
                tail_ptr = head_ptr
                
            elif head_ptr > 0 and tail_ptr > head_ptr:
                new_size = data_end_addr - tail_ptr
                data_pos = (tail_ptr - data_start_addr)/4
                new_rss_data = beam_rss[data_pos : data_pos + new_size / 4]
                new_snr_data = beam_snr[data_pos : data_pos + new_size / 4]
                
                new_size = head_ptr - data_start_addr
                data_pos = 0
                new_rss_data.extend(beam_rss[data_pos : data_pos + new_size / 4])
                new_snr_data.extend(beam_snr[data_pos : data_pos + new_size / 4])
                
                tail_ptr = head_ptr
            else:
                new_rss_data = []
                new_snr_data = []
                pass
            
            entry = {"beam_index":beam_idx,
                     "counter":counter,
                     "timestamp":timestamp,
                     "head_ptr":head_ptr,
                     "tail_ptr":tail_ptr,
                     "rss_data":new_rss_data,
                     "snr_data":new_snr_data,
                     "mac_addr":mac_addr,
            }
            data.append(entry)
            
        return data
    
    @classmethod
    def call(self, fw, cmd=None):
        if cmd is None:
            cmd = self.cmdDefault()
        
        if not cmd['tail_ptr']:
            cmd['tail_ptr'] = [[0] * cmd['beam_num']] * cmd['ap_num']
            
        page_size = (cmd['beam_num']*(cmd['storage_size']+4))*4
        
        data = []
        for ap_index in range(0, cmd['ap_num']):
            base_addr = cmd['rss_mem_addr'] + page_size*ap_index
            ret = fw.mem_dump(base_addr, page_size)
            val = struct.unpack(('%dI' % (page_size/4)), ret)
            ap_data = self.load_parse_data(base_addr, val, cmd, cmd['tail_ptr'][ap_index])
            data.append(ap_data)
        
        return data