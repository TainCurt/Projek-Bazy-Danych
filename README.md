# Projekt Domino
## Bazodanowa aplikacja webowa zajmująca się zarządzaniem współdzielnią mieszkaniową.
Serwis obsługuje dwa typy użytkowników: Administratora oraz Użytkownika (Mieszkańca/Właściciela mieszkania). Portal udostępnia funkcjonalności umożliwiające rejestrację budynków oraz przypisywanie do nich mieszkań. Użytkownicy przypisani do mieszkań otrzymują jedną z ról: TENANT (mieszkaniec) lub OWNER (właściciel).

Jeden użytkownik może być przypisany do wielu mieszkań, natomiast każde mieszkanie może mieć przypisanego tylko jednego właściciela. Administrator posiada uprawnienia do nakładania opłat na poszczególne mieszkania oraz do publikowania ogłoszeń.

Użytkownicy standardowi mają możliwość przeglądania swoich mieszkań oraz zgłaszania problemów i uwag dotyczących mieszkania (FLAT), budynku (BUILDING) lub spraw ogólnych (GENERAL).

## Technologie
### Backend
Serwis Domino opiera się na relacyjnej bazie danych PostgreSQL. Backend aplikacji został zaimplementowany w języku Python z wykorzystaniem frameworka Django. Dodatkowo zastosowano Django REST Framework, będący rozszerzeniem Django, w celu tworzenia interfejsu API umożliwiającego udostępnianie danych w formacie JSON. W projekcie wykorzystano również dekorator api_view, który pozwala na definiowanie funkcyjnych widoków API oraz obsługę żądań HTTP zgodnie z zasadami architektury REST.

### Frontend
Prezentajca frontendu znajduje się w pliku Frontend_Domino_showcase.pdf

## Baza danych oraz Modele
Baza danych serwisu Domino zawiera 8 encji: User, Flat, Building, Rent, Report, Announ, UserFlat, Auth
### Encje
#### Building
Encja reprezentuje budynek zarejestrowany w systemie.  
Przechowuje dane adresowe, takie jak ulica, numer budynku, miasto oraz kod pocztowy.  
Zastosowanie ograniczenia unikalności zapobiega duplikowaniu budynków o tym samym adresie.

#### Flat
Encja opisuje mieszkanie przypisane do konkretnego budynku.  
Zawiera informacje o numerze mieszkania, piętrze, powierzchni oraz statusie dostępności.  
Każde mieszkanie jest jednoznacznie powiązane z jednym budynkiem.

#### User
Encja reprezentuje użytkownika systemu wraz z jego danymi identyfikacyjnymi i rolą.  
Przechowuje informacje o statusie konta oraz dacie utworzenia.  
Użytkownik może być przypisany do jednego lub wielu mieszkań.

#### UserFlat
Encja pośrednicząca realizująca relację wiele-do-wielu pomiędzy użytkownikami a mieszkaniami.  
Określa rolę użytkownika w danym mieszkaniu oraz okres obowiązywania przypisania.  
Umożliwia zachowanie historii relacji użytkownik–mieszkanie.

#### Rent
Encja reprezentuje opłaty czynszowe naliczane dla mieszkań w określonym miesiącu i roku.  
Przechowuje informacje o kwocie, terminie płatności oraz aktualnym statusie opłaty.  
Umożliwia kontrolę należności i zaległości finansowych.

#### Report
Encja służy do zgłaszania problemów i uwag przez użytkowników systemu.  
Zgłoszenia mogą dotyczyć konkretnego mieszkania, budynku lub mieć charakter ogólny.  
Przechowywane są informacje o typie, treści oraz statusie zgłoszenia.

#### Announ
Encja reprezentuje ogłoszenia publikowane w systemie przez uprawnionych użytkowników.  
Zawiera tytuł, treść oraz zakres czasowy obowiązywania ogłoszenia.  
Umożliwia przekazywanie istotnych informacji mieszkańcom.

