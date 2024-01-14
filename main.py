from website import create_app #'website' is a python package because it contains an __init__.py

app = create_app()

if __name__ == '__main__': 
    app.run(debug=True)
#runs the flask application, starts a web server, debug=True means it will auto-rerun the server after any changes are made, turn off for production
