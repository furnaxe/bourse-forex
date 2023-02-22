import requests
import smtplib
import time
import yfinance as yf
import json
import logging
import email.message

logging.basicConfig(level=logging.DEBUG)

# Configuration de l'API Alpha Vantage
API_KEY = 'IJL9YI5AZCQCAHLM'
SYMBOL = 'EUR'
TO_SYMBOL = 'USD'
FUNCTION = 'FX_DAILY'
OUTPUTSIZE = 'compact'
# Configuration de l'e-mail
from_email = 'boursemaverick@gmail.com'
to_email = 'noesisforex@gmail.com'

# Configuration des niveaux d'achat et de vente
point_value = 0.0001
buy_offset = 0.0020
sell_offset = 0.0020
profit_target = point_value * 70
compteur = 1
position_open = False
target_buy_price = 0
target_sell_price = 0

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
}

# Créer le message e-mail
message_init = email.message.EmailMessage()
message_init.set_content("Démarrage du bot")
message_init['Subject'] = "Démarrage du bot"
message_init['From'] = from_email
message_init['To'] = to_email

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login('boursemaverick@gmail.com', 'lmbhnupqabuoitno')
    smtp.send_message(message_init)

while True:
    try:
        logging.info(f"Tentative n°{compteur}")
        
        if compteur % 200 == 0:
            # Créer le message e-mail
            message_alert = email.message.EmailMessage()
            message_alert.set_content(f"Tentative n°{compteur}")
            message_alert['Subject'] = "Tentative n°{compteur}"
            message_alert['From'] = from_email
            message_alert['To'] = to_email
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login('boursemaverick@gmail.com', 'lmbhnupqabuoitno')
                smtp.send_message(message_alert)
                
        # Envoi de la requête GET à l'API
        response1 = requests.get("https://query1.finance.yahoo.com/v6/finance/quote?symbols=EURUSD=X", headers=headers)
        market_price = response1.json()["quoteResponse"]["result"][0]["regularMarketPrice"]
        # Analyser la réponse JSON
        logging.info(f"Prix actuel EUR/USD : {market_price}")
        
        # Obtenir les données forex de l'API Alpha Vantage
        response2 = requests.get(f'https://www.alphavantage.co/query?function={FUNCTION}&from_symbol={SYMBOL}&to_symbol={TO_SYMBOL}&apikey={API_KEY}')
        forex_data = response2.json()
        compteur += 1

        # Obtenir les données des 3 derniers jours
        current_day_data = list(forex_data['Time Series FX (Daily)'].values())[:3]

        # Obtenir la valeur la plus haute des 3 derniers jours pour chaque variable
        top_3days_data = max(current_day_data, key=lambda x: float(x['4. close']))

        current_day_high = float(max(current_day_data, key=lambda x: float(x['2. high']))['2. high'])
        logging.info("Niveau le plus élevé des 3 derniers jours: " + str(current_day_high))
        current_day_low = float(min(current_day_data, key=lambda x: float(x['3. low']))['3. low'])
        logging.info("Niveau le moins élevé des 3 derniers jours: " + str(current_day_low ))
        current_day_close = float(top_3days_data['4. close'])
        logging.info("Dernier niveau de clôture: " + str(current_day_close))
        
        # Vérifier si l'écart entre le minimum et le maximum est suffisamment grand
        if current_day_high - current_day_low < 0.01:
            logging.info("L'écart entre le minimum et le maximum est inférieur à 100 points de base. Impossible d'ouvrir une position.")
            time.sleep(180)
            continue
        
        # Vérifier si le marché a atteint le niveau d'achat
        if not position_open and market_price <= current_day_low + buy_offset:
            # Calculer le prix de vente cible
            target_sell_price = market_price + profit_target
            
            # Créer le message e-mail
            message1 = email.message.EmailMessage()
            message1.set_content("Recommandation : Acheter EUR/USD. Prix actuel : " + str(market_price) + ", objectif de vente : " + str(target_sell_price) + ", niveau d'achat : " + str(current_day_low))
            message1['Subject'] = "Recommandation : Acheter EUR/USD. Prix actuel : " + str(market_price) + ", objectif de vente : " + str(target_sell_price) + ", niveau d'achat : " + str(current_day_low)
            message1['From'] = from_email
            message1['To'] = to_email
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login('boursemaverick@gmail.com', 'lmbhnupqabuoitno')
                smtp.send_message(message1)
            position_open = True
                
        # Vérifier si le marché a atteint le niveau de vente
        elif not position_open and market_price >= current_day_high - sell_offset:
            # Calculer le prix d'achat cible
            target_buy_price = market_price - profit_target

            # Créer le message e-mail
            message2 = email.message.EmailMessage()
            message2.set_content("Recommandation : Vendre EUR/USD. Prix actuel : " + str(market_price) + ", objectif d'achat : " + str(target_buy_price) + ", niveau de vente : " + str(current_day_high))
            message2['Subject'] = "Recommandation : Vendre EUR/USD. Prix actuel : " + str(market_price) + ", objectif d'achat : " + str(target_buy_price) + ", niveau de vente : " + str(current_day_high)
            message2['From'] = from_email
            message2['To'] = to_email
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login('boursemaverick@gmail.com', 'lmbhnupqabuoitno')
                smtp.send_message(message2)
            # Mettre à jour l'état de la position
            position_open = True

        # Vérifier si la position est ouverte et si le marché a atteint le niveau de vente
        elif position_open and market_price >= target_buy_price:
            # Fermer la position
            
            # Créer le message e-mail
            message3 = email.message.EmailMessage()
            message3.set_content("Position fermée : Vendre EUR/USD. Prix actuel : " + str(market_price) + ", profit réalisé : " + str(market_price - target_buy_price))
            message3['Subject'] = "Position fermée : Vendre EUR/USD. Prix actuel : " + str(market_price) + ", profit réalisé : " + str(market_price - target_buy_price)
            message3['From'] = from_email
            message3['To'] = to_email
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login('boursemaverick@gmail.com', 'lmbhnupqabuoitno')
                smtp.send_message(message3)
            # Mettre à jour l'état de la position
            position_open = False
            target_buy_price = 0

        # Vérifier si la position est ouverte et si le marché a atteint le niveau d'achat
        elif position_open and market_price <= target_sell_price:
            # Fermer la position
            
            # Créer le message e-mail
            message4 = email.message.EmailMessage()
            message4.set_content("Position fermée : Acheter EUR/USD. Prix actuel : " + str(market_price) + ", profit réalisé : " + str(target_sell_price - market_price))
            message4['Subject'] = "Position fermée : Acheter EUR/USD. Prix actuel : " + str(market_price) + ", profit réalisé : " + str(target_sell_price - market_price)
            message4['From'] = from_email
            message4['To'] = to_email
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login('boursemaverick@gmail.com', 'lmbhnupqabuoitno')
                smtp.send_message(message4)
            # Mettre à jour l'état de la position
            position_open = False
            target_sell_price = 0
        time.sleep(180)
        
    except Exception as e:
        logging.error(e)
        # Créer le message e-mail
        message_error = email.message.EmailMessage()
        message_error.set_content("Erreur : " + str(e))
        message_error['Subject'] = "Erreur : " + str(e)
        message_error['From'] = from_email
        message_error['To'] = to_email
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login('boursemaverick@gmail.com', 'lmbhnupqabuoitno')
                smtp.send_message(message_error)
        time.sleep(180)
