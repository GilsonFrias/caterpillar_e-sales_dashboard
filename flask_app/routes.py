#
#Dec. 8, 2020

from flask import render_template
from flask import current_app as app


@app.route('/')
def home():
    #home page
    return render_template(
            'index.jinja2',
            title='Plotly Dash Flask Tutorial',
            description='Dashboard Home Page',
            template='home-template',
            body='This is a homepage served with Flask'
    )



