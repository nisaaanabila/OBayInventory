from flask import Flask, render_template
from config import Config
from authlib.integrations.flask_client import OAuth

app = Flask(
    __name__,
    template_folder="Frontend/templates",
    static_folder="Frontend"
)

app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY
print("SECRET KEY =", Config.SECRET_KEY)

oauth = OAuth(app)
app.extensions['google_oauth'] = oauth.register(
    name='google',
    client_id=Config.GOOGLE_CLIENT_ID,
    client_secret=Config.GOOGLE_CLIENT_SECRET,
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
)


from Backend.routes.login import auth
from Backend.routes.owner import owner
from Backend.routes.staff import staff
from Backend.routes.dashboard import dashboard
from Backend.routes.bahan import bahan
from Backend.routes.vendor import vendor
from Backend.routes.produk import produk
from Backend.routes.resep import resep
from Backend.routes.barang_masuk import barang_masuk
from Backend.routes.penggunaan import penggunaan
from Backend.routes.po import po


@app.route("/")
def home():
    return render_template("login.html")


app.register_blueprint(auth)
app.register_blueprint(owner)
app.register_blueprint(staff)
app.register_blueprint(dashboard)
app.register_blueprint(bahan)
app.register_blueprint(vendor)
app.register_blueprint(produk)
app.register_blueprint(resep)
app.register_blueprint(barang_masuk)
app.register_blueprint(penggunaan)
app.register_blueprint(po)

print(app.url_map)
if __name__ == "__main__":
    app.run(debug=True, port=5000)