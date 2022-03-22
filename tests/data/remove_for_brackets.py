for (k, v) in d.items():
    print(k, v)

for module in (core, _unicodefun):
    if hasattr(module, "_verify_python3_env"):
        module._verify_python3_env = lambda: None

# output
for k, v in d.items():
    print(k, v)

for module in (core, _unicodefun):
    if hasattr(module, "_verify_python3_env"):
        module._verify_python3_env = lambda: None
