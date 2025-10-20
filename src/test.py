import importlib

importlib.import_module("black")
print(
    "import OK"
)  # This is correctly using the black src. We are in cd src and using -m black uses it correctly
