class Indent0Plain:
    def output(self):
        """Examples.

        >>> print(chr(32) * 8 + "value")
        	value
        """

    def source(self):
        """Examples.

        >>> text = '''first
        ... 	second'''
        >>> print(text.splitlines()[1] == chr(32) * 4 + 'second')
        True
        """


class Indent0R:
    def output(self):
        r"""Examples.

        >>> print(chr(32) * 8 + "value")
        	value
        """

    def source(self):
        r"""Examples.

        >>> text = '''first
        ... 	second'''
        >>> print(text.splitlines()[1] == chr(32) * 4 + 'second')
        True
        """


class Indent1Plain:
	def output(self):
		"""Examples.

		>>> print(chr(32) * 8 + "value")
			value
		"""

	def source(self):
		"""Examples.

		>>> text = '''first
		... 	second'''
		>>> print(text.splitlines()[1] == chr(32) * 4 + 'second')
		True
		"""


class Indent1R:
	def output(self):
		r"""Examples.

		>>> print(chr(32) * 8 + "value")
			value
		"""

	def source(self):
		r"""Examples.

		>>> text = '''first
		... 	second'''
		>>> print(text.splitlines()[1] == chr(32) * 4 + 'second')
		True
		"""


class Indent2Plain:
   def output(self):
      """Examples.

      >>> print(chr(32) * 2 + "value")
      	value
      """

   def source(self):
      """Examples.

      >>> text = '''first
      ... 	second'''
      >>> print(text.splitlines()[1] == chr(32) * 6 + 'second')
      True
      """


class Indent2R:
   def output(self):
      r"""Examples.

      >>> print(chr(32) * 2 + "value")
      	value
      """

   def source(self):
      r"""Examples.

      >>> text = '''first
      ... 	second'''
      >>> print(text.splitlines()[1] == chr(32) * 6 + 'second')
      True
      """

# output

class Indent0Plain:
    def output(self):
        """Examples.

        >>> print(chr(32) * 8 + "value")
        	value
        """

    def source(self):
        """Examples.

        >>> text = '''first
        ... 	second'''
        >>> print(text.splitlines()[1] == chr(32) * 4 + 'second')
        True
        """


class Indent0R:
    def output(self):
        r"""Examples.

        >>> print(chr(32) * 8 + "value")
        	value
        """

    def source(self):
        r"""Examples.

        >>> text = '''first
        ... 	second'''
        >>> print(text.splitlines()[1] == chr(32) * 4 + 'second')
        True
        """


class Indent1Plain:
    def output(self):
        """Examples.

		>>> print(chr(32) * 8 + "value")
			value
		"""

    def source(self):
        """Examples.

		>>> text = '''first
		... 	second'''
		>>> print(text.splitlines()[1] == chr(32) * 4 + 'second')
		True
		"""


class Indent1R:
    def output(self):
        r"""Examples.

		>>> print(chr(32) * 8 + "value")
			value
		"""

    def source(self):
        r"""Examples.

		>>> text = '''first
		... 	second'''
		>>> print(text.splitlines()[1] == chr(32) * 4 + 'second')
		True
		"""


class Indent2Plain:
    def output(self):
        """Examples.

      >>> print(chr(32) * 2 + "value")
      	value
      """

    def source(self):
        """Examples.

      >>> text = '''first
      ... 	second'''
      >>> print(text.splitlines()[1] == chr(32) * 6 + 'second')
      True
      """


class Indent2R:
    def output(self):
        r"""Examples.

      >>> print(chr(32) * 2 + "value")
      	value
      """

    def source(self):
        r"""Examples.

      >>> text = '''first
      ... 	second'''
      >>> print(text.splitlines()[1] == chr(32) * 6 + 'second')
      True
      """
