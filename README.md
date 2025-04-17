# ![icon](https://github.com/lotablet/mytreno/blob/main/custom_components/mytreno/images/icon.png) MyTreno  
![logo](https://github.com/lotablet/mytreno/blob/main/custom_components/mytreno/images/logo.png)

> Integrazione Home Assistant per monitorare in tempo reale **partenze e arrivi dei treni italiani** tramite il servizio **ViaggiaTreno** di Trenitalia.

---

**MyTreno** ti permette di tenere d'occhio i treni della tua stazione preferita, direttamente da Lovelace.  

---

## ✅ Funzionalità attuali

- Recupero automatico delle **partenze** e degli **arrivi** da qualsiasi stazione italiana
- Integrazione configurabile **via UI** da *Impostazioni → Integrazioni*
- Sensore aggiornato in tempo reale con treni in transito
- Card Lovelace pronta all’uso (per ora in versione `config-template-card`, ma in arrivo quella ufficiale da **HACS**)

---

## 📦 Installazione tramite HACS

1. Vai in **HACS → Integrazioni**
2. Clicca su Menu **⋮ → Aggiungi repository personalizzato**
3. Inserisci questo URL e scegli tipo **"Integrazione"** :
```
https://github.com/lotablet/mytreno
```


4. Dopo aver aggiunto il repository, cerca “**MyTreno**” nell’elenco delle integrazioni HACS
5. Installa e riavvia Home Assistant

### 🔧 Configurazione

1. Vai su **Impostazioni → Dispositivi e Servizi**
2. Clicca su **"Aggiungi Integrazione"**
3. Cerca **MyTreno** e inserisci la città.

---

# 💡 Card Lovelace 



## MyTreno Card

![version](https://img.shields.io/badge/version-1.0-blue)
![hacs](https://img.shields.io/badge/HACS-default-orange)

> Card Lovelace per visualizzare partenze e arrivi dei treni usando ViaggiaTreno.

## 📦 Installazione via HACS

1. Vai in HACS → Frontend → Menu ⋮ → "Custom repositories"
2. Inserisci l'URL della repo e imposta tipo: `Lovelace`:

```
https://github.com/lotablet/mytreno-card/
```


3. Installa `MyTreno Card`
4. Dopo il riavvio, aggiungi questa card in Lovelace:

```
type: custom:my-treno-card
sensor: sensor.mytreno_laspezia
```
