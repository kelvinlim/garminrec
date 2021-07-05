from flask import Flask, render_template
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

if __name__ == '__main__':
    app.run(debug=True, port=3003)
    
    
    


