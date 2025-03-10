

# cities = ['Australia','India','USA','UK','Canada','Germany','France','Italy','Spain','Japan']

# book1 = {"title": "Great Expectations", "author": "Charles Dickens"}
# book2 = {"title": "Bleak House", "author": "Charles Dickens"}
# book3 = {"title": "An Book By No Author"}
# book4 = {"title": "Moby Dick", "author": "Herman Melville"}
# books = [book1,book2,book3,book4]

# cities_upper = [city.upper() for city in cities if len(city) > 5]
# print(cities_upper)

# cities_mapping = {city:city.upper() for city in cities if len(city) > 5}
# print(cities_mapping)   

# print([book["title"] for book in books])
# print({book.get("author", "Author not available") for book in books})

# #filter out none
# print([book.get("author") for book in books if book.get("author")])

#generators

def number_generator():
    for i in range(1,6):
        yield i


gen = number_generator()

# next(gen)
# next(gen)

for number in gen:
    print(number)




