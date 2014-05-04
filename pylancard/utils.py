def matching_command(command, commands_set):
    candidates = {name: function
                  for (name, function) in commands_set.items()
                  if name is not None and name.startswith(command.strip())}
    if len(candidates) == 1:
        return next(iter(candidates.items()))
    elif command in candidates:
        return command, candidates[command]
    elif not candidates and None in commands_set:
        return command, commands_set[None]
    else:
        if not candidates:
            raise KeyError("No such command: %s" % command)
        else:
            raise KeyError("Ambiguous command %s, candidates are %s" %
                           (command, ', '.join(x[0] for x in candidates)))


def split_key_value(arguments):
    words = [tuple(y.strip()
                   for y in x.strip().split('=', 1))
             for x in arguments
             if x.strip()]
    if not words:
        raise ValueError("At least one argument required")

    bad_format = [x[0] for x in words if len(x) < 2]
    if bad_format:
        raise ValueError("Value required for keys: %s" % ', '.join(bad_format))

    return words
