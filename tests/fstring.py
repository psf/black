f'f-string without formatted values is just a string'
f'{{NOT a formatted value}}'
f'some f-string with {a} {few():.2f} {formatted.values!r}'
f"{f'{nested} inner'} outer"
f'space between opening braces: { {a for a in (1, 2, 3)}}'
