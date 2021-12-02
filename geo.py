import geograpy
t = 'XIX International Mineral Processing Congress : Saint Petersburg, Russia, 1995'
places = geograpy.get_place_context(text = t )
print(places)
print(places.countries[0])
print(places.regions[0])
print(places.cities[0])
