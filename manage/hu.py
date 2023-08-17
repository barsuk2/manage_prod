from flask import render_template

from . import bp


@bp.route('/list_reference')
def get_list_reference():
    return render_template('hu/index.html')

@bp.route('/data_from_scanning')
def get_data_from_scanning():
    return render_template('hu/scan_passport.html')

