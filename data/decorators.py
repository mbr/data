from six import PY2, wraps
if PY2:
    from funcsigs import signature
else:
    from inspect import signature


def auto_instantiate(*classes):
    def decorator(f):
        # collect our argspec
        sig = signature(f)

        @wraps(f)
        def _(*args, **kwargs):
            bvals = sig.bind(*args, **kwargs)

            # replace with instance if desired
            for varname, val in bvals.arguments.items():
                anno = sig.parameters[varname].annotation

                if anno in classes:
                    bvals.arguments[varname] = anno(val)

            return f(*bvals.args, **bvals.kwargs)
        return _
    return decorator
