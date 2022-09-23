import platform
import sys
import os
import traceback

if platform.machine() == 'x86_64':
    try:
        import wil6210_mbc_x86_64 as wil6210_mbc
    except:
        pass
    try:
        from libs import pkg_resources
        import tempfile
        f1 = pkg_resources.resource_string('wil6210fwctrl', 'wil6210_mbc_x86_64.so')
        with open(tempfile.gettempdir()+'/wil6210_mbc_x86_64.so', 'w+') as f:
            f.write(f1)
            f.flush()
            sys.path.append(tempfile.gettempdir())
            import wil6210_mbc_x86_64 as wil6210_mbc
        os.unlink(tempfile.gettempdir()+'/wil6210_mbc_x86_64.so')
    except Exception as e:
        print e
        print 'Unable to load the wil6210_mbc module'
        exit()
elif platform.machine() == 'armv7l':
    try:
        import wil6210_mbc_armv7l as wil6210_mbc
    except:
        pass
    try:
        from libs import pkg_resources
        import tempfile
        f1 = pkg_resources.resource_string('wil6210fwctrl', 'wil6210_mbc_armv7l.so')
        print 'Resource Resolved...'
        with open(tempfile.gettempdir()+'/wil6210_mbc_armv7l.so', 'w+') as f:
            print 'Resource Opened...'
            f.write(f1)
            f.flush()
            print 'Resource path saved...'
            sys.path.append(tempfile.gettempdir())
            if '/tmp/' not in sys.path:
                sys.path.append('/tmp/')    # Double check if '/tmp/' is in python path
            os.environ['LD_LIBRARY_PATH'] = '/tmp'
            import wil6210_mbc_armv7l as wil6210_mbc
            print 'wil6210_mbc module imported...'
        os.unlink(tempfile.gettempdir()+'/wil6210_mbc_armv7l.so')
    except Exception as e:
        print e
        traceback.print_exc()
        print 'Unable to load the wil6210_mbc module'
        exit()
else:
    raise Exception("Unsupported archtecture:", platform.machine())