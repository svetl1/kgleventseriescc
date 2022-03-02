import uuid

from fb4.app import AppWrap
from fb4.icons_bp import IconsBlueprint
from fb4.login_bp import LoginForm
from fb4.sqldb import db
from fb4.login_bp import LoginBluePrint
from flask_login import current_user, login_required
from fb4.sse_bp import SSE_BluePrint
from fb4.widgets import Copyright, Link, Icon, Image, Menu, MenuItem, DropDownMenu, LodTable, DropZoneField, ButtonField
from flask import redirect,render_template, request, flash, Markup, url_for, abort
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length
from sqlalchemy import Column
import sqlalchemy.types as types
from datetime import datetime, timedelta
import json
import os
import http.client
import re
import time
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.utils import secure_filename

class InputForm(FlaskForm):
    input = StringField()
    submit = SubmitField()

class App(AppWrap):
    def __init__(self):
        scriptdir = os.path.dirname(os.path.abspath(__file__))
        template_folder=scriptdir + '/templates'

        super().__init__(template_folder = template_folder)

        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'    

        self.app.config['BOOTSTRAP_BTN_STYLE'] = 'primary'
        self.app.config['BOOTSTRAP_BTN_SIZE'] = 'sm'

        db.init_app(self.app)
        self.db=db

        @app.before_first_request
        def before_first_request_func():
            self.initDB()

        @app.route('/', methods=['GET', 'POST'])
        def index():
            return self.home()    

        def initDB(self,limit=50):
            self.db.drop_all()
            self.db.create_all()
            self.initUsers()
            self.initMessages(limit)
            self.initIcons()

        def getMenuEntries(self):
            entries=  [
              ('index',"Home","home",False),
        ]
            return entries

        def getMenuLinks(self):
            links=[]
            for endpoint,title,_mdiIcon,newTab in self.getMenuEntries():
                links.append(Link(self.basedUrl(url_for(endpoint)),title=title,newTab=newTab))
            return links
         
        def home(self):
            menuLinks=self.getMenuLinks()
            return self.render_template('index.html',menuLinks=menuLinks)
    
        def icon(self):
            return self.render_template('icon.html')

        class BootstrapIcon(db.Model):
            id=Column(types.String(30), primary_key=True)
            index=Column(types.Integer)
    
            @hybrid_property
            def url(self):
                myUrl="https://icons.getbootstrap.com/icons/%s/" % self.id
                return myUrl
    
            @hybrid_property
            def link(self):
                myLink=Link(self.url,self.id)
                return myLink
    
            @hybrid_property
            def icon(self):
                myIcon=Icon(self.id)
                myIcon.userdata['#']=self.index
                return myIcon
    
            def asDict(self):
                myDict={
                    'link': self.link,
                    'icon': self.icon
                }
                return myDict
#
#  Command line entry point
#
if __name__ == '__main__':
    ea=App()
    parser=ea.getParser("Flask + Bootstrap4 demo application for bootstrap-flask")
    args=parser.parse_args()
    # allow remote debugging if specified so on command line
    ea.optionalDebug(args)
    ea.run(args)