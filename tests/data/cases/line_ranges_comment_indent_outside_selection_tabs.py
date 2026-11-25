# flags: --line-ranges=7-8
class A:
	def f(self):
		# inner
		pass

	def g(self):
		pass

# output
# flags: --line-ranges=7-8
class A:
    def f(self):
        # inner
        pass

    def g(self):
        pass