#### AuthToken
Encja przechowuje tokeny uwierzytelniające przypisane do użytkowników systemu.  
Służy do autoryzacji dostępu do API oraz identyfikacji aktywnych sesji użytkowników.  
Każdy token posiada unikalny klucz oraz datę utworzenia.
Jest to encja stricte techniczna nie traktujemy jej jako logicznego elementu systemu.

### Struktura kodu

Wszystkie encje zostały napisane za pomocą Modeli z frameworku Django. 
Każda encja ma bardzo podobną strukture wyglądają w następujący sposób:

```python
  class Encja(models.Model):
      Atrybut1 = ...
      Atrybut2 = ...
      Atrybut3 = ...
      ...

      def __str__(self):
          return f"{self.Atrybut1} ..."
```
w celu szczegółowej analizy omówmy encję UserFlat, która jest encję pośrednią pomiędzy encjami User oraz Flat w celu obsługi relacji Many-To-Many. Encja UserFlat zawiera wszystkie elementy, które zawierają się w innych encjach w takiej samej lub mniejszej strukturze

```python
    class UserFlat(models.Model):
    UserFlatId = models.BigAutoField(primary_key=True)
    UserId = models.ForeignKey(User, on_delete=models.CASCADE, related_name='userflats')
    FlatId = models.ForeignKey(Flat, on_delete=models.CASCADE, related_name='userflats')
    UserFlatDateFrom = models.DateField(auto_now_add=True)
    UserFlatDateTo = models.DateField(null=True, blank=True)
    UserFlatRole = models.CharField(max_length=10, choices=UserFlatRole.choices)
    class Meta:
        unique_together = ('UserId', 'FlatId', 'UserFlatDateFrom')

    def __str__(self):
        return f"{self.UserId} - {self.FlatId}"
```
- Encja UserFlat zawiera atrybut ***UserFlatId***, który zawiera klucz główny
- Atrybuty ***UserId*** oraz ***FlatId*** odpowiadają kluczom obcym encji ***User*** oraz ***Flat*** w celu obsługi relacji Many-To-Many
- Atrybut ***UserFlatDateTo*** jest atrybutem opcjonalnym, który nie musi zawierać się w utworzonym obiekcie
- Atrybut ***UserFlatRole*** jest enum zawierającym stany jakie rekord może przyjmowa

Enum w projekcie ma następującą strukture:

```python
    class Enum(models.TextChoices):
        CHOICE1 = 'CHOICE1', 'choice1'
        CHOICE2 = 'CHOICE2', 'choice2'
```
Dla encji UserFlat:
```python
    class UserFlatRole(models.TextChoices):
        OWNER = 'OWNER', 'Właściciel'
        TENANT = 'TENANT', ' Najemca'
```
Pozwala to określić z góry role jakie może przyjąć dany użytkownik
- Klasa ***Meta*** zapewnia, że nie możliwości aby występowały dokładnie dwa takie same rekordy w bazie danych.
- Funkcja ***\_\_str\_\_(self)*** umożliwia lepsze wyświetlanie rekordów bazy danych w celu wygodniejszego testowania. 

## Serializery
Serializery to mechanizm służący do zamiany danych pomiędzy obiektami Pythona a formatami używanymi w API w przypadku serwisu Domino jest to JSON.

### Struktura
Struktura serializerów wygląda następująco: 
```python
    class Serializer(serializers.ModelSerializer)
        class Meta:
        model = Encja
        fields = '__all__'
```
Weźmy pod lupę serializer dla encji User
```python
    class UserSerializer(serializers.ModelSerializer):
        Flats = serializers.PrimaryKeyRelatedField(
            many=True,
            queryset=Flat.objects.all(),
            required=False
        )
    
        class Meta:
            model = User
            fields = '__all__'
            extra_kwargs = {
                'UserPassword' : {'write_only': True},
                'UserRole' : {"required": False},
                'UserDate': {'read_only': True}
            }
    
        def create(self, validated_data):
            ...
        def update(self, instance, validated_data):
            ...
```
Serializer encji User różni się od innych tym, że posiada funkcje ***create*** oraz ***update*** oraz posiada wewnętrzny serializer ***Flat***. Wszystkie te dodatkowe rzeczy służą do implementacji relacji Many-To-Many z encją flat. 
Opisując strukture typowego serializera możemy wyróżnić
- klasa ***Meta*** służąca do konfiguracji serializera
  - ***model***  - mówi z jakiego modelu serialazer będzie pobierał atrybuty
  - ***fields*** - mówi o tym jakie pola będą pobierane

