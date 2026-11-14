<h1 align="center" id="title">🛡️ Phunter</h1>

<p align="center">
    <img src="assets/logo.png" height="200" alt="Logo Phunter"/>
</p>

<p align="center">
    <a href="https://www.python.org/downloads/">
        <img src="https://img.shields.io/badge/Python-3.10%2B-brightgreen" alt="Python 3.10+"/>
    </a>
    <a href="https://www.gnu.org/licenses/gpl-3.0.html">
        <img src="https://img.shields.io/badge/Licenza-GNU-blue" alt="Licenza GNU GPL v3"/>
    </a>
</p>

# 🔎 Informazioni su Phunter

**Phunter è uno strumento progettato per raccogliere informazioni associate a un numero di telefono.**

Può individuare o recuperare, in base alla disponibilità delle fonti consultate:

* Operatore telefonico
* Possibili località associate al numero
* Tipologia di linea
* Reputazione del numero
* Informazioni reperite da fonti pubbliche
* Eventuali segnalazioni come spam
* Eventuale associazione a un account Amazon
* Possibili informazioni sull'intestatario

I risultati dipendono dai servizi esterni disponibili e possono essere incompleti, non aggiornati o non corretti.

## 📦 Installazione

Requisiti:

* Python 3.10 o versione successiva
* Git

Clona il repository e installa le dipendenze:

```bash
git clone https://github.com/terminalupdate/Phunter-Team-Xirus.git
cd Phunter-Team-Xirus
python3 -m pip install -r requirements.txt
```

È consigliato utilizzare un ambiente virtuale:

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 🧭 Utilizzo

Per visualizzare la guida completa:

```bash
python phunter.py --help
```

Le opzioni disponibili sono:

```text
usage: phunter.py \[-h] \[-t \[TARGET]] \[-a \[AMAZON]] \[-p \[PERSON]] \[-f \[FILE]] \[-v] \[-o \[OUTPUT]]

options:
  -h, --help            mostra questo messaggio di aiuto ed esce
  -t \[TARGET], --target \[TARGET]
                        recupera informazioni tramite numero di telefono
  -a \[AMAZON], --amazon \[AMAZON]
                        verifica l'eventuale associazione del numero a un account Amazon
  -p \[PERSON], --person \[PERSON]
                        cerca il possibile intestatario tramite ricerca inversa
                        (Pagine Bianche)
  -f \[FILE], --file \[FILE]
                        recupera informazioni da un file contenente numeri di telefono
  -v, --verify          controlla versione, aggiornamenti, servizi e altri elementi
  -o \[OUTPUT], --output \[OUTPUT]
                        indica il file in cui salvare i risultati
                        (utilizzabile solo con --amazon/-a e --person/-p)
```

### Esempi

Ricerca di un singolo numero:

```bash
python3 phunter.py -t +33666666666
```

Ricerca dei numeri contenuti in un file:

```bash
python3 phunter.py -f file.txt
```

Verifica dell'eventuale associazione ad Amazon:

```bash
python3 phunter.py -a +33666666666
```

Salvataggio del risultato in un file:

```bash
python3 phunter.py -a +33666666666 -o output.txt
```

### 🖼️ Esempio dei risultati

L'immagine seguente mostra un esempio dell'output dello strumento:

!\[Esempio dei risultati](assets/example.png)

> \*\*Attenzione:\*\* utilizzando l'opzione `-p` è necessario accettare le condizioni e rifiutare le notifiche. L'operazione richiede la presenza dell'utente durante l'esecuzione.

## 🧰 Edizione Team Xirus

Questa repository contiene l'edizione di **Phunter mantenuta e sottoposta a interventi di manutenzione da Team Xirus**. Si tratta di un fork indipendente del progetto originale.

* Repository di questa edizione: https://github.com/terminalupdate/Phunter-Team-Xirus
* Progetto di origine: 
* Licenza: GNU General Public License v3.0 (consulta il file `LICENSE`)
* Versione indicata nei metadati del progetto: `0.0.3` (consulta `config.json`)

### Interventi di manutenzione

Questa edizione include miglioramenti e verifiche relativi a:

* Gestione delle richieste HTTP
* Flusso di ricerca dei numeri telefonici
* Gestione dei risultati relativi a spam e reputazione
* Controlli eseguiti tramite l'opzione `--verify`

I test di verifica utilizzano risposte HTTP simulate: non eseguono ricerche reali e non contattano servizi OSINT esterni.

### Verifica locale

Per eseguire i test:

```bash
python -m unittest discover -s tests -v
```

## 🔐 Uso responsabile e tutela della privacy

Phunter deve essere utilizzato esclusivamente per finalità lecite e autorizzate.

Un numero telefonico può costituire un dato personale. Non svolgere ricerche su persone senza una valida motivazione, non diffondere informazioni personali e rispetta sempre la normativa applicabile in materia di privacy e protezione dei dati.

Le informazioni ottenute da fonti di terze parti possono essere incomplete, non aggiornate o inesatte. È responsabilità dell'utilizzatore verificare i risultati e utilizzare lo strumento in modo consapevole.

Questa edizione Team Xirus è un fork indipendente e non costituisce una release ufficiale del progetto originale.

## 📜 Licenza

Il progetto è distribuito secondo i termini della **GNU General Public License v3.0**. Consulta il file `LICENSE` incluso nel repository e rispetta le condizioni della licenza.

## ☕ Sostieni Team Xirus

Se Phunter e il lavoro di manutenzione di Team Xirus ti sono stati utili, puoi contribuire a sostenere lo sviluppo con un piccolo gesto.

Il tuo supporto aiuta a dedicare tempo a:

* Manutenzione e miglioramento degli strumenti
* Correzione di bug e test
* Ricerca e sperimentazione in ambito informatico e OSINT
* Condivisione di progetti e risorse con la community

**Ogni contributo è apprezzato. Grazie per sostenere Team Xirus!**

<!-- Sostituisci TEAM\_XIRUS con il nome utente effettivo del profilo Buy Me a Coffee -->

<a href="https://www.buymeacoffee.com/TEAM\_XIRUS" target="\_blank" rel="noopener noreferrer">
    <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Offrimi un caffè su Buy Me a Coffee" height="50"/>
</a>

