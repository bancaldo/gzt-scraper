# Gzt Scraper 1.0

Questa applicazione scritta in Python 2.7.8, serve per effettuare lo
scraping delle valutazioni dei calciatori di Serie A.
Vengono importati tutti i nomi dei calciatori ed è possibile modificarli
da GUI, qualora si verificassero delle ambiguità.
Una volta importati i nomi, è possibile effettuare lo scraping dei
voti inserendo il numero della giornata interessata.
Verranno creati 2 file txt, uno classico ed uno senza il trequartista.
I file di appoggio dell'applicazione sono:
names.csv -> file contenente tutti i nomi derivati dal primo passaggio di scraping
gazzetta.json -> tutte le valutazioni della giornata estratta

## Moduli utilizzati

Vengono usate le librerie wx per la grafica, django come ORM e scrapy per lo spider.

## Operazioni preliminari

Dopo aver installato django, le librerie wx e scrapy, creare il database.

Creazione database:

```
python manage.py makemigrations players
```

in seguito:

```
python manage.py migrate
Operations to perform:
  Apply all migrations: players
Running migrations:
  Applying players.0001_initial... OK
```

una volta creato il database players.db, lanciare l'applicazione.

```
>python main.py
```

L'iter è il seguente:
prima si importano i giocatori, si correggono le eventuali ambiguità nei nomi,
poi si estraggono le valutazioni di una certa giornata.
I nomi di giocatori verranno corretti a seconda dei valori presenti a database.
E' inoltre possibile inserire un nuovo giocatore manualmente.


### 1. Importare i giocatori

Dal menu 'Import -> import players' importare i giocatori.
Un primo passaggio di correzione nomi ambigui verrà effettuato.


### 2. Estrarre Valutazioni

Dal menu 'Import -> extract evaluations' selezionare la giornata della quale si vogliono
estrarre i dati. Se i dati non saranno ancora presenti sul sito, si verrà avvisati da un
messaggio

### 3. Nuovo giocatore

Dal menu 'Import -> new Player' è possibile inserire manualmente un giocatore
non presente a database

## Licenza

GPL
