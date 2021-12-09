import geograpy

x=geograpy.locator.LocationContext.fromCache()
t="American Federation of Information Processing Societies: Proceedings of the AFIPS '66 Fall Joint Computer Conference, November 7-10, 1966, San Fran, California, USA"
print(x.locateLocation(t, verbose=True)[0])