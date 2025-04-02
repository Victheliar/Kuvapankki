# Kuvapankki
## Sovelluksen toiminnot
* Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen
* Käyttäjä pystyy lisäämään ja poistamaan kuvia
* Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan kuvien kuvaukset
* Käyttäjä näkee sovellukseen lisätyt kuvat
* Käyttäjä pystyy etsimään kuvia hakusanalla
* Sovelluksessa on käyttäjäsivut, jotka näyttävät julkaisujen määrän sekä kaikki käyttäjän julkaisemat kuvat
* Käyttäjä pystyy tallentamaan kuvat kokoelmiin aiheiden mukaan
* Käyttäjä pystyy kommentoimaan muiden käyttäjien kuvia
## Sovelluksen nykyinen tilanne
* Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen
* Käyttäjä pystyy lisäämään ja poistamaan kuvia
* Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan kuvien kuvaukset
* Käyttäjä näkee sovellukseen lisätyt kuvat
* Käyttäjä pystyy etsimään kuvia hakusanalla
## Sovelluksen asennus
1. Asenna flask - kirjasto:
   
   ```
   $ pip install flask
   ```
   
2. Luo tietokannan taulut ja lisää alkutiedot:
   ```
   $ sqlite3 database.db < schema.sql
   ```
   
3. Käynnistä sovellus:
   ```
   $ flask run
   ```
