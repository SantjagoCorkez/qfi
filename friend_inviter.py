from app.flask_app import make_app

app = make_app('development')

if __name__ == '__main__':
    app.run()
