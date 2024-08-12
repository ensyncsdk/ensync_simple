
class SimpleWarning(UserWarning):
    def __str__(self) -> str:
        args = self.args
        if args:
            msg, *rest_args = args
            if rest_args:
                return f"""{msg}: {", ".join(map(repr, rest_args))}"""
            elif msg.__class__ is str:
                return msg
            else:
                return str(msg)
        else:
            return super(SimpleWarning, self).__str__()
