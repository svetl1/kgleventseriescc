# -*- coding: utf-8 -*-
import uuid

from fb4.app import AppWrap
from fb4.icons_bp import IconsBlueprint
from fb4.sse_bp import SSE_BluePrint
from fb4.widgets import Link, Icon, Image, Menu, MenuItem, DropDownMenu, LodTable, DropZoneField, ButtonField
from flask import render_template, request, flash, Markup, url_for, abort
from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length
from datetime import datetime, timedelta
import json
import os
import http.client
import re
import time
from werkzeug.utils import secure_filename


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
                return self.home(result=input)



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
