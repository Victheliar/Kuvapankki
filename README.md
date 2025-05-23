# Kuvapankki
## Sovelluksen toiminnot
* Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen
* Käyttäjä pystyy lisäämään ja poistamaan kuvia
* Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan kuvien kuvaukset ja luokitukset
* Käyttäjä näkee sovellukseen lisätyt kuvat
* Käyttäjä pystyy etsimään kuvia hakusanalla
* Sovelluksessa on käyttäjäsivut, jotka näyttävät julkaisujen määrän sekä kaikki käyttäjän julkaisemat kuvat
* Käyttäjä pystyy lisäämään käyttäjäsivulleen profiilikuvan
* Käyttäjä pystyy valitsemaan julkaisulleen luokittelun
* Käyttäjä pystyy kommentoimaan muiden käyttäjien kuvia
## Toiminta suurella tietomäärällä
Sovelluksen toimintaa on testattu suurella tietomäärällä tiedoston seed.py avulla, eikä mitään eroa toiminnassa juuri havaittu.

## Sovelluksen asennus
1. Asenna `flask` - kirjasto:
   
   ```
   $ pip install flask
   ```
   
2. Luo tietokannan taulut ja lisää alkutiedot:
   ```
   $ sqlite3 database.db < schema.sql
   $ sqlite3 database.db < init.sql
   ```
   
3. Käynnistä sovellus:
   ```
   $ flask run
   ```
