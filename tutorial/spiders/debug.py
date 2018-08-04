class DebugLogger():
    debug_all = False
    debug_token = False
    debug_tag = False
    debug_tree = False
    debug_dollar = True

    def log(self, flag, *args, **kwargs):
        if (flag and self.debug_all):
            print(*args, **kwargs)
