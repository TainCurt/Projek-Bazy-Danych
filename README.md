# Projekt Domino
## Bazodanowa aplikacja webowa zajmująca się zarządzaniem współdzielnią mieszkaniową.
Serwis obsługuje dwa typy użytkowników: Administratora oraz Użytkownika (Mieszkańca/Właściciela mieszkania). Portal udostępnia funkcjonalności umożliwiające rejestrację budynków oraz przypisywanie do nich mieszkań. Użytkownicy przypisani do mieszkań otrzymują jedną z ról: TENANT (mieszkaniec) lub OWNER (właściciel).

Jeden użytkownik może być przypisany do wielu mieszkań, natomiast każde mieszkanie może mieć przypisanego tylko jednego właściciela. Administrator posiada uprawnienia do nakładania opłat na poszczególne mieszkania oraz do publikowania ogłoszeń.

Użytkownicy standardowi mają możliwość przeglądania swoich mieszkań oraz zgłaszania problemów i uwag dotyczących mieszkania (FLAT), budynku (BUILDING) lub spraw ogólnych (GENERAL).

## Technologie
### Backend
Serwis Domino opiera się na relacyjnej bazie danych PostgreSQL. Backend aplikacji został zaimplementowany w języku Python z wykorzystaniem frameworka Django. Dodatkowo zastosowano Django REST Framework, będący rozszerzeniem Django, w celu tworzenia interfejsu API umożliwiającego udostępnianie danych w formacie JSON. W projekcie wykorzystano również dekorator api_view, który pozwala na definiowanie funkcyjnych widoków API oraz obsługę żądań HTTP zgodnie z zasadami architektury REST.

### Frontend
\#będzie

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


