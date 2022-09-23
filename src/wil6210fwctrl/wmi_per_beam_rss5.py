import struct
from wmi_basic import *
import time
from threading import Thread, Lock
from datetime import datetime

class WmiGetBeamRss5(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### get per-beam rss from beacon frame (version 5)
    
    cmd_args = [
        ('rss_mem_addr', 4),
        ('storage_size', 4),
        ('head_ptr_offset', 4),
        ('beam_num', 4),
        ('run_interval', 4),
        ('run_daemon', 4),
        ('get_data', 4),
        ('buffer_size', 4),
    ]
    
    @classmethod
    def cmdDefault(self):
        cmd = self.wmi_get_cmd(self.cmd_args)
        cmd['beam_num'] = 128
        cmd['rss_mem_addr'] = 0x0093eb00
        cmd['storage_size'] = 12
        cmd['sample_size'] = 2
        cmd['header_size'] = 3
        cmd['head_ptr_offset'] = 0
        cmd['run_interval'] = 0.10
        cmd['run_daemon'] = 0
        cmd['get_data'] = 0
        cmd['buffer_size'] = 500
        return cmd
        
    @classmethod
    def get_rss_data(self, cmd, fw):
        base_addr = cmd['rss_mem_addr']
        storage_sample_size = cmd['storage_size']*cmd['sample_size']/4
        beam_page_size = storage_sample_size+cmd['header_size']
        page_size = (cmd['beam_num']*beam_page_size)*4
        
        # while True:
        #     ret = fw.mem_dump(base_addr-4*12, 4)
        #     val = struct.unpack(('%dI' % 1), ret)
        #     if val[0]:
        #         print 'Waiting for firmware data lock %d' % val[0]
        #         time.sleep(0.01)
        #     else:
        #         break
        
        with self.lock:
            ret = fw.mem_dump(base_addr, page_size)
            val = struct.unpack(('%dI' % (page_size/4)), ret)
                
            get_rss_num = 0
            rss_num_total = 0
            
            data_len = -1
            timenow = datetime.now().strftime('%s.%f')
            for beam_idx in range(0, int(cmd['beam_num'])):
                offset = beam_idx * beam_page_size
                counter = val[offset]
                timestamp = val[offset+1]
                head_ptr = val[offset+2] + cmd['head_ptr_offset']
                tail_ptr = self.priv_data['tail_ptr'][beam_idx]
                
                data_start_addr = base_addr-0x00920000+(offset+cmd['header_size'])*4
                data_end_addr = base_addr-0x00920000+(offset+cmd['header_size']+storage_sample_size)*4
                beam_rss_snr = list(val[offset+cmd['header_size'] : offset+cmd['header_size']+storage_sample_size])
                
                beam_rss = []
                for d in beam_rss_snr:
                    beam_rss.append(d & 0xFFFF)
                    beam_rss.append(d >> 16)
                
                if not tail_ptr:
                    tail_ptr = data_start_addr
                
                # calibrate the head_ptr
                if data_len < 0:
                    data_len = head_ptr-data_start_addr
                else:
                    head_ptr = data_start_addr + data_len
                
                if head_ptr > 0 and tail_ptr < head_ptr:
                    new_size = head_ptr-tail_ptr
                    data_pos = (tail_ptr - data_start_addr)/cmd['sample_size']
                    new_rss_data = beam_rss[data_pos : data_pos + new_size / cmd['sample_size']]
                    
                    tail_ptr = head_ptr
                elif head_ptr > 0 and tail_ptr > head_ptr:
                    new_size = data_end_addr - tail_ptr
                    data_pos = (tail_ptr - data_start_addr)/cmd['sample_size']
                    new_rss_data = beam_rss[data_pos : data_pos + new_size / cmd['sample_size']]
                    
                    new_size = head_ptr - data_start_addr
                    data_pos = 0
                    new_rss_data.extend(beam_rss[data_pos : data_pos + new_size / cmd['sample_size']])
                    
                    tail_ptr = head_ptr
                else:
                    new_rss_data = []
                    pass
                
                if beam_idx not in self.priv_data.keys():
                    self.priv_data[beam_idx] = {}
                    self.priv_data[beam_idx]['counter'] = [counter]
                    self.priv_data[beam_idx]['timestamp'] = [timestamp]
                    self.priv_data[beam_idx]['timestamp_sys'] = [float(timenow)]
                    self.priv_data[beam_idx]['head_ptr'] = head_ptr
                    self.priv_data[beam_idx]['rss_data'] = [new_rss_data]
                else:
                    self.priv_data[beam_idx]['counter'].append(counter)
                    self.priv_data[beam_idx]['timestamp'].append(timestamp)
                    self.priv_data[beam_idx]['timestamp_sys'].append(float(timenow))
                    self.priv_data[beam_idx]['head_ptr'] = head_ptr
                    self.priv_data[beam_idx]['rss_data'].append(new_rss_data)
                    
                # check if it is over the buffer size
                while len(self.priv_data[beam_idx]['rss_data']) > cmd['buffer_size']:
                    del self.priv_data[beam_idx]['counter'][0]
                    del self.priv_data[beam_idx]['timestamp'][0]
                    del self.priv_data[beam_idx]['timestamp_sys'][0]
                    del self.priv_data[beam_idx]['rss_data'][0]
                
                self.priv_data['tail_ptr'][beam_idx] = tail_ptr
                get_rss_num = max(get_rss_num, len(new_rss_data))
                rss_num_total = max(rss_num_total, len(self.priv_data[beam_idx]['rss_data']))
                
            print 'per_beam_rss5 [%s]:' % timenow,
            print 'Get %d new entries/beam, total %d entries/beam' % (get_rss_num, rss_num_total)
            
    @classmethod
    def get_rss_data_thread(self, cmd, fw):
        while True:
            self.get_rss_data(cmd, fw)
            if self.stop_thread:
                print 'per_beam_rss5 daemon stops'
                break
            else:
                time.sleep(cmd['run_interval'])
    
    @classmethod
    def call(self, fw, cmd=None):
        self.lock = Lock()

        if cmd is None:
            cmd = self.cmdDefault()
            
        if 'tail_ptr' not in self.priv_data.keys():
            self.priv_data['tail_ptr'] = [0] * int(cmd['beam_num'])
            
        if cmd['get_data']:
            if self.lock:
                with self.lock:
                    ret_data = self.priv_data
                    self.priv_data = {'tail_ptr':ret_data['tail_ptr']}
                    return [ret_data]
                    
            return [{0:0}]
            
        if not cmd['run_daemon']:
            if not self.stop_thread:
                self.stop_thread = True
                self.thread.join()
            else:
                print 'per_beam_rss5 is already stopped'
        else:
            if not self.stop_thread:
                print 'per_beam_rss5 is already running'
            else:
                self.thread = Thread(target=self.get_rss_data_thread, args=(cmd, fw, ))
                self.stop_thread = False
                print 'per_beam_rss5 daemon starts'
                self.lock = Lock()
                self.thread.start()
        
        return [{0:0}]
