#!/usr/bin/env python3

import logging
from datetime import datetime
from logging.config import fileConfig

from flask import Flask, jsonify, request

from services.fundamentus import get_papers, get_details_by_paper

fileConfig('config/logging_config.ini')
LOGGER = logging.getLogger('sLogger')
app = Flask(__name__)

# First update
# lista, dia = dict(get_papers()), datetime.strftime(datetime.today(), '%d')
# lista = {outer_k: {inner_k: float(inner_v) for inner_k, inner_v in outer_v.items()} for outer_k, outer_v in
#          lista.items()}


@app.route("/")
def json_api():
    LOGGER.debug('')
    global lista, dia

    # Then only update once a day
    if dia == datetime.strftime(datetime.today(), '%d'):
        return jsonify(lista)
    else:
        lista, dia = dict(get_papers()), datetime.strftime(datetime.today(), '%d')
        lista = {outer_k: {inner_k: float(inner_v) for inner_k, inner_v in outer_v.items()} for outer_k, outer_v in
                 lista.items()}
        return jsonify(lista)


@app.route("/details", methods=['GET'])
def details():
    paper = request.args.get('paper')
    LOGGER.info(f'Getting detail of: {paper}')
    get_details_by_paper(paper_name=paper)
    return {}

app.run(debug=True)
