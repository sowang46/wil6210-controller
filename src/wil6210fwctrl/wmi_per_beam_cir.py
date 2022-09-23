import struct
# from libs import hipsterplot
from wmi_basic import *

class WmiGetBeamCir(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### get per-beam cir from beacon frame
    
    cir_mem_addr = {"6.2.0.40":0x93eb00,
                    "4.1.0.55":0x8fe000,
    }
    
    @classmethod
    def call(self, fw, cmd=None):
        ret = fw.mem_dump(fw.get_fw_params(self.cir_mem_addr), 4096)
        val = struct.unpack('1024I', ret)
        # print val
        # hipsterplot.plot(val, num_x_chars=len(val)*2-1, num_y_chars=20)
        return val