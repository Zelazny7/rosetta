if sepal_length > 6 or sepal_width > 5:
    new_var = "flower1"
elif species in ['setosa','virginica']:
    new_var = 'ends in A'
elif petal_length > petal_width:
    new_var = petal_width
else:
    new_var = 100
