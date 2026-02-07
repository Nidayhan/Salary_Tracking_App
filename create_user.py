from app import db, User, app
from werkzeug.security import generate_password_hash

def create_user(username, password):
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    print(f"Kullanıcı {username} başarıyla oluşturuldu.")

if __name__ == '__main__':
    with app.app_context():
        username = 'admin'  # Buraya kullanıcı adınızı girin
        password = 'admin123'  # Buraya şifrenizi girin

        create_user(username, password)
