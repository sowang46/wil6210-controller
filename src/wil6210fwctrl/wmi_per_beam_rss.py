import struct
# from libs import hipsterplot
from wmi_basic import *

class WmiGetBeamRss(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### get per-beam rss from beacon frame
    
    rss_mem_addr = {"6.2.0.40":0x942f00,
                    "4.1.0.55":0x8ff300,
    }
    
    @classmethod
    def call(self, fw, cmd=None):
        ret = fw.mem_dump(fw.get_fw_params(self.rss_mem_addr), 256)
        val = struct.unpack('64I', ret)
        # print val
        # hipsterplot.plot(val, num_x_chars=len(val)*2-1, num_y_chars=20)
        return val