## CRUD oraz specjalne zapytania

Backend aplikacji Domino udostępnia zestaw endpointów umożliwiających realizację operacji CRUD (Create, Read, Update, Delete) oraz zapytań specjalnych wynikających z logiki biznesowej systemu. Dostęp do poszczególnych zasobów jest kontrolowany na podstawie roli użytkownika.

---

### Użytkownicy (User)

- **GET `/users/`**  
  Pobranie listy wszystkich użytkowników systemu.

- **POST `/users/`** *(ADMIN)*  
  Utworzenie nowego użytkownika.  
  Podczas tworzenia możliwe jest przypisanie użytkownika do mieszkań – w takim przypadku automatycznie otrzymuje on rolę **TENANT**.

- **GET `/users/{id}/`** *(ADMIN)*  
  Pobranie szczegółowych informacji o użytkowniku.

- **PATCH `/users/{id}/`** *(ADMIN)*  
  Częściowa aktualizacja danych użytkownika (np. zmiana hasła, nazwiska).

- **DELETE `/users/{id}/`** *(ADMIN)*  
  Usunięcie użytkownika z systemu.

---

### Budynki (Building)

- **GET `/buildings/`**  
  Pobranie listy budynków.

- **POST `/buildings/`** *(ADMIN)*  
  Utworzenie nowego budynku.  
  System zapobiega duplikacji budynków o identycznym adresie.

- **GET `/buildings/{id}/`**  
  Pobranie szczegółowych danych budynku.

- **PUT `/buildings/{id}/`** *(ADMIN)*  
  Aktualizacja danych budynku.

- **DELETE `/buildings/{id}/`** *(ADMIN)*  
  Usunięcie budynku wraz z powiązanymi danymi.

---

### Mieszkania (Flat)

- **GET `/buildings/{building_id}/flats/`**  
  Pobranie listy mieszkań w danym budynku.

- **POST `/buildings/{building_id}/flats/`** *(ADMIN)*  
  Dodanie nowego mieszkania do budynku.

- **GET `/buildings/{building_id}/flats/{flat_id}/`**  
  Pobranie szczegółów mieszkania.

- **PUT `/buildings/{building_id}/flats/{flat_id}/`** *(ADMIN)*  
  Aktualizacja danych mieszkania.

- **DELETE `/buildings/{building_id}/flats/{flat_id}/`** *(ADMIN)*  
  Usunięcie mieszkania.

---

### Przypisania użytkowników do mieszkań (UserFlat)

- **GET `/buildings/{building_id}/flats/{flat_id}/tenants/`**  
  Pobranie listy przypisań użytkowników do mieszkania (historia).

- **POST `/buildings/{building_id}/flats/{flat_id}/tenants/`** *(ADMIN)*  
  Przypisanie użytkownika do mieszkania jako **TENANT** lub **OWNER**.  
  System wymusza istnienie tylko jednego aktywnego właściciela (**OWNER**) na mieszkanie.

- **GET `/buildings/{building_id}/flats/{flat_id}/tenants/{userflat_id}/`**  
  Pobranie szczegółów przypisania.

- **PUT `/buildings/{building_id}/flats/{flat_id}/tenants/{userflat_id}/`** *(ADMIN)*  
  Aktualizacja przypisania (np. zmiana roli).

- **DELETE `/buildings/{building_id}/flats/{flat_id}/tenants/{userflat_id}/`** *(ADMIN)*  
  Usunięcie przypisania użytkownika do mieszkania.

---

### Opłaty czynszowe (Rent)

- **GET `/buildings/{building_id}/flats/{flat_id}/rent/`**  
  Pobranie listy naliczeń dla mieszkania.

- **POST `/buildings/{building_id}/flats/{flat_id}/rent/`** *(ADMIN)*  
  Dodanie nowego naliczenia czynszu.

