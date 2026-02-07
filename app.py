from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Kullanıcı Modeli
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Personel Modeli
class Personel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(255), nullable=False)
    
    departman = db.Column(db.String(255), nullable=False)

# Maaş Modeli
class Maas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    personel_id = db.Column(db.Integer, db.ForeignKey('personel.id'), nullable=False)
    yil = db.Column(db.Integer, nullable=False)
    ay = db.Column(db.String(length=20), nullable=False)
    net_maas = db.Column(db.Float, nullable=False)
    yemek = db.Column(db.Float, nullable=False)
    avans = db.Column(db.Float, nullable=False)
    icra = db.Column(db.Float, nullable=False)
    kesinti1 = db.Column(db.Float, nullable=False)
    kesinti2 = db.Column(db.Float, nullable=False)
    aciklama = db.Column(db.Text, nullable=True)
    bankaya_yatan = db.Column(db.Float, nullable=False)
    elden_teslim = db.Column(db.Float, nullable=False)

# Veritabanı tablolarını oluştur
with app.app_context():
    db.create_all()
    

# Giriş Sayfası
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if validate_login(username, password):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash('Kullanıcı adı veya şifre yanlış!', 'danger')

    return render_template('login.html')

# Çıkış Sayfası
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    personeller = Personel.query.all()
    return render_template('index.html', personeller=personeller)

@app.route('/personel/<int:personel_id>')
def personel_detay(personel_id):
    personel = Personel.query.get(personel_id)
    if personel is None:
        return redirect(url_for('index'))
    
    maaslar = Maas.query.filter_by(personel_id=personel_id).all()
    return render_template('personel_detay.html', personel=personel, maaslar=maaslar)

# Kullanıcı Girişi Kontrol Fonksiyonu
def validate_login(username, password):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        return True
    return False


# Personel Ekleme
@app.route('/add', methods=['POST'])
def add_personel():
    if 'username' not in session:
        return redirect(url_for('login'))

    ad = request.form['ad']

    
    departman = request.form['departman']

    # Personeli veritabanına ekleme
    personel = Personel.query.filter_by(ad=ad, departman=departman).first()
    if not personel:
        personel = Personel(ad=ad, departman=departman)
        db.session.add(personel)
        db.session.commit()

    return redirect(url_for('index'))

@app.route('/delete-personel', methods=['POST'])
def delete_personel():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    personel_ids = request.form.getlist('personel_ids')
    if personel_ids:
        for personel_id in personel_ids:
            personel = Personel.query.get(personel_id)
            if personel:
                db.session.delete(personel)
        db.session.commit()
    
    return redirect(url_for('index'))


@app.route('/api/maas-ekle', methods=['POST'])
def api_add_maas():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Giriş yapmanız gerekiyor!'})

    data = request.get_json()
    ad = data.get('ad')
    yil = int(data.get('yil'))
    ay = data.get('ay')
    net_maas = float(data.get('net_maas'))
    yemek = float(data.get('yemek'))
    avans = float(data.get('avans'))
    icra = float(data.get('icra'))
    kesinti1 = float(data.get('kesinti1'))
    kesinti2 = float(data.get('kesinti2'))
    aciklama = data.get('aciklama')
    bankaya_yatan = 17002.00
    elden_teslim = (net_maas + yemek + avans) - (icra + kesinti1 + kesinti2 + bankaya_yatan)

    personel = Personel.query.filter_by(ad=ad).first()
    if personel:
        maas = Maas(
            personel_id=personel.id, yil=yil, ay=ay, net_maas=net_maas, yemek=yemek,
            avans=avans, icra=icra, kesinti1=kesinti1, kesinti2=kesinti2,
            aciklama=aciklama, bankaya_yatan=bankaya_yatan, elden_teslim=elden_teslim
        )
        db.session.add(maas)
        db.session.commit()
        return jsonify({'success': True, 'personel_id': personel.id})
    
    return jsonify({'success': False, 'message': 'Personel bulunamadı!'})



# Personel Güncelleme
@app.route('/update_personel', methods=['POST'])
def update_personel():
    if 'username' not in session:
        return redirect(url_for('login'))

    personel_id = request.form['id']
    ad = request.form['ad']
   
   
    departman = request.form['departman']

    personel = Personel.query.get(personel_id)
    if personel:
        personel.ad = ad
        
       
        personel.departman = departman
        db.session.commit()

    return redirect(url_for('index'))


@app.route('/update_maas', methods=['POST'])
def update_maas():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    data = request.form
    maas_id = data.get('id')
    yil = int(data.get('yil'))
    ay = data.get('ay')
    net_maas = float(data.get('net_maas'))
    yemek = float(data.get('yemek'))
    avans = float(data.get('avans'))
    icra = float(data.get('icra'))
    kesinti1 = float(data.get('kesinti1'))
    kesinti2 = float(data.get('kesinti2'))
    aciklama = data.get('aciklama')
    bankaya_yatan = float(data.get('bankaya_yatan'))
    elden_teslim = float(data.get('elden_teslim'))
    
    maas = Maas.query.get(maas_id)
    if maas:
        maas.yil = yil
        maas.ay = ay
        maas.net_maas = net_maas
        maas.yemek = yemek
        maas.avans = avans
        maas.icra = icra
        maas.kesinti1 = kesinti1
        maas.kesinti2 = kesinti2
        maas.aciklama = aciklama
        maas.bankaya_yatan = bankaya_yatan
        maas.elden_teslim = elden_teslim

        db.session.commit()
    
    return redirect(url_for('personel_detay', id=maas.personel_id))




if __name__ == '__main__':
    app.run(debug=True)
