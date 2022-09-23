from wmi_basic import *
import binascii

class WmiSetRfModule(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### hwm_analog_select_active_rf_module command
    WMI_CMDID = 0x0900
    WMI_EVENTID = 0x1900
    cmd_args = [('module_id', 2),
        ('ut_subtype_id', 2),
        ('rfc_enable_vec', 1),
    ]
    event_args = [('module_id', 2),
        ('ut_subtype_id', 2),
        ('res', 4),
    ]
    
    @classmethod
    def cmdDefault(self):
        cmd = self.wmi_get_cmd(self.cmd_args)
        cmd['module_id'] = 0xb
        cmd['ut_subtype_id'] = 0x207
        cmd['rfc_enable_vec'] = 1
        return cmd
    
    @classmethod
    def call(self, fw, cmd=None):
        if cmd is None:
            cmd = self.cmdDefault()
        cmd_data = fw.wmi_encode_cmd(cmd, self.cmd_args)
        
        WMI_EVENT_DATA = fw.wmi_call(self.WMI_CMDID, 
                                     cmd_data,
                                     self.WMI_EVENTID, 5, 50)
                                            
        print WMI_EVENT_DATA
        wmi_evt = fw.wmi_decode_event(self.event_args, WMI_EVENT_DATA)
        print wmi_evt
        
        mem_data = fw.mem_dump(0x90022c, 4)
        mem_data = binascii.hexlify(mem_data)
        print mem_data
        rf_connected_vec = int(mem_data[6:8], 16)
        rf_enable_vec = int(mem_data[4:6], 16)
        c = 0
        print 'connected_rf_module_vec: ',
        while rf_connected_vec:
            if rf_connected_vec % 2:
                print c,
            rf_connected_vec /= 2
            c += 1
        c = 0
        print '\nenabled_rf_module_vec: ',
        while rf_enable_vec:
            if rf_enable_vec % 2:
                print c,
            rf_enable_vec /= 2
            c += 1
        print ''
        
        return wmi_evt