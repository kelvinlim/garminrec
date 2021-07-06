from flask import Flask, render_template, url_for, send_file
app = Flask(__name__)

@app.route("/")
def index():
   return render_template("index.html")

@app.route("/privacy")
def privacy():
   return render_template("privacy.html")

@app.route("/callback")
def callback():
   return render_template("callback.html")

@app.route("/icon")
def icon():
   #return send_file(url_for('static', filename='z_150_icon.png'))
   return send_file('static/z_150_icon.png')

# change port
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5005)
    
    
    


