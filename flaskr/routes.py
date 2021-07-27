from flask import Flask, request, redirect, render_template, g, url_for, session, jsonify
from json2html import *
from flaskr import app
import requests
import json
import random


@app.route('/')
def home():

    return render_template('circle-pack.html')

