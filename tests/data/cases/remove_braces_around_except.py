# flags: --preview --minimum-version=3.14
# SEE PEP 758 FOR MORE DETAILS
# remains unchanged
try:
    pass
except:
    pass

# remains unchanged
try:
    pass
except ValueError, TypeError, KeyboardInterrupt:
    pass

# parenthesis are removed
try:
    pass
except (ValueError, TypeError, KeyboardInterrupt):
    pass

# parenthesis are not removed
try:
    pass
except (ValueError, TypeError, KeyboardInterrupt) as e:
    pass

# additional cases
# single exception with parentheses
try:
    pass
except (ValueError):
    pass

# single exception without parentheses
try:
    pass
except ValueError:
    pass

# single exception with parentheses and alias
try:
    pass
except (ValueError) as e:
    pass

# single exception without parentheses and alias
try:
    pass
except ValueError as e:
    pass

# tuple with one element and alias
try:
    pass
except (ValueError,) as e:
    pass

# tuple with one element
try:
    pass
except (ValueError,):
    pass

# nested try-except
try:
    try:
        pass
    except (TypeError, KeyboardInterrupt):
        pass
except (ValueError,):
    pass

# except with complex expression
try:
    pass
except (ValueError if True else TypeError):
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
except ValueError, TypeError, KeyboardInterrupt:
    pass

# parenthesis are removed
try:
    pass
except ValueError, TypeError, KeyboardInterrupt:
    pass

# parenthesis are not removed
try:
    pass
except (ValueError, TypeError, KeyboardInterrupt) as e:
    pass

# additional cases
# single exception with parentheses
try:
    pass
except ValueError:
    pass

# single exception without parentheses
try:
    pass
except ValueError:
    pass

# single exception with parentheses and alias
try:
    pass
except ValueError as e:
    pass

# single exception without parentheses and alias
try:
    pass
except ValueError as e:
    pass

# tuple with one element and alias
try:
    pass
except (ValueError,) as e:
    pass

# tuple with one element
try:
    pass
except (ValueError,):
    pass

# nested try-except
try:
    try:
        pass
    except TypeError, KeyboardInterrupt:
        pass
except (ValueError,):
    pass

# except with complex expression
try:
    pass
except ValueError if True else TypeError:
    pass
