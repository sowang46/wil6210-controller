import struct
import binascii
import wmi_get_cir
from wmi_basic import *

class WmiTofSessionStart(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### WMI_TOF_SESSION_START_CMDID
    WMI_CMDID = 0x991
    cmd_args = [('session_id', 4), 
        ('reserved1', 1), 
        ('aoa_type', 1), 
        ('num_of_dest', 2), 
        ('reserved', 4), 
        ('ftm_dest_info', 0), 
    ]
    wmi_ftm_dest_info = [('channel', 1),
        ('flags', 1),
        ('initial_token', 1),
        ('num_of_ftm_per_burst', 1),
        ('num_of_bursts_exp', 1),
        ('burst_duration', 1),
        ('burst_period', 2),
        ('dst_mac', 6),
        ('reserved', 1),
        ('num_burst_per_aoa_meas', 1),
    ]
    WMI_EVENTID = 0x1991
    WMI_FTM_EVENTID = 0x1995
    ftm_event_args = [('session_id', 4), 
        ('dst_mac', 6), 
        ('flags', 1), 
        ('status', 1), 
        ('responder_asap', 1), 
        ('responder_num_ftm_per_burst', 1), 
        ('responder_num_ftm_bursts_exp', 1), 
        ('responder_burst_duration', 1), 
        ('responder_burst_period', 2), 
        ('bursts_cnt', 2), 
        ('tsf_sync', 4), 
        ('actual_ftm_per_burst', 1), 
        ('meas_rf_mask', 4), 
        ('reserved0', 3),
        ('responder_ftm_res', 0)
    ]
    responder_ftm_res_args = [('t1', 6),
        ('t2', 6),
        ('t3', 6),
        ('t4', 6),
        ('tod_err', 2),
        ('toa_err', 2),
        ('tod_err_initiator', 2),
        ('toa_err_initiator', 2),
    ]
    event_args = [('session_id', 4), 
        ('status', 1), 
        ('reserved1', 1),
        ('reserved2', 1), 
        ('reserved3', 1),
    ]
    
    @classmethod
    def cmdDefault(self):
        wmi_ftm_dest_info = self.wmi_get_cmd(self.wmi_ftm_dest_info)
        wmi_ftm_dest_info['channel'] = 1
        wmi_ftm_dest_info['flags'] = 2
        wmi_ftm_dest_info['initial_token'] = 2
        wmi_ftm_dest_info['num_of_ftm_per_burst'] = 4
        wmi_ftm_dest_info['num_of_bursts_exp'] = 0
        wmi_ftm_dest_info['burst_duration'] = 2
        wmi_ftm_dest_info['burst_period'] = 0
        wmi_ftm_dest_info['dst_mac'] = '4066414F9815'
        wmi_ftm_dest_info['num_burst_per_aoa_meas'] = 0
        return wmi_ftm_dest_info
    
    @classmethod
    def call(self, fw, wmi_ftm_dest_info=None):
        if wmi_ftm_dest_info is None:
            wmi_ftm_dest_info = self.cmdDefault()
        wmi_ftm_dest_info_data = fw.wmi_encode_cmd(wmi_ftm_dest_info, self.wmi_ftm_dest_info)
        
        cmd = self.wmi_get_cmd(self.cmd_args)
        cmd['session_id'] = 1
        cmd['aoa_type'] = 0
        cmd['num_of_dest'] = 1
        cmd['ftm_dest_info'] = wmi_ftm_dest_info_data
        cmd_data = fw.wmi_encode_cmd(cmd, self.cmd_args)
        
        fw.send_wmi(self.WMI_CMDID, cmd_data,)
        
        WMI_EVENT_FTM = fw.read_wmi(self.WMI_FTM_EVENTID, 10, 100)
        print WMI_EVENT_FTM
        wmi_ftm_evt = fw.wmi_decode_event(self.ftm_event_args, WMI_EVENT_FTM)
        print wmi_ftm_evt
        print len(wmi_ftm_evt['responder_ftm_res'])
        print wmi_ftm_evt['responder_ftm_res']
        idx = 0
        for i in range(0, wmi_ftm_evt['actual_ftm_per_burst']):
            wmi_responder_ftm_res = fw.wmi_decode_event(self.responder_ftm_res_args, wmi_ftm_evt['responder_ftm_res'][idx:idx+64])
            idx += 64
            print wmi_responder_ftm_res
            t1 = struct.unpack('Q', binascii.unhexlify(wmi_responder_ftm_res['t1']+'0000'))[0]
            t2 = struct.unpack('Q', binascii.unhexlify(wmi_responder_ftm_res['t2']+'0000'))[0]
            t3 = struct.unpack('Q', binascii.unhexlify(wmi_responder_ftm_res['t3']+'0000'))[0]
            t4 = struct.unpack('Q', binascii.unhexlify(wmi_responder_ftm_res['t4']+'0000'))[0]
            print 't1: %d, t2: %d, t3: %d, t4: %d' % (t1, t2, t3, t4)
            rtt = ((t4-t1)-(t3-t2))
            d1 = rtt*3/10000/2
            d2 = rtt*3/10/2 - d1*1000
            print 'RTT: %d (ps), Tx-Rx distance: %d.%dm' % (rtt, d1, d2)
            
        WMI_EVENT_DATA = fw.read_wmi(self.WMI_EVENTID, 10, 100)
        # print WMI_EVENT_DATA
        wmi_evt = fw.wmi_decode_event(self.event_args, WMI_EVENT_DATA)
        print wmi_evt
        
        for i in range(0, int(wmi_ftm_evt['actual_ftm_per_burst'])):
            val = wmi_get_cir.WmiGetCir.call(fw, i)
            
        return wmi_evt