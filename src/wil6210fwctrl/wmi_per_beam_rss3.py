import struct
from wmi_basic import *

class WmiGetBeamRss3(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### get per-beam rss from beacon frame (version 3)
    
    cmd_args = [('tail_ptr', 4),
        ('rss_mem_addr', 4),
        ('storage_size', 4),
        ('head_ptr_offset', 4),
    ]
    
    storage_size = 28
    beam_num = 64
    
    @classmethod
    def cmdDefault(self):
        cmd = self.wmi_get_cmd(self.cmd_args)
        cmd['tail_ptr'] = [0] * self.beam_num
        cmd['rss_mem_addr'] = 0x008FC000
        cmd['storage_size'] = self.storage_size
        cmd['head_ptr_offset'] = 0
        return cmd
    
    @classmethod
    def call(self, fw, cmd=None):
        if cmd is None:
            cmd = self.cmdDefault()
            
        base_addr = cmd['rss_mem_addr']
        self.storage_size = cmd['storage_size']
        page_size = (self.beam_num*(self.storage_size+4))*4
        
        ret = fw.mem_dump(base_addr, page_size)
        val = struct.unpack(('%dI' % (page_size/4)), ret)
        
        data = []
        
        part_size = self.storage_size/2;
        for beam_idx in range(0, self.beam_num):
            offset = beam_idx * (self.storage_size + 4)
            counter = val[offset]
            timestamp = val[offset+1]
            head_ptr = val[offset+2] + cmd['head_ptr_offset']
            tail_ptr = cmd['tail_ptr'][beam_idx]
            
            data_start_addr = base_addr + (offset+4)*4
            data_end_addr = base_addr + (offset+4+part_size)*4
            beam_rss = list(val[offset + 4 : offset + 4 + part_size])
            beam_snr = list(val[offset + 4 + part_size : offset + 4 + self.storage_size])
            
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
            }
            data.append(entry)
        
        return data