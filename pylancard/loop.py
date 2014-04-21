import shlex
import sys


def matching_command(command, commands_set):
    candidates = {name: function
                  for (name, function) in commands_set.items()
                  if name is not None and name.startswith(command.strip())}
    if len(candidates) == 1:
        return next(iter(candidates.values()))
    elif command in candidates:
        return candidates[command]
    elif not candidates and None in commands_set:
        return commands_set[None]
    else:
        if not candidates:
            print("No such command: %s" % command)
        else:
            print("Ambiguous command %s, candidates are %s" %
                  (command, ', '.join(x[0] for x in candidates)))
        print("Type ? for help")


def run(store, commands_set, prompt=''):
    while True:
        try:
            line = input('%s > ' % prompt)
        except EOFError:
            print()
            sys.exit(0)
        command, *arguments = shlex.split(line.strip())
        if not command:
            continue
        function = matching_command(command, commands_set)
        if function is not None:
            prompt = function(command, store, arguments) or ''
