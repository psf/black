class MyClass:
  """Multiline
  class docstring
  """

  def method(self):
    """Multiline
    method docstring
    """
    pass


def foo():
  """This is a docstring with
  some lines of text here
  """
  return


def bar():
  '''This is another docstring
  with more lines of text
  '''
  return


def baz():
  '''"This" is a string with some
  embedded "quotes"'''
  return


def troz():
	'''Indentation with tabs
	is just as OK
	'''
	return


def zort():
        """Another
        multiline
        docstring
        """
        pass

def poit():
  """
  Lorem ipsum dolor sit amet.

  Consectetur adipiscing elit:
   - sed do eiusmod tempor incididunt ut labore
   - dolore magna aliqua
     - enim ad minim veniam
     - quis nostrud exercitation ullamco laboris nisi
   - aliquip ex ea commodo consequat
  """
  pass


def over_indent():
  """
  This has a shallow indent
    - But some lines are deeper
    - And the closing quote is too deep
    """
  pass

# output

class MyClass:
    """Multiline
    class docstring
    """

    def method(self):
        """Multiline
        method docstring
        """
        pass


def foo():
    """This is a docstring with
    some lines of text here
    """
    return


def bar():
    """This is another docstring
    with more lines of text
    """
    return


def baz():
    '''"This" is a string with some
    embedded "quotes"'''
    return


def troz():
    """Indentation with tabs
    is just as OK
    """
    return


def zort():
    """Another
    multiline
    docstring
    """
    pass


def poit():
    """
    Lorem ipsum dolor sit amet.

    Consectetur adipiscing elit:
     - sed do eiusmod tempor incididunt ut labore
     - dolore magna aliqua
       - enim ad minim veniam
       - quis nostrud exercitation ullamco laboris nisi
     - aliquip ex ea commodo consequat
    """
    pass


def over_indent():
    """
    This has a shallow indent
      - But some lines are deeper
      - And the closing quote is too deep
    """
    pass
