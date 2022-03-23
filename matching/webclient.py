# -*- coding: utf-8 -*-

import copy
import os

from fb4.app import AppWrap
from fb4.widgets import Link, LodTable
from flask import render_template, request
from lodstorage.lod import LOD
from py2neo import Graph
import matchAndExtract
import parsingUtils


class App(AppWrap):
    def __init__(self):
        '''
        Constructor
        '''
        scriptdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_folder = scriptdir + '/templates'

        super().__init__(template_folder=template_folder)

        # set default button style and size, will be overwritten by macro parameters
        self.app.config['BOOTSTRAP_BTN_STYLE'] = 'primary'
        self.app.config['BOOTSTRAP_BTN_SIZE'] = 'sm'

        # app.config['BOOTSTRAP_BOOTSWATCH_THEME'] = 'lumen'  # uncomment this line to test bootswatch theme

        app = self.app

        #
        # setup the RESTFUL routes for this application
        #
        @app.route('/')
        def index():
            return self.home()

        @app.route("/match", methods=["GET", "POST"])
        def matchTitles():
            if request.method == "POST":
                input = request.form.get("input")
                return self.home()
            else:
                # This is the main one, edit with classes to be called
                input = request.args.get("input")
                parser = parsingUtils.Normalizer()
                acronym = parser.normalizeAcronym(input)
                graph = Graph("bolt://localhost:7687", auth=("", ""))
                matcher = matchAndExtract.CCtoGraph(graph)
                matcher.startMatching(acronym)
                lod = matcher.extractProperties(acronym)
                return self.home(result=acronym, data=lod, table=self.getHtmlTables(lod))

                # return self.home(result=acronym)

    def getHtmlTables(self, tablelod):
        """
        Converts the given tables into a html table
        Args:
            table:
        Returns:
        """
        lods = copy.deepcopy(tablelod)
        valueMap = self.propertyToLinkMap()
        eventLod = self.convertLodValues(lods, valueMap)
        eventPropertyOrder = ["Ordinal", "Year", "City", "Start date", "End date", "Title",
                              "Series", "wikidataId", "wikicfpId", "DblpConferenceId", "TibKatId"]
        eventFields = LOD.getFields(eventLod)
        eventHeaders = {**{v: v for v in eventPropertyOrder if v in eventFields},
                        **{v: v for v in eventFields if v not in eventPropertyOrder}}
        eventsTable = LodTable(eventLod, headers=eventHeaders, name="Events", isDatatable=True)
        return eventsTable

    def propertyToLinkMap(self) -> dict:
        """
        Returns a mapping to convert a property to the corresponding link
        """
        map = {
            "wikidataId": lambda value: Link(url=f"https://www.wikidata.org/wiki/{value}", title=value),
            "WikiCfpSeries": lambda value: Link(url=f"http://www.wikicfp.com/cfp/program?id={value}", title=value),
            "wikicfpId": lambda value: Link(url=f"http://www.wikicfp.com/cfp/servlet/event.showcfp?eventid={value}",
                                            title=value),
            "DblpConferenceId": lambda value: Link(url=f"https://dblp2.uni-trier.de/db/conf/{value}", title=value),
            "DblpSeries": lambda value: Link(url=f"https://dblp.org/db/conf/{value}/index.html", title=value),
            "TibKatId": lambda value: Link(url=f"https://www.tib.eu/en/search/id/TIBKAT:{value}", title=value),
            "Ordinal": lambda value: int(value) if isinstance(value, float) and value.is_integer() else value
        }
        return map

    @staticmethod
    def convertLodValues(lod: list, valueMap: dict):
        """
        Converts the lod values based on the given map of key to convert functions
        Args:
            lod: list of dicts to convert
            valueMap: map of lod keys to convert functions
        Returns:
            lod
        """
        if lod is None:
            return lod
        for record in lod.copy():
            for key, function in valueMap.items():
                if key in record:
                    record[key] = function(record[key])
        return lod

    def getDisplayIcons(self, icons):
        displayIcons = []
        for icon in icons:
            displayIcons.append("%04d%s%s" % (icon.index, icon.icon, icon.link))
        return displayIcons

    def render_template(self, templateName, **kwArgs):
        '''
        render the given template with the default arguments
        '''
        html = render_template(templateName, **kwArgs)
        return html

    def home(self, **kwArgs):
        return self.render_template('index.html', **kwArgs)


#
#  Command line entry point
#
if __name__ == '__main__':
    a = App()
    parser = a.getParser("Event Series Matching")
    args = parser.parse_args()
    # allow remote debugging if specified so on command line
    a.run(args)
