from wmi_basic import *
import wmi_echo

class WmiPeriodicSweep(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### periodic_beam_sweep
    
    cmd_args = [('interval', 4),
        ('is_tx_mode', 4),
        ('max_beam', 4),
        ('gain_idx', 4),
    ]
    BUFFER_ADDR = 0x8FE004
    
    @classmethod
    def cmdDefault(self):
        cmd = self.wmi_get_cmd(self.cmd_args)
        cmd['interval'] = 100000
        cmd['is_tx_mode'] = 1
        cmd['max_beam'] = 16
        cmd['gain_idx'] = 1
        
        return cmd
    
    @classmethod
    def call(self, fw, cmd=None):
        if cmd is None:
            cmd = self.cmdDefault()
            
        is_tx_mode_addr = self.BUFFER_ADDR + 3*4
        max_beam_addr = self.BUFFER_ADDR + 5*4
        gain_idx_addr = self.BUFFER_ADDR + 6*4
        
        periodic_val_addr = self.BUFFER_ADDR + 0x70
        
        fw.mem_write(is_tx_mode_addr, cmd['is_tx_mode'])
        fw.mem_write(max_beam_addr, cmd['max_beam'])
        fw.mem_write(gain_idx_addr, cmd['gain_idx'])
        fw.mem_write(periodic_val_addr, cmd['interval'])
        
        wmi_echo_params = wmi_echo.WmiEcho.cmdDefault()
        wmi_echo_params['value'] = 0x1100
        wmi_evt = wmi_echo.WmiEcho.call(fw, wmi_echo_params)
        
        return wmi_evt