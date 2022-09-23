import struct
import json
from wmi_basic import *

class WmiGetFrameRss(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### get per-frame rss
    
    header = {"6.2.0.40":0x0093eb00-0xc,
              "4.1.0.55":0x0093eb00-0xc,
    }
    
    @classmethod
    def call(self, fw, cmd=None):
        ret = fw.mem_dump(fw.get_fw_params(self.header), 12)
        val = struct.unpack('3I', ret)
        data = {'overflow': int(val[0]),
                'head': int(val[1]),
                'tail': int(val[2])}
        
        if data['tail'] < data['head']:
            size = data['head']-data['tail']
            rss_byte = fw.mem_dump(data['tail'], size)
            rss = struct.unpack('%dI' % (size/4), rss_byte)
            fw.mem_write(0x0093eb00-0x4, data['tail']+size)
        elif data['tail'] > data['head']:
            size = 0x0093eb00+4096-data['tail']
            rss_byte = fw.mem_dump(data['tail'], size)
            rss = struct.unpack('%dI' % (size/4), rss_byte)
            fw.mem_write(0x0093eb00-0x4, 0x0093eb00)
        else:
            # no data to read
            rss = []
            pass
        
        if data['overflow']:
            fw.mem_write(0x0093eb00-0xc, 0)
        
        data['rss'] = json.dumps(rss).encode('utf-8')
        
        return data