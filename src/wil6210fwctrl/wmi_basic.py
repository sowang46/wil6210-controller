class WmiBasic:
    description = ''
    
    cmd_args = []
    
    stop_thread = True
    lock = None
    thread = None
    
    priv_data = {}
    
    @classmethod
    def stop(self):
        if not self.stop_thread:
            self.stop_thread = True
            self.thread.join()
    
    @classmethod
    def cmdDefault(self):
        return {}
        
    @classmethod
    def call(self, fw, cmd=None):
        return None
        
    @classmethod
    def wmi_get_cmd(self, cmd_args):
        return {args[0]: 0 for args in cmd_args}
    
    @classmethod
    def setCmdArgs(self, val=None):
        cmd_default = self.cmdDefault()
        if val is not None:
            for key in val.keys():
                if key in cmd_default.keys():
                    if type(val[key]).__name__ == 'unicode' and len(val[key]) < 8:
                        cmd_default[key] = int(val[key], 16)
                    else:
                        cmd_default[key] = val[key]
                else:
                    print 'Ignore setting for \'%s\' because it is not in the args list' % key
        return cmd_default
        
    @classmethod
    def print_help(self, name):
        print '\nCommand: %s' % name
        print 'Description:',
        if not self.description:
            print 'None'
        else:
            print self.description
        print 'Accepted parameter(s):',
        wmi_arg = self.setCmdArgs()
        wmi_arg_help = {args[0]: (args[2] if len(args) > 2 else '') for args in self.cmd_args}
        if not wmi_arg:
            print 'None'
        else:
            print ''
            for key, val in wmi_arg.iteritems():
                if key in wmi_arg_help.keys() and wmi_arg_help[key]:
                    print '\t- %s (Default: %s) : %s' % (key, val, wmi_arg_help[key])
                else:
                    print '\t- %s (Default: %s)' % (key, val)