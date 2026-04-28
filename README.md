# BrainMatch 🧠💡

BrainMatch to nowoczesna platforma internetowa łącząca uczniów z korepetytorami. Aplikacja umożliwia zakładanie kont (z podziałem na role: Uczeń, Nauczyciel, Administrator), dodawanie ogłoszeń o korepetycjach, przeglądanie publicznych profilów użytkowników oraz bezpośrednią komunikację poprzez wbudowany system wiadomości (czat).

## 🌟 Główne funkcjonalności

* **System ról:** Uczniowie (mogą przeglądać i pisać wiadomości), Nauczyciele (mogą dodatkowo tworzyć i edytować ogłoszenia) oraz Administratorzy (mają uprawnienia do usuwania dowolnych ogłoszeń).
* **Ogłoszenia (CRUD):** Tworzenie, odczyt, aktualizacja i usuwanie ofert z możliwością filtrowania po przedmiotach i sortowania (np. po dacie lub cenie).
* **Wbudowany komunikator (Czat):** Prywatne konwersacje między użytkownikami z historią wiadomości.
* **Profile publiczne:** Podgląd biogramu, wykształcenia oraz aktywnych ogłoszeń danego nauczyciela.
* **Dynamiczny tryb ciemny/jasny:** Przełącznik ("żarówka") zmieniający motyw całej strony w czasie rzeczywistym z płynnymi animacjami (obsługiwany przez CSS variables i LocalStorage).
* **Responsywny design:** Aplikacja działa płynnie na komputerach, tabletach i smartfonach.

---

## 🛠 Wykorzystane technologie i biblioteki (Mechanika)

Projekt został napisany w języku **Python 3** przy użyciu frameworka **Flask**.

### Backend (Python)
* **Flask:** Główny silnik aplikacji. Odpowiada za routing (obsługę ścieżek URL, np. `@app.route`), łączenie logiki Pythona z widokami (HTML) oraz przesyłanie danych do szablonów przy pomocy silnika **Jinja2** (np. `{{ current_user.username }}`).
* **Flask-SQLAlchemy:** System mapowania obiektowo-relacyjnego (ORM). Dzięki niemu nie trzeba pisać czystego kodu SQL. Mechanika polega na tworzeniu klas Pythona (np. `class User(db.Model)`), które automatycznie stają się tabelami w bazie **SQLite**.
* **Flask-Login:** Moduł do zarządzania sesjami użytkowników. Zapewnia mechanikę bezpiecznego logowania i wylogowywania, udostępnia obiekt `current_user` (pozwalający sprawdzić, kto aktualnie przegląda stronę) oraz dekorator `@login_required` (chroniący prywatne podstrony przed niezalogowanymi).
* **Flask-WTF (WTForms):** Biblioteka do tworzenia i walidacji formularzy HTML. Zabezpiecza aplikację przed atakami CSRF (Cross-Site Request Forgery) poprzez generowanie unikalnych tokenów dla każdego formularza.
* **Werkzeug (Security):** Użyto mechanik `generate_password_hash` oraz `check_password_hash` do bezpiecznego szyfrowania haseł w bazie danych (zapobiega to przetrzymywaniu haseł w czystym tekście).
* **Unittest:** Standardowa biblioteka Pythona użyta do stworzenia zautomatyzowanych testów sprawdzających m.in. rejestrację, dodawanie ogłoszeń czy uprawnienia administratora.

### Frontend
* **HTML5 / CSS3:** Struktura i autorskie style (m.in. tło w kropki, dynamiczne zmienne kolorystyczne `:root`).
* **Bootstrap 5:** Framework CSS/JS użyty do budowy responsywnego układu siatki (Grid), stylizacji kart (Cards), przycisków, formularzy, nawigacji (Navbar) oraz okien modalnych (Modal wylogowania).
* **Vanilla JavaScript:** Lekkie skrypty do obsługi przełączania motywu (Dark Mode) z zapisem wyboru do `localStorage` przeglądarki oraz auto-scrollowania w oknie czatu.

---

## 📁 Struktura plików i ich krótki opis

### Katalog główny
* `run.py` - Główny plik startowy. Uruchamia serwer developerski Flaska.
* `tests.py` - Zestaw kompleksowych testów jednostkowych weryfikujących poprawność działania logiki biznesowej, rejestracji, bazy danych oraz uprawnień (np. test roli Admina).

### Katalog `/app` (Główny moduł aplikacji)
* `__init__.py` - Plik konfiguracyjny (Application Factory). Inicjalizuje aplikację Flask, łączy bazę danych (SQLAlchemy) oraz zarządzanie sesjami (LoginManager).
* `models.py` - Definicja struktury bazy danych. Znajdują się tu klasy: `User` (użytkownicy), `Ad` (ogłoszenia) oraz `Message` (wiadomości z czatu).
* `forms.py` - Definicja formularzy (rejestracja, logowanie, dodawanie ogłoszenia, edycja konta) wraz z regułami walidacji (np. sprawdzanie, czy email nie jest już zajęty).
* `main.py` - Kontroler zawierający główne trasy (routes) aplikacji, takie jak strona główna, lista ogłoszeń, szczegóły ogłoszenia, wysyłanie wiadomości oraz niestandardowe strony błędów (404, 500).
* `auth.py` - Kontroler odpowiedzialny za autoryzację: ścieżki logowania, rejestracji, wylogowania oraz edycji ustawień konta.

### Katalog `/app/templates` (Widoki HTML / Jinja2)
* `base.html` - Szablon matka. Zawiera stałe elementy strony: pasek nawigacji, obsługę trybu ciemnego, wiadomości "flash" oraz modal wylogowania. Inne szablony po nim dziedziczą.
* `index.html` - Strona główna z powitaniem i podglądem najnowszych ofert.
* `ads.html` - Główna tablica ogłoszeń z formularzem filtrowania/sortowania oraz listą ofert ze zdjęciami autorów.
* `ad_details.html` - Widok szczegółowy pojedynczego ogłoszenia z pełnym opisem i panelem kontaktowym.
* `create_ad.html` - Uniwersalny formularz służący do tworzenia nowych i edycji istniejących ogłoszeń.
* `account.html` - Prywatny panel użytkownika pozwalający na edycję danych osobowych, biogramu i zdjęć.
* `public_profile.html` - Publiczna wizytówka nauczyciela, widoczna dla innych użytkowników.
* `messages.html` - Skrzynka odbiorcza – lista użytkowników, z którymi prowadzona jest konwersacja.
* `chat_room.html` - Widok prywatnego czatu z danym użytkownikiem (z dymkami wiadomości po prawej/lewej stronie).
* `404.html` & `500.html` - Niestandardowe, tematyczne strony błędów.

### Katalog `/app/static` (Pliki statyczne)
* `/profile_pics` - Folder przechowujący wgrane przez użytkowników zdjęcia profilowe (oraz `default_profile.jpg`).
* `/cover_pics` - Folder przechowujący zdjęcia w tle na stronach profilowych (oraz `default_cover.jpg`).