- **GET `/buildings/{building_id}/flats/{flat_id}/rent/{rent_id}/`**  
  Pobranie szczegółów naliczenia.

- **PUT `/buildings/{building_id}/flats/{flat_id}/rent/{rent_id}/`** *(ADMIN)*  
  Aktualizacja danych naliczenia.

- **DELETE `/buildings/{building_id}/flats/{flat_id}/rent/{rent_id}/`** *(ADMIN)*  
  Usunięcie naliczenia.

---

### Zgłoszenia (Report)

#### Zgłoszenia użytkownika
- **GET `/my/reports/`**  
  Pobranie listy zgłoszeń zalogowanego użytkownika.

- **POST `/my/reports/`**  
  Utworzenie nowego zgłoszenia typu **GENERAL**, **FLAT** lub **BUILDING**.  
  Dostęp do zgłoszeń typu FLAT i BUILDING jest weryfikowany na podstawie przypisań użytkownika.

---

#### Zarządzanie zgłoszeniami (ADMIN)
- **GET `/reports/`** *(ADMIN)*  
  Pobranie listy wszystkich zgłoszeń (z możliwością filtrowania).

- **GET `/reports/{id}/`** *(ADMIN)*  
  Pobranie szczegółów zgłoszenia.

- **PUT `/reports/{id}/`** *(ADMIN)*  
  Zmiana statusu zgłoszenia.

- **DELETE `/reports/{id}/`** *(ADMIN)*  
  Usunięcie zgłoszenia.

---

### Ogłoszenia (Announ)

- **GET `/announ/`**  
  Pobranie listy ogłoszeń (dostęp publiczny).

- **POST `/announ/`** *(ADMIN)*  
  Dodanie nowego ogłoszenia.

- **GET `/announ/{id}/`**  
  Pobranie szczegółów ogłoszenia.

- **PUT `/announ/{id}/`** *(ADMIN)*  
  Aktualizacja ogłoszenia.

- **DELETE `/announ/{id}/`** *(ADMIN)*  
  Usunięcie ogłoszenia.

---

### Zapytania specjalne i statystyki

- **GET `/rentstats/`** *(ADMIN)*  
  Zestawienie zaległości i naliczeń według budynków dla wskazanego okresu.

- **GET `/flatsrentstats/`** *(ADMIN)*  
  Lista mieszkań, których zaległości przekraczają zadany próg.

- **GET `/reportstats/`** *(ADMIN)*  
  Statystyki zgłoszeń budynkowych według statusów.

## Autoryzacja i kontrola dostępu

Aplikacja Domino wykorzystuje własny mechanizm autoryzacji oparty o tokeny, zaimplementowany przy użyciu Django REST Framework. Autoryzacja realizowana jest na poziomie widoków API i kontroluje dostęp użytkowników do zasobów systemu.

---

### Mechanizm logowania

Uwierzytelnianie użytkownika odbywa się poprzez endpoint logowania:

- **POST `/login/`**

Użytkownik przekazuje w treści żądania swój adres e-mail oraz hasło.  
Po poprawnym uwierzytelnieniu generowany jest unikalny token, który identyfikuje sesję użytkownika.

Każde poprawne logowanie skutkuje utworzeniem nowego tokenu, co umożliwia jednoczesne istnienie wielu aktywnych sesji dla jednego użytkownika.

---

### Token autoryzacyjny

Token przekazywany jest w nagłówku HTTP każdego żądania wymagającego uwierzytelnienia:

Authorization: Token <TOKEN>

Tokeny przechowywane są w encji **AuthToken** i zawierają:
- unikalny klucz tokenu,
- użytkownika, do którego są przypisane,
- datę utworzenia.

Brak tokenu, niepoprawny format nagłówka lub nieistniejący token skutkują odrzuceniem żądania.

---

### Role użytkowników

System rozróżnia dwie role użytkowników:

