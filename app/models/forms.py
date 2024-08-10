from flask_wtf import FlaskForm
from wtforms import StringField, SelectMultipleField


class SearchFeedForm(FlaskForm):
    start_date = StringField('Start Date')
    end_date = StringField('End Date')
    words = StringField('Words')
    sources = SelectMultipleField('Sources', choices=[
        ('1', '444.hu'),
        ('2', 'telex.hu'),
        ('3', '24.hu'),
        ('4', 'origo.hu'),
        ('5', 'hirado.hu'),
        ('6', 'magyarnemzet.hu'),
        ('7', 'index.hu')
    ])
    free_text = StringField('Free Text Search')
