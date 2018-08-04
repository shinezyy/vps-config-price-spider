class DebugLogger():
    debug_all = True
    debug_token = False
    debug_tag = False
    debug_tree = False
    debug_dollar = False
    debug_tuples = False

    def log(self, flag, *args, **kwargs):
        if (flag and self.debug_all):
            print(*args, **kwargs)