- **ADMIN**  
  Użytkownik administracyjny posiada pełny dostęp do funkcjonalności systemu, w tym:
  - zarządzanie użytkownikami,
  - zarządzanie budynkami i mieszkaniami,
  - przypisywanie użytkowników do mieszkań,
  - zarządzanie opłatami, zgłoszeniami i ogłoszeniami,
  - dostęp do statystyk i raportów.

- **USER (RESIDENT / OWNER)**  
  Użytkownik standardowy posiada dostęp wyłącznie do danych, które go dotyczą, w szczególności:
  - przegląd własnych mieszkań,
  - przegląd własnych opłat,
  - zgłaszanie problemów i usterek,
  - przegląd ogłoszeń.

---

### Kontrola dostępu

Kontrola dostępu realizowana jest w warstwie backendu i opiera się na:
- weryfikacji obecności i poprawności tokenu,
- sprawdzeniu roli użytkownika,
- sprawdzeniu powiązań użytkownika z danym zasobem (np. mieszkanie, budynek).

W przypadku naruszenia zasad autoryzacji API zwraca odpowiednie kody HTTP:
- **401 Unauthorized** – brak lub niepoprawny token,
- **403 Forbidden** – brak wymaganych uprawnień,
- **404 Not Found** – próba dostępu do nieistniejącego zasobu.

---

### Endpointy wymagające autoryzacji

Autoryzacji wymagają m.in.:
- wszystkie operacje modyfikujące dane (POST, PUT, PATCH, DELETE),
- endpointy typu `my/*`,
- endpointy administracyjne,
- endpointy statystyczne.

Endpointy publiczne (niewymagające autoryzacji) obejmują m.in.:
- pobieranie listy budynków,
- pobieranie listy mieszkań,
- pobieranie ogłoszeń.

---

Sekcja ta opisuje sposób zabezpieczenia API oraz reguły dostępu do poszczególnych funkcjonalności systemu.

## Uruchomienie projektu

Poniżej przedstawiono instrukcję uruchomienia backendu aplikacji Domino w środowisku lokalnym.

---

### Wymagania wstępne

Do uruchomienia projektu wymagane są:
- Python 3.10 lub nowszy,
- PostgreSQL,
- menedżer pakietów `pip`,
- (opcjonalnie) środowisko wirtualne `venv`.

Wymagane pakiety:
```terminal
pip install django
```

```terminal
pip install djangorestframework
```

```terminal
pip install psycopg2-binary
```

  

---

### Konfiguracja bazy danych
Aplikacja wykorzystuje relacyjną bazę danych PostgreSQL.

W pliku `settings.py` należy skonfigurować połączenie z bazą danych:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'Domino',
        'USER': 'postgres',
        'PASSWORD': '<hasło>',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```
Należy upewnić się, że baza danych istnieje oraz użytkownik posiada odpowiednie uprawnienia.

---
### Migracje bazy danych
Po poprawnej konfiguracji bazy danych należy wykonać migracje:
```terminal
python manage.py makemigrations
python manage.py migrate
```
---
### Utworzenie konta administratora
W celu uzyskania dostępu administracyjnego do systemu należy utworzyć konto administratora poprzez:
```terminal
python manage.py shell
```
Wklejając w nim formułkę dostępną w `api_test/MAIN_ADMIN_FORCED.py`:
```python
from DominoApp.models import User, UserRole
from django.contrib.auth.hashers import make_password
import datetime

admin = User.objects.create(
    UserName="Admin",
    UserSurname="Root",
    UserEmail="admin@root.com",
    UserPassword=make_password("admin123"),
    UserRole=UserRole.ADMIN,
    UserDate=datetime.date.today(),
    UserStatus=True
)
admin.UserId
```
---
### Uruchomienie serwera
Serwer uruchamiany jest poleceniem:
```terminal
python manage.py runserver
```
Backend aplikacji będzie dostępny pod adresem:
```terminal
http://127.0.0.1:8000/
```
---
### Testowanie API
Do testowania API zalecane jest użycie narzędzia REST Client oraz pliku `api_test_final_final.http`. Plik zawiera kompletny scenariusz testowy umożliwiający przetestowanie wszystkich funkcjonalności backendu krok po kroku.
