from functools import wraps


def ensure_dest_exists(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if not self.dest.is_file():
            assert f"dest:{self.dest} must be file"
        self.dest.parent.mkdir(parents=True, exist_ok=True)
        return f(self, *args, **kwargs)

    return wrapper
