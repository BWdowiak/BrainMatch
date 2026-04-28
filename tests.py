import unittest
try:
    from run import app
except ImportError:
    try:
        from main import app
    except ImportError:
        from app import app
        
from app import db
from app.models import User, Ad, Message
from flask import url_for

class BrainMatchTest(unittest.TestCase):

    def setUp(self):
        """Konfiguracja przed każdym testem - baza w pamięci RAM."""
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SERVER_NAME'] = 'localhost'
        self.app = app.test_client()
        
        with app.app_context():
            db.create_all()

    def tearDown(self):
        """Sprzątanie po każdym teście."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def login_test_user(self, user):
        """Omija formularz - loguje bezpośrednio do sesji testowej."""
        with self.app.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True

    # --- 1. TESTY STRONY GŁÓWNEJ I PROFILU ---

    def test_home_page(self):
        with app.app_context():
            response = self.app.get(url_for('main.home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn("WITAJ W BRAINMATCH!".encode('utf-8'), response.data)

    def test_public_profile(self): 
        """Sprawdza, czy profil publiczny nauczyciela ładuje się poprawnie."""
        with app.app_context():
            u = User(username='Kowalski', email='k@t.pl', password_hash='h', role='teacher', first_name='Jan', last_name='Kowalski')
            db.session.add(u)
            db.session.commit()
            profile_url = url_for('main.view_profile', username='Kowalski')
            
        response = self.app.get(profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Jan".encode('utf-8'), response.data)


    def test_user_registration(self):
        with app.app_context():
            register_url = url_for('auth.register')
            
        response = self.app.post(register_url, data={
            'username': 'tester',
            'email': 'tester@brainmatch.pl',
            'password': 'password123',
            'confirm_password': 'password123',
            'role': 'student'
        }, follow_redirects=True)
        
        with app.app_context():
            user = User.query.filter_by(username='tester').first()
            if user:
                self.assertEqual(user.role, 'student')

    def test_student_cannot_create_ad(self): 
        """Sprawdza, czy system blokuje ucznia przed dodaniem ogłoszenia."""
        with app.app_context():
            student = User(username='uczen', email='u@t.pl', password_hash='h', role='student')
            db.session.add(student)
            db.session.commit()
            student_obj = db.session.get(User, student.id)
            new_ad_url = url_for('main.new_ad')
            
        self.login_test_user(student_obj)
        
        response = self.app.get(new_ad_url)
        self.assertEqual(response.status_code, 302)

    def test_unauthorized_ad_deletion(self): 
        """Sprawdza, czy zwykły uczeń dostanie błąd 403 (Zabronione), gdy spróbuje usunąć cudze ogłoszenie."""
        with app.app_context():
            teacher = User(username='nauczyciel', email='n@t.pl', password_hash='h', role='teacher')
            student = User(username='zwykly', email='z@t.pl', password_hash='h', role='student')
            db.session.add_all([teacher, student])
            db.session.commit()
            
            ad = Ad(title='Matma', subject='Matematyka', description='Opis', price=50, author=teacher)
            db.session.add(ad)
            db.session.commit()
            ad_id = ad.id
            student_obj = db.session.get(User, student.id)

        self.login_test_user(student_obj)
        
        with app.app_context():
            delete_url = url_for('main.delete_ad', ad_id=ad_id)
            
        response = self.app.post(delete_url)
        self.assertEqual(response.status_code, 403)


    def test_create_and_delete_ad(self):
        with app.app_context():
            teacher = User(username='nauczyciel_test', email='n@test.pl', password_hash='hash', role='teacher')
            admin = User(username='PawełD', email='admin@test.pl', password_hash='hash', role='admin')
            db.session.add_all([teacher, admin])
            db.session.commit()
            
            ad = Ad(title='Matma Test', subject='Matematyka', description='Opis', price=50.0, author=teacher)
            db.session.add(ad)
            db.session.commit()
            ad_id = ad.id
            admin_user = db.session.get(User, admin.id)

        self.login_test_user(admin_user)
        
        with app.app_context():
            delete_url = url_for('main.delete_ad', ad_id=ad_id)

        response = self.app.post(delete_url, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        with app.app_context():
            deleted_ad = db.session.get(Ad, ad_id)
            self.assertIsNone(deleted_ad)

    def test_update_own_ad(self): 
        """Sprawdza, czy nauczyciel może zaktualizować własne ogłoszenie."""
        with app.app_context():
            teacher = User(username='fizyk', email='f@t.pl', password_hash='h', role='teacher')
            db.session.add(teacher)
            db.session.commit()
            ad = Ad(title='Stary tytuł', subject='Fizyka', description='Brak', price=10, author=teacher)
            db.session.add(ad)
            db.session.commit()
            ad_id = ad.id
            teacher_obj = db.session.get(User, teacher.id)

        self.login_test_user(teacher_obj)
        
        with app.app_context():
            update_url = url_for('main.update_ad', ad_id=ad_id)
            
        self.app.post(update_url, data={
            'title': 'Nowy super tytuł',
            'subject': 'Fizyka',
            'description': 'Lepszy opis',
            'price': 100.0
        })
        
        with app.app_context():
            updated_ad = db.session.get(Ad, ad_id)
            self.assertEqual(updated_ad.title, 'Nowy super tytuł')
            self.assertEqual(updated_ad.price, 100.0)

    def test_ads_filtering(self): 
        """Sprawdza, czy filtrowanie po przedmiocie działa poprawnie."""
        with app.app_context():
            t = User(username='t', email='t@t.pl', password_hash='h', role='teacher')
            db.session.add(t)
            ad1 = Ad(title='Nauka Matmy', subject='Matematyka', description='...', price=50, author=t)
            ad2 = Ad(title='Nauka Chemii', subject='Chemia', description='...', price=50, author=t)
            db.session.add_all([ad1, ad2])
            db.session.commit()
            ads_url = url_for('main.ads', subject='Matematyka')

        response = self.app.get(ads_url)
        self.assertIn("Nauka Matmy".encode('utf-8'), response.data)
        self.assertNotIn("Nauka Chemii".encode('utf-8'), response.data)


    def test_send_message(self):
        with app.app_context():
            u1 = User(username='user1', email='u1@test.pl', password_hash='h', role='student')
            u2 = User(username='user2', email='u2@test.pl', password_hash='h', role='teacher')
            db.session.add_all([u1, u2])
            db.session.commit()
            u1_user = db.session.get(User, u1.id)
            u2_id = u2.id

        self.login_test_user(u1_user)
        
        with app.app_context():
            send_url = url_for('main.send_message', recipient_id=u2_id)

        self.app.post(send_url, data={'message_body': 'Siema, uczysz matmy?'}, follow_redirects=True)
        
        with app.app_context():
            msg = Message.query.filter_by(body='Siema, uczysz matmy?').first()
            self.assertIsNotNone(msg)

    def test_messages_inbox(self): 
        """Sprawdza, czy w zakładce 'Wiadomości' widać osobę, z którą rozmawialiśmy."""
        with app.app_context():
            u1 = User(username='StudentOlek', email='o@t.pl', password_hash='h', role='student')
            u2 = User(username='NauczycielMarek', email='m@t.pl', password_hash='h', role='teacher')
            db.session.add_all([u1, u2])
            db.session.commit()
            
            msg = Message(sender_id=u1.id, recipient_id=u2.id, body='Dzień dobry!')
            db.session.add(msg)
            db.session.commit()
            
            u1_obj = db.session.get(User, u1.id)

        self.login_test_user(u1_obj)
        
        with app.app_context():
            inbox_url = url_for('main.messages')
            
        response = self.app.get(inbox_url)
        self.assertIn("NauczycielMarek".encode('utf-8'), response.data)

if __name__ == '__main__':
    unittest.main()