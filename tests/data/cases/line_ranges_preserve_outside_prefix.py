# flags: --line-ranges=2-10
print("format me"  )
 # format whitespace
  # format whitespace
   # format whitespace
print( "format me" )
   # format whitespace
  # format whitespace
 # format whitespace
print(  "format me")



print("don't format me"  )
 # don't format whitespace
  # don't format whitespace
   # don't format whitespace
print( "don't format me" )
   # don't format whitespace
  # don't format whitespace
 # don't format whitespace
print(  "don't format me")

# output
# flags: --line-ranges=2-10
print("format me")
# format whitespace
# format whitespace
# format whitespace
print("format me")
# format whitespace
# format whitespace
# format whitespace
print("format me")



print("don't format me"  )
 # don't format whitespace
  # don't format whitespace
   # don't format whitespace
print( "don't format me" )
   # don't format whitespace
  # don't format whitespace
 # don't format whitespace
print(  "don't format me")
