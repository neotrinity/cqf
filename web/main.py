import os
import numpy
from scipy.stats import norm

from flask import Flask
import flask_debugtoolbar
from flask_debugtoolbar_lineprofilerpanel.profile import line_profile

app = Flask(__name__)

app.config['SECRET_KEY'] = 'jdsfl3cvmnslvlasdjoewr393ejl3j'


with app.app_context():
    # all your bluprints gets bolted on here
    from api.views import api_bp
    app.register_blueprint(api_bp)

# @app.route('/')
# @line_profile
# def hello():
#     arr = numpy.array([[1.0, 1.1], [1.2, 1.3]])
#     result = "<html><body>Checking numpy.. scipy works"
#     result += repr(arr)
#     result += "cdf: %s" % str(norm.cdf(0.24))
#     result += "ppf: %s" % str(norm.cdf(0.24))
#     result+="</body></html>"
#     return result

if __name__ == "__main__":
    app.debug = True
    app.config['DEBUG_TB_PROFILER_ENABLED'] = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    # Specify the debug panels you want
    app.config['DEBUG_TB_PANELS'] = [
        'flask_debugtoolbar.panels.versions.VersionDebugPanel',
        'flask_debugtoolbar.panels.timer.TimerDebugPanel',
        'flask_debugtoolbar.panels.headers.HeaderDebugPanel',
        'flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
        'flask_debugtoolbar.panels.template.TemplateDebugPanel',
        'flask_debugtoolbar.panels.sqlalchemy.SQLAlchemyDebugPanel',
        'flask_debugtoolbar.panels.logger.LoggingPanel',
        'flask_debugtoolbar.panels.profiler.ProfilerDebugPanel',
        # Add the line profiling
        'flask_debugtoolbar_lineprofilerpanel.panels.LineProfilerPanel'
    ]
    toolbar = flask_debugtoolbar.DebugToolbarExtension(app)

    app.run()