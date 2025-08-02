# flags: --preview --minimum-version=3.9
# SEE PEP 758 FOR MORE DETAILS
# remains unchanged
try:
    pass
except:
    pass

# remains unchanged
try:
    pass
except ValueError:
    pass

# parenthesis are removed
try:
    pass
except (ValueError):
    pass

# parenthesis are removed
try:
    pass
except (ValueError) as e:
    pass

# parenthesis are removed
try:
    pass
except ValueError as e:
    pass

# remains unchanged
try:
    pass
except (ValueError,):
    pass

# remains unchanged
try:
    pass
except (ValueError,) as e:
    pass

# remains unchanged
try:
    pass
except (ValueError, TypeError, KeyboardInterrupt):
    pass

# remains unchanged
try:
    pass
except (ValueError, TypeError, KeyboardInterrupt) as e:
    pass

# parenthesis are removed
try:
    pass
except (ValueError if True else TypeError):
    pass

# inner except: parenthesis are not removed
# outer except: parenthsis are not removed
try:
    try:
        pass
    except (TypeError, KeyboardInterrupt):
        pass
except (ValueError,):
    pass

# output
# SEE PEP 758 FOR MORE DETAILS
# remains unchanged
try:
    pass
except:
    pass

# remains unchanged
try:
    pass
except ValueError:
    pass

# parenthesis are removed
try:
    pass
except ValueError:
    pass

# parenthesis are removed
try:
    pass
except ValueError as e:
    pass

# parenthesis are removed
try:
    pass
except ValueError as e:
    pass

# remains unchanged
try:
    pass
except (ValueError,):
    pass

# remains unchanged
try:
    pass
except (ValueError,) as e:
    pass

# remains unchanged
try:
    pass
except (ValueError, TypeError, KeyboardInterrupt):
    pass

# remains unchanged
try:
    pass
except (ValueError, TypeError, KeyboardInterrupt) as e:
    pass

# parenthesis are removed
try:
    pass
except ValueError if True else TypeError:
    pass

# inner except: parenthesis are not removed
# outer except: parenthsis are not removed
try:
    try:
        pass
    except (TypeError, KeyboardInterrupt):
        pass
except (ValueError,):
    pass
