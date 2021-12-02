#Changelog

##03.12.2021
* First attempts with geograpy3
	- Usage of places.countries/places.cities.places.regions
	- City accuracy depends on presence of country in input
	- Meaning of places.regions?
	- Are city acronyms relevant to common cases?
* First attempts with Spacy
	- Extracting data using entity.label_ checking
	- Roman ordinals - are they relevant, how are they checked?
	- Difficulties in extracting date (multiple occurences with/without day+month, unreliable differentiation from ordinals, non-uniform date formatting)
* Refining the data extraction process
	1. geograpy3 on input -> region, country, city
	2. Split input
	3. Match to *st/nd/rd/th -> ordinal
	4. Maintain a month (abbreviation) data structure
	5. Lookup months in split input
	6. One or two months?
	7. First number after each month's name
	8. spacy on split input looking for 4-digit numeral -> year
	9. Remove extracted properties
	10. Title is a WIP
		