from wmi_basic import *

class WmiGetSSID(WmiBasic):
    WMI_CMDID = 0x828
    WMI_EVENTID = 0x1828
    cmd_args = []
    ssid_len = 20
    event_args = [('ssid_length', 4),
        ('ssid', ssid_len),
    ]

    @classmethod
    def cmdDefault(self):
        cmd = self.wmi_get_cmd(self.cmd_args)
        return cmd

    @classmethod
    def call(self, fw, cmd=None):
        if cmd is None:
            cmd = self.cmdDefault()
        cmd_data = fw.wmi_encode_cmd(cmd, self.cmd_args)
        WMI_EVENT_DATA = fw.wmi_call(self.WMI_CMDID,
                                     cmd_data,
                                     self.WMI_EVENTID, 3)
        #Print WMI_EVENT_DATA
        wmi_evt = fw.wmi_decode_event(self.event_args, WMI_EVENT_DATA)
        ssid_str = str(wmi_evt.get('ssid'))
        ssid_ascii_str = []
        for ii in range(0,ssid_len/2-1):
            alp_ascii_int = int(str(ssid_str[ii*2:ii*2+2]), 16)
            ssid_ascii_str.append(alp_ascii_int)
        print ''.join(map(chr,ssid_ascii_str))
        return wmi_evt      

