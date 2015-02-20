import flask
from .forms import BcdForm, HjmForm

from hjm.hjmpricer import HJMPricer
from bcd import get_bcd

api_bp = flask.Blueprint('api', __name__)


@api_bp.route('/', methods=['GET'])
def index():
    return flask.render_template('index.html')


@api_bp.route('/bcd', methods=['GET', 'POST'])
def bcd():
    form = BcdForm()
    if flask.request.method == 'POST':
        if form.validate_on_submit():
            price, sims, pca = get_bcd(form.entities.data,
                                    form.copula_type.data,
                                    form.seniority.data,
                                    float(form.frequency.data),
                                    form.premium_accrued.data,
                                    form.effective_date.data,
                                    form.maturity_date.data,
                                    form.recovery_rate.data,
                                    form.no_of_simulations.data)
            return flask.jsonify(price=price, sims=sims, pca=pca, status=True)
        else:
            return flask.jsonify(error="calibrate error", status=False)
    else:
        return flask.render_template('bcd.html', form=form)

@api_bp.route('/hjm', methods=['GET', 'POST'])
def hjm():
    form = HjmForm()

    if flask.request.method == 'POST':
        if form.validate_on_submit():
            #hjmp = HJMPricer(1.0, "ZCB", 10.0, 0, 0, 3, 1000)
            hjmp = HJMPricer(form.principal.data,
                                form.product.data,
                                form.maturity.data,
                                form.interest_rate.data,
                                form.frequency.data,
                                form.no_of_factors.data,
                                form.no_of_simulations.data)

            (price, sims), pca = hjmp.getHjmPrice()

            return flask.jsonify(price=price, sims=sims, pca=pca, status=True)
            #e = [x.data for x in form]
            #return flask.jsonify(entities=e, status=True)
        else:
            return flask.jsonify(error="hjm error", status=False)
    else:
        #import pdb; pdb.set_trace()
        return flask.render_template('hjm.html', form=form)

    #hjmp = HJMPricer(1.0, "ZCB", 10.0, 0, 0, 3, 1000)
    #(price, sims), pca = hjmp.getHjmPrice2()
    #return flask.jsonify(price=price, sims=sims, pca=pca, status=True)