import inspect
import traceback

class Cleaner(object):
    def at_start(self): pass
    def at_success(self): pass
    def at_failure(self): pass

class WrapperWithCleaners(object):
    def __init__(self, cleaners=[]):
        self.cleaners = cleaners
    def __call__(self, f):
        def wrap(f, cleaner):
            def g(*a,**b):
                try:
                    cleaner.at_start()
                    output = f(*a,**b)
                    cleaner.at_success()
                    return output
                except:
                    cleaner.at_failure()
                    raise
            return g
        for cleaner in self.cleaners:
            if isinstance(cleaner,Cleaner):
                print 'wrapping cleaner'
                f = wrap(f, cleaner)        
        return f

def smart_traceback():
    tb = traceback.format_exc()
    frames = []
    for item in inspect.trace():
        frame = item[0]
        frames.append(dict(filename = frame.f_code.co_filename,
                           line_number = frame.f_lineno,
                           locals_variables = frame.f_locals,
                           global_variables = frame.f_globals))
    return dict(tb=tb, frames=frames)
        
class CleanerExample(Cleaner):
    def __init__(self): print 'connecting'
    def at_start(self): print 'pool connection'
    def at_success(self): print 'commit'
    def at_failure(self): print 'rollback'
    def insert(self,**data): print 'inserting %s' % data

db = CleanerExample()

@WrapperWithCleaners((db,))
def action(x):
    db.insert(key=1/x)
    return

try:
    a = action(1)
    a = action(0)
except:
    print smart_traceback()['frames'][-1]