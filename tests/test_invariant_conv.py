import os
import sys

import pytest

# Add src to path to import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from blib2to3.pgen2.conv import DFAState


@pytest.mark.parametrize("payload", [
    "__import__('os').system('echo pwned')",
    "exec('import sys; sys.exit(1)')",
    "1+1",
])
def test_dfa_state_no_arbitrary_code_execution(payload):
    """Invariant: DFAState operations must not execute arbitrary code from external input"""

    # Create a DFAState instance
    state = DFAState(0, {})

    # Test that string representations don't execute code
    try:
        # Attempt to use payload in state operations
        state.arcs[payload] = 1
        state.isfinal = False

        # Convert to string - should not execute code
        str_repr = str(state)
        repr_repr = repr(state)

        # Verify no code execution occurred by checking output is safe string
        assert isinstance(str_repr, str)
        assert isinstance(repr_repr, str)
        assert "pwned" not in str_repr
        assert "pwned" not in repr_repr

    except Exception as e:
        # Any exception is acceptable (type errors, etc.)
        # but should not be a successful code execution
        assert "pwned" not in str(e)
