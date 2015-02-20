import datetime
from flask_wtf import Form
from wtforms import validators
from wtforms import SelectMultipleField as _SelectMultipleField, DateField, IntegerField as _IntegerField
from wtforms.widgets import TextInput as _TextInput
from wtformsparsleyjs import (Select,
                        SelectField,
                        IntegerField,
                        DecimalField,
                        BooleanField,
                        FloatField)

from bcd.entity import ENTITIES

class SpecialTextInput(_TextInput):
    def __call__(self, field, **kwargs):
        kwargs[u'parsley-senioritylimit'] = '0'
        return super(SpecialTextInput, self).__call__(field, **kwargs)

class SpecialIntegerField(_IntegerField):
    def __init__(self, *args, **kwargs):
        super(SpecialIntegerField, self).__init__(widget=SpecialTextInput(), *args, **kwargs)

class SelectMultipleField(_SelectMultipleField):
    def __init__(self, *args, **kwargs):
        super(SelectMultipleField, self).__init__(widget=Select(multiple=True), *args, **kwargs)

class BcdForm(Form):
    entities = SelectMultipleField('Entities',
        [validators.InputRequired()],
        choices=sorted([(k, "%s [%s]" % (v, k)) for k, v in ENTITIES.items()]))

    copula_type = SelectField('Copula Type',
        [validators.InputRequired()],
        choices=[('gaussian', 'Gaussian Copula'),
                    ('student', 'StudentT Copula')])

    seniority = SpecialIntegerField('Seniority', [validators.InputRequired(),
        validators.NumberRange(min=0, max=10)], default=1)

    basis = SelectField('Basis',
        [validators.InputRequired()],
        choices=[('ACT360', 'ACT360')])

    frequency = SelectField('Frequency', [validators.InputRequired()],
        choices=[('0.83333333', 'Monthly'),
                    ('0.25', 'Quaterly'),
                    ('0.5', 'Half-Yearly'),
                    ('1.0', 'Yearly')])

    premium_accrued = BooleanField('Premium Accrued?', [validators.InputRequired()], default=True)

    effective_date = DateField('Effective Date', [validators.InputRequired()],
        format='%Y/%m/%d', default=datetime.date(2010, 05, 01))

    maturity_date = DateField('Maturity Date', [validators.InputRequired()],
        format='%Y/%m/%d', default=datetime.date(2015, 05, 01))

    recovery_rate = FloatField('Recovery Rate', [validators.InputRequired(),
        validators.NumberRange(min=0.0, max=1.0)], default=0.43)

    no_of_simulations = IntegerField('No of simulations', [validators.InputRequired(),
        validators.NumberRange(min=100, max=10000)], default=1000)

    def validate_seniority(form, field):
        if field.data > len(form.entities.data):
            raise validators.ValidationError('Seniority - %s greater than no: of entities - %s' % (field.data, form.entities.data))


class HjmForm(Form):

    principal = FloatField('Principal', [validators.InputRequired(),
                    validators.NumberRange(min=0.0, max=1.0)], default=1.0)
    product = SelectField('Product',[validators.InputRequired()],
                            choices=[('ZCB', 'Zero Coupon Bond'),
                                        ('CAP', 'C A P')])
    maturity = FloatField('Maturity', [validators.InputRequired(),
        validators.NumberRange(min=1.0, max=10.0)], default=10.0)
    interest_rate = IntegerField('Interest Rate', [validators.InputRequired(),
        validators.NumberRange(min=0, max=10)], default=0)
    frequency = IntegerField('Frequency', [validators.InputRequired(),
        validators.NumberRange(min=0, max=10)], default=0)
    no_of_factors = IntegerField('No of factors', [validators.InputRequired(),
        validators.NumberRange(min=0, max=10)], default=3)
    no_of_simulations = IntegerField('No of simulations', [validators.InputRequired(),
        validators.NumberRange(min=100, max=5000)], default=1000)


