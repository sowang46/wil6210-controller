import struct
from wmi_basic import *

class WmiBeamRssV2X(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### get per-beam rss from beacon frame (version 4)
    
    rss_mem_addr = {"6.2.0.40":0x008FC000,
                    "4.1.0.55":0x008FC000,
    }
    cmd_args = [('rss_mem_addr', 4),
                ('mac_store_addr', 4),
                ('timestamp_addr', 4),
    ]
    
    beam_num = 64
    
    @classmethod
    def cmdDefault(self):
        cmd = self.wmi_get_cmd(self.cmd_args)
        cmd['rss_mem_addr'] = 0x0093F300
        cmd['mac_store_addr'] = 0x0093F500
        cmd['timestamp_addr'] = 0x0093F600
        return cmd
    
    @classmethod
    def call(self, fw, cmd=None):
        if cmd is None:
            cmd = self.cmdDefault()
            
        # Get RSS/SNR
        base_addr = cmd['rss_mem_addr']
        page_size = self.beam_num*4
        
        ret = fw.mem_dump(base_addr, page_size)
        val = struct.unpack(('%dI' % (page_size/4)), ret)
        
        rss_data = []
        snr_data = []
        mac_addr_data = []
        timestamp_data = []
        
        for beam_idx in range(0, self.beam_num):
            offset = beam_idx         
            beam_rss_snr = val[offset]
            beam_rss = (beam_rss_snr & 0xFFFFF)
            beam_snr = (beam_rss_snr >> 20)
            rss_data.append(beam_rss)
            snr_data.append(beam_snr)

        # Get MAC address
        base_addr = cmd['mac_store_addr']
        page_size = self.beam_num*4
        
        ret = fw.mem_dump(base_addr, page_size)
        val = struct.unpack(('%dI' % (page_size/4)), ret)
        mac_addr_data = []

        for beam_idx in range(0, self.beam_num):
            offset = beam_idx
            mac_addr_data.append(val[offset])

        # Get timestamp
        base_addr = cmd['timestamp_addr']
        page_size = self.beam_num*4
        
        ret = fw.mem_dump(base_addr, page_size)
        val = struct.unpack(('%dI' % (page_size/4)), ret)
        timestamp_data = []

        for beam_idx in range(0, self.beam_num):
            offset = beam_idx
            timestamp_data.append(val[offset])
        
        return {'rss_data': rss_data, 'snr_data': snr_data, \
                'mac_addr_data': mac_addr_data, \
                'timestamp_data': timestamp_data, }