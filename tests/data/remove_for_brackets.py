# Only remove tuple brackets after `for`
for (k, v) in d.items():
    print(k, v)

# Don't touch tuple brackets after `in`
for module in (core, _unicodefun):
    if hasattr(module, "_verify_python3_env"):
        module._verify_python3_env = lambda: None

# output
# Only remove tuple brackets after `for`
for k, v in d.items():
    print(k, v)

# Don't touch tuple brackets after `in`
for module in (core, _unicodefun):
    if hasattr(module, "_verify_python3_env"):
        module._verify_python3_env = lambda: None
