import struct
# from libs import hipsterplot
from wmi_basic import *

class WmiGetCir(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### get cir
    
    @classmethod
    def call(self, fw, slot):
        if slot == 0:
            ret = fw.mem_dump(0x91f3D8, 64)
            val = struct.unpack('16I', ret)
        elif slot == 1:
            ret = fw.mem_dump(0x91f438, 64)
            val = struct.unpack('16I', ret)
        elif slot == 2:
            ret = fw.mem_dump(0x91f498, 64)
            val = struct.unpack('16I', ret)
        else:
            ret = fw.mem_dump(0x883844, 64)
            val = struct.unpack('16I', ret)
        print val
        # hipsterplot.plot(val, num_x_chars=len(val)*2-1, num_y_chars=20)
        return val