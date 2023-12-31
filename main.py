from flask import Flask, render_template, redirect, request
from datetime import datetime

app = Flask('__main__')

@app.route('/')
def index():
      copyright_year = datetime.now().year
      return render_template('index.html', year=copyright_year)

if '__name__' == '__main__':
      app.run(debug=True)