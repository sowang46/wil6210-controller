import struct
from wmi_basic import *

class WmiGetBeamRss2(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### get per-beam rss from beacon frame
    
    rss_mem_addr = {"6.2.0.40":0x008FC000,
                    "4.1.0.55":0x008FC000,
    }
    storage_size = 28
    beam_num = 64
    page_offset = (beam_num*(storage_size+4))*4
    
    @classmethod
    def call(self, fw, cmd=None):
        base_addr = fw.get_fw_params(self.rss_mem_addr)
        
        ret = fw.mem_dump(base_addr, 0x2000)
        ret_snr = fw.mem_dump(base_addr+self.page_offset, 0x2000)
        val = struct.unpack('2048I', ret)
        val_snr = struct.unpack('2048I', ret_snr)
        
        data = []
        
        for beam_idx in range(0, self.beam_num):
            offset = beam_idx * (self.storage_size + 4)
            counter = val[offset]
            overflow = val[offset+1]
            head_ptr = val[offset+2]
            tail_ptr = val[offset+3]
            
            data_start_addr = base_addr + (offset+4)*4
            data_end_addr = base_addr + (offset+4+self.storage_size)*4
            tail_ptr_addr = base_addr + (offset+3)*4
            beam_rss = list(val[offset+4:offset+4+self.storage_size])
            beam_snr = list(val_snr[offset+4:offset+4+self.storage_size])
            
            if tail_ptr < head_ptr:
                new_size = head_ptr-tail_ptr
                data_pos = (tail_ptr - data_start_addr)/4
                new_rss_data = beam_rss[data_pos : data_pos + new_size / 4]
                new_snr_data = beam_snr[data_pos : data_pos + new_size / 4]
                
                fw.mem_write(tail_ptr_addr, head_ptr)
                
            elif tail_ptr > head_ptr:
                new_size = data_end_addr - tail_ptr
                data_pos = (tail_ptr - data_start_addr)/4
                new_rss_data = beam_rss[data_pos : data_pos + new_size / 4]
                new_snr_data = beam_snr[data_pos : data_pos + new_size / 4]
                
                new_size = head_ptr - data_start_addr
                data_pos = 0
                new_rss_data.extend(beam_rss[data_pos : data_pos + new_size / 4])
                new_snr_data.extend(beam_snr[data_pos : data_pos + new_size / 4])
                
                fw.mem_write(tail_ptr_addr, head_ptr)
            else:
                new_rss_data = []
                new_snr_data = []
                pass
            
            if overflow:
                counter_addr = base_addr + (offset+1)*4
                fw.mem_write(counter_addr, 0)
            
            # print "beam %d," % beam_idx
            # print new_rss_data
            # print counter
            # print overflow
            # print '0x%02x' % head_ptr
            # print '0x%02x' % tail_ptr
            # print ''
            entry = {"beam_index":beam_idx,
                     "counter":counter,
                     "overflow":overflow,
                     "head_ptr":head_ptr,
                     "tail_ptr":tail_ptr,
                     "rss_data":new_rss_data,
                     "snr_data":new_snr_data,
            }
            data.append(entry)
        
        return data