from datetime import datetime
import os
import random
import string
from werkzeug.utils import secure_filename
from os.path import join, dirname, realpath
import pymongo
from bson.objectid import ObjectId
from flask import Flask, redirect, url_for, render_template, request, session, jsonify, send_file
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image
from flask_socketio import SocketIO, emit, rooms, join_room, leave_room, disconnect
from datetime import timedelta
import stripe
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
# Path for uploading files
# For profile images
UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'static/profileImages')
UPLOAD_FOLDER1 = join(dirname(realpath(__file__)), 'static/chatdata')
UPLOAD_FOLDER2 = join(dirname(realpath(__file__)), 'static/samples')
UPLOAD_FOLDER3 = join(dirname(realpath(__file__)), 'static/actorprofilepic')
UPLOAD_FOLDER4 = join(dirname(realpath(__file__)), 'static/scriptFiles')
UPLOAD_FOLDER5 = join(dirname(realpath(__file__)), 'static/projectFiles')
base_url = "https://www.voicescity.com"
#myclient = pymongo.MongoClient('mongodb+srv://taimour:123321@cluster0.ktylv.mongodb.net/voiceover?retryWrites=true&w=majority')
#mydb = myclient["voiceover"]

app = Flask(__name__)

app.config['SECRET_KEY'] = 'top-secret!'
app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'apikey'
app.config['MAIL_PASSWORD'] = "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"
api_key = "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"
default_sender = "no-reply@voicescity.com"
app.config['MAIL_DEFAULT_SENDER'] = "no-reply@voicescity.com"
mail = Mail(app)
app.client = pymongo.MongoClient('mongodb+srv://taimour:123321@cluster0.ktylv.mongodb.net/voiceover?retryWrites=true&w=majority',connect=False)
app.db = app.client.voiceover
mydb = app.db

socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")
app.secret_key = "voiceover1234**!!"

# Upload folder configuration for Profile images
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER1'] = UPLOAD_FOLDER1
app.config['UPLOAD_FOLDER2'] = UPLOAD_FOLDER2
app.config['UPLOAD_FOLDER3'] = UPLOAD_FOLDER3
app.config['UPLOAD_FOLDER4'] = UPLOAD_FOLDER4
app.config['UPLOAD_FOLDER5'] = UPLOAD_FOLDER5

stripe_keys = {
    'secret_key': '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',
    'publishable_key': 'pk_live_51JaoxYApD01HTCoksZKga2L785BUDKutB4r44jF691sarepOVFSDa9lubAaeJrns3GVwhsdhFyJaLaTieHacsyTe00MMb65fwk'
}
stripe.api_key = stripe_keys['secret_key']

# test email
@app.route("/send-mail")
def sendmail():
    try:
        msg = Message("testing", recipients=['taimour_hadi@hotmail.com'])
        msg.html = str("Message send")
        mail.send(msg)
        return str("Message send")
    except Exception as e:
        return str(e)
@app.route("/get_my_ip", methods=["GET"])
def get_my_ip():
    return jsonify({'ip': request.remote_addr}), 200

# Code generate for activation of account.
def id_generator(size=8, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
    return ''.join(random.choice(chars) for _ in range(size))


# Fetch records using list (dead_line, proposals, (category, age, gender),
# languages, accents, countries, delivery_options)
banklistarray = [' Aareal Bank, Wiesbaden, Germany', ' Aargauische Kantonalbank, Aarau, Switzerland',
                 ' Abacus Federal Savings Bank, New York, United States', ' AB Bank, Dhaka, Bangladesh',
                 ' AB SEB bankas, Vilnius, Lithuania', ' ABC Islamic Bank, Manama, Bahrain',
                 ' ABC Bank (Kenya), Nairobi, Kenya', ' ABC Bank (Uganda), Kampala, Uganda',
                 ' Abhyudaya Co-operative Bank Ltd, Mumbai, India', ' ABLV Bank, AS, Riga, Latvia',
                 ' ABN AMRO, Amsterdam, Netherlands', ' ABN AMRO Group, Amsterdam, Netherlands',
                 ' Absa Group Limited, Johannesburg, South Africa',
                 ' Abu Dhabi Commercial Bank, Abu Dhabi, United Arab Emirates',
                 ' Abu Dhabi Islamic Bank, Abu Dhabi, United Arab Emirates',
                 ' ACBA-Credit Agricole Bank, Yerevan, Armenia', ' Access Bank Azerbaijan, Baku, Azerbaijan',
                 ' Access Bank Group, Lagos, Nigeria', ' AccessBank Liberia, Monrovia, Liberia',
                 ' Access Bank plc, Lagos, Nigeria', ' Access Bank Rwanda, Kigali, Rwanda',
                 ' AccessBank Azerbaijan, Baku, Azerbaijan', ' AccessBank Tajikistan, Dushanbe, Tajikistan',
                 ' Access Bank Zambia,   Lusaka, Zambia', ' Achmea Bank, The Hague, Netherlands',
                 ' Achmea Hypotheekbank, Den Bosch, Netherlands', ' Acleda Bank, Phnom Penh, Cambodia',
                 ' Acleda Bank Myanmar, Yangon, Myanmar', ' Adabank, Istanbul, Turkey',
                 ' Addiko Bank, Klagenfurt, Austria', ' AEK Bank 1826, Thun, Switzerland',
                 ' Affin Bank, Kuala Lumpur, Malaysia', ' Afghanistan International Bank, Kabul, Afghanistan',
                 ' AfrAsia Bank Limited, Port Louis, Mauritius', ' Afrasia Bank Zimbabwe Limited, Harare, Zimbabwe',
                 ' African Bank, Midrand, South Africa', ' African Export–Import Bank (Afreximbank), Cairo, Egypt',
                 ' African Investment Bank, Tripoli, Libya', ' Afriland First Bank, Yaoundé, Cameroon',
                 ' Agrani Bank, Dhaka, Bangladesh', ' Agricultural Bank of Libya, Tripoli, Libya',
                 ' Agricultural Bank of China, Beijing, China', ' Agricultural Cooperative Bank of Iraq, Baghdad, Iraq',
                 ' Agricultural Development Bank of Ghana, Accra, Ghana',
                 ' Agriculture Development Bank, Ramshah Path, Kathmandu', ' Agrobank, Kuala Lumpur, Malaysia',
                 ' Agroindustrijsko Komercijalna Banka, Nis, Serbia', ' Agroinvestbank, Dushanbe, Tajikistan',
                 ' Ahli Bank Qatar, Doha, Qatar', ' Ahli United Bank, Manama, Bahrain',
                 ' Ahli United Bank Kuwait, Safat, Kuwait', ' Aichi Bank, Nagoya, Japan',
                 ' AIK Banka, Belgrade, Serbia', ' Ak Bars Holding, Kazan, Russia', ' Akbank, Istanbul, Turkey',
                 ' Akiba Commercial Bank, Dar es Salaam, Tanzania', ' Akita Bank, Akita, Japan',
                 ' Aktia Bank, Helsinki, Finland', ' Al Ahli Bank of Kuwait, Safat, Kuwait',
                 ' Al-Amanah Islamic Investment Bank of the Philippines, Zamboanga City, Philippines',
                 ' Al-Arafah Islami Bank Limited, Dhaka, Bangladesh', ' Alawwal Bank, Riyadh, Saudi ',
                 ' Albaraka Türk, Istanbul, Turkey', ' Al Baraka Banking Group, Manama, Bahrain',
                 ' Albaraka Türk, Istanbul, Turkey', ' Al Bilad Bank, Riyadh, Saudi Arabia',
                 ' Al Hilal Bank, Abu Dhabi, United Arab Emirates', ' Al Rajhi Bank, Riyadh, Saudi Arabia',
                 ' Al Rajhi Bank Malaysia, Kuala Lumpur, Malaysia', ' Al Shamal Islamic Bank, Khartoum, Sudan',
                 ' Al Watany Bank of Egypt (AWB), Giza, Egypt', ' Alfa-Bank, Moscow, Russia',
                 ' Alfa-Bank (Ukraine)|Alfa-Bank, Kyiv, Ukraine', ' Alinma Bank, Riyadh, Saudi ',
                 ' Alior Bank, Warsaw, Poland', ' Allahabad Bank, Calcutta, India',
                 ' Allbank Panama, Panama City, Panama', ' Allgemeine Sparkasse Oberosterreich, Linz, Austria',
                 ' Alliance Bank JSC, Almaty, Kazakhstan', ' Alliance Bank Malaysia Berhad, Kuala Lumpur, Malaysia',
                 ' Allianz, Munich, Germany', ' Allied Bank Limited, Lahore, Pakistan',
                 ' Allied Banking Corporation, Makati, Philippines', ' Allied Bank Zimbabwe Limited, Harare, Zimbabwe',
                 ' Allied Irish Banks (AIB), Dublin, Ireland', ' Alterna Bank, Ontario, Canada',
                 ' Alternatif Bank, Istanbul, Turkey', ' Ally Financial, Detroit, United States',
                 ' Aloqabank, Tashkent, Uzbekistan', ' AlpenBank, Innsbruck, Austria', ' Alpha Bank, Athens, Greece',
                 ' Alpha Bank Albania, Tirana, Albania', ' Alpha Bank Cyprus, Nicosia, Cyprus',
                 ' Alpha Bank Romania, Bucharest, Romania', ' Alpha Bank Skopje, Skopje, Macedonia',
                 ' Alpha Bank UK, London, United Kingdom', ' Alternatif Bank, Istanbul, Turkey',
                 ' Amagasaki Shinkin Bank, Amagasaki, Japan', ' AmalBank, Accra, Ghana',
                 ' Amalgamated Bank, New York, United States', ' Amalgamated Bank of Chicago, Chicago, United States',
                 ' Amana Bank Limited|Amana Bank, Dar es Salaam, Tanzania', ' Amana Bank (Sri Lanka), Sri Lanka',
                 ' AM Bank, Beirut, Lebanon', ' AmBank Group, Kuala Lumpur, Malaysia', ' Amen Bank, Tunis, Tunisia',
                 ' Ameriabank, Yerevan, Armenia', ' American Continental Bank, Los Angeles, United States',
                 ' American National Corporation, Omaha, United States',
                 ' American Premier Bank, Arcadia, United States', ' Ameris Bancorp, Jacksonville, United States',
                 ' Amin Investment Bank, Tehran, Iran ', ' AMP Limited, Sydney, Australia',
                 ' Amsterdam Trade Bank, Amsterdam, Netherlands', ' Anadolubank, Istanbul, Turkey',
                 ' Andbank, Andorra La Vella, Andorra ', ' Andbank Panama, Panama City, Panama',
                 ' Andhra Bank, Hyderabad, India', ' Ansar-VDP Unnayan Bank, Dhaka, Bangladesh',
                 ' Antwerp Diamond Bank, Antwerp, Belgium', ' ANZ Amerika Samoa Bank, Pago Pago, American Samoa',
                 ' ANZ Bank New Zealand, Auckland, New Zealand', ' ANZ Royal Bank, Phom Penh, Cambodia',
                 ' Australia and New Zealand Banking Group, Melbourne, Australia', ' Aomori Bank, Aomori, Japan',
                 ' Aozora Bank, Tokyo, Japan', ' Appenzeller Kantonalbank, Appenzell, Switzerland',
                 ' Apple Bank for Savings, New York, United States', ' APS Bank, Birkirkara, Malta ',
                 ' Arab Bangladesh Bank, Dhaka, Bangladesh', ' Arab Bank, Amman, Jordan',
                 ' Arab Banking Corporation, Manama, Bahrain', ' Arab Banking Corporation Algeria, Algiers, Algeria',
                 ' Arab Banking Corporation Brasil, São Paulo, Brazil', ' Arab Banking Corporation Egypt, Cairo, Egypt',
                 ' Arab Banking Corporation Jordan, Amman, Jordan', ' Arab Banking Corporation Tunisia, Tunis, Tunisia',
                 ' Arab Israel Bank, Nesher, Israel', ' Arab National Bank (ANB), Riyadh, Saudi Arabia',
                 ' Arab Tunisian Bank (ATB), Tunis, Tunisia', ' Arbejdernes Landsbank, Copenhagen, Denmark',
                 ' Arbuthnot Latham, London, United Kingdom', ' ArdShinInvestBank, Yerevan, Armenia',
                 ' Argenta Group, Antwerp, Belgium', ' Argenta (bank), Antwerp, Belgium',
                 ' Arion Bank, Reykjavik, Iceland', ' Arkada Bank, Kyiv, Ukraine', ' ArmSwissBank, Yerevan, Armenia',
                 ' Artsakhbank, Yerevan, Armenia', ' Arvest Bank, Bentonville, United States',
                 ' AS SEB Pank, Tallinn, Estonia', ' Asahi Shinkin Bank, Tokyo, Japan',
                 ' ASB Bank, Auckland, New Zealand', ' Asia Commercial Bank (ACB), Ho Chi Minh City, Vietnam',
                 ' Asia Green Development Bank, Yangon, Myanmar', ' Asia United Bank, Pasig, Philippines',
                 ' Askari Bank, Rawalpindi, Pakistan', ' ASN Bank, The Hague, Netherlands',
                 ' Astoria Bank, Lake Success, United States', ' AtaBank, Baku, Azerbaijan',
                 ' Atlantic Bank Group, Lome, Togo', ' Atlas Mara Bank Zambia Limited, Lusaka, Zambia',
                 ' Attica Bank, Athens, Greece', ' Attijariwafa Bank, Casablanca, Morocco',
                 ' Auburn National Bancorporation, Auburn, United States', ' Aurskog Sparebank, Aurskog, Norway',
                 ' AU Small Finance Bank, Rajasthan, India ', ' Auswide Bank, Bundaberg, Australia',
                 ' Awash International Bank, Addis Ababa, Ethiopia', ' Axa Bank Belgium, Brussels, Belgium',
                 ' Axis Bank, Mumbai, India', ' Ayandeh Bank, Tehran, Iran', ' Ayeyarwady Bank, Yangon, Myanmar',
                 ' Azania Bank, Dar es Salaam, Tanzania', ' Azer-Turk Bank, Baku, Azerbaijan',
                 ' Azerigasbank, Baku, Azerbaijan', ' Azizi Bank, Kabul, Afghanistan', ' B2B Bank, Toronto, Canada',
                 ' B&N Bank, Moscow, Russia', ' Baader Bank AG, Unterschleißheim, Germany',
                 ' Babylon Bank, Baghdad, Iraq', ' BAC Credomatic, Managua, Nicaragua',
                 ' Bahrain Development Bank, Manama, Bahrain', ' Bahrain Islamic Bank (BISB), Manama, Bahrain',
                 ' Baiduri Bank, Bandar Seri Begawan, Brunei',
                 ' Balboa Bank and Trust, Ciudad de Panamá, Republic of Panama', ' BanBajío, Leon, Mexico',
                 ' Banc of California, Irvine, United States', ' Banca Apulia, San Severo (Foggia), Italy',
                 ' BancABC, Gaborone, Botswana', ' Banca Carige, Genoa, Italy',
                 ' Banca Cassa di Risparmio di Firenze, Florence, Italy',
                 ' Banca Cassa di Risparmio di Savigliano, Savigliano, Italy',
                 ' Banca Comercială Română, Bucharest, Romania', ' Banca delle Marche, Ancona, Italy',
                 ' Banca dello Stato del Cantone Ticino, Bellinzona, Switzerland', " Banca dell'Umbria, Perugia, Italy",
                 ' Banca del Mezzogiorno – MedioCredito Centrale, Rome, Italy',
                 ' Banca del Monte di Lucca, Lucca, Italy', ' Banca di Cambiano, Castelfiorentino, Italy',
                 ' Banca di Credito Cooperativo di Alba Langhe e Roero, Alba, Italy',
                 ' Banca di Credito Popolare, Torre Del Greco, Italy', ' Banca di Credito Sardo, Cagliari, Italy',
                 ' Banca di Sassari, Sassari, Italy', ' Banca Etruria, Arezzo, Italy', ' Banca Finnat, Rome, Italy',
                 ' Banca Generali, Trieste, Italy', ' Banca IFIS, Venice, Italy', ' Banca IMI, Milan, Italy',
                 ' Banca Intermobiliare, Turin, Italy', ' Banca Intesa Beograd, Belgrade, Serbia',
                 ' Banca Intesa Russia, Moscow, Russia', ' Banca Intesa Serbia, Belgrade, Serbia',
                 ' Banca Italease, Milano, Italy', ' Banca March, Palma de Mallorca, Spain',
                 ' Banca Mediocredito del Friuli Venezia Giulia, Udine, Italy', ' Banca Mediolanum, Milano, Italy',
                 ' Banca Monte dei Paschi di Siena, Siena, Italy', ' Banca Monte Parma, Parma, Italy',
                 ' Banca Monte Paschi Belgio, Brussels, Belgium', ' Banca Nazionale del Lavoro, Roma, Italy',
                 ' Banca Padovana Credito Cooperativo, Campodarsego (Pd), Italy',
                 " Banca Popolare dell'Emilia Romagna, Modena, Italy", ' Banca Popolare di Bari, Bari, Italy',
                 ' Banca Popolare di Crema, Crema, Italy', ' Banca Popolare di Milano, Milano, Italy',
                 ' Banca Popolare di Novara, Novara, Italy', ' Banca Popolare di Sondrio, Sondrio, Italy',
                 ' Banca Popolare di Sondrio Switzerland, Lugano, Switzerland',
                 ' Banca Popolare di Spoleto, Spoleto, Italy', ' Banca Popolare di Vicenza, Vicenza, Italy',
                 ' Banca Popolare FriulAdria, Pordenone, Italy',
                 " Banca Privada d'Andorra, Escaldes-Engordany, Andorra", ' Banca Prossima, Milano, Italy',
                 ' Banca Pueyo, Badajoz, Spain', ' Banca Regionale Europea, Milano, Italy',
                 ' Bancaribe, Caracas, Venezuela', ' Banca Romaneasca, Bucharest, Romania',
                 ' Banca Sella, Biella, Italy', ' Banca Transilvania, Cluj-Napoca, Romania',
                 ' Banco Alfa, São Paulo, Brazil', ' Banco Amambay, Asunción, Paraguay',
                 ' Banco Angolano de Investimentos, Luanda, Angola', ' Banco AV Villas, Bogotá D.C., Colombia',
                 ' Banco Azteca, Iztapalapa, Mexico', ' Banco BICE, Santiago, Chile',
                 ' Banco Bicentenario, Caracas, Venezuela', ' Banco Bilbao Vizcaya Argentaria, Bilbao, Spain',
                 ' Banco BPM, Milan, Italy', ' Banco BISA, La Paz, Bolivia', ' Banco BMG, São Paulo, Brazil',
                 ' Banco Bradesco, São Paulo, Brazil', ' Banco Caboverdiano de Negócios, Praia, Cape Verde',
                 ' Banco Caixa Geral, Vigo, Spain', ' Banco Comercial do Atlântico, Santiago, Cape Verde',
                 ' Banco Continental (Honduras)|Banco Continental, San Pedro Sula, Honduras',
                 ' Banco Credicoop, Buenos Aires, Argentina', ' Banco Crédito y Ahorro Ponceño, Ponce, Puerto Rico',
                 ' Banco de Bogota, Bogotá D.C., Colombia', ' Banco de Brasilia, Brasilia, Brazil',
                 ' Banco de Chile, Santiago, Chile', ' Banco de Comércio e Indústria, Angola',
                 ' Banco de Costa Rica, San José, Costa Rica', ' Banco de Crédito de Bolivia, La Paz, Bolivia',
                 ' Banco de Crédito del Perú, Lima, Peru', ' Banco de Crédito e Inversiones (BCI), Santiago, Chile',
                 ' Banco de Desenvolvimento de Angola, Angola',
                 ' Bank of the Nation (Peru)|Banco de la Nacion, San Isidro, Peru',
                 ' Banco de la Nacion Argentina, Buenos Aires, Argentina',
                 ' Banco de la Produccion, Managua, Nicaragua', ' Banco de la Republica, Montevideo, Uruguay',
                 ' Banco de la Republica Oriental del Uruguay, Buenos Aires, Argentina',
                 ' Banco de Machala, Machala, Ecuador',
                 ' Banco de Occidente Credencial|Banco de Occidente, Cali, Colombia',
                 ' Banco de Ponce, Ponce, Puerto Rico', ' Banco de Portugal, Lisbon, Portugal',
                 ' Banco de Poupança e Crédito, Luanda, Angola', ' Banco de Sabadell, Sabadell, Spain',
                 ' Banco de Valencia, Valencia, Spain', ' Banco de Venezuela, Caracas, Venezuela',
                 ' Banco del Estado de Chile, Santiago, Chile', ' Banco del Pacifico, Guayaquil, Ecuador',
                 ' Banco del Sur, Puerto Ordaz, Venezuela', ' Banco Delta Asia, Macau, Macao',
                 ' Banco di Desio e della Brianza, Desio, Italy', ' Banco di Napoli, Naples, Italy',
                 ' Banco di Sardegna, Sassari, Italy', ' Banco do Nordeste, Fortaleza, Brazil',
                 ' Banco do Brasil, Brasilia, Brazil', ' Banco Económico (Angola), Luanda, Angola',
                 ' Banco Español de Crédito, Madrid, Spain', ' Banco Espírito Santo, Lisbon, Portugal',
                 ' Banco Espírito Santo Angola, Largo das Ingombotas, Angola', ' Banco Falabella, Santiago, Chile',
                 ' Banco Gallego, La Coruña, Spain', ' Banco Hipotecario, Buenos Aires, Argentina',
                 ' Banco Hipotecario del Uruguay (BHU), Montevideo, Uruguay',
                 ' Banco Industrial de Venezuela, Caracas, Venezuela', ' Banco Interatlântico, Santiago, Cape Verde',
                 ' Banco Internacional de Costa Rica, San José, Costa Rica',
                 ' Banco Internacional de São Tomé e Príncipe, Sao Tome, Central Africa',
                 ' Banco Internacional del Peru, Lima, Peru', ' Banco Internacional do Funchal, Lisbon, Portugal',
                 ' Banco Invest, Lisbon, Portugal', ' Banco Itau Argentina, Buenos Aires, Argentina',
                 ' Banco Itau Chile, Santiago, Chile', ' Banco Itau Paraguay, Asunción, Paraguay',
                 ' Banco Latinoamericano de Comercio Exterior, Panama City, Panama',
                 ' Banco Macro, Buenos Aires, Argentina', ' Banco Mercantil, Caracas, Venezuela',
                 ' Banco Mercantil Santa Cruz, La Paz, Bolivia', ' Bancomext, Mexico City, Mexico',
                 ' Banco Nacional de Bolivia, La Paz, Bolivia', ' Banco Nacional de Costa Rica, San José, Costa Rica',
                 ' Banco Nacional de Crédito, Caracas, Venezuela',
                 ' Banco Nacional de Investimento, Maputo, Mozambique',
                 ' Banco Nacional de Panama, Panama City, Panama', ' Banco Nacional Ultramarino, Lisbon, Portugal',
                 ' Banco Occidental de Descuento, Maracaibo, Venezuela', ' Banco Palmas, Ceara, Brazil',
                 ' Banco Pan, São Paulo, Brazil', ' Banco Paris, Santiago, Chile', ' Banco Pastor, La Coruña, Spain',
                 ' Banco Patagonia, Buenos Aires, Argentina', ' Banco Penta, Santiago, Chile',
                 ' Banco Pichincha, Pichincha, Ecuador', ' Banco Popolare, Verona, Italy',
                 ' Banco Popular, San Pedro Sula, Honduras', ' Banco Popular, Bogotá D.C., Colombia',
                 ' Banco Popular, Madrid, Spain', ' Banco Português de Investimento  (BPI), Porto, Portugal',
                 ' Banco Regional, Encarnacion, Paraguay', ' Banco Ripley, Santiago, Chile',
                 ' Banco Sabadell, Alicante, Spain', ' Banco Safra, São Paulo, Brazil',
                 ' Banco Santander, Madrid, Spain',
                 ' Banco Santander (Mexico)|Banco Santander (México) S.A., Mexico City, Mexico',
                 ' Banco Santander Brasil, São Paulo, Brazil', ' Banco Santander Chile, Santiago, Chile',
                 ' Banco Santander Portugal, Lisbon, Portugal', ' Banco Santander Rio, Buenos Aires, Argentina',
                 ' Banco Santander Totta, Lisbon, Portugal', ' Banco Venezolano de Crédito, Caracas, Venezuela',
                 ' Banco Votorantim, São Paulo, Brazil', ' Bancolombia, Medellin, Colombia',
                 ' BancorpSouth, Tupelo, United States', ' Bancpost, Bucharest, Romania',
                 ' Bancrecer, Caracas, Venezuela', ' Bandhan Bank, Kolkata, India', ' Banesco, Caracas, Venezuela',
                 ' Banestes, Vitoria, Brazil', ' Bangkok Bank, Bangkok, Thailand',
                 ' Bangladesh Bank, Dhaka, Bangladesh', ' Bangladesh Commerce Bank Limited, Dhaka, Bangladesh',
                 ' Bangladesh Development Bank, Dhaka, Bangladesh', ' Bangladesh Krishi Bank, Dhaka, Bangladesh',
                 ' Bangladesh Samabaya Bank Limited, Dhaka, Bangladesh', ' Banisi, Panama City, Panama',
                 ' Banistmo, Panama City, Panama', ' Banka Kombëtare Tregtare, Tirana, Albania',
                 ' Bank AL Habib, Multan, Pakistan', ' Bank Alfalah, Karachi, Pakistan',
                 ' Bank Al-Maghrib, Rabat, Morocco', ' Bank Asia Limited, Dhaka, Bangladesh',
                 ' Bank Asya, Istanbul, Turkey', ' Bank Audi, Beirut, Lebanon', ' Bank Australia, Victoria, Australia',
                 ' Bank Austria, Vienna, Austria', ' Bank BPH, Gdansk, Poland',
                 ' Bank Central Asia (BCA), Jakarta, Indonesia', ' Bank Day, Tehran, Iran',
                 ' Bank Eskhata, Khujand, Tajikistan', ' Bank-e-Millie Afghan, Kabul, Afghanistan',
                 ' Bank First, Victoria, Australia',
                 ' Bank for Investment and Development of Vietnam (BIDV), Ho Chi Minh City, Vietnam',
                 ' Bank Forum, Kyiv, Ukraine', ' Bank für Sozialwirtschaft, Cologne and Berlin, Germany',
                 ' Bank für Tirol und Vorarlberg, Innsbruck, Austria', ' Bank Gaborone, Gaborone, Botswana',
                 ' Bank Gospodarstwa Krajowego, Warsaw, Poland', ' Bank Gutmann, Vienna, Austria',
                 ' Bank Handlowy w Warszawie, Warsaw, Poland', ' Bank Hapoalim, Tel Aviv, Israel',
                 ' Bankhaus Löbbecke, Berlin, Germany', ' Bankhaus Spängler, Salzburg, Austria',
                 ' Bank im Bistum Essen, Essen, Germany', ' Banking Company of West Africa, Dakar, Senegal',
                 ' Bank Insinger de Beaufort, Amsterdam, Netherlands',
                 ' Bank Internasional Indonesia, Jakarta, Indonesia',
                 ' Bank Islam Brunei Darussalam, Bandar Seri Begawan, Brunei',
                 ' BankIslami Pakistan, Karachi, Pakistan', ' Bank Keshavarzi (Agri Bank), Tehran, Iran',
                 ' Bank Leumi, Tel Aviv, Israel', ' Bank M, Dar es Salaam, Tanzania',
                 ' Bank Mandiri, Jakarta, Indonesia', ' Bank Maskan, Tehran, Iran', ' Bank Massad, Tel Aviv, Israel',
                 ' Bank Mellat, Tehran, Iran', ' Bank Melli Iran, Tehran, Iran',
                 ' Bank Mendes Gans, Amsterdam, Netherlands', ' Bank Millennium, Warsaw, Poland',
                 ' Bank Mizrahi-Tefahot, Ramat Gan, Israel', ' Bank Muamalat Indonesia, Jakarta, Indonesia',
                 ' Bank Muamalat Malaysia, Kuala Lumpur, Malaysia', ' Bank Muscat, Muscat, Oman',
                 ' Bank Nederlandse Gemeenten, The Hague, Netherlands', ' Bank Negara Indonesia, Jakarta, Indonesia',
                 ' Bank Norwegian, Fornebu, Norway', ' Bank OCBC NISP, Jakarta, Indonesia',
                 ' Bank Ochrony Srodowiska, Warsaw, Poland', ' Bank of Africa Group, Bamako, Mali',
                 ' Bank of Africa Kenya Limited, Nairobi, Kenya', ' Bank of Africa Uganda Limited, Kampala, Uganda',
                 ' Bank of Africa (Red Sea), Djibouti (City), Djibouti', ' Bank of Aland, Mariehamn, Finland',
                 ' Bank of Albania, Tirana, Albania', ' Bank of Algeria, Algiers, Algeria',
                 ' Bank of America, Charlotte, United States', ' Bank of Ayudhya, Bangkok, Thailand',
                 ' Bank of Azad Jammu & Kashmir, Muzaffarabad, Azad Kashmir', ' Bank of Baghdad, Baghdad, Iraq',
                 ' Bank of Bahrain and Kuwait (BBK), Manama, Bahrain', ' Bank of Baroda, Mumbai, India',
                 ' Bank of Baroda Uganda Limited, Kampala, Uganda', ' Bank of Beijing, Beijing, China',
                 ' Bank of Beirut, Beirut, Lebanon', ' Bank of Baroda, Gujarat, India',
                 ' Bank of Botswana, Gaborone, Botswana', ' Bank of Cape Verde, Praia, Cap Verde',
                 ' Bank of Central African States, Yaoundé, Cameroon', ' Bank of Ceylon, Colombo, Sri Lanka',
                 ' Bank of China, Beijing, China', ' Bank of China Hong Kong, Hong Kong, Hong Kong',
                 ' Bank of China#Canada|Bank of China (Canada), Ontario, Canada',
                 ' Bank of Commerce, Makati City, Philippines', ' Bank of Communications, Shanghai, China',
                 ' Bank of Cyprus, Nicosia, Cyprus', ' Bank of Dalian, Dalian, China',
                 ' Bank of Finland, Helsinki, Finland', ' Bank of France, Paris, France',
                 ' Bank of Georgia, Tbilisi, Georgia', ' Bank of Ghana, Accra, Ghana',
                 ' Bank of Greenland, Aabenraa, Denmark', ' Bank of Hawaii Corporation, Honolulu, United States',
                 ' Bank of India, Mumbai, India', ' Bank of Industry and Mine, Tehran, Iran',
                 ' Bank of Italy, Rome, Italy', ' Bank of Ireland, Dublin, Ireland', ' Bank of Iwate, Morioka, Japan',
                 ' Bank of Jerusalem, Jerusalem, Israel', ' Bank of Jilin, Changchun, China',
                 ' Bank of Jordan, Amman, Jordan', ' Bank of Kaohsiung, Kaohsiung, Taiwan',
                 ' Bank of Khartoum, Khartoum, Sudan', ' Bank of Kigali, Kigali, Rwanda',
                 ' Bank of Korea, Jung District, Seoul', ' Bank of Kyoto, Kyoto, Japan',
                 ' Bank of Latvia, Riga, Latvia', ' Bank of Lithuania, Vilnius, Lithuania ',
                 ' Bank of London and The Middle East, London, United Kingdom', ' Bank of Maharashtra, Pune, India',
                 ' Bank of Maldives, Male, Maldives', ' Bank of Melbourne (1989), Melbourne, Australia',
                 ' Bank of Melbourne (2011), Melbourne, Australia', ' Bank of Mexico, Mexico City, Mexico',
                 ' Bank of Mongolia, Ulaanbaatar, Mongolia', ' Bank of Montreal, Montreal, Canada',
                 ' Bank of Montserrat, Brades, Montserrat', ' Bank of Moscow, Moscow, Russia',
                 ' Bank of Mozambique, Maputo, Mozambique', ' Bank of Namibia, Namibia ',
                 ' Bank of New York Mellon, New York, United States', ' Bank of New Zealand, Auckland, New Zealand',
                 ' Bank of Ningbo, Ningbo, China', ' Bank of Papua New Guinea, Port Moresby, Papua New Guinea',
                 ' Bank of Punjab, Lahore, Pakistan', ' Bank of Qingdao, Qingdao, China',
                 ' Bank of Queensland, Brisbane, Australia', ' Bank of Shanghai, Shanghai, China',
                 ' Bank of Sierra Leone, Freetown, Sierra Leone', ' Bank of Slovenia, Ljubljana, Slovenia',
                 ' Bank of South Australia, Adelaide, South Australia',
                 ' Bank of South Pacific, Port Moresby, Papua New Guinea', ' Bank of South Sudan, Juba, South Sudan',
                 ' Bank of Spain, Madrid, Spain', ' Bank of St Lucia, Castries, St Lucia',
                 ' Bank of Syria and Overseas, Damascus, Syria', ' Bank of Taiwan, Taipei, Taiwan',
                 ' Bank of Taizhou, Taizhou, China', ' Bank of Tanzania, Dar es Salaam, Tanzania',
                 ' Bank of the City of Buenos Aires, Buenos Aires, Argentina', ' Bank of the Nation (Peru), Lima, Peru',
                 ' Bank of the Orient, California, United States', ' Bank of the Ozarks, Little Rock, United States',
                 ' Bank of the Philippine Islands, Makati City, Philippines',
                 ' Bank of the Province of Buenos Aires, Buenos Aires, Argentina',
                 ' Bank of the Republic of Haiti, Port-au-Prince, Haiti', ' Bank of the Ryukyus, Naha, Japan',
                 ' Bank of the West, San Francisco, California', ' Bank of Tianjin, Tianjin, China',
                 ' Bank of Tokyo Mitsubishi, Tokyo, Japan', ' Bank of Uganda, Kampala, Uganda',
                 ' Bank of Valletta, Valletta, Malta', ' Bank of Western Australia, Perth, Australia',
                 ' Bank of Yokohama, Yokohama, Japan', ' Bank of Zambia, Lusaka, Zambia',
                 ' Bank One Mauritius, Port Louis, Mauritius', ' Bank Otsar Ha-Hayal, Israel ',
                 ' Bank Pasargad, Tehran, Iran', ' Bank Pekao, Warsaw, Poland', ' Bank Permata, Jakarta, Indonesia',
                 ' Bank Pocztowy, Bydgoszcz, Poland', ' Bank Polska Kasa Opieki, Warsaw, Poland',
                 ' Bank Pundi Indonesia, Jakarta, Indonesia', ' Bank Rakyat Indonesia, Jakarta, Indonesia',
                 ' Bank Refah, Tehran, Iran', ' Bank Respublika, Baku, Azerbaijan',
                 ' Bank Rossiya, St Petersburg, Russia', ' Bank Saderat Iran (BSI), Tehran, Iran',
                 ' Bank Saint Petersburg, St Petersburg, Russia', ' Bank Sepah, Tehran, Iran',
                 ' Bank Simpanan Nasional, Kuala Lumpur, Malaysia', ' Bank SinoPac, Taipei, Taiwan',
                 ' Bank South Pacific, Port Moresby, Papua New Guinea', ' Bank Sparhafen Zürich, Zürich, Switzerland',
                 ' Bank Spółdzielczy w Brodnicy, Brodnica, Poland', ' Bank Stern, Paris, France',
                 ' Bank Tabungan Negara (BTN), Jakarta, Indonesia', ' Bank Tejarat, Tehran, Iran',
                 ' Bank Ten Cate & Cie, Amsterdam, Netherlands', ' BankVic, Melbourne, Australia',
                 ' Bankwest, Perth, Western Australia', ' Bank Windhoek, Windhoek, Namibia',
                 ' Bank Zachodni WBK, Wroclaw, Poland', ' Banka Kombetare Tregtare, Tirana, Albania',
                 ' BankAtlantic Bancorp, Fort Lauderdale, United States', ' Bankhaus Bauer, Stuttgart, Germany',
                 ' Bankhaus Lampe, Bielefeld, Germany', ' Bankhaus Reuschel & Co., Munich, Germany',
                 ' Bankia, Madrid, Spain', ' Bankinter, Madrid, Spain', ' Bankmecu, Kew, Australia',
                 ' BankMuscat (SAOG), Muscat, Oman', ' BankNordik, Tórshavn, Faroe Islands',
                 ' Bankoa, San Sebastian, Spain', ' BankUnited, Miami Lakes, United States',
                 ' Banque Bemo Saudi Fransi, Damascus, Syria', ' Banque Cantonale de Fribourg, Fribourg, Switzerland',
                 ' Banque Cantonale de Geneve, Geneva, Switzerland', ' Banque Cantonale du Valais, Sion, Switzerland',
                 ' Banque Cantonale Neuchateloise, Neuchâtel, Switzerland',
                 ' Banque Cantonale Vaudoise, Lausanne, Switzerland',
                 ' Banque Commerciale du Congo, Kinshasa, DRC Congo', ' Banque du Développement du Mali, Bamako, Mali',
                 ' Banque de Luxembourg, Luxembourg, Luxembourg', " Banque de l'Habitat, Tunis, Tunisia",
                 " Banque de l'Habitat du Mali, Bamako, Mali", ' Banque du Liban, Beirut, Lebanon',
                 " Banque de l'Union Haitienne, Port-au-Prince, Haiti", ' Banque de Tunisie, Tunis, Tunisia',
                 ' Banque de Tunisie et des Emirats, Tunis, Tunisia', ' Banque du Caire, Cairo, Egypt',
                 " Banque et Caisse d'Épargne de l'État, Luxembourg City, Luxembourg",
                 ' Banque Francaise Commerciale Ocean Indien, Paris, France',
                 ' Banque Internationale a Luxembourg, Luxembourg, Luxembourg',
                 ' Banque Internationale Arabe de Tunisie, Tunis, Tunisia',
                 ' Banque Internationale du Benin (BIBE), Cotonou, Benin',
                 ' Banque Internationale pour la Centrafrique, Bangui, Central African Republic',
                 ' Banque Libano-Française S.A.L., Beirut, Lebanon', ' Banque Misr, Cairo, Egypt',
                 ' Banque Nagelmackers, Brussels, Belgium', ' Banque Nationale Agricole, Tunis, Tunisia',
                 ' Banque Nationale de Développement Agricole, Bamako, Mali', ' Banque Pharaon & Chiha, Lebanon',
                 " Banque pour le Commerce et l'Industrie – Mer Rouge, Djibouti (City), Djibouti",
                 ' Banque Populaire du Rwanda, Kigali, Rwanda',
                 ' Banque Populaire Maroco Centrafricaine, Bangui, Central African Republic',
                 ' Banque Raiffeisen, Luxembourg, Luxembourg',
                 " Banque Sahélo-Saharienne pour l'Investissement et le Commerce, Tripoli, Libya",
                 ' Banque Saudi Fransi, Riyadh, Saudi Arabia', ' Banque Transatlantique, Paris, France',
                 ' Banque Zitouna, Tunis, Tunisia', ' BanRegio, Monterrey, Mexico', ' Banrisul, Porto Alegre, Brazil',
                 ' Bansi, Guadalajara, Mexico', ' Banobras, Mexico City, Mexico', ' Banorte, Monterrey, Mexico',
                 ' Barclays, London, United Kingdom', ' Barclays Africa Group, Johannesburg, South Africa',
                 ' Barclays Bank Mauritius, Ebene, Mauritius', ' Barclays Bank of Kenya, Nairobi, Kenya',
                 ' Barclays Bank of Uganda, Kampala, Uganda', ' Barclays Bank Tanzania, Dar es Salaam, Tanzania',
                 ' Basellandschaftliche Kantonalbank, Liestal, Switzerland',
                 ' Basrah International Bank for Investment, Baghdad, Iraq', ' BASIC Bank Limited, Dhaka, Bangladesh',
                 ' Basler Kantonalbank, Basel, Switzerland', ' Bausparkasse Schwäbisch Hall, Schwäbisch Hall, Germany',
                 ' BAWAG P.S.K., Vienna, Austria', ' Bayerische Landesbank, München, Germany',
                 ' Bayerische Landesbank, Munich, Germany', ' BayernLB, Munich, Germany',
                 ' Baylake Corp, Sturgeon Bay, United States', ' BBBank, Karlsruhe, Germany',
                 ' BBCN Bancorp, Los Angeles, United States', ' BBVA Banco Frances, Buenos Aires, Argentina',
                 ' BBVA Chile, Santiago, Chile', ' BBVA Compass, Alabama, USA', ' BBVA Continental, Lima, Peru',
                 ' BBVA México, Mexico City, Mexico', ' BBVA Provincial, Caracas, Venezuela',
                 ' BCR Chișinău, Chisinau, Republic of Moldova', ' BDO Unibank, Makati City, Philippines',
                 ' Belarusbank, Minsk, Belarus', ' Belfius, Brussels, Belgium',
                 ' Bendigo and Adelaide Bank, Bendigo, Australia', ' Beobank, Brussel, Belgium',
                 ' Berenberg Bank, Hamburg, Germany', ' Berlin Hyp, Berlin, Germany',
                 ' Berliner Sparkasse, Berlin, Germany', ' Bermuda Commercial Bank, Hamilton, Bermuda',
                 ' Bermuda Monetary Authority, Hamilton, Bermuda', ' Berner Kantonalbank, Berne, Switzerland',
                 ' Bethmann Bank, Frankfurt am Main, Germany', ' Beyond Bank Australia, Adelaide, South Australia',
                 ' BGFIBank Group, Libreville, Gabon', ' BGL BNP Paribas, Luxembourg, Luxembourg',
                 ' BHF Bank, Frankfurt am Main, Germany', ' Bhutan National Bank, Thimphu, Bhutan',
                 ' Bidvest Bank, Johannesburg, South Africa', ' Bilbao Bizkaia Kutxa, Bilbao, Spain',
                 ' BIMB Holdings, Kuala Lumpur, Malaysia', ' BinckBank, Amsterdam, Netherlands',
                 ' Birleşik Fon Bankası, Istanbul, Turkey', ' BLOM Bank, Beirut, Lebanon',
                 ' Birleşik Fon Bankası, Istanbul, Turkey', ' BLC bank, Beirut, Lebanon', ' BMCI, Casablanca, Morocco',
                 ' BMO Harris Bank, Chicago, United States', ' BMW Bank, Munich, Germany',
                 ' BNC Bancorp, Thomasville, United States', ' BNP Paribas, Paris, France',
                 ' BNP Paribas Bank Polska, Warsaw, Poland', ' BNP Paribas CIB, Paris, France',
                 ' BNP Paribas Fortis, Brussels, Belgium', ' BNP Paribas Investment Partners, Paris, France',
                 ' BOK Financial Corporation, Tulsa, United States', ' Bolig- og Næringsbanken, Trondheim, Norway',
                 ' Botswana Savings Bank, Gaborone, Botswana', ' Boubyan Bank, Safat, Kuwait', ' BPCE, Paris, France',
                 ' BPER Banca, Modena, Italy', ' BRAC Bank Limited, Dhaka, Bangladesh',
                 ' Bradford & Bingley, Bingley, United Kingdom', ' Brazilian Development Bank, Rio de Janeiro, Brazil',
                 ' BRD – Groupe Société Générale, Bucharest, Romania', ' Bremer Bank (German bank), Bremen, Germany',
                 ' British Arab Commercial Bank, London, United Kingdom', ' Brown Shipley, London, United Kingdom',
                 ' BSI Ltd|Banca della Svizzera Italiana, Lugano, Switzerland', ' BTA Bank, Almaty, Kazakhstan',
                 ' BTA Bank, Tbilisi, Georgia', ' BTG Pactual, Rio de Janeiro, Brazil',
                 ' Budapest Bank, Budapest, Hungary', ' Buffalo Commercial Bank, Juba, South Sudan',
                 ' Bulgarian Development Bank, Sofia, Bulgaria', ' Burgan Bank, Sharq, Kuwait',
                 ' Burj Bank, Karachi, Pakistan', ' Busan Bank, Busan, South ', ' Butterfield Bank, Hamilton, Bermuda',
                 ' Byblos Bank, Beirut, Lebanon', ' Byline Bank, Chicago, United States',
                 ' C. Hoare & Co, London, United Kingdom', ' Cairo Amman Bank, Amman, Jordan',
                 ' Caisse des dépôts et consignations, Paris, France',
                 ' Caixa Económica de Cabo Verde, Praia, Cape Verde',
                 ' Caixa Econômica Federal, Rio de Janeiro, Brazil', ' Caixa Geral de Depósitos, Lisbon, Portugal',
                 ' Caixabank, Barcelona, Spain', ' Caixa Rural Galega, Lugo, Spain',
                 ' Caja de Ahorros, Panama City, Panama', ' Caja de Ahorros y Monte de Piedad de Madrid, Madrid, Spain',
                 ' Caja de Ahorros y Monte de Piedad de Navarra, Pamplona, Spain',
                 ' Caja General de Ahorros de Canarias, Santa Cruz de Tenerife, Spain', ' Caja Murcia, Murcia, Spain',
                 ' CajaSur, Cordoba, Spain', ' CAL Bank, Accra, Ghana',
                 ' California First National Bancorp, Irvine, United States',
                 ' Cambodia Asia Bank, Phnom Penh, Cambodia', ' Cambodia Commercial Bank, Phnom Penh, Cambodia',
                 ' Cambodian Public Bank, Phnom Penh, Cambodia',
                 ' Camco Financial Corporation, Cambridge, United States', ' Canadia Bank, Phnom Penh, Cambodia',
                 ' Canadian Imperial Bank of Commerce, Toronto, Canada', ' Canadian Western Bank, Edmonton, Canada',
                 ' Canara Bank, Bangalore, India', ' Capital Bank (Botswana), Gaborone, Botswana',
                 ' Capital Bank (Haiti), Pétion-Ville, Haiti', ' Capital Bank of Jordan, Amman, Jordan',
                 ' Capital G Bank, Hamilton, Bermuda', ' Capital One Bank, Glen Allen, United States',
                 ' Capital One Financial Corporation, McLean, United States',
                 ' Cardinal Financial Corporation, McLean, United States', ' Cargills Bank, Colombo, Sri Lanka',
                 ' Carispezia, La Spezia, Italy', ' Cascade Bancorp, Bend, United States',
                 ' Cassa dei Risparmi di Forlì e della Romagna, Forlì, Italy',
                 ' Cassa Depositi e Prestiti, Rome, Italy',
                 ' Cassa di Risparmio del Friuli Venezia Giulia, Gorizia, Italy',
                 ' Cassa di Risparmio della Provincia di Chieti, Chieti, Italy',
                 ' Cassa di Risparmio della Provincia di Viterbo, Viterbo, Italy',
                 ' Cassa di Risparmio di Alessandria, Alessandria, Italy', ' Cassa di Risparmio di Asti, Asti, Italy',
                 ' Cassa di Risparmio di Biella e Vercelli, Biella, Italy',
                 ' Cassa di Risparmio di Bolzano-Sudtiroler Sparkasse, Bolzano, Italy',
                 ' Cassa di Risparmio di Bra, Bra, Italy', ' Cassa di Risparmio di Cento, Cento, Italy',
                 ' Cassa di Risparmio di Cesena, Cesena, Italy', ' Cassa di Risparmio di Fermo, Fermo, Italy',
                 ' Cassa di Risparmio di Ferrara, Ferrara, Italy', ' Cassa di Risparmio di Fossano, Fossano, Italy',
                 ' Cassa di Risparmio di Genova e Imperia, Genova, Italy',
                 ' Cassa di Risparmio di Orvieto, Orvieto, Italy',
                 ' Cassa di Risparmio di Pistoia e Pescia, Pistoia, Italy',
                 ' Cassa di Risparmio di Ravenna, Ravenna, Italy',
                 ' Cassa di Risparmio di Rimini (CARIM), Rimini, Italy',
                 ' Cassa di Risparmio di Saluzzo, Saluzzo, Italy',
                 ' Cassa di Risparmio di San Miniato, San Miniato, Italy',
                 ' Cassa di Risparmio di Venezia, Venice, Italy', ' Cassa di Risparmio di Volterra, Volterra, Italy',
                 ' Cassa Padana, Leno, Italy', ' Catalunya Banc (CatalunyaCaixa), Barcelona, Spain',
                 ' Cater Allen, London, England', ' Cathay Bank, Los Angeles, United States',
                 ' Cathedral Investment Bank, Dominica, Western Antilles',
                 ' Cathay General Bancorp, Los Angeles, United States', ' Cathay United Bank, Taipei, Taiwan',
                 ' Catholic Syrian Bank, Thrissur, India', ' Cavmont Bank, Lusaka, Zambia',
                 ' CCB Brasil, São Paulo, Brazil', ' CDH Investment Bank, Blantyre, Malawi',
                 ' CDG Capital, Rabat, Morocco', ' CEC Bank, Bucharest, Romania', ' Centenary Bank, Kampala, Uganda',
                 ' Centennial Bank, Conway, Arkansas, United States',
                 ' Central Bank (Utah)|Central Bank, Provo, Utah, United States',
                 ' Central Bank of Argentina, Buenos Aires, Argentina',
                 ' Central Bank of Azerbaijan, Baku, Azerbaijan ', ' Central Bank of Bahrain, Manama, Bahrain',
                 ' Central Bank of Barbados, Bridgetown, Saint Michael', ' Central Bank of Bolivia, La Paz, Bolivia',
                 ' Central Bank of Bosnia and Herzegovina, Sarajevo, Bosnia and Herzegovina',
                 ' Central Bank of Brazil, Brasilia, Brazil', ' Central Bank of Chile, Santiago, Chile',
                 ' Central Bank of Costa Rica, San José, Costa Rica', ' Central Bank of Cyprus, Nicosia, Cyprus',
                 ' Central Bank of Djibouti, Djibouti (City), Djibouti', ' Central Bank of Egypt, Cairo, Egypt',
                 ' Central Bank of Eswatini, Mbabane, Eswatini', ' Central Bank of Iceland, Reykjavik, Iceland',
                 ' Central Bank of India, Mumbai, India', ' Central Bank of Iran, Tehran, Iran',
                 ' Central Bank of Iraq, Baghdad, Iraq', ' Central Bank of Kenya, Nairobi, Kenya',
                 ' Central Bank of Kuwait, Kuwait City, Kuwait', ' Central Bank of Lesotho, Lesotho, South Africa',
                 ' Central Bank of Liberia, Monrovia, Liberia', ' Central Bank of Libya, Tripoli, Liberia',
                 ' Central Bank of Madagascar, Malagasy, Madagascar', ' Central Bank of Malta, Valletta, Malta ',
                 ' Central Bank of Mauritania, Nouakchott, Mauritania',
                 ' Central Bank of Montenegro, Podgorica, Montenegro', ' Central Bank of Nicaragua, Managua, Nicaragua',
                 ' Central Bank of Nigeria, Abuja, Nigeria', ' Central Bank of Paraguay, Asunción, Paraguay',
                 ' Central Bank of The Gambia, Banjul, The Gambia',
                 " Central Bank of the Democratic People's Republic of Korea, Pyongyang, North Korea",
                 ' Central Bank of the Republic of China (Taiwan), Zhongzheng, Taipei',
                 ' Central Bank of the Republic of Turkey, Ankara, Turkey',
                 ' Central Bank of the United Arab Emirates, Abu Dhabi, United Arab Emirates',
                 ' Central Bank of Tunisia, Tunis, Tunisia', ' Central Bank of Turkmenistan, Ashgabat, Turkmenistan',
                 ' Central Bank of Samoa, Apia, Samoa',
                 ' Central Bank of São Tomé and Príncipe, Sao Tome, Central Africa',
                 ' Central Bank of Somalia, Mogadishu, Somalia', ' Central Bank of Seychelles, Victoria, Seychelles',
                 ' Central Bank of Suriname, Paramaribo, Suriname', ' Central Bank of Syria, Damascus, Syria',
                 ' Central Bank of the Republic of Guinea, Guinea ',
                 ' Central Bank of the Turkish Republic of Northern Cyprus, North Nicosia, Northern Cyprus',
                 ' Central Bank of Uruguay, Montevideo, Uruguay', ' Central Bank of Uzbekistan, Uzbekistan ',
                 ' Central Bank of Venezuela, Caracas, Venezuela',
                 ' Central Bank of West African States, Dakar, Senegal', ' Central Bank of Yemen, Aden, Yemen',
                 ' Central Cooperative Bank, Sofia, Bulgaria',
                 ' Central Pacific Financial Corp., Honolulu, United States',
                 ' Central Reserve Bank of Peru, Lima, Peru', ' Century Bank Limited, Putalisadak, Kathmandu ',
                 ' Československá obchodní banka, Prague, Slovakia', ' Cetelem, Paris, France',
                 ' Cham Bank, Damascus, Syria', ' Chang Hwa Bank, Taipei, Taiwan',
                 ' Chase Bank, New York, United States', ' Chase Bank Kenya Limited, Nairobi, Kenya',
                 ' ChiantiBanca, Monteriggioni, Italy', ' Chiba Bank, Chiba, Japan',
                 ' China Banking Corporation, Makati City, Philippines', ' China Bohai Bank, Tianjin, China',
                 ' China Citic Bank, Beijing, China', ' China Construction Bank Corporation, Beijing, China',
                 ' China Construction Bank (Macau), Macau, China', ' China Everbright Bank, Beijing, China',
                 ' China Guangfa Bank, Guangzhou, China', ' China Merchants Bank, Shenzhen, China',
                 ' China Minsheng Bank, Beijing, China', ' China Zheshang Bank, Ningbo, China',
                 ' Chiyu Banking Corporation, Hong Kong, Hong Kong', ' Chong Hing Bank, Hong Kong, Hong Kong',
                 ' CIB Bank, Budapest, Hungary', ' CIBC Bank USA, Chicago, United States',
                 ' CIBC FirstCaribbean International Bank, Warrens, Barbados', ' CIMB Group, Kuala Lumpur, Malaysia',
                 ' CIMB Niaga, Jakarta, Indonesia', ' CIT Group, Livingston, United States',
                 ' Citadele Banka, Riga, Latvia', ' Citibank Argentina, Buenos Aires, Argentina',
                 ' Citibank Australia, Sydney, Australia', ' Citibank Bahrain, Manama, Bahrain',
                 ' Citibank Canada, Toronto, Canada', ' Citibank (China), Shanghai, China',
                 ' Citibank Ecuador, Guayaquil, Ecuador', ' Citibank Europe, Dublin, Ireland',
                 ' Citibank (Hong Kong), Hong Kong, China', ' Citibank India, Mumbai, India',
                 ' Citibank Indonesia, Jakarta, Indonesia', ' Citibank Korea, Seoul, South Korea',
                 ' Citibank Malaysia, Kuala Lumpur, Malaysia', ' Citibank Singapore Marina View, Singapore',
                 ' Citibank Thailand, Bangkok, Thailand', ' Citibank Uganda, Kampala, Uganda',
                 ' Citibank United Arab Emirates, Dubai, United Arab Emirates ', ' Citibank, New York, United States',
                 ' CITIC Bank International, Hong Kong, China', ' Citigroup, New York, United States',
                 ' Citizens Republic Bancorp, Flint, Michigan, United States',
                 ' City National Bank (California), Los Angeles, California',
                 ' City National Corporation, Beverly Hills, United States', ' City Union Bank, Kumbakonam, India',
                 ' Civil Bank Limited, Kamaladi, Kathmandu', ' Clarien Bank, Hamilton, Bermuda',
                 ' Close Brothers Group, London, United Kingdom', ' Clydesdale Bank, Glasgow, United Kingdom',
                 ' Comdirect, Quickborn, Germany', ' Comerica, Dallas, United States',
                 ' Commerce Bancshares, Kansas City, United States',
                 ' Commercial Bank Centrafrique, Bangui, Central African Republic',
                 ' Commercial Bank Group, Douala, Cameroon', ' Commercial Bank of Africa, Nairobi, Kenya',
                 ' Commercial Bank of Africa (Tanzania), Dar es Salaam, Tanzania',
                 ' Commercial Bank of Cameroon, Douala, Cameroon', ' Commercial Bank of Ceylon, Colombo, Sri Lanka',
                 ' Commercial Bank of Dubai, Dubai, United Arab Emirates',
                 ' Commercial Bank of Eritrea, Asmara, Eritrea', ' Commercial Bank of Ethiopia, Addis Ababa, Ethiopia',
                 ' Commercial Bank of Kuwait, Safat, Kuwait', ' Commercial Bank of Syria, Damascus, Syria',
                 ' Commerzbank, Frankfurt am Main, Germany', ' Commonwealth Bank, Sydney, Australia',
                 ' Community Bank Bangladesh Limited, Bangladesh ',
                 ' Community Bank System, DeWitt, New York, United States',
                 ' Community West Bancshares, Goleta, United States', ' CommunityOne Bancorp, Asheboro, United States',
                 ' Compagnie Financière Edmond de Rothschild, Paris, France',
                 ' Compagnie Générale de Banque, Kigali, Rwanda',
                 ' Compagnie Monégasque de Banque, Monte Carlo, Monaco', ' Compartamos Banco, Mexico City, Mexico',
                 ' Consolidated Bank of Kenya, Nairobi, Kenya', ' Consorsbank, Nürnberg, Germany',
                 ' Consors Finanz, Munich, Germany', ' Continental Bank of Canada, Toronto, Canada',
                 ' Cooperative Bank, Skopje, Macedonia', ' Cooperative Bank, Yangon, Myanmar',
                 ' Cooperative Bank, Wellington, New Zealand', ' Co-operative Bank of Kenya, Nairobi, Kenya',
                 ' Cooperative Bank of Oromia, Addis Ababa, Ethiopia', ' Corporate Commercial Bank, Sofia, Bulgaria',
                 ' Corporation Bank, Mangalore, India', ' Cosmos Bank, Pune, India',
                 ' COTA Commercial Bank, Taichung, Taiwan', ' Coventry Building Society, Coventry, United Kingdom',
                 ' Crane Bank, Kampala, Uganda', ' CRDB Bank, Dar es Salaam, Tanzania',
                 ' Credins Bank, Tirana, Albania', ' Crediop, Rome, Italy', ' Credit Agricole, Montrouge, France',
                 ' Crédit Agricole Cariparma, Parma, Italy', ' Credit Agricole CIB, Paris, France',
                 ' Credit Agricole CIB Hungary, Budapest, Hungary', ' Credit Agricole CIB Ukraine, Kyiv, Ukraine',
                 ' Crédit Agricole Corporate and Investment Bank, Paris, France',
                 ' Credit Agricole Egypt, Cairo, Egypt', ' Crédit Agricole Italia, Parma, Italy',
                 ' Credit Agricole Srbija, Novi Sad, Serbia', ' Crèdit Andorrà, Andorra la Vella, Andorra',
                 ' Credit Bank, Ulaanbataar, Mongolia', ' Credit Bank, Nairobi, Kenya',
                 ' Credit Bank of Albania, Tirana, Albania', ' Credit Bank of Moscow, Moscow, Russia',
                 ' Crédit Industriel et Commercial (CIC), Paris, France', ' Crédit du Nord, Paris, France',
                 ' Credit Europe Bank, Amsterdam, Netherlands', ' Crédit Foncier de France, Charenton, France',
                 ' Credit Immobilier et Hotelier (CIH), Casablanca, Morocco',
                 ' Credit Industriel et Commercial (CIC), Paris, France', ' Credit Lyonnais, Paris, France',
                 ' Credit Mutuel, Paris, France', ' Credit Suisse Group, Zurich, Switzerland',
                 ' Credito Bergamasco, Bergamo, Italy', ' Credito Emiliano, Reggio Emilia, Italy',
                 ' Credito Fondiario (Fonspa), Rome, Italy', ' Credito Siciliano, Acireale, Italy',
                 ' Credito Valtellinese, Sondrio, Italy', ' Crelan, Brussels, Belgium',
                 ' Croatian National Bank, Zagreb, Croatia', ' CS Alterna Bank, Ottawa, Canada',
                 ' CSCBank SAL, Beirut, Lebanon', ' CTBC Bank, Taipei, Taiwan',
                 ' CTBC Bank#Canadian subsidiary|CTBC Bank (Canada), Vancouver, Canada',
                 ' CTBC Financial Holding, Taipei, Taiwan', ' Cultura Sparebank, Oslo, Norway',
                 ' Cyprus Development Bank, Nicosia, Cyprus', ' Da Afghanistan Bank, Kabul, Afghanistan',
                 ' DAB BNP Paribas, Munich, Germany', ' Daedong Credit Bank, Pyongyang, North Korea',
                 ' Dah Sing Bank, Hong Kong, China', ' Danske Bank, Copenhagen, Denmark',
                 ' Danske Bank (Norway), Trondheim, Norway',
                 ' Danske Bank (Northern Ireland), Belfast, Northern Ireland',
                 ' Dar es Salaam Community Bank, Dar es Salaam, Tanzania',
                 ' Dar Es Salaam Investment Bank, Baghdad, Iraq', ' Davivienda, Bogotá, Colombia',
                 ' Daycoval, São Paulo, Brazil', ' DBS Bank, Singapore, Singapore',
                 ' DBS Bank (Hong Kong), Hong Kong, China', ' DCB Bank, Mumbai, India',
                 ' Degussa Bank, Frankfurt am Main, Germany', ' DekaBank Deutsche Girozentrale, Berlin, Germany',
                 ' DekaBank (Germany), Frankfurt am Main, Germany', ' Delta Bank, Minsk, Belarus',
                 ' Delta Bank, Kyiv, Ukraine', ' Dena Bank, Mumbai, India',
                 ' De Nederlandsche Bank, Amsterdam, Netherlands', ' Denizbank, Istanbul, Turkey',
                 ' Denmark Bancshares, Denmark, Wisconsin, United States', ' Desjardins Group, Levis, Canada',
                 ' De Surinaamsche Bank, Paramaribo, Suriname',
                 ' Deutsche Apotheker- und Ärztebank, Düsseldorf, Germany',
                 ' Deutsche Bank, Frankfurt am Main, Germany', ' Deutsche Bank (Italy), Milano, Italy',
                 ' Deutsche Bundesbank, Frankfurt am Main, Germany', ' Deutsche Hypothekenbank, Hannover, Germany',
                 ' Deutsche Pfandbriefbank, Unterschleißheim, Germany', ' Deutsche Postbank, Bonn, Germany',
                 ' Deutsche Kreditbank, Berlin, Germany',
                 ' Deutsche WertpapierService Bank, Frankfurt am Main, Germany',
                 ' Deutsche Zentral-Genossenschaftsbank, Frankfurt am Main, Germany',
                 ' Deutscher Sparkassen- und Giroverband, Berlin, Germany',
                 ' Development Bank of Ethiopia, Addis Ababa, Ethiopia', ' Development Bank of Kenya, Nairobi, Kenya',
                 ' Development Bank of the Philippines (DBP), Makati City, Philippines',
                 ' Development Bank of Vojvodina, Novi Sad, Serbia', ' Development Credit Bank, Mumbai, India',
                 ' Development Finance Corporation Belize, Belmopan, Belize', ' De Volksbank, Utrecht, Netherlands',
                 ' Dexia, Brussels, Belgium', ' DFCC Bank, Colombo, Sri Lanka', ' DFCU Group, Kampala, Uganda',
                 ' DGB Financial Group, Daegu, South Korea', ' Dhaka Bank, Dhaka, Bangladesh',
                 ' Dhaka Bank Limited, Dhaka, Bangladesh', ' Dhanalakshmi Bank, Thrissur, India',
                 ' Dhanlaxmi Bank, Kerala, India', ' DHB Bank, Rotterdam, Netherlands', ' Diamond Bank, Lagos, Nigeria',
                 ' Diamond Trust Bank Group, Nairobi, Kenya',
                 ' Diamond Trust Bank (Tanzania) Limited, Dar es Salaam, Tanzania',
                 ' Diamond Trust Bank (Uganda), Kampala, Uganda', ' Die Zweite Sparkasse, Vienna, Austria',
                 ' Dime Community Bank, Brooklyn, United States', ' Direktna Banka, Kragujevac, Serbia',
                 ' Discover Financial Services, Riverwoods, Illinois, United States', ' DNB ASA, Oslo, Norway',
                 ' Dnister, Lviv, Ukraine', ' doBank, Verona, Italy', ' Donner & Reuschel, Hamburg, Germany',
                 ' Doral Financial Corporation, San Juan, Puerto Rico|San Juan, Puerto Rico',
                 ' DSK Bank, Sofia, Bulgaria', ' DSK Hyp, Frankfurt, Germany', ' Dresdner Bank, Frankfurt, Germany',
                 ' Dubai Bank, Dubai, United Arab Emirates', ' Dubai Bank Kenya, Nairobi, Kenya',
                 ' Dubai Islamic Bank, Dubai, United Arab Emirates', ' Dubai Islamic Bank Pakistan, Karachi, Pakistan',
                 ' Dutch Bangla Bank, Dhaka, Bangladesh', ' Düsseldorfer Hypothekenbank, Düsseldorf, Germany',
                 ' DVB Bank, Frankfurt am Main, Germany', ' Dyer & Blair Investment Bank, Nairobi, Kenya',
                 ' DZ Bank, Frankfurt am Main, Germany', ' ', ' Eagle Bancorp, Bethesda, Maryland, United States',
                 ' East West Bancorp, Pasadena, United States',
                 ' Eastern Bank Ltd (Bangladesh)|Eastern Bank Ltd, Dhaka, Bangladesh',
                 ' Eastern Bank, Boston, United States', ' Eastern Bank Ltd (historic)|Eastern Bank Ltd, London, UK',
                 ' Eastern Caribbean Central Bank, Basseterre, St. Kitts    ', ' Ecobank Ghana Limited, Accra, Ghana',
                 ' Ecobank Kenya, Nairobi, Kenya', ' Ecobank Nigeria, Lagos, Nigeria',
                 ' Ecobank Rwanda, Kigali, Rwanda', ' Ecobank Transnational, Lomé, Togo',
                 ' Ecobank Uganda, Kampala, Uganda', ' Ecobank Zimbabwe, Harare, Zimbabwe',
                 ' Edekabank, Hamburg, Germany', ' Educational Services of America, Knoxville, United States',
                 ' EFG Group, Geneva, Switzerland', ' EFG International, Zurich, Switzerland',
                 ' Egg Banking|Egg, London, United Kingdom', ' Emigrant Savings Bank, New York, United States',
                 ' Emirates Islamic Bank, Dubai, United Arab Emirates', ' Emirates NBD, Dubai, United Arab Emirates',
                 ' Emporiki Bank, Athens, Greece', ' EN Bank, Tehran, Iran', ' EON Bank, Kuala Lumpur, Malaysia',
                 ' eQ Bank, Helsinki, Finland', ' Equatorial Commercial Bank, Nairobi, Kenya',
                 ' Equitas Small Finance Bank, Chennai, India', ' Equity Bank Kenya Limited, Nairobi, Kenya',
                 ' Equity Bank Uganda Limited, Kampala, Uganda', ' Equity Group Holdings Limited, Nairobi, Kenya',
                 ' E.SUN Commercial Bank, Taipei, Taiwan', ' Etibank, Istanbul, Turkey',
                 ' Eritrean Investment and Development Bank, Asmara, Eritrea', ' Erste Bank Novi Sad, Novi Sad, Serbia',
                 ' Erste Group, Vienna, Austria', ' ESAF Small Finance Bank, Mannuthy, Thrissur',
                 ' Espírito Santo Financial Group, Luxembourg, Luxembourg', ' Euler Hermes, Paris, France',
                 ' Eurasian Bank, Almaty, Kazakhstan ', ' Euro Bank, Wroclaw, Poland',
                 ' Eurobank a.d., Belgrade, Serbia', ' Eurobank Bulgaria (Postbank), Sofia, Bulgaria',
                 ' Eurobank Ergasias, Athens, Greece', ' Eurocity Bank, Frankfurt, Germany',
                 ' Eurohypo, Frankfurt, Germany', ' EverBank, Jacksonville, Florida, United States',
                 ' Everest Bank, Kathmandu, Nepal', ' EVO Banco, Madrid, Spain', ' Evocabank, Yerevan, Armenia ',
                 ' Evrofinance Mosnarbank, Moscow, Russia', ' Exchange Bank of Canada, Toronto, Canada',
                 ' Exim Bank (Bangladesh), Dhaka, Bangladesh', ' Exim Bank (Tanzania), Dar es Salaam, Tanzania',
                 ' Exim Bank (Uganda), Kampala, Uganda', ' Export Development Bank of Iran, Tehran, Iran',
                 ' Export–Import Bank of Romania, Bucharest, Romania',
                 ' Export–Import Bank of Korea, Seoul, South Korea',
                 ' Export-Import Bank of Thailand, Bangkok, Thailand',
                 ' Export-Import Bank of the Republic of China, Taipei, Taiwan',
                 ' Export–Import Bank of the United States, Washington, D.C., United States',
                 ' Express Bank, Baku, Azerbaijan', ' F.N.B. Corp, Hermitage, United States',
                 ' Faisal Islamic Bank of Egypt, Giza, Egypt', ' Faisal Islamic Bank of Sudan, Khartoum, Sudan',
                 ' Family Bank, Nairobi, Kenya', ' Far Eastern Bank, Singapore, Singapore',
                 ' Faysal Bank, Karachi, Pakistan', ' FCA Bank, Turin, Italy', ' FDH Bank, Blantyre, Madagascar',
                 ' Federal Bank, Alwaye, India', ' Federal Bank of the Middle East, Dar es Salaam, Tanzania',
                 ' FFA Private Bank, Beirut, Lebanon', ' FHB Mortgage Bank, Budapest, Hungary',
                 ' Fibabanka, Istanbul, Turkey', ' Fidelity Bank Ghana, Accra, Ghana',
                 ' Fidelity Bank Nigeria, Lagos State, Nigeria',
                 ' Fidelity Southern Corporation, Atlanta, United States', ' Fidi Toscana, Florence, Italy',
                 ' Fidobank, Kyiv, Ukraine', ' Fifth Third Bancorp, Cincinnati, United States',
                 ' FIH Erhvervsbank, Copenhagen, Denmark', ' Finance House, Abu Dhabi, United Arab Emirates',
                 ' Financial Bank Benin, Cotonou, Benin', ' Financial Institutions, Warsaw, New York, United States',
                 ' Finansbank, Istanbul, Turkey', ' Finco Services Inc, United States', ' FINECO, Brescia, Italy',
                 ' First Abu Dhabi Bank, Abu Dhabi, United Arab Emirates',
                 ' First Alliance Bank Zambia Limited, Lusaka, Zambia',
                 ' First American International Bank, Brooklyn, United States',
                 ' First Bancorp, Damariscotta, United States',
                 ' First BanCorp, San Juan, Puerto Rico|San Juan, Puerto Rico',
                 ' First Bancorp, Troy, North Carolina, United States',
                 ' First Bancorp, Lebanon, Virginia, United States', ' First Bank of Nigeria, Lagos, Nigeria',
                 ' First Busey Corporation, Champaign, United States', ' First Business Bank (FBB), Athens, Greece',
                 ' First Citizens BancShares, Dyersburg, United States',
                 ' First Citizens BancShares, Raleigh, United States',
                 ' First Citizens Bank, Port of Spain, Trinidad and Tobago',
                 ' First City Monument Bank, Lagos, Nigeria', ' First Community Bank, Nairobi, Kenya',
                 ' First Community Bancshares, Killeen, Texas, United States',
                 ' First Community Bancshares, Bluefield, United States',
                 ' First Financial Bancorp, Cincinnati, United States',
                 ' First General Bank, Rowland Heights, United States',
                 ' First Guaranty Bancshares, Hammond, United States',
                 ' First Gulf Bank, Abu Dhabi, United Arab Emirates',
                 ' First Horizon National Corporation, Memphis, United States',
                 ' First International Bank of Israel (FIBI), Tel Aviv, Israel',
                 ' First Interstate BancSystem, Billings, United States', ' First Investment Bank, Sofia, Bulgaria',
                 ' First Investment Bank (PJSC), Kyiv, Ukraine', ' First Merchant Bank, Blantyre, Malawi',
                 ' First Merchants Corporation, Muncie, United States', ' First Midwest Bancorp, Itasca, United States',
                 ' First MicroFinance Bank (Afghanistan), Afghanistan',
                 ' First MicroFinance Bank (Tajikistan), Tajikistan ',
                 ' First National Bank of Botswana, Gaborone, Botswana',
                 ' First National Bank of Omaha, New York, United States',
                 ' First Nations Bank of Canada, Saskatoon, Canada',
                 ' First National of Nebraska, Omaha, United States',
                 ' First International Bank (Liberia), Monrovia, Liberia',
                 ' First National Bank (South Africa), Botswana, South Africa',
                 ' First Niagara Financial Group, Buffalo, United States',
                 ' First Security Islami Bank Limited, Dhaka, Bangladesh', ' First Somali Bank, Mogadishu, Somalia',
                 ' First Ukrainian International Bank, Kyiv, Ukraine', ' First Westroads Bank, Omaha, United States',
                 ' First Women Bank Limited, Karachi, Pakistan ',
                 ' FirstCaribbean International Bank, St Michael, Barbados',
                 ' FirstMerit Corporation, Akron, United States', ' FirstRand, Sandton, South Africa',
                 ' Fondo Común, Caracas, Venezuela',
                 " Foreign Trade Bank of the Democratic People's Republic of Korea, Pyongyang, North Korea",
                 ' Forex Bank, Stockholm, Sweden', ' Fonkoze, Port-au-Prince, Haiti',
                 ' Fourth National Bank of Chicago, USA', ' Frankfurter Volksbank, Frankfurt, Germany',
                 ' Fransabank, Beirut, Lebanon', ' François Desjardins, Montreal, Canada',
                 ' Fubon Bank (Hong Kong), Hong Kong, China', ' Fubon Financial Holding Co., Taipei, Taiwan',
                 ' Fukuoka Financial Group, Fukuoka, Japan', ' Fulton Financial Corp, Lancaster, United States',
                 ' Future Bank, Manama, Bahrain', ' Fürst Fugger Privatbank, Augsburg, Germany',
                 " Fürstlich Castell'sche Bank, Würzburg, Germany", ' Garanti Bank, Levent, Turkey',
                 ' Garanti BBVA, Istanbul, Turkey', ' Gazprombank, Moscow, Russia', ' GCB Bank, Accra, Ghana',
                 ' GEFA Bank, Wuppertal, Germany', ' Geniki Bank, Athens, Greece', ' Getin Bank, Warsaw, Poland',
                 ' Getin Noble Bank, Warsaw, Poland', ' GFH BSC, Bahrain ', ' GFH Financial Group, Manama, Bahrain',
                 ' Ghana Commercial Bank, Accra, Ghana', ' Ghavamin Bank, Tehran, Iran',
                 ' Giro Commercial Bank, Nairobi, Kenya', ' Girobank, Willemstad, Netherlands Antilles',
                 ' Glacier Bancorp, Kalispell, United States', ' Glarner Kantonalbank, Glarus, Switzerland',
                 ' GLS Bank, Bochum, Germany', ' Global Bank Liberia, Monrovia, Liberia',
                 ' Global Commerce Bank, Georgia, United States', ' Golden Bank, Housten, United States',
                 ' Golomt Bank, Ulaanbataar, Mongolia', ' Government Savings Bank, Bangkok, Thailand',
                 ' Graubundner Kantonalbank, Chur, Switzerland', ' Grameen Bank, Dhaka, Bangladesh',
                 ' Greater Bank, Hamilton, Australia', ' Grong Sparebank, Grong, Norway',
                 ' Groupe Banque Populaire, Paris, France', ' Groupe BPCE, Paris, France',
                 " Groupe Caisse d'Epargne, Paris, France", ' Grupo Financiero Banamex, Mexico City, Mexico',
                 ' Grupo Financiero Banorte, Mexico City, Mexico',
                 ' Grupo Financiero BBVA Bancomer, Mexico City, Mexico',
                 ' Grupo Financiero Galicia, Buenos Aires, Argentina',
                 ' Grupo Financiero Santander México, Mexico City, Mexico', ' Guaranty Trust Bank, Lagos, Nigeria',
                 ' Guaranty Trust Bank (Kenya), Nairobi, Kenya', ' Guaranty Trust Bank (Rwanda), Kigali, Rwanda',
                 ' Guaranty Trust Bank (Uganda), Kampala, Uganda', ' Guardian Bank, Nairobi, Kenya',
                 ' Gulf African Bank, Nairobi, Kenya', ' Gulf Bank of Kuwait, Kuwait City, Kuwait',
                 ' Gulf Commercial Bank, Baghdad, Iraq', ' Gulf Finance House, Manama, Bahrain',
                 ' Gulf International Bank, Manama, Bahrain', ' Habib Bank AG Zurich, Zurich, Switzerland',
                 ' Habib Metropolitan Bank, Karachi, Pakistan', ' HabibMetro, Karachi, Pakistan',
                 ' Halk Bank, Ashgabat, Turkmenistan', ' Halkbank a.d., Belgrade, Serbia',
                 ' Halk Bankası, Ankara, Turkey', ' Halyk Bank, Almaty, Kazakhstan',
                 ' Hamburger Sparkasse, Hamburg, Germany', ' Hana Financial Group, Seoul, South Korea',
                 ' Hang Seng Bank, Hong Kong, Hong Kong', ' Hanseatic Bank, Hamburg, Germany',
                 ' Harbin Bank, Harbin, China', ' Hatton National Bank, Colombo, Sri Lanka',
                 ' Hauck & Aufhäuser, Frankfurt, Germany', ' HBL Pakistan, Habib Bank Limited Karachi, Pakistan',
                 ' HBOS, Edinburgh, United Kingdom', ' HBZ Bank, Durban, South Africa', ' HDFC Bank, Mumbai, India',
                 ' Helaba, Frankfurt am Main, Germany', ' Helgeland Sparebank, Mosjøen, Norway',
                 ' Hellenic Bank, Strovolos, Cyprus', ' Hello bank!, Paris, France',
                 ' Heritage Bank, Queensland, Australia', ' Himalayan Bank, Kathmandu, Nepal',
                 ' Hoerner Bank, Heilbronn, Germany', ' Høland og Setskog Sparebank, Bjørkelangen, Norway',
                 ' Hokkaido Bank, Sapporo, Japan', ' Hokkoku Bank, Kanazawa, Japan', ' Hokuriku Bank, Toyama, Japan',
                 ' Hokuto Bank, Akita, Japan', ' Centennial Bank|Home Bancshares, Conway, United States',
                 ' Home Credit and Finance Bank, Moscow, Russia', ' Home Credit & Finance Bank, Moscow, Russia',
                 ' Home Credit Bank Belarus, Minsk, Belarus', ' Home Credit Bank Kazakhstan, Almaty, Kazakhstan',
                 ' Home Credit Czech Republic, Brno, Czech Republic', ' Home Credit Slovakia, Piestany, Slovakia',
                 ' Hong Leong Bank, Kuala Lumpur, Malaysia', ' Horizon Bancorp, Michigan City, United States',
                 ' Housing Finance Company of Kenya, Nairobi, Kenya', ' Housing Financing Fund, Reykjavik, Iceland',
                 ' Hrvatska poštanska banka, Zagreb, Croatia', ' HSBC Bank, London, United Kingdom',
                 ' HSBC Bank Argentina, Buenos Aires, Argentina', ' HSBC Bank Australia, Sidney, Australia',
                 ' HSBC Bank Bermuda, Hamilton, Bermuda', ' HSBC Bank Canada, Vancouver, Canada',
                 ' HSBC Bank (Chile), Santiago, Chile', ' HSBC Bank Egypt, Cairo, Egypt',
                 ' HSBC Bank Malaysia, Kuala Lumpur, Malaysia', ' HSBC Bank Malta, Valletta, Malta',
                 ' HSBC Bank Middle East, Saint Helier, Jersey', ' HSBC Bank Polska, Warsaw, Poland',
                 ' HSBC Bank (Taiwan), Taipei, Taiwan', ' HSBC Bank (Turkey), Istanbul, Turkey',
                 ' HSBC Bank USA, New York, United States', ' HSBC France, Paris, France',
                 ' HSBC Holdings, London, United Kingdom', ' HSBC Saudi Arabia, Riyadh, Saudi Arabia',
                 ' HSBC Sri Lanka, Colombo, Sri Lanka', ' HSBC Trinkaus, Düsseldorf, Germany',
                 ' HSBC México, Mexico City, Mexico', ' HSH Nordbank, Hamburg, Germany',
                 ' Hua Xia Bank, Beijing, China', ' Hudson City Bancorp, Paramus, United States',
                 ' Hume Bank, Albury, Australia', ' Hungarian National Bank, Budapest, Hungary',
                 ' Huntington Bancshares, Columbus, United States', ' Hypo Alpe Adria Bank Beograd, Belgrade, Serbia',
                 ' Hypo Alpe Adria Bank Croatia, Zagreb, Croatia',
                 ' Hypo Alpe Adria Bank dd Banja Luka, Mostar, Bosnia-Herzegovina',
                 ' Hypo Alpe Adria Bank dd Mostar, Mostar, Bosnia-Herzegovina',
                 ' Hypo Alpe Adria Bank International, Klagenfurt, Austria',
                 ' Hypo Alpe Adria Bank Italy, Unknown, Italy',
                 ' Hypo Alpe Adria Bank Montenegro, Podgorica, Montenegro',
                 ' Hypo Alpe Adria Bank Slovenia, Ljubljana, Slovenia', ' Hypo Noe Landesbank, Sankt Pölten, Austria',
                 ' Hypo Real Estate Holding, Munich, Germany', ' HypoVereinsbank, Munich, Germany',
                 ' Ibercaja Banco, Zaragoza, Spain', ' ICBC Turkey, Istanbul, Turkey', ' ICCREA Holding, Roma, Italy',
                 ' ICICI Bank, Mumbai, India', ' ICICI Bank#ICICI Bank Canada|ICICI Bank Canada, Toronto, Canada',
                 ' IDBI, Mumbai, India', ' Idea Bank, Warsaw, Poland', ' Idea Bank (Romania), Bucharest, Romania',
                 ' IDFC First Bank, Mumbai, India', ' IFIC Bank, Dhaka, Bangladesh',
                 ' IKB Deutsche Industriebank, Düsseldorf, Germany', ' İlbank, Ulus, Turkey',
                 ' IMB Banking & Financial Services, Wollongong, Australia', ' Imexbank, Odessa, Ukraine',
                 ' Imperial Bank Limited, Nairobi, Kenya', ' Inbursa, Mexico City, Mexico',
                 ' Indian Bank, Chennai, India', ' Indian Overseas Bank, Chennai, India',
                 ' Indre Sogn Sparebank, Årdalstangen, Norway', ' Indo-Zambia Bank Limited, Lusaka, Zambia',
                 ' IndusInd Bank, Mumbai, India', ' Industrial and Commercial Bank of China (Asia), Hong Kong, China',
                 ' Industrial and Commercial Bank of China (Macau), Macau, China',
                 ' Industrial Bank (China), Fuzhou, China', ' Industrial Bank of Iraq, Baghdad, Iraq',
                 ' Industrial Bank of Korea, Seoul, South Korea', ' Industrial Bank of Kuwait, Safat, Kuwait',
                 ' Industrial Bank (Washington D.C.), Washington D.C., United States',
                 ' Industrial Development Bank, Karachi, Pakistan', ' InecoBank, Yerevan, Armenia',
                 ' ING Australia, Sydney, Australia', ' ING Bank, Amsterdam, Netherlands',
                 ' ING Bank Śląski, Katowice, Poland', ' ING Belgium, Brussels, Belgium',
                 ' ING DiBa, Frankfurt am Main, Germany', ' ING Group, Amsterdam, Netherlands',
                 ' ING Vysya Bank, Bangalore, India', ' Insinger de Beaufort, Luxembourg, Luxembourg',
                 ' Innwa Bank, Yangon, Myanmar', ' Istituto per il Credito Sportivo, Rome, Italy',
                 ' Inter-American Development Bank, Washington D,C, United States', ' Interbank, Kyiv, Ukraine',
                 ' Interbank Burundi, Bujumbura, Burundi', ' Intercontinental Bank, Lagos, Nigeria',
                 ' International Bancshares Corp, Laredo, United States',
                 ' International Bank of Azerbaijan (IBA), Baku, Azerbaijan',
                 ' International Bank of Azerbaijan-Georgia, Tbilisi, Georgia',
                 ' International Bank of Qatar, Doha, Qatar',
                 ' Internationales Bankenhaus Bodensee, Friedrichshafen, Germany',
                 ' International Investment Bank, Budapest, Hungary', ' Intesa Sanpaolo, Torino, Italy',
                 ' Intesa Sanpaolo Bank (Albania), Tirana, Albania', ' Intesa Sanpaolo Bank Ireland, Dublin, Ireland',
                 ' Intesa Sanpaolo Bank Romania, Arad, Romania',
                 ' Intesa Sanpaolo Banka Bosnia/Herzegovina, Sarajevo, Bosnia-Herzegovina',
                 ' Investcorp, Manama, Bahrain', ' Investec Bank, London, United Kingdom',
                 ' Investitionsbank Berlin, Berlin, Germany', ' Investment Bank of Greece, Athens, Greece',
                 ' Investors Bank, New Jersey, United States', ' Investrust Bank, Lusaka, Zambia',
                 ' Iraqi Islamic Bank, Baghdad, Iraq', ' Iranian-European Bank, Hamburg, Germany',
                 ' Iran-Venezuela Bi-National Bank, Tehran, Iran', ' Isbank, Moscow, Russia',
                 ' Islamic Bank of Britain, Birmingham, United Kingdom',
                 ' Islamic Cooperation Investment Bank, Tehran, Iran',
                 ' Islamic International Arab Bank, Amman, Jordan', ' Islandsbanki, Reykjavik, Iceland',
                 ' Israel Discount Bank, Tel Aviv, Israel',
                 ' Istituto Centrale delle Banche Popolari Italiane, Milano, Italy',
                 ' Istrobanka, Bratislava, Slovakia', ' İş Yatırım, Istanbul, Turkey',
                 ' Itaú Corpbanca, Santiago, Chile', ' Itau Unibanco Holding S.A., São Paulo, Brazil',
                 ' Ithmaar Bank, Manama, Bahrain', ' Ivory Bank, Juba, South Sudan', ' IWBank, Milan, Italy',
                 ' I&M Bank Limited, Nairobi, Kenya', ' I&M Bank Tanzania Limited, Dar es Salaam, Tanzania',
                 ' I&M Bank Rwanda Limited, Kigali, Rwanda', ' Jæren Sparebank, Bryne, Norway',
                 ' Jamii Bora Bank, Nairobi, Kenya', ' Jammu & Kashmir Bank, Srinagar, India',
                 ' Jamuna Bank, Dhaka, Bangladesh', ' Janata Bank, Dhaka, Bangladesh',
                 ' Janata Bank Nepal Limited, Kathmandu, Nepal', ' Japan Post Bank, Tokyo, Japan',
                 ' Jefferies Group, New York, United States', ' Jio Payments Bank, Mumbai, India',
                 ' Johnson Financial Group, Racine, United States',
                 ' Joint Stock Commercial Bank for Foreign Trade of Vietnam, Hanoi, Vietnam',
                 ' Jordan Ahli Bank, Amman, Jordan', ' Jordan Kuwait Bank, Amman, Jordan', ' Joyo Bank, Mito, Japan',
                 ' JP Morgan, Frankfurt am Main, Germany', ' JP Morgan Chase & Co, New York, United States',
                 ' JS Bank, Karachi, Pakistan', ' Jubanka, Belgrade, Serbia', ' Jubilee Bank, Dhaka, Bangladesh',
                 ' JUBMES banka, Belgrade, Serbia', ' Julian Hodge Bank, Cardiff, United Kingdom',
                 ' Julius Baer Group, Zurich, Switzerland', ' Juniper Advisory, Chicago, United States',
                 ' Jyske Bank, Silkeborg, Denmark', ' Kabul Bank, Kabul, Afghanistan',
                 ' Kanbawza Bank, Yangon, Myanmar', ' Kanto Tsukuba Bank, Tsuchiura City, Japan',
                 ' Kapital Bank, Baku, Azerbaijan', ' Karafarin Bank, Tehran, Iran',
                 ' Kardan Investment Bank, Tehran, Iran', ' Karmasangsthan Bank, Dhaka, Bangladesh',
                 ' Karnataka Bank, Mangalore, India', ' Karur Vysya Bank, Karur, India',
                 ' KASB Bank, Karachi, Pakistan', ' Kasikornbank, Bangkok, Thailand',
                 ' Kazinvestbank, Almaty, Kazakhstan', ' Kazkommertsbank, Almaty, Kazakhstan',
                 ' KB Financial Group Inc, Seoul, South Korea', ' KBC Bank, Brussels, Belgium',
                 ' KBC Bank Ireland, Dublin, Ireland', ' KCB Bank Kenya Limited, Nairobi, Kenya',
                 ' KCB Bank Rwanda Limited, Kigali, Rwanda', ' KBC Group, Brussels, Belgium',
                 ' KCB Bank South Sudan Limited, Juba, South Sudan', ' KCB Bank Uganda Limited, Kampala, Uganda',
                 ' KD-Bank, Dortmund, Germany', ' Kempen & Co, Amsterdam, Netherlands',
                 ' Kenya Commercial Bank, Nairobi, Kenya', ' KeyBank, Cleveland, United States',
                 ' KeyCorp, Cleveland, United States', ' Keytrade Bank, Brussels, Belgium',
                 ' KfW|KfW Bank, Frankfurt, Germany', ' KfW IPEX-Bank, Frankfurt, Germany', ' KGI Bank, Taipei, Taiwan',
                 ' Khaleeji Commercial Bank, Manama, Bahrain', ' Khushhali Bank, Islamabad, Pakistan',
                 ' Kiatnakin Bank, Bangkok, Thailand', ' Kiwibank, Wellington, New Zealand',
                 ' Klakki, Reykjavik, Iceland ', ' Komercni banka, Prague, Czech Republic',
                 ' Komercijalna banka, Belgrade, Serbia', ' Komercijalna banka Budva, Budva, Serbia',
                 ' Komerční banka Bratislava, Bratislava, Slovakia', ' Korea Development Bank, Seoul, South Korea',
                 ' Korea Exchange Bank, Seoul, South Korea', ' Kotak Mahindra Bank, Mumbai, India',
                 ' KredoBank, Lviv, Ukraine', ' Kreissparkasse Ludwigsburg, Ludwigsburg, Germany',
                 ' Krung Thai Bank, Bangkok, Thailand', ' Kumari Bank, Kathmandu, Nepal',
                 ' Kumho Investment Bank, South Korea ', ' Kutxabank, Bilbao, Spain',
                 ' Kuwait Finance House, Safat, Kuwait', ' Kuwait International Bank, Safat, Kuwait',
                 ' K&H Bank, Budapest, Hungary', ' La Banque Postale, Paris, France', ' La Caixa, Valencia, Spain',
                 ' Laiki Bank, Thessaloniki, Greece', ' Lakshmi Vilas Bank, Karur, India',
                 ' Land Bank of Taiwan, Taipei, Taiwan', ' Landesbank Baden-Württemberg (LBBW), Stuttgart, Germany',
                 ' Landesbank Berlin Holding (LBB), Berlin, Germany', ' Landesbank Saar, Saarbrücken, Germany',
                 ' Landkreditt Bank, Oslo, Norway', ' Landsbankinn, Reykjavik, Iceland',
                 ' Landwirtschaftliche Rentenbank, Frankfurt am Main, Germany',
                 ' Lansforsakringar Bank, Stockholm, Sweden', ' Latvijas Krājbanka, Riga, Latvia',
                 ' Laurentian Bank of Canada, Montreal, Canada', ' Lauritzen Corporation, Omaha, United States',
                 ' Laxmi Bank, Kathmandu, Nepal', ' LCL S.A., Lyon, France', ' Lebanese Swiss Bank, Beirut, Lebanon',
                 ' Leeds Building Society, Leeds, United Kingdom', ' Letshego Bank Tanzania, Dar es Salaam, Tanzania',
                 ' LGT Group, Vaduz, Liechtenstein', ' Liberbank, Madrid, Spain',
                 ' Liberty Bank (Georgia), Tbilisi, Georgia', ' Libyan Foreign Bank, Tripoli, Libya',
                 ' Liechtensteinische Landesbank, Vaduz, Liechtenstein',
                 ' Lloyds Banking Group, London, United Kingdom', ' Lombard Bank, Valletta, Malta ',
                 ' London Scottish Bank, Manchester, United Kingdom', ' Luminor Bank, Tallinn, Estonia',
                 ' Luzerner Kantonalbank, Lucerne, Switzerland', ' M&T Bank Corporation, Buffalo, United States',
                 ' M.M. Warburg & Co., Hamburg, Germany', ' Macau Chinese Bank, Macau, Macao',
                 ' Mackinac Financial Corporation, Traverse City, United States', ' Macquarie Group, Sydney, Australia',
                 " Maduro & Curiel's Bank, Willemstad, Netherlands Antilles", ' MagNet Bank, Budapest, Hungary ',
                 ' Makedonska banka, Skopje, Republic of Macedonia', ' Malayan Banking Berhad, Kuala Lumpur, Malaysia',
                 ' Manas Bank, Kyrgyzstan ', ' Manulife Bank of Canada, Waterloo, Canada',
                 ' Maple Bank, Frankfurt, Germany', ' Mashreqbank, Dubai, United Arab Emirates',
                 ' MauBank, Ebene Cybercity, Mauritius', ' Mauritius Commercial Bank, Port Louis, Mauritius',
                 ' Maybank, Kuala Lumpur, Malaysia', ' mBank, Warsaw, Poland', ' MBCA Bank, Harare, Zimbabwe',
                 ' MCB Bank, Lahore, Pakistan', ' MCB Bank Limited, Lahore, Pakistan',
                 ' MCB Madagascar, Antananarivo, Madagascar', ' MCB Islamic Bank Limited, Lahore, Pakistan',
                 ' MDM Bank, Novosibirsk, Russia', ' ME Bank, Melbourne, Australia', ' Mediobanca, Milano, Italy',
                 ' Mediocredito Italiano, Milan, Italy', ' Mediterranean Bank, Valletta, Malta',
                 ' MeesPierson, Rotterdam, Netherlands', ' Meem (bank), Manama, Bahrain',
                 ' Meezan Bank, Karachi, Pakistan', ' MeDirect Bank Malta, Sliema, Malta',
                 ' Mega Bank Nepal Limited, Nepal, India', ' Mega International Commercial Bank, Taipei, Taiwan',
                 ' Meghna Bank, Dhaka, Bangladesh', ' Mekong Housing Bank, Ho Chi Minh City, Vietnam',
                 ' Melhus Sparebank, Melhus, Norway', ' Mellat Bank, Yerevan, Armenia',
                 ' Mellat Investment Bank, Tehran, Iran', ' Members Equity Bank, Melbourne, Australia',
                 ' Mercantil Servicios Financieros, Caracas, Venezuela',
                 ' Mercantile Bank (Bangladesh), Dhaka, Bangladesh',
                 ' Mercantile Bank Limited, South Africa, Sandown, Gauteng, South Africa',
                 ' Mercantile Discount Bank, Tel Aviv, Israel', ' Mercedes-Benz Bank, Stuttgart, Germany',
                 ' Merck Finck & Co, Munich, Germany', ' Merkur Bank, Munich, Germany', ' Metbank, Harare, Zimbabwe',
                 ' Metrocorp Bancshares, Houston, United States', ' Metzler Bank, Frankfurt, Germany',
                 ' Mendelssohn & Co., Berlin, Germany', ' MEVAS Bank, Hong Kong, China',
                 ' Michinoku Bank, Aomori, Japan', ' Middle East Bank (Kenya), Nairobi, Kenya',
                 ' MidWestOne Financial Group, Iowa City, United States', ' Migros Bank, Zurich, Switzerland',
                 ' Millennium BCP, Lisbon, Portugal', ' Mir Business Bank, Moscow, Russia',
                 ' Mitsubishi UFJ Financial Group, Tokyo, Japan', ' Mizuho Corporate Bank, Tokyo, Japan',
                 ' Mizuho Financial Group, Tokyo, Japan', ' MKB Bank, Budapest, Hungary ',
                 ' MKB Unionbank, Sofia, Bulgaria', ' Modhumoti Bank Limited, Bangladesh ',
                 ' Moldova Agroindbank, Chisinau, Moldova', ' M Oriental Bank, Nairobi, Kenya',
                 ' Monetary Authority of Brunei Darussalam, Bandar Seri Begawan, Brunei',
                 ' Monet Investment Bank, Ulaanbaatar, Mongolia', ' Montepio (bank), Lisbon, Portugal',
                 ' Moody Bancshares, Galveston, United States', ' Mora Banc Grup, Andorra la Vella, Andorra',
                 ' Morgan Stanley, New York, United States', ' MP Bank, Reykjavik, Iceland',
                 ' MPS Capital Services, Florence, Italy', ' Münchner Bank, Munich, Germany',
                 ' Municipal Bank of Rosario, Rosario, Argentina', ' MUFG Bank, Tokyo, Japan',
                 ' MUFG Union Bank, New York, United States', ' Mutiara Bank, Jakarta, Indonesia',
                 ' Mutual Trust Bank Limited, Dhaka, Bangladesh', ' Myanma Apex Bank, Nay Pyi Taw, Myanmar',
                 ' Myanma Economic Bank, Naypyidaw, Myanmar', ' Myanma Foreign Trade Bank, Yangon, Myanmar',
                 ' Myanma Investment and Commercial Bank, Yangon, Myanmar', ' MyState Limited, Hobart, Australia',
                 ' N M Rothschild & Sons, London, United Kingdom', ' N26 (bank)|N26, Berlin, Germany',
                 ' Nabil Bank, Kathmandu, Nepal', ' Nadra Bank, Kyiv, Ukraine', ' Nainital Bank, Nainital, India',
                 ' Nanto Bank, Nara, Japan', ' Nanyang Commercial Bank, Hong Kong, China',
                 ' Nathan Bostock, Maidstone, England', ' National Agricultural Cooperative Federation, South Korea ',
                 ' National Australia Bank, Melbourne, Australia',
                 ' National Australia Bank (180 Queen Street), Queensland, Australia',
                 ' National Australia Bank (308 Queen Street), Queensland, Australia',
                 ' National Bank, Dhaka, Bangladesh', ' National Bank, Essen, Germany',
                 ' National Bank Limited, Bengali, Bangladesh',
                 ' National Bank of Abu Dhabi, Abu Dhabi, United Arab Emirates',
                 ' National Bank of Angola, Luanda, Angola', ' National Bank of Bahrain, Manama, Bahrain',
                 ' National Bank of Belize, Belmopan, Belize', ' National Bank of Canada, Montreal, Canada',
                 ' National Bank of Commerce (Tanzania), Dar es Salaam, Tanzania',
                 ' National Bank of Dominica, Roseau, Dominica', ' National Bank of Egypt, Cairo, Egypt',
                 ' National Bank of Fujairah, Fujairah, United Arab Emirates',
                 ' National Bank of Georgia, Tbilisi, Georgia', ' National Bank of Greece, Athens, Greece',
                 ' National Bank of Greece, NBG Malta, Sliema, Malta', ' National Bank of Kenya, Nairobi, Kenya',
                 ' National Bank of Kazakhstan, Almaty, Kazakhstan ', ' National Bank of Kuwait, Safat, Kuwait',
                 ' National Bank of Liechtenstein, Vaduz, Liechtenstein', ' National Bank of Malawi, Blantyre, Malawi',
                 ' National Bank of Moldova, Chisinau, Moldova', ' National Bank of Oman, Ruwi, Oman',
                 ' National Bank of Pakistan, Karachi, Pakistan', ' National Bank of Rwanda, Kigali, Rwanda',
                 ' National Bank of Samoa, Apia, Samoa', ' National Bank of Slovakia, Bratislava, Slovakia',
                 ' National Bank of Sudan, Khartoum, Sudan', ' National Bank of Tajikistan, Dushanbe, Tajikistan',
                 ' National Bank of the Republic of Belarus, Minsk, Belarus',
                 ' National Bank of the Kyrgyz Republic, Bishkek, Kyrgyz Republic',
                 ' National Bank of Ukraine, Kyiv, Ukraine', ' National Bank of Uzbekistan, Tashkent, Uzbekistan',
                 ' National Bank of Vanuatu, Port Vila, Vanuatu', ' National Bank of Yemen, Aden, Yemen',
                 ' National Commercial Bank, Al Bayda, Libya',
                 ' National Commercial Bank (Saudi Arabia)|National Commercial Bank, Jeddah, Saudi Arabia',
                 ' National Development Bank of Sri Lanka, Colombo, Sri Lanka',
                 ' National Industrial Credit Bank, Nairobi, Kenya', ' National Investment Bank, Accra, Ghana',
                 ' National Microfinance Bank, Dar es Salaam, Tanzania', ' National Reserve Bank, Moscow, Russia',
                 ' National Savings Bank (Sri Lanka), Colombo, Sri Lanka',
                 ' National Westminster Bank, London, United Kingdom', ' Nations Trust Bank, Colombo, Sri Lanka',
                 ' Nationwide Building Society, Northampton, United Kingdom', ' Natixis, Paris, France',
                 ' NBD Bank, Nizhny Novgorod, Russia', ' NBS Bank, Blantyre, Malawi',
                 ' NBT Bancorp, Norwich, United States', ' NCC Bank, Dhaka, Bangladesh',
                 ' Nedbank Group, Johannesburg, South Africa', ' Nederlandse Waterschapsbank, The Hague, Netherlands',
                 ' Nepal Bank, Kathmandu, Nepal', ' Nepal Bangladesh Bank, Kathmandu, Nepal ',
                 ' Nepal Investment Bank, Kathmandu, Nepal', ' Nepal Rastra Bank, Kathmandu, Nepal',
                 ' Nepal SBI Bank, Kathmandu, Nepal',
                 ' Netherlands Development Finance Company, The Hague, Netherlands',
                 ' New Bank of Santa Fe, Santa Fe Province, Argentina',
                 ' Newcastle Building Society, Newcastle upon Tyne, United Kingdom',
                 ' Newcastle Permanent Building Society, Newcastle, Australia',
                 ' New York Community Bancorp, Westbury, United States', ' New Kabul Bank, Kabul, Afghanistan',
                 ' Nexi, Milan, Italy', ' NIB Bank, Karachi, Pakistan', ' NIBC Bank, The Hague, Netherlands',
                 ' NIC Bank Group, Nairobi, Kenya', ' NIC Bank Tanzania, Dar es Salaam, Tanzania',
                 ' Nicolet Bankshares, Green Bay, United States', ' Nile Commercial Bank, Juba, South Sudan',
                 ' NLB Group, Ljubljana, Slovenia', ' NMB Bank Nepal, Kathmandu, Nepal', ' Nomos Bank, Moscow, Russia',
                 ' Nomura Holdings, Tokyo, Japan', ' Nonghyup Bank, Seoul, South Korea',
                 ' Noor Bank, Dubai, United Arab Emirates', ' Norddeutsche Landesbank (NORD LB), Hanover, Germany',
                 ' Nordea Bank Finland, Helsinki, Finland', ' Nordea Bank Norge, Oslo, Norway',
                 ' Nordea Bank Polska, Gdynia, Poland', ' Nordlandsbanken (NB), Bodø, Norway',
                 ' Norges Bank, Oslo, Norway', ' Norinchukin Bank, Tokyo, Japan', ' Norisbank, Bonn, Germany',
                 ' Norne Securities, Oslo, Norway', ' North Valley Bancorp, Redding, United States',
                 ' Northeast Bancorp, Lewiston, United States', ' Northern Trust Corporation, Chicago, United States',
                 ' Norvik Banka, Riga, Latvia',
                 ' Norwich and Peterborough Building Society, Peterborough, United Kingdom',
                 ' Nottingham Building Society, Nottingham, United Kingdom',
                 ' Nova Ljubljanska Banka (NLB), Ljubljana, Slovenia', ' Novikombank, Moscow, Russia',
                 ' Novo Banco, Lisbon, Portugal', ' NRB Bank, Dhaka, Bangladesh', ' NRW.BANK, Düsseldorf, Germany',
                 ' Nuevo Banco de Santa Fe, Santa Fe, Argentina', ' Nurol Bank, Maslak, Turkey',
                 ' Nykredit, Copenhagen, Denmark', ' Oberbank, Linz, Austria', ' OCBC Wing Hang Bank, Hong Kong, China',
                 ' Ocean Bank, Hai Duong, Vietnam', ' Ocean Bankshares, Miami, United States',
                 ' Oceanic Bank, Abuja, Nigeria', ' ODDO BHF, Paris, France',
                 ' OFG Bancorp, San Juan, Puerto Rico|San Juan, Puerto Rico',
                 ' Old National Bancorp, Evansville, United States', ' Oldenburgische Landesbank, Oldenburg, Germany',
                 ' Oman Arab Bank, Ruwi, Oman', ' Omni Bank (California), Alhambra, United States',
                 ' One Bank Limited, Dhaka, Bangladesh', ' Openbank, Madrid, Spain',
                 ' OP Financial Group, Helsinki, Finland', ' OP-Pohjola Group, Helsinki, Finland',
                 ' Orienbank, Dushanbe, Tajikistan', ' Orient Bank, Kampala, Uganda',
                 ' Orient Bank, Ho Chi Minh City, Vietnam', ' Oriental Bank of Commerce, New Delhi, India',
                 ' Oriental Commercial Bank, Nairobi, Kenya', ' Oromia International Bank, Addis Ababa, Ethiopia',
                 ' Ostsächsische Sparkasse Dresden, Dresden, Germany',
                 ' Otkritie Financial Corporation, Moscow, Russia', ' Otkritie FC Bank, Moscow, Russia',
                 ' OTP Bank, Budapest, Hungary', ' Oversea Chinese Banking Corporation (OCBC), Singapore, Singapore',
                 ' Pacific & Western Bank of Canada, London, Canada',
                 ' Pacific Capital Bancorp, Santa Barbara, United States',
                 ' Pacific Global Bank, Chicago, United States',
                 ' Pacific Mercantile Bancorp, Costa Mesa, United States',
                 ' Pacific Premier Bancorp, Irvine, United States', ' Pacwest Bancorp, San Diego, United States',
                 ' Padma Bank Limited, Dhaka, Bangladesh', ' Pan Asia Banking Corporation PLC, Colombo, Sri Lanka',
                 ' Paramount Universal Bank, Nairobi, Kenya', ' Parsian Bank, Tehran, Iran',
                 ' PASHA Bank Georgia, Tbilisi, Georgia', ' Pashtany Bank, Kabul, Afghanistan',
                 ' Patria Bank, Bucharest, Romania', ' Pax-Bank, Cologne, Germany',
                 ' Peoples, Colorado Springs, United States',
                 ' Peoples Bancorp|Peoples Bancorp of North Carolina, Newton, United States',
                 " People's Bank (Sri Lanka), Colombo, Sri Lanka", " People's Bank of Zanzibar, Zanzibar, Tanzania",
                 " People's Savings Bank (Celje), Celje, Slovenia",
                 ' Persia International Bank, London, United Kingdom',
                 ' Philippine Bank of Communications, Makati City, Philippines',
                 ' Philippine National Bank, Pasay, Philippines', ' Philippine Veterans Bank, Makati City, Philippines',
                 ' Philtrust Bank, Manila, Philippines', ' Phnom Penh Commercial Bank, Phnom Penh, Cambodia',
                 ' Ping An Bank, Shenzhen, China', ' Pinnacle Financial Partners, Nashville, United States',
                 ' Piraeus Bank Group, Athens, Greece', ' Piraeus Bank Romania, Bucharest, Romania',
                 ' PKO Bank Polski, Warsaw, Poland', ' PlainsCapital Corporation, Dallas, United States',
                 ' P&N Bank, Perth, Australia', ' PNB Banka, Riga, Latvia',
                 ' PNC Financial Services Group, Pittsburgh, United States', ' Polaris Bank Limited, Lagos, Nigeria',
                 ' Police Bank, Sydney, Australia',
                 ' Popular, Inc., Hato Rey, San Juan, Puerto Rico|San Juan, Puerto Rico',
                 ' Portuguese Commercial Bank, Porto, Portugal ', ' Post Bank (Russia), Moscow, Russia',
                 ' Post Bank of Iran, Tehran, Iran', ' Postal Savings Bank of China, Beijing, China',
                 ' Poste Italiane, Rome, Italy', ' Poštová banka, Bratislava, Slovakia',
                 ' Prabhu Bank, Kathmandu, Nepal', ' Pravex Bank, Kyiv, Ukraine',
                 ' Preferred Bank, Los Angeles, United States', ' Premier Bank, Dhaka, Bangladesh',
                 " President's Choice Bank, Toronto, Canada", ' Prime Bank (Kenya), Nairobi, Kenya',
                 ' Prime Bank Limited, Dhaka, Bangladesh', ' Prime Commercial Bank, Kathmandu, Nepal',
                 ' Primorska banka, Rijeka, Croatia', ' Principality Building Society, Cardiff, United Kingdom',
                 ' PrivatBank, Riga, Latvia', ' PrivatBank, Dnipropetrovsk, Ukraine',
                 ' Privatebancorp, Chicago, United States', ' Privredna banka Zagreb, Zagreb, Croatia',
                 ' Probank, Athens, Greece', ' Probashi Kallyan Bank, Dhaka, Bangladesh',
                 ' ProCredit Bank (Romania), Bucharest, Romania', ' Prometey Bank, Yerevan, Armenia',
                 ' Prominvestbank, Kyiv, Ukraine', ' Promsvyazbank, Moscow, Russia',
                 ' Prosperity Bancshares, Houston, United States',
                 ' Provident Financial Services, Jersey City, United States',
                 ' Prva banka Crne Gore, Podgorica, Montenegro', ' PSD Bank, Bonn, Germany',
                 ' PSD Bank München, Augsburg, Germany', ' Pubali Bank, Dhaka, Bangladesh',
                 ' Public Bank, Kuala Lumpur, Malaysia', ' Public Bank (Hong Kong), Hong Kong, China',
                 ' Punjab & Sind Bank, New Delhi, India', ' Punjab National Bank, New Delhi, India',
                 ' Qarz Al-Hasaneh Mehr Iran Bank, Tehran, Iran', ' Qatar Central Bank, Doha, Qatar',
                 ' Qatar Development Bank, Doha, Qatar', ' Qatar Islamic Bank (QIB), Doha, Qatar',
                 ' Qatar National Bank, Doha, Qatar', ' QCR Holdings, Moline, United States',
                 ' Qonto (neobank), Paris, France', ' Qudos Bank, Sydney, Australia',
                 ' Quontic Bank, New York, United States', ' Queensland National Bank, Brisbane, Australia',
                 ' Rabobank Group, Utrecht, Netherlands', ' Rabobank New Zealand, Wellington, New Zealand',
                 ' Rafidain Bank, Baghdad, Iraq', ' Raiffeisen (Albania), Albania',
                 ' Raiffeisenbank (Bulgaria), Sofia, Bulgaria', ' Raiffeisenbank (Russia), Moscow, Russia',
                 ' Raiffeisen Bank Aval, Kyiv, Ukraine', ' Raiffeisen Bank International, Vienna, Austria',
                 ' Raiffeisen Bank (Romania), Bucharest, Romania',
                 ' Raiffeisenlandesbank Niederösterreich-Wien, Vienna, Austria',
                 ' Raiffeisenlandesbank Oberösterreich, Linz, Austria',
                 ' Raiffeisen Landesbank Tirol, Innsbruck, Austria', ' Raiffeisen Zentralbank, Vienna, Austria',
                 ' Rajshahi Krishi Unnayan Bank, Rajshahi, Bangladesh',
                 ' Rakbank, Ras Al-Khaimah, United Arab Emirates', ' Rasheed Bank, Baghdad, Iraq',
                 ' Rastriya Banijya Bank, Kathmandu, Nepal', ' Ratnakar Bank, Kolhapur, India',
                 ' Rawbank, Kinshasa, DRC Congo', ' Raymond James Financial, St Petersburg, Florida, United States',
                 ' RBL Bank, Mumbai, India', ' RCI Banque, Paris, France', ' Real Bank, Kharkiv, Ukraine',
                 ' Real Estate Bank of Iraq, Baghdad, Iraq', ' Refah Bank, Tehran, Iran',
                 ' Regional Australia Bank, Armidale, Australia', ' Regions Financial Corp, Birmingham, United States',
                 ' Reisebank, Frankfurt, Germany', ' Renaissance Credit, Moscow, Russia',
                 ' Renasant Bank|Renasant Corporation, Tupelo, United States', ' Renta 4 Banco, Madrid, Spain',
                 ' Republic Bancorp, Louisville, United States', ' Republic Bank, Port of Spain, Trinidad and Tobago',
                 ' Republic First Bancorp, Philadelphia, United States',
                 ' Reserve Bank of Australia, Sydney, Australia', ' Reserve Bank of India, Mumbai, India',
                 ' Reserve Bank of Malawi, Malawi', ' Reserve Bank of Zimbabwe, Harare, Zimbabwe ',
                 ' Resona Holdings, Osaka, Japan', ' Reverta, Riga, Latvia', ' RHB Bank Berhad, Kuala Lumpur, Malaysia',
                 ' Ridgewood Savings Bank, New York, United States', ' Rietumu Banka, Riga, Latvia',
                 ' Riyad Bank, Riyadh, Saudi Arabia', ' Rodovid Bank, Kyiv, Ukraine',
                 ' Rogers Communications#Rogers Bank|Rogers Bank, Toronto, Canada',
                 ' Rokel Commercial Bank, Freetown, Sierra Leone', ' Rosbank, Moscow, Russia',
                 ' Rossiya Bank, Saint Petersburg, Russia', ' Rossiysky Kredit Bank, Moscow, Russia',
                 ' Rothschild & Co, Paris, France', ' Rothschild Martin Maurel, Marseille, France',
                 ' Royal Bank of Canada, Toronto, Canada', ' Royal Bank of Scotland, Edinburgh, United Kingdom',
                 ' Royal Bank Zimbabwe, Harare, Zimbabwe', ' Royal Business Bank, Los Angeles, United States',
                 ' Royal Monetary Authority of Bhutan, Thimphu, Bhutan', ' Rupali Bank Limited, Dhaka, Bangladesh',
                 ' Russian Agricultural Bank, Moscow, Russia', ' Russian National Commercial Bank, Moscow, Russia',
                 ' Russian Standard Bank, Moscow, Russia', ' Russtroybank, Moscow, Russia',
                 ' Rwanda Development Bank, Kigali, Rwanda', '{{div col|colwidth=31em}}',
                 ' Safra National Bank of New York, New York, United States', ' Sahara Bank, Tripoli, Liberia',
                 " Sainsbury's Bank, London, United Kingdom", ' Saitama Bank, Urawa, Saitama|Urawa, Japan',
                 ' Salaam Somali Bank, Mogadishu, Somalia', ' Sal. Oppenheim, Cologne, Germany',
                 ' Saman Bank, Tehran, Iran', ' Samba Financial Group, Riyadh, Saudi Arabia',
                 ' Sampath Bank, Colombo, Sri Lanka', ' Sanasa Development Bank, Kirulapone, Sri Lanka',
                 ' Sandnes Sparebank, Sandnes, Norway', ' Santander Bank, Massachusetts, USA',
                 ' Santander Bank Polska, Wroclaw, Poland', ' Santander Brasil, São Paulo, Brazil',
                 ' Santander Consumer Bank (Deutschland), Mönchengladbach, Germany',
                 ' Santander México, Mexico City, Mexico', ' Santander UK, London, United Kingdom',
                 ' Saraswat Bank, Mumbai, India', ' Sarmayeh Bank, Tehran, Iran',
                 ' Sasfin Bank, Waverley, South Africa', ' Saudi British Bank, Riyadh, Saudi Arabia',
                 ' Sberkassa, Russia ', ' SB Sberbank of Russia JSC, Almaty, Kazakhstan', ' S-Bank, Helsinki, Finland',
                 ' Sberbank of Russia, Moscow, Russia', ' Sberbank Europe Group, Vienna, Austria',
                 ' SBM Bank Kenya Limited, Nairobi, Kenya', ' Schroders, London, United Kingdom',
                 ' Scotiabank, Toronto, Canada', ' SEB Group, Stockholm, Sweden',
                 ' Security Bank Corporation, Makati City, Philippines', ' Sekerbank, Istanbul, Turkey',
                 ' Seven Bank, Tokyo, Japan', ' Seylan Bank, Colombo, Sri Lanka',
                 ' Shahjalal Islami Bank Limited, Dhaka, Bangladesh',
                 " Shamil Bank of Yemen and Bahrain, Sana'a, Yemen", ' Shamrao Vithal Co-operative Bank, Mumbai, India',
                 ' Shanghai Commercial Bank, Hong Kong, Hong Kong',
                 ' Shanghai Commercial and Savings Bank, Taipei, Taiwan',
                 ' Shanghai Pudong Development Bank, Shanghai, China',
                 ' Sharjah Islamic Bank, Sharjah, United Arab Emirates', ' Shawbrook Bank, Manchester, United Kingdom',
                 ' Shengjing Bank, Shenyang, China', ' Shimanto Bank, Dhaka, Bangladesh',
                 ' Shinhan Bank, Seoul, South Korea', ' Shinhan Financial Group, Seoul, South Korea',
                 ' Shinsei Bank, Tokyo, Japan', ' Shizuoka Bank, Shizuoka, Japan', ' Shoko Chukin Bank, Tokyo, Japan',
                 ' Shonai Bank, Tsuruoka, Japan', ' Siam Commercial Bank, Bangkok, Thailand',
                 ' Siddhartha Bank, Kathmandu, Nepal', ' Sierra Leone Commercial Bank, Freetown, Sierra Leone',
                 ' Signature Bank, New York, United States', ' Sidian Bank, Nairobi, Kenya',
                 ' Silkbank Limited, Karachi, Pakistan', ' Sina Bank, Tehran, Iran', ' Sindh Bank, Karachi, Pakistan',
                 ' Skipton Building Society, Skipton, United Kingdom', ' Skue Sparebank, Nesbyen, Norway',
                 ' Skye Bank, Lagos, Nigeria', ' Slovenská sporiteľňa, Bratislava, Slovakia',
                 ' Slovenska zarucna a rozvojova banka, Bratislava, Slovakia', ' SNS Bank, Utrecht, Netherlands',
                 ' Social Islami Bank Limited, Dhaka, Bangladesh', ' Société Générale, Paris, France',
                 ' Société Marseillaise de Crédit, Marseille, France',
                 " Société Nationale de Crédit et d'Investissement, Luxembourg City, Luxembourg",
                 ' Societe Tunisienne de Banque, Tunis, Tunisia', ' Sofitasa, San Cristobal, Venezuela',
                 ' Sogebank, Port-au-Prince, Haiti', ' Sonali Bank, Dhaka, Bangladesh',
                 ' Soneri Bank, Lahore, Pakistan', ' South African Reserve Bank, Pretoria, South Africa',
                 ' South Bangla Agriculture and Commerce Bank Limited, Dhaka, Bangladesh',
                 ' South Indian Bank, Thrissur, India', ' Southeast Bank Limited, Dhaka, Bangladesh',
                 ' Southern Bank, Mount Olive, United States', ' Southwestern National Bank, Houston, United States',
                 ' Sovereign Bancorp, Philadelphia, United States', ' Spar Nord Bank, Aalborg, Denmark',
                 ' Sparda-Bank, Frankfurt, Germany', ' SpareBank 1 BV, Sandefjord, Norway',
                 ' SpareBank 1 Nøtterøy–Tønsberg, Nøtterøy, Norway', ' SpareBank 1 Østfold Akershus, Moss, Norway',
                 ' SpareBank 1 Ringerike Hadeland, Hønefoss, Norway', ' SpareBank 1 SMN, Trondheim, Norway',
                 ' SpareBank 1 SR-Bank, Stavanger, Norway', ' Sparebanken Hedmark, Hamar, Norway',
                 ' Sparebanken More, Aalesund, Norway', ' Sparebanken Nord-Norge, Tromsø, Norway',
                 ' Sparebanken Nordvest, Kristiansund, Norway', ' Sparebanken Sør, Kristiansand, Norway',
                 ' Sparebanken Sogn og Fjordane, Sogn og Fjordane, Norway', ' Sparebanken Vest, Bergen, Norway',
                 ' Sparkasse Hagen, Hagen, Germany', ' Sparkasse Leipzig, Leipzig, Germany',
                 ' Sparkasse Mittelholstein, Rendsburg, Germany', ' Sparkasse zu Lübeck, Lübeck, Germany',
                 ' Spire Bank, Nairobi, Kenya', ' Spitamen Bank, Dushanbe, Tajikistan',
                 ' St.George Bank, Sydney, Australia', ' Stadtsparkasse München, München, Germany',
                 ' Stanbic Bank, Johannesburg, South Africa', ' Stanbic Bank Uganda Limited, Kampala, Uganda',
                 ' Stanbic Holdings plc, Nairobi, Kenya', ' Stanbic IBTC Holdings, Lagos, Nigeria',
                 ' Standard Bank Group (Stanbank), Johannesburg, South Africa',
                 ' Standard Bank Limited, Dhaka, Bangladesh', ' Standard Bank Malawi, Lilongwe, Malawi',
                 ' Standard Bank Namibia, Windhoek, Namibia', ' Standard Chartered, London, United Kingdom',
                 ' Standard Chartered Bangladesh, Dhaka, Bangladesh', ' Standard Chartered Bank Ghana, Accra, Ghana',
                 ' Standard Chartered Bank Hong Kong, Hong Kong, Hong Kong',
                 ' Standard Chartered Kenya, Nairobi, Kenya', ' Standard Chartered Korea, Seoul, South Korea',
                 ' Standard Chartered Nepal, New Baneshwor, Kathmandu, Nepal',
                 ' Standard Chartered Pakistan, Karachi, Pakistan', ' Standard Chartered Uganda, Kampala, Uganda',
                 ' Standard Chartered Zambia, Lusaka, Zambia', ' Standard Chartered Zimbabwe, Harare, Zimbabwe',
                 ' State Bank of Bikaner and Jaipur, Jaipur, India', ' State Bank of Hyderabad, Hyderabad, India',
                 ' State Bank of India, Mumbai, India', ' State Bank of Mauritius, Port Louis, Mauritius',
                 ' State Bank of Mysore, Bangalore, India', ' State Bank of Patiala, Patiala, India',
                 ' State Bank of Travancore, Thiruvananthapuram, India',
                 ' State Export-Import Bank of Ukraine, Kyiv, Ukraine', ' State Savings Bank of Ukraine, Kyiv, Ukraine',
                 ' State Street Corp, Boston, United States', ' Sterling Bancorp, New York, United States',
                 ' Sterling Financial Corporation, Spokane, United States', ' Steyler Bank, Sant Augustin, Germany',
                 ' Stifel Financial Corp, St Louis, United States', ' Südwestbank,  Stuttgart, Germany',
                 ' Stusid Bank, Tunis, Tunisia', ' Stuttgarter Volksbank, Stuttgart, Germany',
                 ' Sudtiroler Volksbank, Bolzano, Italy', ' Sumitomo Mitsui Banking Corporation, Tokyo, Japan',
                 ' Sumitomo Mitsui Financial Group, Tokyo, Japan', ' Sumitomo Mitsui Trust Bank, Tokyo, Japan',
                 ' Summit Bancorp, Arkadelphia, Arkansas, United States', ' Summit Bank, Karachi, Pakistan',
                 ' Suncorp Bank, Brisbane, Australia', ' Suncorp Metway, Brisbane, Australia',
                 ' Sunny Bank, Taipei, Taiwan', ' Sunrise Bank, Kathmandu, Nepal',
                 ' SunTrust Banks, Atlanta, United States', ' Sun West Mortgage, California, United States',
                 ' Suomen AsuntoHypoPankki, Helsinki, Finland', ' Susquehanna Bancshares, Lititz, United States',
                 ' Svenska Handelsbanken, Stockholm, Sweden', ' Swedbank, Stockholm, Sweden',
                 ' Sydbank, Aabenraa, Denmark', ' Syndicate Bank, Manipal, India',
                 ' Synovus Financial Corp, Columbus, United States',
                 ' Syria International Islamic Bank, Damascus, Syria', ' T Bank, Athens, Greece',
                 " Tadhamon International Islamic Bank, Sana'a, Yemen", ' Taichung Commercial Bank, Taichung, Taiwan',
                 ' Taipei Fubon Bank, Taiwan ', ' Taishin International Bank, Taipei, Taiwan',
                 ' Taiwan Cooperative Bank, Taipei, Taiwan', ' Taiwan Financial Holdings Group, Taipei, Taiwan',
                 ' Takarékbank, Budapest, Hungary', ' Talmer Bancorp, Troy, United States',
                 ' Tamilnad Mercantile Bank, Tuticorin, India', ' Tangerine Bank, Toronto, Canada',
                 ' Tanzania Investment Bank, Dar es Salaam, Tanzania', ' Tapiola Bank, Espoo, Finland',
                 ' Targobank, Düsseldorf, Germany', ' Tatra banka, Bratislava, Slovakia',
                 ' Taunus Corporation, New York, United States', ' TBC Bank, Tbilisi, Georgia',
                 ' TBI Bank, Sofia, Bulgaria', ' TCF Financial Corporation, Detroit, United States',
                 ' Teachers Mutual Bank, Homebush, Australia', ' Tejarat Bank, Tehran, Iran',
                 ' Tesco Bank, Edinburgh, United Kingdom', ' Texas Capital Bancshares, Dallas, United States',
                 ' Texim Bank, Sofia, Bulgaria', ' The 77 Bank, Tohoku, Japan', ' Thanachart Bank, Bangkok, Thailand',
                 ' The Bank of East Asia, Hong Kong, Hong Kong', ' The BANK of Greenland, Nuuk, Greenland',
                 ' The City Bank, Dhaka, Bangladesh', ' The Commercial Bank of Qatar, Doha, Qatar',
                 ' The Farmers Bank Limited, Dhaka, Bangladesh',
                 ' The Hongkong and Shanghai Banking Corporation, Hong Kong, Hong Kong',
                 ' The National Bank TNB, Palestine ', ' The Senshu Bank, Japan ',
                 ' Theodoor Gilissen Bankiers, Amsterdam, Netherlands', ' Thüringer Aufbaubank, Thüringen, Germany',
                 ' TIAA Bank, Florida, United States', ' TIB Development Bank, Dar es Salaam, Tanzania',
                 ' Time Bank Zimbabwe, Harare, Zimbabwe', ' Tinkoff Bank, Moscow, Russia',
                 ' Tinkoff Credit Systems, Moscow, Russia', ' Tirana Bank, Tirana, Albania',
                 ' TMB Bank, Bangkok, Thailand', ' Toho Bank, Fukushima, Japan', ' Tohoku Bank, Morioka, Japan',
                 ' Tokyo Star Bank, Tokyo, Japan', ' Tomato Bank, Okayama, Japan',
                 ' Tompkins Financial Corporation, Ithaca, United States',
                 ' Toronto Dominion Bank (TD Bank), Toronto, Canada', ' Tourism Development Bank, Kathmandu, Nepal',
                 ' Trade and Development Bank, Ulaanbataar, Mongolia', ' Trade Bank of Iraq, Baghdad, Iraq',
                 ' Transcapitalbank, Moscow, Russia', ' Transnational Bank, Nairobi, Kenya',
                 ' Triodos Bank, Zeist, Netherlands', ' Tropical Bank, Kampala, Uganda',
                 ' Truist Financial, Charlotte, United States', ' Trust Bank Limited (Bangladesh), Dhaka, Bangladesh',
                 ' Trust Merchant Bank (TMB), Kinshasa, DRC Congo', ' Trustco Bank Namibia, Ongwediva, Namibia',
                 ' TSB Bank (United Kingdom), Edingburgh, United Kingdom',
                 ' Turk Ekonomi Bankasi (TEB), Istanbul, Turkey', ' Turkish Bank, Istanbul, Turkey',
                 ' Turkiye Is Bankasi, Istanbul, Turkey', ' Türk Ekonomi Bankası, Istanbul, Turkey',
                 ' Türk Ticaret Bankası, Istanbul, Turkey', ' Türkiye İş Bankası, Levent, Istanbul, Turkey',
                 ' Tyro Payments, Sydney, Australia', ' UBank, Sydney, Australia', ' UBI Banca, Bergamo, Italy',
                 ' UBS, Zurich, Switzerland', ' UCO Bank, Calcutta, India',
                 ' Uganda Development Bank Limited, Kampala, Uganda', ' Ukrainian Credit-Banking Union, Kyiv, Ukraine',
                 ' UkrSibbank, Kyiv, Ukraine', ' Ukrsotsbank, Kyiv, Ukraine', ' Ulster Bank Ireland, Dublin, Ireland',
                 ' Umpqua Holdings Corporation, Portland, United States', ' Umweltbank, Nürnberg, Germany',
                 ' Unibank (Azerbaijan)|Unibank, Baku, Azerbaijan', ' Unibank (Haiti)|Unibank, Port-au-Prince, Haiti',
                 ' UniBank|Unibank Ghana, Accra, Ghana', ' Unibank (Azerbaijan), Baku, Azerbaijan',
                 ' Unicaja, Malaga, Spain', ' UniCredit, Milan, Italy',
                 ' UniCredit Bank Czech Republic and Slovakia, Prague, Czech Republic',
                 ' UniCredit Bank Romania, Bucharest, Romania', ' UniCredit Bank Russia, Moscow, Russia',
                 ' UniCredit Bank Serbia, Belgrade, Serbia', ' UniCredit Bank Slovenia, Ljubljana, Slovenia',
                 ' UniCredit Bulbank, Sofia, Bulgaria', ' UniCredit Tiriac Bank, Bucharest, Romania',
                 ' Union Bancaire Privée, Geneva, Switzerland', ' Union Bank (Albania), Tirana, Albania',
                 ' Union Bank of Colombo, Colombo, Sri Lanka', ' Union Bank of India, Mumbai, India',
                 ' Union Bank of Israel, Tel Aviv, Israel', ' Union Bank of Nigeria, Lagos, Nigeria',
                 ' Union Bank of Taiwan, Taipei, Taiwan', ' Union Bank UK, London, United Kingdom',
                 ' Union National Bank, Abu Dhabi, United Arab Emirates', ' Union Trust Bank, Freetown, Sierra Leone',
                 ' Unione di Banche Italiane, Bergamo, Italy', ' Unione Fiduciaria, Milan, Italy',
                 ' Unipol Banca, Bologna, Italy', ' Unistream, Russia ', ' United Amara Bank, Yangon, Myanmar',
                 ' United Bank for Africa, Lagos, Nigeria', ' United Bank for Africa (Uganda), Nigeria',
                 ' United Bank of Albania, Tirana, Albania', ' United Bank of India, Calcutta, India',
                 ' United Bank Limited (Pakistan), Karachi, Pakistan', ' United Bankshares, Charleston, United States',
                 ' United Bulgarian Bank, Sofia, Bulgaria',
                 ' United Coconut Planters Bank (UCPB), Makati City, Philippines',
                 ' United Commercial Bank, Dhaka, Bangladesh', ' United Commercial Bank Ltd, Dhaka, Bangladesh',
                 ' United Community Banks, Blairsville, United States', ' United Gulf Bank, Manama, Bahrain',
                 ' United International Bank, New York, United States', ' United Orient Bank, New York, United States',
                 ' United Overseas Bank, Singapore, Singapore',
                 ' United Security Bancshares, Thomasville, United States', ' Unity Bank, Abuja, Nigeria',
                 ' Unity Trust Bank, Birmingham, United Kingdom', ' Urner Kantonalbank, Altdorf, Switzerland',
                 ' Uralsib, Moscow, Russia', ' Urban Partnership Bank, Chicago, United States',
                 ' Urwego Opportunity Bank, Kigali, Rwanda', ' US Bancorp, Minneapolis, United States',
                 ' UT Bank, Accra, Ghana', ' Uttara Bank, Dhaka, Bangladesh', ' VakıfBank, Levent, Istanbul, Turkey',
                 ' Valley National Bancorp, Wayne, United States',
                 ' Vancouver City Savings Credit Union, Vancouver, Canada',
                 " Van Lanschot Kempen, 's-Hertogenbosch, Netherlands", ' Varengold Bank, Hamburg, Germany',
                 ' Vattanac Bank, Phnom Penh, Cambodia', ' VBS Mutual Bank, Louis Trichardt, South Africa',
                 ' VBU Volksbank im Unterland eG, Schwaigern, Germany', ' VDK Spaarbank, Belgium',
                 ' VEB.RF, Moscow, Russia', ' VEM Aktienbank, Munich, Germany', ' Veneto Banca, Montebelluna, Italy',
                 ' Victoria Commercial Bank, Nairobi, Kenya',
                 ' Vietnam Bank for Agriculture and Rural Development, Hanoi, Vietnam',
                 ' Vijaya Bank, Bangalore, India', ' Viking Bank, Saint Petersburg, Russia',
                 ' Virginia Commerce Bancorp, Arlington, United States', ' Vnesheconombank, Moscow, Russia',
                 ' Volksbank Bielefeld-Gütersloh, Gütersloh, Germany', ' Volksbank Neckartal, Eberbach, Germany',
                 ' Volt Bank, Sydney, Australia', ' Voss Veksel- og Landmandsbank, Voss, Norway',
                 ' Vostochny Bank, Blagoveshchensk, Russia', ' Vozrozhdenie Bank, Moscow, Russia',
                 ' VP Bank AG, Vaduz, Liechtenstein', ' Všeobecná úverová banka, Bratislava, Slovakia',
                 ' VTB Bank, St Petersburg, Russia', ' VTB Bank Deutschland, Frankfurt am Main, Germany',
                 ' Walser Privatbank, Hirschegg, Austria', ' Warka Bank, Baghdad, Iraq',
                 ' Washington Federal, Seattle, United States', ' WeBank (Italy), Milan, Italy',
                 ' Webster Financial Corp, Waterbury, United States', ' Wegagen Bank, Addis Ababa, Ethiopia',
                 ' Wells Fargo & Co, San Francisco, United States',
                 ' West Bromwich Building Society, West Bromwich, United Kingdom',
                 ' Westamerica Bancorp, San Rafael, United States', ' Westpac, Sydney, Australia',
                 ' WGZ Bank, Düsseldorf, Germany', ' Wing Hang Bank, Hong Kong, Hong Kong',
                 ' Wing Lung Bank, Hong Kong, Hong Kong', ' Wintrust Financial Corp, Lake Forest, United States',
                 ' Wirecard, Munich, Germany', ' Woodforest Financial Group, The Woodlands, United States',
                 ' Woori Bank, Seoul, South Korea', ' Woori Financial Group, Seoul, South Korea',
                 ' Workers United, New York, United States', ' Wüstenrot Bank, Ludwigsburg, Germany',
                 ' Wüstenrot & Württembergische, Stuttgart, Germany', ' XacBank, Ulaanbataar, Mongolia',
                 ' Xiamen International Bank, Xiamen, China', ' Xinja, Sydney, Australia', ' yA Bank, Oslo, Norway',
                 ' Yamagata Bank, Tokyo, Japan', ' Yamaguchi Bank, Shimonoseki, Japan',
                 ' Yapi Kredi Bank Azerbaijan, Baku, Azerbaijan', ' Yapı ve Kredi Bankası, Istanbul, Turkey',
                 " Yemen Commercial Bank, Sana'a, Yemen", ' Yes Bank, Mumbai, India', ' Yoma Bank, Yangon, Myanmar',
                 ' Yorkshire Building Society, Bradford, United Kingdom', ' Zag Bank, High River Canada',
                 ' Zagrebacka Banka, Zagreb, Croatia', ' Zamanbank, Kazakhstan ',
                 ' Zambia National Commercial Bank, Lusaka, Zambia',
                 ' Zarai Taraqiati Bank Limited, Islamabad, Pakistan', ' ZAO Raiffeisenbank, Moscow, Russia',
                 ' Zenith Bank, Lagos, Nigeria', ' Zhejiang Chouzhou Commercial Bank, Yiwu, China',
                 ' Zhejiang Tailong Commercial Bank, Taizhou, China',
                 ' Zions Bancorporation, Salt Lake City, United States',
                 ' Ziraat Bankası, Ulus, Ankara|Ulus, Ankara, Turkey', ' Ziraat Katılım, Turkey ',
                 ' Zuger Kantonalbank, Zug, Switzerland', ' Zurich Cantonal Bank, Zurich, Switzerland']

def fetch_record():
    languages = ['Select Language(s)', 'Afrikaans', 'Albanian', 'Arabic', 'Armenian', 'Basque', 'Bengali',
                 'Bulgarian', 'Catalan', 'Cambodian', 'Chinese (Mandarin)', 'Croatian',
                 'Czech', 'Danish', 'Dutch', 'English', 'Estonian', 'Fiji', 'Finnish',
                 'French', 'Georgian', 'German', 'Greek', 'Gujarati', 'Hebrew', 'Hindi',
                 'Hungarian', 'Icelandic', 'Indonesian', 'Irish', 'Italian', 'Japanese',
                 'Javanese', 'Korean', 'Latin', 'Latvian', 'Lithuanian', 'Macedonian', 'Malay',
                 'Malayalam', 'Maltese', 'Maori', 'Marathi', 'Mongolian', 'Nepali', 'Norwegian',
                 'Persian', 'Polish', 'Portuguese', 'Punjabi', 'Quechua', 'Romanian', 'Russian',
                 'Samoan', 'Serbian', 'Slovak', 'Slovenian', 'Spanish', 'Swahili', 'Swedish',
                 'Tamil', 'Tatar', 'Telugu', 'Thai', 'Tibetan', 'Tonga', 'Turkish', 'Ukrainian',
                 'Urdu', 'Uzbek', 'Vietnamese', 'Welsh', 'Xhosa']
    countries = ['Select Country', 'Afghanistan', 'Aland Islands', 'Albania', 'Algeria', 'American Samoa', 'Andorra',
                 'Angola',
                 'Anguilla', 'Antarctica', 'Antigua and Barbuda', 'Argentina', 'Armenia', 'Aruba',
                 'Australia',
                 'Austria', 'Azerbaijan', 'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 'Belarus',
                 'Belgium',
                 'Belize', 'Benin', 'Bermuda', 'Bhutan', 'Bolivia', 'Bosnia and Herzegovina',
                 'Botswana',
                 'Bouvet Island', 'Brazil', 'British Indian Ocean Territory', 'Brunei Darussalam',
                 'Bulgaria',
                 'Burkina Faso', 'Burundi', 'Cambodia', 'Cameroon', 'Canada', 'Cape Verde',
                 'Cayman Islands',
                 'Central African Republic', 'Chad', 'Chile', 'China', 'Christmas Island',
                 'Cocos (Keeling) Islands',
                 'Colombia', 'Comoros', 'Congo', 'Congo, The Democratic Republic of The',
                 'Cook Islands', 'Costa Rica',
                 "Cote D'ivoire", 'Croatia', 'Cuba', 'Cyprus', 'Czech Republic', 'Denmark', 'Djibouti',
                 'Dominica',
                 'Dominican Republic', 'Ecuador', 'Egypt', 'El Salvador', 'Equatorial Guinea',
                 'Eritrea', 'Estonia',
                 'Ethiopia', 'Falkland Islands (Malvinas)', 'Faroe Islands', 'Fiji', 'Finland',
                 'France', 'French Guiana', 'French Polynesia', 'French Southern Territories', 'Gabon',
                 'Gambia', 'Georgia', 'Germany', 'Ghana', 'Gibraltar', 'Greece', 'Greenland', 'Grenada',
                 'Guadeloupe', 'Guam', 'Guatemala', 'Guernsey', 'Guinea', 'Guinea-bissau', 'Guyana',
                 'Haiti', 'Heard Island and Mcdonald Islands', 'Holy See (Vatican City State)',
                 'Honduras', 'Hong Kong', 'Hungary', 'Iceland', 'India', 'Indonesia',
                 'Iran, Islamic Republic of', 'Iraq', 'Ireland', 'Isle of Man', 'Israel', 'Italy',
                 'Jamaica', 'Japan', 'Jersey', 'Jordan', 'Kazakhstan', 'Kenya', 'Kiribati',
                 "Korea, Democratic People's Republic of", 'Korea, Republic of', 'Kyrgyzstan',
                 "Lao People's Democratic Republic", 'Latvia', 'Lebanon', 'Lesotho', 'Liberia',
                 'Libyan Arab Jamahiriya', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Macao',
                 'Macedonia, The Former Yugoslav Republic of', 'Madagascar', 'Malawi', 'Malaysia',
                 'Maldives', 'Mali', 'Malta', 'Marshall Islands', 'Martinique', 'Mauritania',
                 'Mauritius', 'Mayotte', 'Mexico', 'Micronesia, Federated States of',
                 'Moldova, Republic of', 'Monaco', 'Mongolia', 'Montenegro', 'Montserrat', 'Morocco',
                 'Mozambique', 'Myanmar', 'Namibia', 'Nauru', 'Nepal', 'Netherlands',
                 'Netherlands Antilles', 'New Caledonia', 'New Zealand', 'Nicaragua', 'Niger',
                 'Nigeria', 'Niue', 'Norfolk Island', 'Northern Mariana Islands', 'Norway', 'Oman',
                 'Pakistan', 'Palau', 'Palestinian Territory, Occupied', 'Panama', 'Papua New Guinea',
                 'Paraguay', 'Peru', 'Philippines', 'Pitcairn', 'Poland', 'Portugal', 'Puerto Rico',
                 'Qatar', 'Reunion', 'Romania', 'Russian Federation', 'Rwanda', 'Saint Helena',
                 'Saint Kitts and Nevis', 'Saint Lucia', 'Saint Pierre and Miquelon',
                 'Saint Vincent and The Grenadines', 'Samoa', 'San Marino', 'Sao Tome and Principe',
                 'Saudi Arabia', 'Senegal', 'Serbia', 'Seychelles', 'Sierra Leone', 'Singapore',
                 'Slovakia', 'Slovenia', 'Solomon Islands', 'Somalia', 'South Africa',
                 'South Georgia and The South Sandwich Islands', 'Spain', 'Sri Lanka', 'Sudan',
                 'Suriname', 'Svalbard and Jan Mayen', 'Swaziland', 'Sweden', 'Switzerland',
                 'Syrian Arab Republic', 'Taiwan, Province of China', 'Tajikistan',
                 'Tanzania, United Republic of', 'Thailand', 'Timor-leste', 'Togo', 'Tokelau', 'Tonga',
                 'Trinidad and Tobago', 'Tunisia', 'Turkey', 'Turkmenistan', 'Turks and Caicos Islands',
                 'Tuvalu', 'Uganda', 'Ukraine', 'United Arab Emirates', 'United Kingdom',
                 'United States', 'United States Minor Outlying Islands', 'Uruguay', 'Uzbekistan',
                 'Vanuatu', 'Venezuela', 'Viet Nam', 'Virgin Islands, British', 'Virgin Islands, U.S.',
                 'Wallis and Futuna', 'Western Sahara', 'Yemen', 'Zambia', 'Zimbabwe']
    dead_line = ['Select Deadline', "1 Hour", "2 Hours", "3 Hours", "4 Hours", "6 Hours", "8 Hours",
                 "12 Hours", "24 Hours", "36 Hours", "48 Hours", "3 Days", "4 Days",
                 "5 Days", "6 Days", "7 Days"]
    delivery_options = ["Select option(s)", "Digital Delivery", "Remote live direction", "ISDN", "Source Connect",
                        "Phone patch", "ipDTL", "On-site Recording"]
    proposals = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
    table = mydb["category"]
    categorie = table.find({})
    categories = []
    for category in categorie:
        categories.append(category)

    accents = ['Select Accent(s)', 'Afghan', 'African (General)', 'Algerian', 'Arabic', 'Armenian', 'Australian',
               'Austrian',
               'Bangladesh, India', 'Basque', 'Bavarian', 'Belgian', 'Belgian (Brabants)', 'Bosnian', 'British',
               'Bulgarian', 'Canadian', 'Canadian (Maritimes)', 'Canadian (Newfoundland)', 'Canadian (West)',
               'Cantonese', 'Caribbean', 'Caribbean (Bahamian', 'Caribbean (Barbadian', 'Caribbean (Bermudian)',
               'Caribbean (Cuban)', 'Caribbean (Dominican)', 'Caribbean (Haitian', 'Caribbean (Jamaican',
               'Caribbean (Puerto Rican)', 'Caribbean (Tobagonian', 'Caribbean (Trinidadian', 'Celtic',
               'Central African', 'Central African', 'Central American', 'Central American', 'Central American (Costa',
               'Chinese', 'Creole, Patois', 'Croatian', 'Czech', 'Danish', 'Dutch', 'East Africa',
               'East Africa (Kenyan)', 'East Africa (Ugandan)', 'Eastern European', 'Egyptian', 'England - East (East',
               'England - East Midlands', 'England - London', 'England - North East', 'England - North West',
               'England - Received', 'England - South East', 'England - South West', 'England - West Midlands',
               'England - Yorkshire', 'Farsi', 'Finnish', 'Flemish', 'French', 'French (Parisienne)',
               'French (Quebecois)', 'French (Standard', 'Gaelic', 'Georgian (Kartvelian)', 'German', 'Greek',
               'Hawaiian', 'Hebrew', 'Hungarian', 'Icelandic', 'India (Bihari)', 'India (Haryanvi)', 'India (Hindi)',
               'India (Hinglish)', 'India (Marathi)', 'India (Rajasthani)', 'India (Telugu)', 'India, Pakistan',
               'India, Pakistan (Urdu)', 'Indian (Gujarati)', 'Indian (India)', 'Indonesian', 'Iraqi', 'Irish',
               'Irish Eastern (Leinster,', 'Irish Northern (Ulster,', 'Irish Southern (Munster,',
               'Irish Western (Connacht,', 'Israeli', 'Italian', 'Italian American', 'Italian Central (Roman,',
               'Italian Northern', 'Italian Southern', 'Japanese', 'Jewish', 'Jordanian', 'Kazakh', 'Khmer', 'Korean',
               'Laotian', 'Latino', 'Latvian', 'Lebanese', 'Lithuanian', 'Macedonian', 'Malay', 'Maltese', 'Mandarin',
               'Maori', 'Mediterranean', 'Mexican', 'Mexico (Northern)', 'Mexico (Southern)', 'Native American',
               'Nepali', 'New Zealand', 'North African', 'North African', 'North African', 'North American',
               'Norwegian', 'Norwegian (Bokmal)', 'Norwegian (Nynorsk)', 'Nuyorican', 'Pakistani', 'Palestinian',
               'Persian', 'Philippines (Cebuano)', 'Philippines (Filipino,', 'Polish', 'Polynesian', 'Portuguese',
               'Romanian', 'Russian', 'Scandinavian', 'Scottish', 'Scottish (Aberdeen,', 'Scottish (Edinburgh)',
               'Scottish (Glaswegian)', 'Scottish (Highland,', 'Scottish (Lowland,', 'Scottish (Standard', 'Serbian',
               'Silesian', 'Singaporean', 'Singaporean (Singlish)', 'Slavic', 'Slovakian', 'Slovenian', 'South African',
               'South African', 'South African (Xhosa)', 'South African', 'South African (Zulu)', 'South American',
               'South American', 'South American', 'South American', 'South American', 'South American',
               'South American', 'South American', 'South American', 'South American', 'South American',
               'South American', 'Southern Africa', 'Spanish', 'Spanish (Andalusian)', 'Spanish (Castilian)',
               'Spanish (Catalan)', 'Spanish (Galician)', 'Spanish (International', 'Spanish (Valenciano)', 'Swabian',
               'Swahili', 'Swedish', 'Swiss', 'Swiss German', 'Syrian', 'Taiwanese', 'Thai', 'Trans-Atlantic',
               'Turkish', 'Ukrainian', 'US (Gullah, Geechee)', 'US African American', 'US Appalachia',
               'US Cajun (Creole,', 'US General American', 'US Mid-Atlantic', 'US Midwest (Chicago,', 'US New England',
               'US New Orleans', 'US New York (New', 'US South (Deep South,', 'US South West (Texas)',
               'US Upper Midwest', 'US West Coast', 'US Western', 'Vietnamese', 'Welsh', 'West African', 'West African',
               'West African (Hausa)', 'West African (Igbo)', 'West African', 'West African', 'West African (Yoruba)',
               'Yiddish']
    return languages, countries, dead_line, categories, delivery_options, proposals, accents


# Fetch category, gender and age for mobile api's
def fetch_category():
    table = mydb['category']
    category_data = table.find({})
    gender = [{"Category Name": "Select Gender",
               "Price per Word": 0.0,
               "Standard Price": 0.0,
               "Type": "gender",
               "_id": "0",
               "timeStamp": "Sun, 24 Jan 2021 23:44:14 GMT"}]
    category = [{"Category Name": "Select Category(s)",
                 "Price per Word": 0.0,
                 "Standard Price": 0.0,
                 "Type": "gender",
                 "_id": "0",
                 "timeStamp": "Sun, 24 Jan 2021 23:44:14 GMT"}]
    age = [{"Category Name": "Select age(s)",
            "Price per Word": 0.0,
            "Standard Price": 0.0,
            "Type": "gender",
            "_id": "0",
            "timeStamp": "Sun, 24 Jan 2021 23:44:14 GMT"}]

    for each_category in category_data:
        if each_category['Type'] == 'age':
            each_category['_id'] = str(each_category['_id'])
            age.append(each_category)
        elif each_category['Type'] == 'gender':
            each_category['_id'] = str(each_category['_id'])
            gender.append(each_category)
        elif each_category['Type'] == 'category':
            each_category['_id'] = str(each_category['_id'])
            category.append(each_category)
    return age, gender, category


# Fetch category, gender and age for a particular actor using its id in actor document for mobile api's
def fetch_user_category(actor_id):
    table = mydb['category']
    category_data = table.find({})
    gender = [{"Category Name": "Select Gender",
               "Price per Word": 0.0,
               "Standard Price": 0.0,
               "Type": "gender",
               "_id": "0",
               "timeStamp": "Sun, 24 Jan 2021 23:44:14 GMT"}]
    category = [{"Category Name": "Select Category",
                 "Price per Word": 0.0,
                 "Standard Price": 0.0,
                 "Type": "gender",
                 "_id": "0",
                 "timeStamp": "Sun, 24 Jan 2021 23:44:14 GMT"}]
    age = [{"Category Name": "Select age",
            "Price per Word": 0.0,
            "Standard Price": 0.0,
            "Type": "gender",
            "_id": "0",
            "timeStamp": "Sun, 24 Jan 2021 23:44:14 GMT"}]
    languages = ['Select language']
    accents = ['Select accent']

    actor_table = mydb['actor']
    actor_data = actor_table.find_one({"_id": ObjectId(actor_id)})

    for each_category in category_data:
        if each_category['Type'] == 'age':
            if str(each_category['_id']) in actor_data['catdata']:
                each_category['_id'] = str(each_category['_id'])
                age.append(each_category)
        elif each_category['Type'] == 'gender':
            if str(each_category['_id']) in actor_data['catdata']:
                each_category['_id'] = str(each_category['_id'])
                gender.append(each_category)
        elif each_category['Type'] == 'category':
            if str(each_category['_id']) in actor_data['catdata']:
                each_category['_id'] = str(each_category['_id'])
                category.append(each_category)
    for langauge in actor_data['languages']:
        languages.append(langauge)
    for accent in actor_data['accents']:
        accents.append(accent)
    return age, gender, category, languages, accents


# Function to call each time.
def bid_function(mydata, myfile):
    data = mydata
    sampleslist = myfile

    actor_name = data["actorName"]
    actor_id = data["actorId"]
    buyer_id = data["buyrId"]
    project_id = data["projId"]
    actor_description = data["actorDescription"]
    actor_time = data["actorCmplTime"]

    bidTable = mydb["bidding"]
    bidTable.insert_one({"actor_id": ObjectId(actor_id), "buyer_id":
        ObjectId(buyer_id), "project_id": ObjectId(project_id),
                         "timeStamp": datetime.now(),
                         "status": "pending", "requestby": "actor"})

    table = mydb["buyer"]
    if 'amount' in mydata:
        mydic1 = {"actor_name": actor_name, "actor_description": actor_description, "offer": str(mydata['amount']),
              "job_complete": actor_time, "playlist": sampleslist, "_id": ObjectId(actor_id)}    
    else:
        mydic1 = {"actor_name": actor_name, "actor_description": actor_description,
              "job_complete": actor_time, "playlist": sampleslist, "_id": ObjectId(actor_id)}
    table.update({"_id": ObjectId(buyer_id), "projects.project_id": ObjectId(project_id)},
                 {"$push": {"projects.$.responses": mydic1}})
    buyer_data = table.find_one({"_id": ObjectId(buyer_id)})

    # msg = Message("New request for project", recipients=[buyer_data['email']])
    # msg.html = str("New Request received against the project you posted.<br><br>Regards, <br>Voices City")
    # mail.send(msg)
    return True


# Function to call each time for bidding by actor.
def bid_function_api(mydata, myfile):
    data = mydata
    sampleslist = myfile

    actor_name = data["user[username]"]
    actor_id = data["user[userid]"]

    buyer_id = data["_id"]
    project_id = data["project_id"]
    actor_description = data["desc"]
    actor_time = data["completion"]

    bidTable = mydb["bidding"]
    bidTable.insert_one({"actor_id": ObjectId(actor_id), "buyer_id":
        ObjectId(buyer_id), "project_id": ObjectId(project_id),
                         "timeStamp": datetime.now(),
                         "status": "pending", "requestby": "actor"})

    table = mydb["buyer"]
    mydic1 = {"actor_name": actor_name, "actor_description": actor_description,
              "job_complete": actor_time, "playlist": sampleslist, "_id": ObjectId(actor_id)}
    table.update({"_id": ObjectId(buyer_id), "projects.project_id": ObjectId(project_id)},
                 {"$push": {"projects.$.responses": mydic1}})

    table = mydb["actor"]
    table.update_one({"_id": ObjectId(actor_id)},
                     {"$addToSet": {"sentoffers":
                                        {"actor_id": ObjectId(actor_id),
                                         "buyer_id": ObjectId(buyer_id),
                                         "project_id": ObjectId(project_id),
                                         "timeStamp": datetime.now()}}})
    buyer_data = table.find_one({"_id": ObjectId(buyer_id)})

    msg = Message("New request for project", recipients=[buyer_data['email']])
    msg.html = str("New Request received against the project you posted.<br><br>Regards, <br>Voices City")
    mail.send(msg)
    return True


# Home page without login.
@app.route("/")
def home():
    try:
        if session.get("email") and session.get("type") and session.get("username"):
            if request.method == "POST":
                return redirect(url_for("home"))
            else:
                username = session.get("username")
                email = session.get("email")
                type = session.get("type")
                return render_template("index.html", username=username, email=email, type=type)
        else:
            return render_template("index.html", type=None)
    except Exception as e:
        session["error"] = str(e) + str(".\t\t Route: '\'")
        return redirect(url_for("show_error"))


# Home page without login.
@app.route("/actors", methods=["GET", "POST"])
def actors():
    try:
        if request.method == "POST":
            session["searchItem"] = str(request.form["searchItem"])
            return redirect(url_for("actors"))
        languages, countries, dead_line, categories, delivery_options, proposals, accents = fetch_record()
        search_item = ""
        gender = ""
        age = ""
        accent = ""
        if request.args.get("age"):
            age = request.args.get("age")
        if request.args.get("gender"):
            gender = request.args.get("gender")
        if request.args.get("category") and request.args.get("language"):
            catego1 = request.args.getlist("category")
            langauge = request.args.getlist("language")
            accent = request.args.getlist("accent")
            catego1.append(age)
            catego1.append(gender)
        elif session.get("searchItem"):
            search_item = session.get("searchItem")
            session.pop("searchItem", None)
        else:
            catego1 = []
            for each_category in categories:
                catego1.append(str(each_category['_id']))
            langauge = languages

        type1 = session.get("type")
        email = session.get("email")

        table = mydb["actor"]
        # actors_data = table.find({"active": 1}, {"password": 0, "passwordHash": 0, "activateLink": 0, "email": 0})
        # actors = []
        # for i in actors_data:
        #     actors.append(i)
        if gender == "":
            the_actors = table.aggregate([
            # {"$match": {"planType": {"or": ['premium', 'gold']}}},
            {
                "$project": {"playlists": 1, "userName": 1, "profilePicture": 1,
                             "Location": 1}
            }
            ,
            {
                "$unwind": "$playlists"
            }
            ,
            {
                "$project": {
                    "playlists": "$playlists",
                    "userName": "$userName",
                    "profilePicture": "$profilePicture",
                    "profilePicture": "$profilePicture",
                    "Location": "$Location",
                    "matchesgener": {"$cond": {"if": {"$eq": [{"$size": {
                        "$setIntersection": [langauge, "$playlists.playlist_language"
                                             ]}}, 0]}, "then": "NULL", "else": "True"}},
                    "matchesgender": {"$cond": {"if": {"$eq": [{"$size": {
                        "$setIntersection": ["$playlists.playlist_category",
                                             catego1]}}, 0]}, "then": "NULL",
                        "else": "True"}}
                }
            },
            {
                "$match": {
                    "$or": [{"matchesgener": {"$eq": "True"}}, {"matchesgender": {"$eq": "True"}}]}
            }
        ])
            actors = []
            for i in the_actors:
                actors.append(i)
        else:
            gender_list = gender.split(" ")
            the_actors = table.aggregate([
            # {"$match": {"planType": {"or": ['premium', 'gold']}}},
            {
                "$project": {"playlists": 1, "userName": 1, "profilePicture": 1,
                             "Location": 1}
            }
            ,
            {
                "$unwind": "$playlists"
            }
            ,
            {
                "$project": {
                    "playlists": "$playlists",
                    "userName": "$userName",
                    "profilePicture": "$profilePicture",
                    "profilePicture": "$profilePicture",
                    "Location": "$Location",
                    "matchesgener": {"$cond": {"if": {"$eq": [{"$size": {
                        "$setIntersection": [langauge, "$playlists.playlist_language"
                                             ]}}, 1]}, "then": "True", "else": "NULL"}},
                    "matchesgender": {"$cond": {"if": {"$eq": [{"$size": {
                        "$setIntersection": ["$playlists.playlist_category",
                                             catego1]}}, 3]}, "then": "True",
                        "else": "NULL"}},
                    "matchesgender1": {"$cond": {"if": {"$eq": [{"$size": {
                        "$setIntersection": ["$playlists.playlist_category",
                                             gender_list]}},1]}, "then": "True",
                        "else": "False"}}
                }
            },
            {
                "$match": {
"$and": [{"matchesgener": {"$eq": "True"}}, {"matchesgender": {"$eq": "True"}}]}
            } 
        ])
            actors = []
            for i in the_actors:
                actors.append(i)
        return render_template("actors.html", type=type1, languages=languages, categories=categories, accents=accents,
                               actors=actors, gender=gender, age=age, accent=accent, category=catego1, language=langauge, email=email,
                               search_item=search_item)
    except Exception as e:
        session["error"] = str(e) + str(".\t\t Route: '\actors'")
        return redirect(url_for("show_error"))


# Actor profile without login.
@app.route("/actorprofile", methods=["GET", "POST"])
def actorprofile():
    try:
        if request.method == "POST":
            return redirect(url_for("actorprofile"))
        else:
            username = session.get("username")
            email = session.get("email")
            type = session.get("type")
            actor_id = request.args.get("id")
            actorTable = mydb["actor"]
            actordata = actorTable.find_one({"_id": ObjectId(actor_id)},
                                            {'password': 0, 'passwordHash': 0, 'active': 0, 'activateLink': 0})
            error = ""
            if session.get("error"):
                error = session.get("error")
                session.pop("error", None)
            message = ""
            if session.get("message"):
                message = session.get("message")
                session.pop("message", None)
            languages, countries, dead_line, categories, delivery_options, proposals, accents = fetch_record()

            return render_template("actor-profile.html", username=username, email=email, type=type, error=error,
                                   message=message, actordata=actordata,
                                   actor_id=actor_id, languages=languages, categories=categories)
    except Exception as e:
        session["error"] = str(e) + str(".\t\tRoute: /actor-profile")
        return redirect(url_for("show_error"))


# Jobs for the actor without login
@app.route("/job")
def job():
    try:
        if request.method == "POST":
            return redirect(url_for(about_us))
        else:
            username = session.get("username")
            email = session.get("email")
            type = session.get("type")
            languages, countries, dead_line, categories, delivery_options, proposals, accents = fetch_record()
            categories1 = []
            for i in categories:
                categories1.append(str(i['_id']))
            accents1 = []
            for i in accents:
                accents1.append(str(i))
            actor_languages = languages
            actor_accents = accents1
            actor_category = categories1

            buyer_table = mydb["buyer"]
            projcts = buyer_table.aggregate([
                {
                    "$project": {"projects": 1}
                },
                {
                    "$unwind": "$projects"
                },
                {
                    "$match": {"projects.status": "posted"}
                },
                {
                    "$project": {
                        "projects": "$projects",
                        "matchesgener": {"$cond": {"if": {"$eq": [{"$size": {
                            "$setIntersection": ["$projects.project_language",
                                                 actor_languages]}}, 0]}, "then": "NULL", "else": "True"}},
                        "matchesgender": {"$cond": {"if": {"$eq": [{"$size": {
                            "$setIntersection": ["$projects.project_gender_age",
                                                 actor_category]}}, 0]}, "then": "NULL", "else": "True"}}
                        # ,
                        # "matchesaccent": {"$cond": {"if": {"$eq": [{"$size": {
                        #     "$setIntersection": ["$projects.project_accent",
                        #                          actor_accents]}}, 0]}, "then": "NULL", "else": "True"}}
                    }
                },
                {
                    "$match": {
                        "$or": [{"matchesgener": {"$eq": "True"}}, {"matchesgender": {"$eq": "True"}}]}
                }
            ])
            prjcts = []
            for i in projcts:
                i['_id'] = str(i['_id'])
                i['projects']['project_id'] = str(i['projects']['project_id'])
                if "responses" in i['projects']:
                    i['projects']['responsestotal'] = len(i['projects']['responses'])
                    i['projects'].pop('responses', None)
                    i['projects'].pop('acceptOffers', None)

                prjcts.append(i)

            return render_template("jobsNotLogin.html", username=username, email=email, type=type, data_job=prjcts,
                                   languages=languages, countries=countries, dead_line=dead_line, categories=categories,
                                   accents=accents)
    except Exception as e:
        session["error"] = str(e) + ", ROute: \t\t/job"
        return redirect(url_for("show_error"))


# Search job by form of /job route.
@app.route("/search-job")
def search_job():
    try:
        if request.method == "POST":
            return redirect(url_for(search_job))
        else:
            username = session.get("username")
            email = session.get("email")
            type = session.get("type")

            actor_languages = request.args.getlist("language")
            actor_category = request.args.getlist("category")
            actor_accent = request.args.getlist("accent")

            buyer_table = mydb["buyer"]
            projcts = buyer_table.aggregate([
                {
                    "$project": {"projects": 1}
                },
                {
                    "$unwind": "$projects"
                },
                {
                    "$match": {"projects.status": "posted"}
                },
                {
                    "$project": {
                        "projects": "$projects",
                        "matchesgener": {"$cond": {"if": {"$eq": [{"$size": {
                            "$setIntersection": ["$projects.project_language",
                                                 actor_languages]}}, 0]}, "then": "NULL", "else": "True"}},
                        "matchesgender": {"$cond": {"if": {"$eq": [{"$size": {
                            "$setIntersection": ["$projects.project_gender_age",
                                                 actor_category]}}, 0]}, "then": "NULL", "else": "True"}}
                        # ,
                        # "matchesgender": {"$cond": {"if": {"$eq": [{"$size": {
                        #     "$setIntersection": ["$projects.project_accent",
                        #                          actor_category]}}, 0]}, "then": "NULL", "else": "True"}}
                    }
                },
                {
                    "$match": {
                        "$or": [{"matchesgener": {"$eq": "True"}}, {"matchesgender": {"$eq": "True"}}]}
                }
            ])
            prjcts = []
            for i in projcts:
                i['_id'] = str(i['_id'])
                i['projects']['project_id'] = str(i['projects']['project_id'])
                if "responses" in i['projects']:
                    i['projects'].pop('responses', None)
                    i['projects'].pop('acceptOffers', None)

                prjcts.append(i)

            actordata = {}
            if session.get("userid") is not None:
                userid = session.get("userid")
                table = mydb["actor"]
                actordata = table.find({"_id": ObjectId(userid)})

            languages, countries, dead_line, categories, delivery_options, proposals, accents = fetch_record()
            return render_template("Jobs.html", username=username, email=email, type=type, data_job=prjcts,
                                   categories=categories, actordata=actordata, languages=languages,
                                   countries=countries, dead_line=dead_line)
    except Exception as e:
        session["error"] = str(e) + ", ROute: \t\t/job-search"
        return redirect(url_for("show_error"))


# Search for voiuce actorsby main search of layout
@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        session["searchItem"] = str(request.form["searchItem"])
        return redirect(url_for("search"))
    gender = ""
    catego1 = ""
    langauge = ""
    search_item = ""
    if request.args.get("gender") and request.args.get("category") and request.args.get("langauge"):
        gender = request.args.get("gender")
        catego1 = request.args.get("category")
        langauge = request.args.get("langauge")
    elif session.get("searchItem"):
        search_item = session.get("searchItem")
        session.pop("searchItem", None)
    type1 = session.get("type")
    email = session.get("email")
    languages, countries, dead_line, categories, delivery_options, proposals, accents = fetch_record()
    table = mydb["actor"]
    actors = table.find({"active": 1}, {"password": 0, "passwordHash": 0, "activateLink": 0, "email": 0})
    return render_template("search.html", type=type1, languages=languages, categories=categories,
                           actors=actors, gender=gender, category=catego1, language=langauge, email=email,
                           search_item=search_item, accents=accents)




# ask for user type? (Actor or Job Poster)
@app.route("/signup")
def signup():
    if session.get("email") and session.get("type") and session.get("username"):
        if session.get("type") == "buyer":
            return redirect(url_for("account"))
        elif session.get("type") == "actor":
            return redirect(url_for("actorhome"))
    else:
        return render_template("signup.html", type=None)



# Payment Plans.
@app.route("/paymentplans", methods=["GET", "POST"])
def plans():
    return render_template("paymentplan.html", type=None)


# Payment Renew.
@app.route("/re-new-paymentplan", methods=["GET", "POST"])
def renewplan():
    # try:
    if session.get("email") and session.get("type") == "actor" \
            and session.get("username"):
        if request.method == "POST":
            actor_id = session.get("userid")
            actorTable = mydb["actor"]
            paymentPlan = request.json["paymentmethod"]
            paymentmethod = "None"
            if paymentPlan == "bronze":
                paymentmethod = request.form["paymentType"]
            print(paymentPlan, paymentmethod)


            actordata = actorTable.find_one({"_id": ObjectId(actor_id)})
            email = actordata["email"]
            amount = request.json["amount"]
            print(amount)
            if paymentPlan != "standard":
                customer = stripe.Customer.create(
                    email=email,
                    source=request.json['token']
                )
                stripe.Charge.create(
                    customer=customer.id,
                    amount=amount,
                    currency='USD',
                    description=request.json['description']
                )

            amount = amount / 100
            actorTable.update_one({"_id": ObjectId(actor_id)}, {"$set": {
                "planType": paymentPlan, "planPayment": paymentmethod, "planDate": datetime.now()
            }})

            return "true"
        else:
            username = session.get("username")
            email = session.get("email")
            type = session.get("type")
            userid = session.get("userid")
            print(username, email)

            return render_template("renewpayment.html", username=username, email=email,
                                   type=type,userid=userid,key=stripe_keys['publishable_key'])
    else:
        return redirect("/login")

    # except Exception as e:
    #     return str(e)




# As an company or person to hire and post job. (buyer).
@app.route("/hiresignup", methods=["GET", "POST"])
def hiresignup():
    try:
        if session.get("email") and session.get("user") == "buyer":
            return redirect("/")
        else:
            if request.method == "POST":
                data = request.form
                email = data["email"]
                username = data["username"]
                companyname = data["companyname"]
                password = data["password"]
                password_hash = generate_password_hash(password)
                linkhash = generate_password_hash(password + email)
                buyertable = mydb["buyer"]
                actorTable = mydb["actor"]
                oldrecordbuyer = buyertable.find_one({"email": email})
                oldrecordactor = actorTable.find_one({"email": email})
                if oldrecordbuyer == None and oldrecordactor == None:
                    buyertable.insert_one({"email": email, "userName": username, "companyName": companyname,
                                           "password": password, "passwordHash": password_hash, "type": "buyer",
                                           "timeStamp": datetime.now(), "active": 0, "activateLink": linkhash})

                    data = {
                            "personalizations": [
                                {
                                "to": [
                                    {
                                    "email": email
                                    }
                                ],
                                "subject": username + ", please confirm your email address"
                                }
                            ],
                            "from": {
                                "email": default_sender,
                                "name": "voices city"
                            },
                            "content": [
                                {
                                "type": "text/html",
                                "value": """<th style="margin:0 auto; color:#0a0a0a; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-bottom:16px; padding-left:16px; padding-right:16px; text-align:left; width:564px">
	<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
		<tbody>
			<tr style="padding:0; text-align:left; vertical-align:top">
				<th style="margin:0; color:#0a0a0a; font-family:Helvetica,Arial,sans-serif; font-size:14px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left">
					<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
						<tbody>
							<tr style="padding:0; text-align:left; vertical-align:top">
								<td style="margin:0; border-collapse:collapse!important; color:#0a0a0a; font-family:Helvetica,Arial,sans-serif; font-size:32px; font-weight:400; line-height:10px; margin:0; padding:0; text-align:left; vertical-align:top; word-wrap:break-word" height="10px">&nbsp;</td>
							</tr>
						</tbody>
					</table>
					<p style="margin:22px 0 0"><img data-imagetype="External" src=\"""" + base_url + """/static/mail.png" title="Mail Icon" alt="Mail Icon" style="margin:auto; display:block; width:80px"> </p>
					<h4 style="width:221px; height:25px; font-size:20px; font-weight:500; line-height:1.25; letter-spacing:normal; text-align:center; margin:24px auto auto">Let's confirm your email! </h4>
					<hr style="width:520px; height:1px; background-color:#c9d0d9; border:none; margin-top:40px">
					<div style="padding:0 24px">
						<p style="font-size:16px; font-weight:normal; font-stretch:normal; font-style:normal; line-height:1.5; letter-spacing:normal; color:#4f5963; margin-top:30px; margin-bottom:30px">Hi """ + username + """,</p>
						<p style="font-size:16px; font-weight:normal; font-stretch:normal; font-style:normal; line-height:1.5; letter-spacing:normal; color:#4f5963; margin-top:30px; margin-bottom:30px">Thank you for creating a Voicescity.com account. In order to complete the registration process, please click the button below to verify your email address: </p><a href='""" + base_url + """/activate?code=""" + email + """&hashkey=""" + linkhash + """' target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="border-radius:4px; background-color:#1171bb; font-size:18px; padding:12px 24px; color:white; margin:10px 0; display:inline-block; text-decoration:none" data-linkindex="1">Verify Your Email </a>
						<p style="font-size:16px; font-weight:normal; font-stretch:normal; font-style:normal; line-height:1.5; letter-spacing:normal; color:#4f5963; margin-top:30px; margin-bottom:30px">Once you’ve verified your email you’ll gain full access to your Voicescity.com account. The verification link will expire 24 hours after your original registration request was submitted. </p>
						<p style="font-size:16px; font-weight:normal; font-stretch:normal; font-style:normal; line-height:1.5; letter-spacing:normal; color:#4f5963; margin-top:30px; margin-bottom:30px">If you experience any issues or have questions regarding your Voicescity.com account, please contact us at <a href="mailto:support@voicescity.com" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="color:#1171bb" data-linkindex="2">support@voicescity.com</a>, or at <span style="color:#1171bb">+447888884150</span> (Monday to Friday, 8:00 AM to 8:00 PM EST). </p>
						<p style="font-size:16px; font-weight:normal; font-stretch:normal; font-style:normal; line-height:1.5; letter-spacing:normal; color:#4f5963; margin-top:30px; margin-bottom:30px">Thank You.</p><strong><span style="color:#000066">Customer Support Team</span></strong>
						<br aria-hidden="true"><strong><span style="color:#1171bb">Voicescity.com</span></strong>
						<br aria-hidden="true">+447888884150
						<br aria-hidden="true"><a href="mailto:support@voicescity.com" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" data-linkindex="3">support@voicescity.com</a> | <a href="https://voicescity.com/" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" data-linkindex="4">voicescity.com</a> </div>
				</th>
				<th style="margin:0; color:#0a0a0a; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0!important; text-align:left; width:0"></th>
			</tr>
		</tbody>
	</table>
</th>
<table style="margin:0 auto; background:#ffffff; border:1px solid #ccc; border-collapse:collapse; border-spacing:0; border:none; color:grey; float:none; margin:0 auto; padding:0; text-align:center; vertical-align:top; width:600px" align="center">
	<tbody>
		<tr style="padding:0; text-align:left; vertical-align:top">
			<td style="margin:0; border-collapse:collapse!important; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; vertical-align:top; word-wrap:break-word">
				<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
					<tbody>
						<tr style="padding:0; text-align:left; vertical-align:top">
							<td style="margin:0; border-collapse:collapse!important; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:15px; font-weight:400; line-height:15px; margin:0; padding:0; text-align:left; vertical-align:top; word-wrap:break-word" height="15px">&nbsp;</td>
						</tr>
					</tbody>
				</table>
				<table style="border-collapse:collapse; border-spacing:0; display:table; padding:0; text-align:left; vertical-align:top; width:100%">
					<tbody>
						<tr style="padding:0; text-align:left; vertical-align:top">
							<th style="margin:0 auto; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-bottom:0; padding-left:16px; padding-right:16px; text-align:left; width:564px">
								<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
									<tbody>
										<tr style="padding:0; text-align:left; vertical-align:top">
											<th style="margin:0; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left">
												<center style="min-width:532px; width:100%"><span align="center" style="font-size:12px">LET'S BE FRIENDS</span></center>
											</th>
											<th style="margin:0; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0!important; text-align:left; width:0"></th>
										</tr>
									</tbody>
								</table>
							</th>
						</tr>
					</tbody>
				</table>
				<table style="border-collapse:collapse; border-spacing:0; display:table; padding:0; text-align:left; vertical-align:top; width:100%">
					<tbody>
						<tr style="padding:0; text-align:left; vertical-align:top">
							<th style="margin:0 auto; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-left:27px; padding-right:16px; text-align:left; width:564px">
								<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
									<tbody>
										<tr style="padding:0; text-align:left; vertical-align:top">
											<th style="margin:0; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left">
												<center style="min-width:532px; width:100%">
													<table style="margin:0 auto; border-collapse:collapse; border-spacing:0; float:none; margin:0 auto; padding:0; text-align:center; vertical-align:top; width:auto!important" align="center">
														<tbody>
															<tr style="padding:0; text-align:left; vertical-align:top">
																<td style="margin:0; border-collapse:collapse!important; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; vertical-align:top; word-wrap:break-word">
																	<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
																		<tbody>
																			<tr style="padding:0; text-align:left; vertical-align:top">
																				<th style="margin:0 auto; color:inherit; float:none; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-right:10px; text-align:center">
																					<a href="https://twitter.com/VoicesCity2?s=08" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="margin:0; color:#17b; font-family:Helvetica,Arial,sans-serif; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; text-decoration:none" data-linkindex="5"><img data-imagetype="External" src="http://voicescity.com/static/twitter.png" originalsrc="http://go.pardot.com/l/55082/2015-09-30/3gccd5/55082/68476/SocialButton3_TWR_BlueOnWhite_50X75.png" data-connectorsauthtoken="1" data-imageproxyendpoint="/actions/ei" data-imageproxyid="" alt="Twitter" style="border:none; clear:both; display:block; max-width:100%; outline:0; text-decoration:none; width:20"> </a>
																				</th>	
																				<th style="margin:0 auto; color:inherit; float:none; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-right:10px; text-align:center">
																					<a href="https://www.facebook.com/Voices-City-332687944647576/" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="margin:0; color:#17b; font-family:Helvetica,Arial,sans-serif; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; text-decoration:none" data-linkindex="6"><img data-imagetype="External" src="http://voicescity.com/static/facebook.png" originalsrc="http://go.pardot.com/l/55082/2015-09-30/3gcccp/55082/68474/SocialButton2_FB_BlueOnWhite_50X75.png" data-connectorsauthtoken="1" data-imageproxyendpoint="/actions/ei" data-imageproxyid="" alt="Facebook" style="border:none; clear:both; display:block; max-width:100%; outline:0; text-decoration:none; width:30"> </a>
																				</th>
																				<th style="margin:0 auto; color:inherit; float:none; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-right:10px; text-align:center">
																					<a href="https://www.linkedin.com/in/voices-city-33990a205" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="margin:0; color:#17b; font-family:Helvetica,Arial,sans-serif; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; text-decoration:none" data-linkindex="7"><img data-imagetype="External" src="http://voicescity.com/static/linkedin.png" originalsrc="http://go.pardot.com/l/55082/2015-09-30/3gccd7/55082/68478/SocialButton1_LI_BlueOnWhite_50X75.png" data-connectorsauthtoken="1" data-imageproxyendpoint="/actions/ei" data-imageproxyid="" alt="LinkedIn" style="border:none; clear:both; display:block; max-width:100%; outline:0; text-decoration:none; width:20"> </a>
																				</th>
																			</tr>
																		</tbody>
																	</table>
																</td>
															</tr>
														</tbody>
													</table>
												</center>
											</th>
											<th style="margin:0; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0!important; text-align:left; width:0"></th>
										</tr>
									</tbody>
								</table>
							</th>
						</tr>
					</tbody>
				</table>
			</td>
		</tr>
	</tbody>
</table>
</table>"""                                 }
                            ]
                            }
                    sg = SendGridAPIClient(api_key)
                    response = sg.client.mail.send.post(request_body=data)
                    print(response.status_code)
                    print(response.body)
                    print(response.headers)
                    # msg = Message(username + "please confirm your email address", recipients=[email])
                    # msg.html
                    # mail.send(msg)

                    session["message"] = "Please check your email to activate your account."
                    return redirect("/login")
                else:

                    session["loginerror"] = """Account with this email address already exists."""
                    session["loginusername"] = username
                    session["logincompany"] = companyname
                    session["loginemail"] = email
                    return redirect("/hiresignup")
            else:
                loginerror = "NULL"
                loginusername= ""
                logincompany= ""
                loginemail= ""
                if session.get("loginerror"):
                    loginerror = session.get("loginerror")
                    session.pop("loginerror", None)

                    loginusername = session.get("loginusername")
                    session.pop("loginusername", None)
                    logincompany = session.get("logincompany")
                    session.pop("logincompany", None)
                    loginemail = session.get("loginemail")
                    session.pop("loginemail", None)

                message = ""
                if session.get("message"):
                    message = session.get("message")
                    session.pop("message", None)
                return render_template("Hiresignup.html", loginerror=loginerror, message=message, type=None,
                                       loginusername=loginusername, logincompany=logincompany, loginemail=loginemail)
    except Exception as e:
        session["loginerror"] = str(
            e) + "/ Some thing went wrong please try later. Or you can write to us any time if you face any problem from contact us tab."
        return redirect("/hiresignup")


@app.route("/activate")
def activataccount():
    try:
        email = request.args.get("code")
        linkhash = request.args.get("hashkey")
        buyerTable = mydb["buyer"]
        actorTable = mydb["actor"]
        buyerdata = buyerTable.find_one({"email": email, "activateLink": linkhash})
        actordata = actorTable.find_one({"email": email, "activateLink": linkhash})
        if buyerdata != None and actordata == None:
            if linkhash == buyerdata["activateLink"]:
                buyerTable.update_one({"email": email}, {"$set": {"active": 1}})
                data = {
                            "personalizations": [
                                {
                                "to": [
                                    {
                                    "email": email
                                    }
                                ],
                                "subject": "Welcome to voicescity.com, " + buyerdata['userName']
                                }
                            ],
                            "from": {
                                "email": default_sender,
                                "name": "voices city"
                            },
                            "content": [
                                {
                                "type": "text/html",
                                "value":"""<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody>
			<tr>
				<td style="direction:ltr; font-size:0px; padding:20px 0; padding-bottom:32px; padding-top:32px; text-align:center; vertical-align:top;">
					<div class="x_m_185219368036138757mj-column-per-100" style="font-size:13px; text-align:left; direction:ltr; display:inline-block; vertical-align:top; width:100%;">
						<table border="0" cellpadding="0" cellspacing="0" style="vertical-align:top;" width="100%">
							<tbody>
								<tr>
									<td align="left" style="font-size:0px; padding:10px 25px; padding-top:0; word-break:break-word;">
										<div style="font-family: Roboto, sans-serif, serif, EmojiFont; font-size: 16px; font-weight: 400; line-height: 24px; text-align: left; color: rgb(79, 89, 99) !important;">Hi <span class="marklxu12zej1" data-markjs="true" data-ogab="" data-ogac="" data-ogsb="" data-ogsc="">""" + buyerdata['userName'] + """</span>,
											<br aria-hidden="true">
											<br aria-hidden="true">Welcome to <span class="marklxu12zej1" data-markjs="true" data-ogab="" data-ogac="" data-ogsb="" data-ogsc="">Voicescity</span> - the community of creators! If you&apos;re here, you must be ready to expand your professional network by hiring the most professional and qualified creative talent who are best-suited for your projects. It&apos;s always free to post a job, and you&apos;ll receive custom responses from our trusted and experienced talent within the hour. Pay securely, and only when you are ready to hire!</div>
									</td>
								</tr>
							</tbody>
						</table>
					</div>
				</td>
			</tr>
		</tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(236, 241, 245) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(236, 241, 245) !important; width: 100%;">
		<tbody>
			<tr>
				<td style="direction:ltr; font-size:0px; padding:20px 0; padding-bottom:32px; padding-top:32px; text-align:center; vertical-align:top;">
					<div class="x_m_185219368036138757mj-column-per-100" style="font-size:13px; text-align:left; direction:ltr; display:inline-block; vertical-align:top; width:100%;">
						<table border="0" cellpadding="0" cellspacing="0" style="vertical-align:top;" width="100%">
							<tbody>
								<tr>
									<td align="center" class="x_m_185219368036138757h2" style="font-size:0px; padding:10px 25px; padding-top:16px; word-break:break-word;">
										<div style="font-family: Roboto, sans-serif, serif, EmojiFont; font-size: 13px; font-weight: 500; line-height: 1; text-align: center; color: rgb(25, 34, 43) !important;">Hiring Talent is Fast and Simple:</div>
									</td>
								</tr>
							</tbody>
						</table>
					</div>
				</td>
			</tr>
		</tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(236, 241, 245) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(236, 241, 245) !important; width: 100%;">
		<tbody>
			<tr>
				<td style="direction:ltr; font-size:0px; padding:20px 0; padding-bottom:32px; padding-top:0; text-align:center; vertical-align:top;">
					<div class="x_m_185219368036138757mj-column-px-100" style="font-size:13px; text-align:left; direction:ltr; display:inline-block; vertical-align:top; width:100%;">
						<table border="0" cellpadding="0" cellspacing="0" style="vertical-align:top;" width="100%">
							<tbody>
								<tr>
									<td align="center" class="x_m_185219368036138757icon-image" style="font-size:0px; padding:10px 25px; word-break:break-word;">
										<table border="0" cellpadding="0" cellspacing="0" style="border-collapse:collapse; border-spacing:0px;">
											<tbody>
												<tr>
													<td style="width:50px;"><img data-imagetype="External" src="https://go.pardot.com/l/55082/2021-06-25/j9lzf3/55082/1624647353W1Osi3az/1.png" alt="" style="margin: 0 auto 0 0; text-align: left; display: block; outline: currentcolor none medium; text-decoration: none; width: 100%; border-width: 0px; border-style: solid;" width="100" border="0"></td>
												</tr>
											</tbody>
										</table>
									</td>
								</tr>
							</tbody>
						</table>
					</div>
					<div class="x_m_185219368036138757mj-column-per-65" style="font-size:13px; text-align:left; direction:ltr; display:inline-block; vertical-align:top; width:100%;">
						<table border="0" cellpadding="0" cellspacing="0" style="vertical-align:top;" width="100%">
							<tbody>
								<tr>
									<td align="left" class="x_m_185219368036138757h4 x_m_185219368036138757text-center-m" style="font-size:0px; padding:10px 25px; word-break:break-word;">
										<div style="font-family: Roboto, sans-serif, serif, EmojiFont; font-size: 13px; font-weight: 500; line-height: 1; text-align: left; color: rgb(25, 34, 43) !important;">Post a Job (It&apos;s Free!)</div>
									</td>
								</tr>
								<tr>
									<td align="left" class="x_m_185219368036138757text-center-m" style="font-size:0px; padding:10px 25px; padding-top:0; padding-bottom:0; word-break:break-word;">
										<div style="font-family: Roboto, sans-serif, serif, EmojiFont; font-size: 16px; font-weight: 400; line-height: 24px; text-align: left; color: rgb(79, 89, 99) !important;">Post your free job with what you&apos;re looking for and we&apos;ll send you auditions from matched professional creative talent. You&rsquo;ll get custom responses within hours!</div>
									</td>
								</tr>
							</tbody>
						</table>
					</div>
				</td>
			</tr>
		</tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(236, 241, 245) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(236, 241, 245) !important; width: 100%;">
		<tbody>
			<tr>
				<td style="direction:ltr; font-size:0px; padding:20px 0; padding-bottom:32px; padding-top:0; text-align:center; vertical-align:top;">
					<div class="x_m_185219368036138757mj-column-px-100" style="font-size:13px; text-align:left; direction:ltr; display:inline-block; vertical-align:top; width:100%;">
						<table border="0" cellpadding="0" cellspacing="0" style="vertical-align:top;" width="100%">
							<tbody>
								<tr>
									<td align="center" class="x_m_185219368036138757icon-image" style="font-size:0px; padding:10px 25px; word-break:break-word;">
										<table border="0" cellpadding="0" cellspacing="0" style="border-collapse:collapse; border-spacing:0px;">
											<tbody>
												<tr>
													<td style="width:50px;"><img data-imagetype="External" src="https://go.pardot.com/l/55082/2021-06-25/j9lzf5/55082/1624647370mFcIMSF5/2.png" alt="" style="margin: 0 auto 0 0; text-align: left; display: block; outline: currentcolor none medium; text-decoration: none; width: 100%; border-width: 0px; border-style: solid;" width="100" border="0"></td>
												</tr>
											</tbody>
										</table>
									</td>
								</tr>
							</tbody>
						</table>
					</div>
					<div class="x_m_185219368036138757mj-column-per-65" style="font-size:13px; text-align:left; direction:ltr; display:inline-block; vertical-align:top; width:100%;">
						<table border="0" cellpadding="0" cellspacing="0" style="vertical-align:top;" width="100%">
							<tbody>
								<tr>
									<td align="left" class="x_m_185219368036138757h4 x_m_185219368036138757text-center-m" style="font-size:0px; padding:10px 25px; word-break:break-word;">
										<div style="font-family: Roboto, sans-serif, serif, EmojiFont; font-size: 13px; font-weight: 500; line-height: 1; text-align: left; color: rgb(25, 34, 43) !important;">Hire &amp; Pay</div>
									</td>
								</tr>
								<tr>
									<td align="left" class="x_m_185219368036138757text-center-m" style="font-size:0px; padding:10px 25px; padding-top:0; padding-bottom:0; word-break:break-word;">
										<div style="font-family: Roboto, sans-serif, serif, EmojiFont; font-size: 16px; font-weight: 400; line-height: 24px; text-align: left; color: rgb(79, 89, 99) !important;">Listen to auditions, compare quotes, collaborate with your team, and securely message talent. Once you&apos;ve decided on the best one for your project, click to hire.</div>
									</td>
								</tr>
							</tbody>
						</table>
					</div>
				</td>
			</tr>
		</tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(236, 241, 245) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(236, 241, 245) !important; width: 100%;">
		<tbody>
			<tr>
				<td style="direction:ltr; font-size:0px; padding:20px 0; padding-bottom:32px; padding-top:0; text-align:center; vertical-align:top;">
					<div class="x_m_185219368036138757mj-column-px-100" style="font-size:13px; text-align:left; direction:ltr; display:inline-block; vertical-align:top; width:100%;">
						<table border="0" cellpadding="0" cellspacing="0" style="vertical-align:top;" width="100%">
							<tbody>
								<tr>
									<td align="center" class="x_m_185219368036138757icon-image" style="font-size:0px; padding:10px 25px; word-break:break-word;">
										<table border="0" cellpadding="0" cellspacing="0" style="border-collapse:collapse; border-spacing:0px;">
											<tbody>
												<tr>
													<td style="width:50px;"><img data-imagetype="External" src="https://go.pardot.com/l/55082/2021-06-25/j9lzf7/55082/1624647387hhGkhoKP/3.png" alt="" style="margin: 0 auto 0 0; text-align: left; display: block; outline: currentcolor none medium; text-decoration: none; width: 100%; border-width: 0px; border-style: solid;" width="100" border="0"></td>
												</tr>
											</tbody>
										</table>
									</td>
								</tr>
							</tbody>
						</table>
					</div>
					<div class="x_m_185219368036138757mj-column-per-65" style="font-size:13px; text-align:left; direction:ltr; display:inline-block; vertical-align:top; width:100%;">
						<table border="0" cellpadding="0" cellspacing="0" style="vertical-align:top;" width="100%">
							<tbody>
								<tr>
									<td align="left" class="x_m_185219368036138757h4 x_m_185219368036138757text-center-m" style="font-size:0px; padding:10px 25px; word-break:break-word;">
										<div style="font-family: Roboto, sans-serif, serif, EmojiFont; font-size: 13px; font-weight: 500; line-height: 1; text-align: left; color: rgb(25, 34, 43) !important;">Download Files</div>
									</td>
								</tr>
								<tr>
									<td align="left" class="x_m_185219368036138757text-center-m" style="font-size:0px; padding:10px 25px; padding-top:0; padding-bottom:0; word-break:break-word;">
										<div style="font-family: Roboto, sans-serif, serif, EmojiFont; font-size: 16px; font-weight: 400; line-height: 24px; text-align: left; color: rgb(79, 89, 99) !important;">Pay and download files - make your payment securely and high-quality audio or text files will be delivered to you. All of this can take as little as a day.</div>
									</td>
								</tr>
							</tbody>
						</table>
					</div>
				</td>
			</tr>
		</tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(236, 241, 245) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(236, 241, 245) !important; width: 100%;">
		<tbody>
			<tr>
				<td style="direction:ltr; font-size:0px; padding:20px 0; padding-bottom:0; text-align:center; vertical-align:top;">
					<div class="x_m_185219368036138757mj-column-per-100" style="font-size:13px; text-align:left; direction:ltr; display:inline-block; vertical-align:top; width:100%;">
						<table border="0" cellpadding="0" cellspacing="0" style="vertical-align:top;" width="100%">
							<tbody>
								<tr>
									<td style="font-size:0px; word-break:break-word;">
										<div aria-hidden="true" style="height:0px;">&nbsp;</div>
									</td>
								</tr>
							</tbody>
						</table>
					</div>
				</td>
			</tr>
		</tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody>
			<tr>
				<td style="direction:ltr; font-size:0px; padding:20px 0; padding-bottom:32px; padding-top:32px; text-align:center; vertical-align:top;">
					<div class="x_m_185219368036138757mj-column-per-100" style="font-size:13px; text-align:left; direction:ltr; display:inline-block; vertical-align:top; width:100%;">
						<table border="0" cellpadding="0" cellspacing="0" style="vertical-align:top;" width="100%">
							<tbody>
								<tr>
									<td align="center" class="x_m_185219368036138757h2" style="font-size:0px; padding:10px 25px; padding-top:16px; word-break:break-word;">
										<div style="font-family: Roboto, sans-serif, serif, EmojiFont; font-size: 13px; font-weight: 500; line-height: 1; text-align: center; color: rgb(25, 34, 43) !important;">Ready to Dive in?</div>
									</td>
								</tr>
							</tbody>
						</table>
					</div>
				</td>
			</tr>
		</tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody>
			<tr>
				<td style="direction:ltr; font-size:0px; padding:20px 0; padding-bottom:32px; padding-top:0; text-align:center; vertical-align:top;">
					<div class="x_m_185219368036138757mj-column-per-100" style="font-size:13px; text-align:left; direction:ltr; display:inline-block; vertical-align:top; width:100%;">
						<table border="0" cellpadding="0" cellspacing="0" style="vertical-align:top;" width="100%">
							<tbody>
								<tr>
									<td align="left" style="font-size:0px; padding:10px 25px; padding-top:0; word-break:break-word;">
										<div style="font-family: Roboto, sans-serif, serif, EmojiFont; font-size: 16px; font-weight: 400; line-height: 24px; text-align: left; color: rgb(79, 89, 99) !important;">Explore our service categories and check out the creative professionals who will bring your projects to life:</div>
									</td>
								</tr>
							</tbody>
						</table>
					</div>
				</td>
			</tr>
		</tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody></tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody></tbody>
	</table>
</div>
<div class="x_m_185219368036138757center-container-md" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody></tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody></tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody></tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody></tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody></tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody>
			<tr>
				<td style="direction:ltr; font-size:0px; padding:20px 0; padding-bottom:0; padding-top:0; text-align:center; vertical-align:top;">
					<div class="x_m_185219368036138757mj-column-per-45 x_m_185219368036138757card x_m_185219368036138757card-sm" style="font-size:13px; text-align:left; direction:ltr; display:inline-block; vertical-align:top; width:100%;">

					</div>
					<div class="x_m_185219368036138757mj-column-per-45 x_m_185219368036138757card x_m_185219368036138757card-sm" style="font-size:13px; text-align:left; direction:ltr; display:inline-block; vertical-align:top; width:100%;">
					</div>
					<div class="x_m_185219368036138757mj-column-per-45 x_m_185219368036138757card x_m_185219368036138757card-sm" style="font-size:13px; text-align:left; direction:ltr; display:inline-block; vertical-align:top; width:100%;">
					</div>
					<div class="x_m_185219368036138757mj-column-per-45 x_m_185219368036138757card x_m_185219368036138757card-sm" style="font-size:13px; text-align:left; direction:ltr; display:inline-block; vertical-align:top; width:100%;">
					</div>
				</td>
			</tr>
		</tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody></tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody></tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody></tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody></tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody></tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody>
			<tr>
				<td style="direction:ltr; font-size:0px; padding:20px 0; padding-bottom:0; padding-top:12px; text-align:center; vertical-align:top;">
					<div class="x_m_185219368036138757mj-column-per-100" style="font-size:13px; text-align:left; direction:ltr; display:inline-block; vertical-align:top; width:100%;">
						<table border="0" cellpadding="0" cellspacing="0" style="vertical-align:top;" width="100%">
							<tbody></tbody>
						</table>
					</div>
				</td>
			</tr>
		</tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody></tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody></tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody></tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody></tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody></tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(236, 241, 245) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(236, 241, 245) !important; width: 100%;">
		<tbody></tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody></tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(236, 241, 245) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(236, 241, 245) !important; width: 100%;">
		<tbody></tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody></tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(236, 241, 245) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(236, 241, 245) !important; width: 100%;">
		<tbody></tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody></tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody></tbody>
	</table>
</div>
<div class="x_m_185219368036138757card" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody></tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody></tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody></tbody>
	</table>
</div>
<div class="x_m_185219368036138757card" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody></tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody></tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody></tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(236, 241, 245) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(236, 241, 245) !important; width: 100%;">
		<tbody></tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(236, 241, 245) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(236, 241, 245) !important; width: 100%;">
		<tbody></tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(236, 241, 245) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(236, 241, 245) !important; width: 100%;">
		<tbody></tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody></tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody></tbody>
	</table>
</div>
<div style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody></tbody>
	</table>
</div>
<div class="x_m_185219368036138757container x_m_185219368036138757container-sm" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(236, 241, 245) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(236, 241, 245) !important; width: 100%;">
		<tbody>
			<tr>
				<td style="direction:ltr; font-size:0px; padding:20px 0; padding-bottom:0; padding-top:0; text-align:center; vertical-align:top;">
					<div class="x_m_185219368036138757mj-column-per-100" style="font-size:13px; text-align:left; direction:ltr; display:inline-block; vertical-align:top; width:100%;">
						<table border="0" cellpadding="0" cellspacing="0" style="vertical-align:top;" width="100%">
							<tbody>
								<tr>
									<td align="center" class="x_m_185219368036138757h2" style="font-size:0px; padding:10px 25px; padding-top:24px; padding-bottom:0; word-break:break-word;">
										<div style="font-family: Roboto, sans-serif, serif, EmojiFont; font-size: 13px; font-weight: 500; line-height: 1; text-align: center; color: rgb(25, 34, 43) !important;">Want to Get Started?</div>
									</td>
								</tr>
								<tr>
									<td align="center" class="x_m_185219368036138757center-container-lg" style="font-size:0px; padding:10px 25px; padding-top:0; word-break:break-word;">
										<div style="font-family: Roboto, sans-serif, serif, EmojiFont; font-size: 16px; line-height: 24px; text-align: center; color: rgb(79, 89, 99) !important;">Post your first job for free and let the professionals come right to you.</div>
									</td>
								</tr>
								<tr>
									<td align="center" class="x_m_185219368036138757btn-primary" style="font-size:0px; padding:10px 25px; padding-top:24px; padding-bottom:24px; word-break:break-word;">
										<table border="0" cellpadding="0" cellspacing="0" style="border-collapse:separate; line-height:100%;">
											<tbody>
												<tr>
													<td align="center" bgcolor="#1171bb" style="border: medium none; border-radius: 3px; padding: 10px 25px; background-color: rgb(17, 113, 187) !important; background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box;" valign="middle"><a data-auth="NotApplicable" data-linkindex="11" href="https://voicescity.com/post-job" rel="noreferrer noopener" style="background-color: rgb(17, 113, 187) !important; background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; font-family: Roboto, sans-serif; font-size: 18px; font-weight: 500; line-height: 120%; margin: 0px; text-transform: none; text-decoration: none; color: rgb(255, 255, 255) !important;" target="_blank">Post Your First Job&nbsp;</a></td>
												</tr>
											</tbody>
										</table>
									</td>
								</tr>
							</tbody>
						</table>
					</div>
				</td>
			</tr>
		</tbody>
	</table>
</div>
<div class="x_m_185219368036138757container x_m_185219368036138757container-sm" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody>
			<tr>
				<td style="direction:ltr; font-size:0px; padding:20px 0; padding-bottom:0; padding-top:0; text-align:center; vertical-align:top;">
					<div class="x_m_185219368036138757mj-column-per-100" style="font-size:13px; text-align:left; direction:ltr; display:inline-block; vertical-align:top; width:100%;">
						<table border="0" cellpadding="0" cellspacing="0" style="vertical-align:top;" width="100%">
							<tbody>
								<tr>
									<td align="center" class="x_m_185219368036138757center-container-lg" style="font-size:0px; padding:10px 25px; padding-top:0; word-break:break-word;">
										<div class="x_m_185219368036138757mj-column-per-100" style="font-size:13px; text-align:left; direction:ltr; display:inline-block; vertical-align:top; width:100%;">
											<table border="0" cellpadding="0" cellspacing="0" style="vertical-align:top;" width="100%">
												<tbody>
													<tr>
														<td align="left" style="font-size:0px; padding:10px 25px; padding-top:0; word-break:break-word;">
															<div style="font-family: Roboto, sans-serif, serif, EmojiFont; font-size: 16px; font-weight: 400; line-height: 24px; text-align: left; color: rgb(79, 89, 99) !important;">
																<br aria-hidden="true">
																<br aria-hidden="true">All the best and here to help,
																<br aria-hidden="true">
																<br aria-hidden="true"><span style="font-size:14px; text-align:left;"><span style="color: rgb(79, 89, 99) !important;"><span style="font-family: Roboto, sans-serif, serif, EmojiFont;"><span style="font-style:normal;"><span style="font-variant-ligatures:normal;"><span style="font-weight:400;"><span style="white-space:normal;"><span style="background-color: rgb(255, 255, 255) !important;"><span style="text-decoration-style:initial;"><span style="text-decoration-color:initial;"><span style="line-height:1.44;"><b style="font-weight:normal;"><span style="font-family: Arial, serif, EmojiFont;"><span style="color: rgb(0, 0, 102) !important;"><span style="font-weight:700;"><span style="font-style:normal;"><span style="font-variant:normal;"><span style="text-decoration:none;"><span style="vertical-align:baseline;"><span style="white-space:pre-wrap;">Arif</span></span>
																</span>
																</span>
																</span>
																</span>
																</span>
																</span>
																</b>
																</span>
																</span>
																</span>
																</span>
																</span>
																</span>
																</span>
																</span>
																</span>
																</span>
																</span>
																<br style="color: rgb(79, 89, 99) !important; font-family: Roboto, sans-serif; font-size: 14px; font-style: normal; font-variant-ligatures: normal; font-weight: 400; text-align: left; white-space: normal; background-color: rgb(255, 255, 255) !important; text-decoration-style: initial; text-decoration-color: initial;" aria-hidden="true"><span style="font-size:14px; text-align:left;"><span style="color: rgb(79, 89, 99) !important;"><span style="font-family: Roboto, sans-serif, serif, EmojiFont;"><span style="font-style:normal;"><span style="font-variant-ligatures:normal;"><span style="font-weight:400;"><span style="white-space:normal;"><span style="background-color: rgb(255, 255, 255) !important;"><span style="text-decoration-style:initial;"><span style="text-decoration-color:initial;"><span style="line-height:1.44;"><b style="font-weight:normal;"><span style="font-family: Arial, serif, EmojiFont;"><span style="color: rgb(102, 102, 102) !important;"><span style="font-weight:400;"><span style="font-style:normal;"><span style="font-variant:normal;"><span style="text-decoration:none;"><span style="vertical-align:baseline;"><span style="white-space:pre-wrap;">Manager, Customer Experience</span></span>
																</span>
																</span>
																</span>
																</span>
																</span>
																</span>
																</b>
																</span>
																</span>
																</span>
																</span>
																</span>
																</span>
																</span>
																</span>
																</span>
																</span>
																</span>
																<br aria-hidden="true"><b style="color: rgb(79, 89, 99) !important; font-family: Roboto, sans-serif; font-size: 14px; font-style: normal; font-variant-ligatures: normal; text-align: left; white-space: normal; background-color: rgb(255, 255, 255) !important; text-decoration-style: initial; text-decoration-color: initial; font-weight: normal;"><span style="font-family: Arial, serif, EmojiFont;"><span style="color: rgb(17, 113, 187) !important;"><span style="font-weight:700;"><span style="font-style:normal;"><span style="font-variant:normal;"><span style="text-decoration:none;"><span style="vertical-align:baseline;"><span style="white-space:pre-wrap;">Voicescity</span></span></span></span></span></span></span></span></b>
																<br aria-hidden="true"><span style="font-size:14px; text-align:left;"><span style="color: rgb(79, 89, 99) !important;"><span style="font-style:normal;"><span style="font-variant-ligatures:normal;"><span style="font-weight:400;"><span style="white-space:normal;"><span style="background-color: rgb(255, 255, 255) !important;"><span style="text-decoration-style:initial;"><span style="text-decoration-color:initial;"><span style="font-family: Arial, serif, EmojiFont;"><span style="color: rgb(102, 102, 102) !important;"><span style="font-variant-numeric:normal;"><span style="font-variant-east-asian:normal;"><span style="vertical-align:baseline;"><span style="white-space:pre-wrap;"><a data-auth="NotApplicable" data-linkindex="12" href="mailto:info@voicescity.com" rel="noreferrer noopener" target="_blank">info@<span class="marklxu12zej1" data-markjs="true" data-ogab="" data-ogac="" data-ogsb="" data-ogsc="">voicescity</span>.com</a> |</span>
																</span>
																</span>
																</span>
																</span>
																</span>
																</span>
																</span>
																</span>
																</span>
																</span>
																</span>
																</span>
																</span>
																</span><a data-auth="NotApplicable" data-linkindex="13" href="https://voicescity.com" rel="noreferrer noopener" style="color: rgb(17, 113, 187) !important; text-decoration-line: none; text-decoration-style: initial !important; text-decoration-color: initial !important; font-family: Roboto, sans-serif; font-size: 14px; font-style: normal; font-variant-ligatures: normal; font-weight: 400; text-align: left; white-space: normal; background-color: rgb(255, 255, 255) !important;" target="_blank">&nbsp;<span style="font-family: Arial, serif, EmojiFont;"><span style="color: rgb(17, 85, 204) !important;"><span style="font-variant-numeric:normal;"><span style="font-variant-east-asian:normal;"><span style="text-decoration-line:underline;"><span style="vertical-align:baseline;"><span style="white-space:pre-wrap;">www.<span class="marklxu12zej1" data-markjs="true" data-ogab="" data-ogac="" data-ogsb="" data-ogsc="">voicescity</span>.com</span></span></span></span></span></span></span></a></div>
														</td>
													</tr>
												</tbody>
											</table>
										</div>
									</td>
								</tr>
								<tr>
									<td align="center" class="x_m_185219368036138757btn-primary" style="font-size:0px; padding:10px 25px; padding-top:24px; padding-bottom:0; word-break:break-word;">
										<table border="0" cellpadding="0" cellspacing="0" style="border-collapse:separate; line-height:100%;">
											<tbody></tbody>
										</table>
									</td>
								</tr>
							</tbody>
						</table>
					</div>
				</td>
			</tr>
		</tbody>
	</table>
</div>
<div class="x_m_185219368036138757container x_m_185219368036138757container-center" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; margin: 0px auto; max-width: 598px;">
	<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-position: 0% 0%; background-repeat: repeat; background-attachment: scroll; background-image: none; background-size: auto; background-origin: padding-box; background-clip: border-box; background-color: rgb(255, 255, 255) !important; width: 100%;">
		<tbody>
			<tr>
				<td style="direction:ltr; font-size:0px; padding:20px 0; padding-bottom:32px; padding-top:32px; text-align:center; vertical-align:top;">
					<div class="x_m_185219368036138757mj-column-per-100" style="font-size:13px; text-align:left; direction:ltr; display:inline-block; vertical-align:top; width:100%;">
						<table border="0" cellpadding="0" cellspacing="0" style="vertical-align:top;" width="100%">
							<tbody>
								<tr>
									<td align="center" class="x_m_185219368036138757icon-image" style="font-size:0px; padding:10px 25px; word-break:break-word;">
										<table border="0" cellpadding="0" cellspacing="0" style="border-collapse:collapse; border-spacing:0px;">
											<tbody>
												<tr>
													<td style="width:548px;"><img data-imagetype="External" src="https://storage.pardot.com/55082/309745/deco_icon_help.png" alt="" style="margin: 0 auto 0 0; text-align: left; display: block; border: 0px none; outline: currentcolor none medium; text-decoration: none; height: auto; width: 100%;" width="548" height="auto"></td>
												</tr>
											</tbody>
										</table>
									</td>
								</tr>
								<tr>
									<td align="center" class="x_m_185219368036138757h2" style="font-size:0px; padding:10px 25px; padding-top:24px; padding-bottom:0; word-break:break-word;">
										<div style="font-family: Roboto, sans-serif, serif, EmojiFont; font-size: 13px; font-weight: 500; line-height: 1; text-align: center; color: rgb(25, 34, 43) !important;">We&rsquo;re here for you!</div>
									</td>
								</tr>
								<tr>
									<td align="center" class="x_m_185219368036138757center-container-md" style="font-size:0px; padding:10px 25px; padding-top:0; word-break:break-word;">
										<div style="font-family: Roboto, sans-serif, serif, EmojiFont; font-size: 16px; line-height: 24px; text-align: center; color: rgb(79, 89, 99) !important;">Questions? Head over to our <a data-auth="NotApplicable" data-linkindex="14" href="https://www.voicescity.com/help" rel="noreferrer noopener" target="_blank">help page</a>, check out <a data-auth="NotApplicable" data-linkindex="15" href="https://www.voicescity.com/blogs" rel="noreferrer noopener" target="_blank">our blog</a>, or email us at <a data-auth="NotApplicable" data-linkindex="16" href="mailto:support@voicescity .com" rel="noreferrer noopener" target="_blank">support@<span class="marklxu12zej1" data-markjs="true" data-ogab="" data-ogac="" data-ogsb="" data-ogsc="">voicescity</span>.com</a>.</div>
									</td>
								</tr>
							</tbody>
						</table>
					</div>
				</td>
			</tr>
		</tbody>
	</table>
</div>
<table style="margin:0 auto; border-collapse:collapse; border-spacing:0; float:none; margin:0 auto; padding:0; text-align:center; vertical-align:top; width:auto!important" align="center">
	<tbody>
		<tr style="padding:0; text-align:left; vertical-align:top">
			<td style="margin:0; border-collapse:collapse!important; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; vertical-align:top; word-wrap:break-word">
				<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
					<tbody>
						<tr style="padding:0; text-align:left; vertical-align:top">
							<th style="margin:0 auto; color:inherit; float:none; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-right:10px; text-align:center">
								<a href="https://twitter.com/VoicesCity2?s=08" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="margin:0; color:#17b; font-family:Helvetica,Arial,sans-serif; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; text-decoration:none" data-linkindex="5"><img data-imagetype="External" src="http://voicescity.com/static/twitter.png" originalsrc="http://go.pardot.com/l/55082/2015-09-30/3gccd5/55082/68476/SocialButton3_TWR_BlueOnWhite_50X75.png" data-connectorsauthtoken="1" data-imageproxyendpoint="/actions/ei" data-imageproxyid="" alt="Twitter" style="border:none; clear:both; display:block; max-width:100%; outline:0; text-decoration:none; width:20px;"> </a>
							</th>
							<th style="margin:0 auto; color:inherit; float:none; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-right:10px; text-align:center">
								<a href="https://www.facebook.com/Voices-City-332687944647576/" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="margin:0; color:#17b; font-family:Helvetica,Arial,sans-serif; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; text-decoration:none" data-linkindex="6"><img data-imagetype="External" src="http://voicescity.com/static/facebook.png" originalsrc="http://go.pardot.com/l/55082/2015-09-30/3gcccp/55082/68474/SocialButton2_FB_BlueOnWhite_50X75.png" data-connectorsauthtoken="1" data-imageproxyendpoint="/actions/ei" data-imageproxyid="" alt="Facebook" style="border:none; clear:both; display:block; max-width:100%; outline:0; text-decoration:none; width:30px;"> </a>
							</th>
							<th style="margin:0 auto; color:inherit; float:none; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-right:10px; text-align:center">
								<a href="https://www.linkedin.com/in/voices-city-33990a205" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="margin:0; color:#17b; font-family:Helvetica,Arial,sans-serif; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; text-decoration:none" data-linkindex="7"><img data-imagetype="External" src="http://voicescity.com/static/linkedin.png" originalsrc="http://go.pardot.com/l/55082/2015-09-30/3gccd7/55082/68478/SocialButton1_LI_BlueOnWhite_50X75.png" data-connectorsauthtoken="1" data-imageproxyendpoint="/actions/ei" data-imageproxyid="" alt="LinkedIn" style="border:none; clear:both; display:block; max-width:100%; outline:0; text-decoration:none; width:20px;"> </a>
							</th>
						</tr>
					</tbody>
				</table>
			</td>
		</tr>
	</tbody>
</table>""" } ] }
                sg = SendGridAPIClient(api_key)
                response = sg.client.mail.send.post(request_body=data)
            else:
                session["loginerror"] = """Unknown activation link is."""
        elif actordata != None and buyerdata == None:
            if linkhash == actordata["activateLink"]:
                actorTable.update_one({"email": email}, {"$set": {"active": 1}})
                data = {
                            "personalizations": [
                                {
                                "to": [
                                    {
                                    "email": email
                                    }
                                ],
                                "subject": "Welcome to Voicescity.com, " + actordata['userName']
                                }
                            ],
                            "from": {
                                "email": default_sender,
                                "name": "voices city"
                            },
                            "content": [
                                {
                                "type": "text/html",
                                "value":"""<p style="font-weight:bold; text-align:center;">Welcome to <span class="markcqhh5y3do" data-markjs="true" data-ogab="" data-ogac="" data-ogsb="" data-ogsc="">Voicescity</span>.com """ + actordata['userName'] +  """</p>
<p>Thanks for creating an account, we&apos;re so happy you decided to join the #1 voice-over marketplace!</p>
<p>Your username is <strong>""" + actordata['userName'] + """</strong>. If you forget this, you can always <a data-auth="NotApplicable" data-linkindex="1" href="https://www.voicescity.com/login" rel="noreferrer noopener" target="_blank">log in</a> with your email (so don&apos;t worry).</p>
<p style="font-weight:bold;">Now what?</p>
<ul>
	<li style="padding-bottom:10px;"><a data-auth="NotApplicable" data-linkindex="2" href="https://www.voicescity.com/actor-editprofile" rel="noreferrer noopener" target="_blank">Fill out your <span class="markcqhh5y3do" data-markjs="true" data-ogab="" data-ogac="" data-ogsb="" data-ogsc="">Voicescity</span>.com profile</a>
		<br aria-hidden="true">Let clients know why you&apos;re so awesome!&nbsp;</li>
	<li style="padding-bottom:10px;"><a data-auth="NotApplicable" data-linkindex="3" href="https://www.voicescity.com/actor-editprofile" rel="noreferrer noopener" target="_blank">Upload a demo</a>
		<br aria-hidden="true">Without one of these, you won&apos;t be in the search directory (making you tough to find).&nbsp;</li>
	<li><a data-auth="NotApplicable" data-linkindex="4" href="https://www.voicescity.com/actorprofile?id=""" + str(actordata['_id']) + """\" rel="noreferrer noopener" target="_blank">Share your profile</a>
		<br aria-hidden="true">Why not let everyone in your social streams know where to find you?&nbsp;</li>
</ul>
<p><span style="font-weight:bold;">Need help?</span>"""
	# <br aria-hidden="true">No worries! We have <a data-auth="NotApplicable" data-linkindex="5" href="https://www.voices.com/help" rel="noreferrer noopener" target="_blank">this handy section</a> that might be what you need. Otherwise, <a data-auth="NotApplicable" data-linkindex="6" href="https://www.voices.com/service/customer_care" rel="noreferrer noopener" target="_blank">drop us a line</a>! We&apos;re always happy to help.&nbsp;</p>
+ """<p>Stay tuned for more useful information! We look forward to working with you.</p>
<p>Welcome to <span class="markcqhh5y3do" data-markjs="true" data-ogab="" data-ogac="" data-ogsb="" data-ogsc="">Voicescity</span>.com!</p>
<p style="padding:2px;">
	<br>
</p>
<p>Sincerely yours,</p>
<p>The <span class="markcqhh5y3do" data-markjs="true" data-ogab="" data-ogac="" data-ogsb="" data-ogsc="">Voicescity</span>.com Team
	<br aria-hidden="true">Voicescity.com
	<br aria-hidden="true">Phone: +447888884150
	<br aria-hidden="true"><a data-auth="NotApplicable" data-linkindex="7" href="https://www.voicescity.com/" rel="noreferrer noopener" target="_blank">https://www.<span class="markcqhh5y3do" data-markjs="true" data-ogab="" data-ogac="" data-ogsb="" data-ogsc="">voicescity</span>.com</a></p>
<table style="margin:0 auto; border-collapse:collapse; border-spacing:0; float:none; margin:0 auto; padding:0; text-align:center; vertical-align:top; width:auto!important" align="center">
	<tbody>
		<tr style="padding:0; text-align:left; vertical-align:top">
			<td style="margin:0; border-collapse:collapse!important; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; vertical-align:top; word-wrap:break-word">
				<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
					<tbody>
						<tr style="padding:0; text-align:left; vertical-align:top">
							<th style="margin:0 auto; color:inherit; float:none; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-right:10px; text-align:center">
								<a href="https://twitter.com/VoicesCity2?s=08" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="margin:0; color:#17b; font-family:Helvetica,Arial,sans-serif; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; text-decoration:none" data-linkindex="5"><img data-imagetype="External" src="http://voicescity.com/static/twitter.png" originalsrc="http://go.pardot.com/l/55082/2015-09-30/3gccd5/55082/68476/SocialButton3_TWR_BlueOnWhite_50X75.png" data-connectorsauthtoken="1" data-imageproxyendpoint="/actions/ei" data-imageproxyid="" alt="Twitter" style="border:none; clear:both; display:block; max-width:100%; outline:0; text-decoration:none; width:20px;"> </a>
							</th>
							<th style="margin:0 auto; color:inherit; float:none; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-right:10px; text-align:center">
								<a href="https://www.facebook.com/Voices-City-332687944647576/" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="margin:0; color:#17b; font-family:Helvetica,Arial,sans-serif; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; text-decoration:none" data-linkindex="6"><img data-imagetype="External" src="http://voicescity.com/static/facebook.png" originalsrc="http://go.pardot.com/l/55082/2015-09-30/3gcccp/55082/68474/SocialButton2_FB_BlueOnWhite_50X75.png" data-connectorsauthtoken="1" data-imageproxyendpoint="/actions/ei" data-imageproxyid="" alt="Facebook" style="border:none; clear:both; display:block; max-width:100%; outline:0; text-decoration:none; width:30px;"> </a>
							</th>
							<th style="margin:0 auto; color:inherit; float:none; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-right:10px; text-align:center">
								<a href="https://www.linkedin.com/in/voices-city-33990a205" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="margin:0; color:#17b; font-family:Helvetica,Arial,sans-serif; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; text-decoration:none" data-linkindex="7"><img data-imagetype="External" src="http://voicescity.com/static/linkedin.png" originalsrc="http://go.pardot.com/l/55082/2015-09-30/3gccd7/55082/68478/SocialButton1_LI_BlueOnWhite_50X75.png" data-connectorsauthtoken="1" data-imageproxyendpoint="/actions/ei" data-imageproxyid="" alt="LinkedIn" style="border:none; clear:both; display:block; max-width:100%; outline:0; text-decoration:none; width:20px;"> </a>
							</th>
						</tr>
					</tbody>
				</table>
			</td>
		</tr>
	</tbody>
</table>""" } ] }
                sg = SendGridAPIClient(api_key)
                response = sg.client.mail.send.post(request_body=data)
            else:
                session["loginerror"] = """Unknown activation link is."""
        else:
            session["loginerror"] = """Unknown activation link is."""
        return redirect("/login")
    except Exception as e:
        session["loginerror"] = str(
            e) + "/ Some thing went wrong please try later. Or you can write to us any time if you face any problem from contact us tab."
        return redirect("/login")


# Job seeker
@app.route("/worksignup", methods=["GET", "POST"])
def worksignup():
    try:
        if session.get("email") and session.get("user") == "actor":
            return redirect("/")
        else:
            if request.method == "POST":
                email = request.json["email"]
                username = request.json["username"]
                password = request.json["password"]
                print(password)
                phoneno = request.json["phone"]
                planType = request.json["plantype"]
                planPayment = "None"
                # if planType == "standard":
                    # planPayment = request.form["paymentype"]
                password_hash = generate_password_hash(password)
                linkhash = generate_password_hash(password + email)
                buyertable = mydb["buyer"]
                actorTable = mydb["actor"]
                oldrecordbuyer = buyertable.find_one({"email": email})
                oldrecordactor = actorTable.find_one({"email": email})
                if oldrecordbuyer == None and oldrecordactor == None:
                    if planType != "standard":
                        amount = request.json["amount"]
                        print(amount)
                        try:
                            customer = stripe.Customer.create(
                                email=email,
                                source=request.json['token']
                            )
                            stripe.Charge.create(
                                customer=customer.id,
                                amount=amount,
                                currency='USD',
                                description=request.json['description']
                            )
                        except stripe.error.CardError as e:
                            session["loginerror"] = e.user_message
                            return "Failure", 500
                    actorTable.insert_one({"email": email, "userName": username, "phoneNo": phoneno,
                                           "password": password, "passwordHash": password_hash, "type": "actor",
                                           "timeStamp": datetime.now(), "active": 0, "activateLink": linkhash,
                                           "planPayment": planPayment, "planType": planType,
                                           "planDate": datetime.now()})
                    data = {
                            "personalizations": [
                                {
                                "to": [
                                    {
                                    "email": email
                                    }
                                ],
                                "subject": username + ", please confirm your email address"
                                }
                            ],
                            "from": {
                                "email": default_sender,
                                "name": "voices city"
                            },
                            "content": [
                                {
                                "type": "text/html",
                                "value": """<th style="margin:0 auto; color:#0a0a0a; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-bottom:16px; padding-left:16px; padding-right:16px; text-align:left; width:564px">
	<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
		<tbody>
			<tr style="padding:0; text-align:left; vertical-align:top">
				<th style="margin:0; color:#0a0a0a; font-family:Helvetica,Arial,sans-serif; font-size:14px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left">
					<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
						<tbody>
							<tr style="padding:0; text-align:left; vertical-align:top">
								<td style="margin:0; border-collapse:collapse!important; color:#0a0a0a; font-family:Helvetica,Arial,sans-serif; font-size:32px; font-weight:400; line-height:10px; margin:0; padding:0; text-align:left; vertical-align:top; word-wrap:break-word" height="10px">&nbsp;</td>
							</tr>
						</tbody>
					</table>
					<p style="margin:22px 0 0"><img data-imagetype="External" src=\"""" + base_url + """/static/mail.png" title="Mail Icon" alt="Mail Icon" style="margin:auto; display:block; width:80px"> </p>
					<h4 style="width:221px; height:25px; font-size:20px; font-weight:500; line-height:1.25; letter-spacing:normal; text-align:center; margin:24px auto auto">Let's confirm your email! </h4>
					<hr style="width:520px; height:1px; background-color:#c9d0d9; border:none; margin-top:40px">
					<div style="padding:0 24px">
						<p style="font-size:16px; font-weight:normal; font-stretch:normal; font-style:normal; line-height:1.5; letter-spacing:normal; color:#4f5963; margin-top:30px; margin-bottom:30px">Hi """ + username + """,</p>
						<p style="font-size:16px; font-weight:normal; font-stretch:normal; font-style:normal; line-height:1.5; letter-spacing:normal; color:#4f5963; margin-top:30px; margin-bottom:30px">Thank you for creating a Voicescity.com account. In order to complete the registration process, please click the button below to verify your email address: </p><a href='""" + base_url + """/activate?code=""" + email + """&hashkey=""" + linkhash + """' target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="border-radius:4px; background-color:#1171bb; font-size:18px; padding:12px 24px; color:white; margin:10px 0; display:inline-block; text-decoration:none" data-linkindex="1">Verify Your Email </a>
						<p style="font-size:16px; font-weight:normal; font-stretch:normal; font-style:normal; line-height:1.5; letter-spacing:normal; color:#4f5963; margin-top:30px; margin-bottom:30px">Once you’ve verified your email you’ll gain full access to your Voicescity.com account. The verification link will expire 24 hours after your original registration request was submitted. </p>
						<p style="font-size:16px; font-weight:normal; font-stretch:normal; font-style:normal; line-height:1.5; letter-spacing:normal; color:#4f5963; margin-top:30px; margin-bottom:30px">If you experience any issues or have questions regarding your Voicescity.com account, please contact us at <a href="mailto:support@voicescity.com" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="color:#1171bb" data-linkindex="2">support@voicescity.com</a>, or at <span style="color:#1171bb">+447888884150</span> (Monday to Friday, 8:00 AM to 8:00 PM EST). </p>
						<p style="font-size:16px; font-weight:normal; font-stretch:normal; font-style:normal; line-height:1.5; letter-spacing:normal; color:#4f5963; margin-top:30px; margin-bottom:30px">Thank You.</p><strong><span style="color:#000066">Customer Support Team</span></strong>
						<br aria-hidden="true"><strong><span style="color:#1171bb">Voicescity.com</span></strong>
						<br aria-hidden="true">+447888884150
						<br aria-hidden="true"><a href="mailto:support@voicescity.com" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" data-linkindex="3">support@voicescity.com</a> | <a href="https://voicescity.com/" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" data-linkindex="4">voicescity.com</a> </div>
				</th>
				<th style="margin:0; color:#0a0a0a; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0!important; text-align:left; width:0"></th>
			</tr>
		</tbody>
	</table>
</th>
<table style="margin:0 auto; background:#ffffff; border:1px solid #ccc; border-collapse:collapse; border-spacing:0; border:none; color:grey; float:none; margin:0 auto; padding:0; text-align:center; vertical-align:top; width:600px" align="center">
	<tbody>
		<tr style="padding:0; text-align:left; vertical-align:top">
			<td style="margin:0; border-collapse:collapse!important; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; vertical-align:top; word-wrap:break-word">
				<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
					<tbody>
						<tr style="padding:0; text-align:left; vertical-align:top">
							<td style="margin:0; border-collapse:collapse!important; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:15px; font-weight:400; line-height:15px; margin:0; padding:0; text-align:left; vertical-align:top; word-wrap:break-word" height="15px">&nbsp;</td>
						</tr>
					</tbody>
				</table>
				<table style="border-collapse:collapse; border-spacing:0; display:table; padding:0; text-align:left; vertical-align:top; width:100%">
					<tbody>
						<tr style="padding:0; text-align:left; vertical-align:top">
							<th style="margin:0 auto; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-bottom:0; padding-left:16px; padding-right:16px; text-align:left; width:564px">
								<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
									<tbody>
										<tr style="padding:0; text-align:left; vertical-align:top">
											<th style="margin:0; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left">
												<center style="min-width:532px; width:100%"><span align="center" style="font-size:12px">LET'S BE FRIENDS</span></center>
											</th>
											<th style="margin:0; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0!important; text-align:left; width:0"></th>
										</tr>
									</tbody>
								</table>
							</th>
						</tr>
					</tbody>
				</table>
				<table style="border-collapse:collapse; border-spacing:0; display:table; padding:0; text-align:left; vertical-align:top; width:100%">
					<tbody>
						<tr style="padding:0; text-align:left; vertical-align:top">
							<th style="margin:0 auto; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-left:27px; padding-right:16px; text-align:left; width:564px">
								<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
									<tbody>
										<tr style="padding:0; text-align:left; vertical-align:top">
											<th style="margin:0; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left">
												<center style="min-width:532px; width:100%">
													<table style="margin:0 auto; border-collapse:collapse; border-spacing:0; float:none; margin:0 auto; padding:0; text-align:center; vertical-align:top; width:auto!important" align="center">
														<tbody>
															<tr style="padding:0; text-align:left; vertical-align:top">
																<td style="margin:0; border-collapse:collapse!important; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; vertical-align:top; word-wrap:break-word">
																	<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
																		<tbody>
																			<tr style="padding:0; text-align:left; vertical-align:top">
																				<th style="margin:0 auto; color:inherit; float:none; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-right:10px; text-align:center">
																					<a href="https://twitter.com/VoicesCity2?s=08" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="margin:0; color:#17b; font-family:Helvetica,Arial,sans-serif; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; text-decoration:none" data-linkindex="5"><img data-imagetype="External" src="http://voicescity.com/static/twitter.png" originalsrc="http://go.pardot.com/l/55082/2015-09-30/3gccd5/55082/68476/SocialButton3_TWR_BlueOnWhite_50X75.png" data-connectorsauthtoken="1" data-imageproxyendpoint="/actions/ei" data-imageproxyid="" alt="Twitter" style="border:none; clear:both; display:block; max-width:100%; outline:0; text-decoration:none; width:20px;"> </a>
																				</th>	
																				<th style="margin:0 auto; color:inherit; float:none; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-right:10px; text-align:center">
																					<a href="https://www.facebook.com/Voices-City-332687944647576/" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="margin:0; color:#17b; font-family:Helvetica,Arial,sans-serif; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; text-decoration:none" data-linkindex="6"><img data-imagetype="External" src="http://voicescity.com/static/facebook.png" originalsrc="http://go.pardot.com/l/55082/2015-09-30/3gcccp/55082/68474/SocialButton2_FB_BlueOnWhite_50X75.png" data-connectorsauthtoken="1" data-imageproxyendpoint="/actions/ei" data-imageproxyid="" alt="Facebook" style="border:none; clear:both; display:block; max-width:100%; outline:0; text-decoration:none; width:30px"> </a>
																				</th>
																				<th style="margin:0 auto; color:inherit; float:none; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-right:10px; text-align:center">
																					<a href="https://www.linkedin.com/in/voices-city-33990a205" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="margin:0; color:#17b; font-family:Helvetica,Arial,sans-serif; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; text-decoration:none" data-linkindex="7"><img data-imagetype="External" src="http://voicescity.com/static/linkedin.png" originalsrc="http://go.pardot.com/l/55082/2015-09-30/3gccd7/55082/68478/SocialButton1_LI_BlueOnWhite_50X75.png" data-connectorsauthtoken="1" data-imageproxyendpoint="/actions/ei" data-imageproxyid="" alt="LinkedIn" style="border:none; clear:both; display:block; max-width:100%; outline:0; text-decoration:none; width:20px;"> </a>
																				</th>
																			</tr>
																		</tbody>
																	</table>
																</td>
															</tr>
														</tbody>
													</table>
												</center>
											</th>
											<th style="margin:0; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0!important; text-align:left; width:0"></th>
										</tr>
									</tbody>
								</table>
							</th>
						</tr>
					</tbody>
				</table>
			</td>
		</tr>
	</tbody>
</table>
</table>"""                                 }
                            ]
                            }
                    sg = SendGridAPIClient(api_key)
                    response = sg.client.mail.send.post(request_body=data)
                    print(response.status_code)
                    print(response.body)
                    print(response.headers)
                    
                    # response = sg.send(message)
                    # print(response.status_code)
                    # print(response.body)
                    # print(response.headers)
                    session["message"] = "Please check your email to activate your account."
                    return "Success"
                    return redirect("/login")

                else:
                    session["loginerror"] = """Account with this email address already exists."""
                    session["loginemail"] = email
                    session["loginphoneno"] = phoneno
                    session["loginusername"] = ""
                    return redirect("/worksignup")
            else:
                loginerror = "NULL"
                loginemail = ""
                loginphoneno = ""
                loginusername = ""
                if session.get("loginerror"):
                    loginerror = session.get("loginerror")
                    session.pop("loginerror", None)
                    loginemail = session.get("loginemail")
                    session.pop("loginemail", None)
                    loginphoneno = session.get("loginphoneno")
                    session.pop("loginphoneno", None)
                    loginusername = session.get("loginusername")
                    session.pop("loginusername", None)
                message = ""
                if session.get("message"):
                    message = session.get("message")
                    session.pop("message", None)
                plantype = None
                if request.args.get("plantype"):
                    plantype = request.args.get("plantype")
                else:
                    if loginerror == "NULL" and message == "":
                        return redirect(url_for("plans"))
                return render_template("Worksignup.html", loginerror=loginerror, type=None,
                                       plantype=plantype, message=message, loginemail=loginemail,
                                       loginphoneno=loginphoneno, loginusername=loginusername,key=stripe_keys['publishable_key'])
    except Exception as e:
        session["loginerror"] = str(
            e) + "/ Some thing went wrong please try later. Or you can write to us any time if you face any problem from contact us tab."
        return redirect("/worksignup")


# Normal login
@app.route("/login", methods=["GET", "POST"])
def login():
    try:
        if request.method == "POST":
            data = request.form
            email = data["email"]
            password = data["password"]
            buyerTable = mydb["buyer"]
            actorTable = mydb["actor"]
            buyerdata = buyerTable.find_one({"email": email})
            actordata = actorTable.find_one({"email": email})
            if buyerdata != None and actordata == None:
                if int(buyerdata["active"]) == 1:
                    if check_password_hash(buyerdata["passwordHash"], password):
                        session["email"] = email
                        session["username"] = buyerdata["userName"]
                        session["type"] = "buyer"
                        session["userid"] = str(buyerdata["_id"])
                        return redirect("/home")
                    else:
                        session["loginemail"] = email
                        session["loginerror"] = "Password is incorrect."
                        return redirect("/login")
                else:
                    session["loginerror"] = "Your account is not active."
                    return redirect("/login")
            elif actordata != None and buyerdata == None:
                if int(actordata["active"]) == 1:
                    if check_password_hash(actordata["passwordHash"], password):
                        session["email"] = email
                        session["username"] = actordata["userName"]
                        session["type"] = "actor"
                        session["userid"] = str(actordata["_id"])
                        return redirect("/actor-home")
                    else:
                        session["loginemail"] = email
                        session["loginerror"] = "Password is incorrect."
                        return redirect("/login")
                else:
                    session["loginerror"] = "Your account is not active."
                    return redirect("/login")
            else:
                session["loginemail"] = email
                session["loginerror"] = "Email or Password is incorrect."
                return redirect("/login")
        else:
            loginerror = "NULL"
            if session.get("loginerror"):
                loginerror = session.get("loginerror")
                session.pop("loginerror", None)
            loginemail = ""
            if session.get("loginemail"):
                loginemail = session.get("loginemail")
                session.pop("loginemail", None)
            message = ""
            if session.get("message"):
                message = session.get("message")
                session.pop("message", None)
            return render_template("login.html", loginerror=loginerror, loginemail=loginemail, message=message,
                                   type=None)
    except Exception as e:
        session["loginerror"] = str(
            e) + "/ Some thing went wrong please try later. Or you can write to us any time if you face any problem from contact us tab."
        return redirect("/login")

@app.route('/forget_password',methods=["GET", "POST"])
def forget_password():
    try:
        if request.method == "POST":
            data = request.form
            email = data["email"]
            # number = data["number"]
            buyerTable = mydb["buyer"]
            actorTable = mydb["actor"]
            buyerdata = buyerTable.find_one({"email": email})
            actordata = actorTable.find_one({"email": email})
            # print("buyerdata", buyerdata)
            # print("actordata", actordata)
            # print(type(email),email)

            if buyerdata != None and actordata == None:
                if int(buyerdata["active"]) == 1:
                    newpass = id_generator()
                    hashpassword = generate_password_hash(newpass)
                    buyerTable.update_one({"email": email}, {"$set": {"password": newpass,"passwordHash":hashpassword}})
                    data = {
                            "personalizations": [
                                {
                                "to": [
                                    {
                                    "email": email
                                    }
                                ],
                                "subject": "Reset Password"
                                }
                            ],
                            "from": {
                                "email": default_sender,
                                "name": "voices city"
                            },
                            "content": [
                                {
                                "type": "text/html",
                                "value":"""Hi, <br>You can find you new password below:<br><br> <strong>Password: """ + str(
                        newpass) + """</strong>
                        <p> You change your password by clicking <a href="https://www.voicescity.com/change_password" style="color:blue;">here</a></p> 
                            <br><br> Regards, <br>Voices City""" }
                            ]
                            }
                    # msg = Message("Reset Password", recipients=[email])

                    # msg.html = """Hi, <br>You can find you new password below:<br><br> <strong>Password: """ + str(
                    #     newpass) + """</strong> 
                    #         <br><br> Regards, <br>Voices City"""
                    # mail.send(msg)
                    sg = SendGridAPIClient(api_key)
                    response = sg.client.mail.send.post(request_body=data)
                    session["message"] = "Please check your email for new password."
                    return redirect("/forget_password")
                else:
                    return redirect("/forget_password")

            elif actordata != None and buyerdata == None:
                if int(actordata["active"]) == 1:

                    newpass = id_generator()
                    hashpassword = generate_password_hash(newpass)
                    actorTable.update_one({"email": email}, {"$set": {"password": newpass,"passwordHash": hashpassword}})
                    data = {
                            "personalizations": [
                                {
                                "to": [
                                    {
                                    "email": email
                                    }
                                ],
                                "subject": "Reset Password"
                                }
                            ],
                            "from": {
                                "email": default_sender,
                                "name": "voices city"
                            },
                            "content": [
                                {
                                "type": "text/html",
                                "value":"""Hi, <br>You can find you new password below:<br><br> <strong>Password: """ + str(
                        newpass) + """</strong>
                        <p> You change your password by clicking <a href="https://www.voicescity.com/change_password" style="color:blue;">here</a></p>  
                            <br><br> Regards, <br>Voices City""" }
                            ]
                            }
                    # msg = Message("Reset Password", recipients=[email])

                    # msg.html = """Hi, <br>You can find you new password below:<br><br> <strong>Password: """ + str(
                    #     newpass) + """</strong> 
                    #         <br><br> Regards, <br>Voices City"""
                    # mail.send(msg)
                    sg = SendGridAPIClient(api_key)
                    response = sg.client.mail.send.post(request_body=data)
                    session["message"] = "Please check your email for new password."
                    return redirect("/forget_password")

                else:
                    session["loginerror"] = "Your account is not active.Please check your email to activate your account."
                    return redirect("/forget_password")
            else:
                session["loginerror"] = "Email or Password is incorrect."
                return redirect("/forget_password")
        else:
            loginerror = "NULL"
            if session.get("loginerror"):
                loginerror = session.get("loginerror")
                session.pop("loginerror", None)
            loginemail = ""
            if session.get("loginemail"):
                loginemail = session.get("loginemail")
                session.pop("loginemail", None)
            message = ""
            if session.get("message"):
                message = session.get("message")
                session.pop("message", None)
            return render_template("forget_password.html", loginerror=loginerror, loginemail=loginemail, message=message,
                                   type=None)
    except Exception as e:
        session["loginerror"] = str(
            e) + "/ Some thing went wrong please try later. Or you can write to us any time if you face any problem from contact us tab."
        return redirect("/forget_password")

# Buyer Home page (Job poster or Hire a worker)
@app.route("/home", methods=["GET", "POST"])
def account():
    try:
        if session.get("email") and session.get("type") == "buyer" \
                and session.get("username"):
            if request.method == "POST":
                return redirect("/home")
            else:
                username = session.get("username")
                email = session.get("email")
                type = session.get("type")
                error = ""
                if session.get("error"):
                    error = session.get("error")
                    session.pop("error", None)
                message = ""
                if session.get("message"):
                    message = session.get("message")
                    session.pop("message", None)
                return render_template("buyerhome.html", username=username, email=email,
                                       type=type, error=error, message=message)
        else:
            return redirect("/login")
    except Exception as e:
        session["error"] = str(e)
        return redirect(url_for("account"))


# Buyer Profile edit.
@app.route("/editprofile", methods=["GET", "POST"])
def editprofile():
    try:
        if session.get("email") and session.get("type") == "buyer" and session.get("username"):
            if request.method == "POST":
                email = session.get("email")
                type = session.get("type")
                userid = session.get("userid")
                if type == "buyer":
                    table = mydb["buyer"]
                elif type == "actor":
                    table = mydb["actor"]
                else:
                    session["error"] = "Invalid user type error"
                    return redirect(url_for("editprofile"))
                data = request.form
                user_name = data["userName"]
                user_email = data["userEmail"]
                user_contact = data["userContact"]
                user_password = data["userPassword"]
                user_company = data["userCompany"]
                user_city = data["userCity"]
                user_country = data["userCountry"]
                if "userImage" in request.files:
                    user_file = request.files["userImage"]
                if user_email == email:
                    hashpassword = generate_password_hash(user_password)
                    filename1 = "profile.png"
                    if "userImage" in request.files:
                        if user_file.filename != "":
                            filename1 = secure_filename(user_file.filename)
                            filename1 = str(datetime.now().strftime("%Y%m%d-%H%M")) + "_" + filename1
                            user_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
                    table.update_one({"email": email, "_id": ObjectId(userid)},
                                     {"$set":
                                          {"userName": user_name, "companyName": user_company,
                                           "password": user_password,
                                           "passwordHash": hashpassword, "user_city": user_city,
                                           "user_country": user_country, "user_contact": user_contact,
                                           "userImage": filename1}
                                      })
                    session["message"] = "Profile Updated successfully."
                    return redirect(url_for("editprofile"))
                else:
                    session["error"] = "Email not matched."
                    return redirect(url_for("editprofile"))
            else:
                username = session.get("username")
                email = session.get("email")
                type = session.get("type")
                if type == "buyer":
                    buyerTable = mydb["buyer"]
                    data = buyerTable.find_one({"email": email})
                elif type == "actor":
                    actorTable = mydb["actor"]
                    data = actorTable.find_one({"email": email})
                else:
                    session["error"] = "Invalid type user error."
                    return redirect('/home')
                if data != None and data != ():
                    name_user = data["userName"]
                    email_user = data["email"]
                    password_user = data["password"]
                    company_user = ""
                    if type == "buyer":
                        company_user = data["companyName"]
                    if "user_contact" in data and "user_country" in data and "user_city" in data and "userImage" in data:
                        city_user = data["user_city"]
                        country_user = data["user_country"]
                        contact_user = data["user_contact"]
                        image_user = data["userImage"]
                    else:
                        city_user = ""
                        country_user = ""
                        contact_user = ""
                        image_user = ""
                    error = ""
                    if session.get("error"):
                        error = session.get("error")
                        session.pop("error", None)
                    message = ""
                    if session.get("message"):
                        message = session.get("message")
                        session.pop("message", None)
                    languages, countries, dead_line, categories, delivery_options, proposals, accents = fetch_record()
                    return render_template("editprofile.html", username=username, email=email, type=type,
                                           name_user=name_user, email_user=email_user, password_user=password_user,
                                           company_user=company_user, city_user=city_user, country_user=country_user,
                                           contact_user=contact_user, image_user=image_user, error=error,
                                           message=message, countries=countries,data=data)
                else:
                    error = "Some thing went wrong."
                    if session.get("error"):
                        error = session.get("error")
                        session.pop("error", None)
                    message = ""
                    if session.get("message"):
                        message = session.get("message")
                        session.pop("message", None)
                    return render_template("editprofile.html", username=username, email=email, type=type,
                                           error=error, message=message)
        else:
            return redirect(url_for("login"))
    except Exception as e:
        session["error"] = "Some thing went wrong please or contact admin. (" + str(e) + ")."
        return redirect(url_for("show_error"))

@app.route("/editbankinfo", methods=["POST"])
def editbankinfo():
    if request.method == "POST":

        bankName = request.form["bankName"]
        accountTitle = request.form["accountTitle"]
        accountNo = request.form["accountNo"]
        ibannumber = request.form["ibannumber"]
        swiftcode = request.form["swiftcode"]
        email = session.get("email")
        type = session.get("type")
        userid = session.get("userid")
        print(type)
        if type == "buyer":
            table = mydb["buyer"]
        elif type == "actor":
            table = mydb["actor"]
        else:
            session["error"] = "Invalid user type error"
            return redirect(url_for("editprofile"))

        table.update_one({"_id": ObjectId(userid)}, {"$set":{"bankName": bankName, "accountTitle": accountTitle,
                                                             "accountNo": accountNo, "ibannumber": ibannumber,
                                                             "swiftcode": swiftcode, "bankStatus": "completed"}})
        if type == "actor":
            return redirect("/actor-editprofile")
        else:
            return redirect("/editprofile")

# Post a new Job by the buyer. as a draft.
@app.route("/post-job", methods=["GET", "POST"])
def postjob():
    # try:
        if session.get("email") and session.get("type") == "buyer" and session.get("username"):
            if request.method == "POST":
                files = request.files
                email = session.get("email")
                usertype = session.get("type")
                data = request.form
                project_name = data["projectName"]
                project_description = data["projectDescription"]
                project_usage = data["projectUsage"]
                project_language = data.getlist("projectLanguage")
                project_accent = data.getlist("projectAccent")
                project_gender_age = data.getlist("projectGenderAge")
                project_length = data["projectLength"]
                project_length_type = data["projectLengthType"]
                project_delivery_option = data.getlist("projectDeliveryOption")
                project_script = data["inputscript"]
                project_script_file = files["scriptFile"]
                # project_custom_audition = data["projectCustomAudition"]
                project_deadline = data.getlist("projectDeadline")
                project_proposal = data.getlist("projectProposal")
                project_budget = data["projectBudget"]

                if project_budget == "variable":
                    project_cost = data["projectCost1"]
                elif project_budget == "fixed":
                    project_cost = data["projectCost"]
                if usertype == "buyer":
                    table = mydb["buyer"]
                else:
                    session["error"] = "Invalid user type error"
                    return redirect(url_for("postjob"))
                buyer_id = session.get("userid")
                scriptFile = ""
                if project_script_file.filename != "":
                    # scriptFile = project_script_file.filename
                    scriptFile = secure_filename(project_script_file.filename)
                    scriptFile = str(project_name).replace("-", "") + "-" + str(scriptFile).replace("-", "")
                    project_script_file.save(os.path.join(app.config['UPLOAD_FOLDER4'], str(scriptFile)))
                mydic1 = {"project_name": project_name, "project_description": project_description,
                          "project_usage": project_usage, "project_language": project_language,
                          "project_gender_age": project_gender_age, "project_length": project_length,
                          "project_length_type": project_length_type, "project_accent": project_accent,
                          "project_delivery_option": project_delivery_option,
                          "project_deadline": project_deadline, "project_proposal": project_proposal,
                          "project_budget": project_budget, "project_cost": project_cost,
                          "timestamp": datetime.now(), "status": "draft", "project_id": ObjectId(),
                          "paymentStatus": "unpaid", "script file": scriptFile, "script": project_script, "live": False}
                table.update({"_id": ObjectId(buyer_id)},
                             {'$addToSet': {"projects": mydic1}})
                table.update_one({"_id": ObjectId(buyer_id)},
                                 {"$inc": {"scout_payment": int(project_cost)}})
                session["message"] = "Added successfully."
                return redirect(url_for("projects"))
            else:
                username = session.get("username")
                email = session.get("email")
                type = session.get("type")
                table = mydb["category"]
                categories = table.find({})
                error = ""
                if session.get("error"):
                    error = session.get("error")
                    session.pop("error", None)
                message = ""
                if session.get("message"):
                    message = session.get("message")
                    session.pop("message", None)
                languages, countries, dead_line, categories, delivery_options, proposals, accents = fetch_record()
                min_date = str(datetime.now()).split(" ")[0]
                return render_template("postjob.html", username=username, email=email,
                                       type=type, categories=categories, error=error, message=message,
                                       dead_line=dead_line, delivery_options=delivery_options,
                                       languages=languages, proposals=proposals, accents=accents,
                                       min_date=min_date)
        else:
            return redirect("/login")
    # except Exception as e:
    #     session["error"] = str(e) + str(".\t\tRoute: /post-job")
    #     return redirect(url_for("show_error"))


# Post a new Job by the buyer after paying.
@app.route("/post-job-payment", methods=["GET", "POST"])
def postjob_payment():
    try:
        if session.get("email") and session.get("type") == "buyer" and session.get("username"):
            if request.method == "POST":
                try:
                    email = session.get("email")
                    usertype = session.get("type")
                    data = request.form
                    files = ""
                    if 'scriptFile' in request.files:
                        files = request.files["scriptFile"]
                    project_name = data["projectName"]
                    project_description = data["projectDescription"]
                    project_usage = data["projectUsage"]
                    project_language = data["projectLanguage"]
                    project_language = project_language.split(',')
                    project_accent = data["projectAccent"]
                    project_accent = project_accent.split(',')
                    project_gender_age = data["projectGenderAge"]
                    project_gender_age2 = data["projectGenderAge1"]
                    project_gender_age3 = data["projectGenderAge2"]
                    project_gender_age = project_gender_age + "," + project_gender_age2 + "," + project_gender_age3
                    project_gender_age = project_gender_age.split(',')
                    project_length = data["projectLength"]
                    project_length_type = data["projectLengthType"]
                    project_script = data["inputscript"]
                    # project_script_file = files["scriptFile"]
                    project_delivery_option = data["projectDeliveryOption"]
                    project_delivery_option = project_delivery_option.split(',')
                    # project_custom_audition = data["projectCustomAudition"]
                    project_deadline = data.getlist("projectDeadline")
                    project_proposal = data.getlist("projectProposal")
                    # project_proposal = list(project_proposal)
                    project_budget = data["projectBudget"]
                    project_cost = data["projectCost"]

                    project_bank = data["bankId"]
                    project_account = data["bankAccount"]
                    project_amount = data["bankAmount"]
                    scriptFile = ""
                    if 'scriptFile' in request.files:
                        if files.filename != "":
                            # scriptFile = project_script_file.filename
                            scriptFile = secure_filename(files.filename)
                            # scriptFile = str(project_name) + " - " + str(scriptFile)
                            scriptFile = str(project_name).replace("-", "") + "-" + str(scriptFile).replace("-", "")
                            files.save(os.path.join(app.config['UPLOAD_FOLDER4'], str(scriptFile)))

                    if usertype == "buyer":
                        table = mydb["buyer"]
                    else:
                        session["error"] = "Invalid user type error"
                        return redirect(url_for("postjob"))
                    buyer_id = session.get("userid")
                    mydic1 = {"project_name": project_name, "project_description": project_description,
                              "project_usage": project_usage, "project_language": project_language,
                              "project_gender_age": project_gender_age, "project_length": project_length,
                              "project_length_type": project_length_type,
                              "project_delivery_option": project_delivery_option, "project_accent": project_accent,
                              "project_deadline": project_deadline, "project_proposal": project_proposal,
                              "project_budget": project_budget, "project_cost": project_cost,
                              "timestamp": datetime.now(), "status": "draft", "project_id": ObjectId(),
                              "paymentStatus": "unpaid", "script file": scriptFile, "script": project_script,"live":True}
                            #   "paymentDetail": {
                            #       "bank": project_bank, "account": project_account, "amount": project_amount,
                            #       "timestamp": datetime.now()
                            #   }}
                    table.update({"_id": ObjectId(buyer_id)},
                                 {'$addToSet': {"projects": mydic1}})
                    table.update_one({"_id": ObjectId(buyer_id)},
                                     {"$inc": {"scout_payment": int(project_cost)}})

                    buyer_data = table.find_one({"_id": ObjectId(buyer_id)})
                    session["message"] = "Added successfully."
                    data = {
                            "personalizations": [
                                {
                                "to": [
                                    {
                                    "email": email
                                    }
                                ],
                                "subject": "Project Status"
                                }
                            ],
                            "from": {
                                "email": default_sender,
                                "name": "voices city"
                            },
                            "content": [
                                {
                                "type": "text/html",
                                "value": """<th style="margin:0 auto; color:#0a0a0a; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-bottom:16px; padding-left:16px; padding-right:16px; text-align:left; width:564px">
	<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
		<tbody>
			<tr style="padding:0; text-align:left; vertical-align:top">
				<th style="margin:0; color:#0a0a0a; font-family:Helvetica,Arial,sans-serif; font-size:14px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left">
					<p><strong>Your project: """ + project_name + """</strong></p>
					<p>Hello """ + buyer_data['userName'] + """,</p>
					<p>Thank you for posting a project on Voicescity!</p>
					<p>Our client success team is currently reviewing your project. You can check its status in the <a href="https://www.voicescity.com/projects" style="color:blue;"> project dashboard.</a></p>
					<p>If you have any questions, please feel free to <a href="mailto:support@voicescity.com" style="color: blue">contact us.</a></p>
					<p>Kind Regards,</p>
					<p><strong>Voicescity Team </strong>
						<p>
							<br aria-hidden="true"><strong><span style="color:#1171bb">Voicescity.com</span></strong>
							<br aria-hidden="true">+447888884150
							<br aria-hidden="true"><a href="mailto:support@voicescity.com" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" data-linkindex="3">support@voicescity.com</a> | <a href="https://voicescity.com/" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" data-linkindex="4">voicescity.com</a> </div>
				</th>
				<th style="margin:0; color:#0a0a0a; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0!important; text-align:left; width:0"></th>
			</tr>
		</tbody>
	</table>
</th>
<table style="margin:0 auto; background:#ffffff; border:1px solid #ccc; border-collapse:collapse; border-spacing:0; border:none; color:grey; float:none; margin:0 auto; padding:0; text-align:center; vertical-align:top; width:600px" align="center">
	<tbody>
		<tr style="padding:0; text-align:left; vertical-align:top">
			<td style="margin:0; border-collapse:collapse!important; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; vertical-align:top; word-wrap:break-word">
				<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
					<tbody>
						<tr style="padding:0; text-align:left; vertical-align:top">
							<td style="margin:0; border-collapse:collapse!important; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:15px; font-weight:400; line-height:15px; margin:0; padding:0; text-align:left; vertical-align:top; word-wrap:break-word" height="15px">&nbsp;</td>
						</tr>
					</tbody>
				</table>
				<table style="border-collapse:collapse; border-spacing:0; display:table; padding:0; text-align:left; vertical-align:top; width:100%">
					<tbody>
						<tr style="padding:0; text-align:left; vertical-align:top">
							<th style="margin:0 auto; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-bottom:0; padding-left:16px; padding-right:16px; text-align:left; width:564px">
								<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
									<tbody>
										<tr style="padding:0; text-align:left; vertical-align:top">
											<th style="margin:0; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left">
												<center style="min-width:532px; width:100%"><span align="center" style="font-size:12px">LET'S BE FRIENDS</span></center>
											</th>
											<th style="margin:0; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0!important; text-align:left; width:0"></th>
										</tr>
									</tbody>
								</table>
							</th>
						</tr>
					</tbody>
				</table>
				<table style="border-collapse:collapse; border-spacing:0; display:table; padding:0; text-align:left; vertical-align:top; width:100%">
					<tbody>
						<tr style="padding:0; text-align:left; vertical-align:top">
							<th style="margin:0 auto; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-left:27px; padding-right:16px; text-align:left; width:564px">
								<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
									<tbody>
										<tr style="padding:0; text-align:left; vertical-align:top">
											<th style="margin:0; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left">
												<center style="min-width:532px; width:100%">
													<table style="margin:0 auto; border-collapse:collapse; border-spacing:0; float:none; margin:0 auto; padding:0; text-align:center; vertical-align:top; width:auto!important" align="center">
														<tbody>
															<tr style="padding:0; text-align:left; vertical-align:top">
																<td style="margin:0; border-collapse:collapse!important; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; vertical-align:top; word-wrap:break-word">
																	<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
																		<tbody>
																			<tr style="padding:0; text-align:left; vertical-align:top">
																				<th style="margin:0 auto; color:inherit; float:none; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-right:10px; text-align:center">
																					<a href="https://twitter.com/VoicesCity2?s=08" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="margin:0; color:#17b; font-family:Helvetica,Arial,sans-serif; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; text-decoration:none" data-linkindex="5"><img data-imagetype="External" src="http://voicescity.com/static/twitter.png" originalsrc="http://go.pardot.com/l/55082/2015-09-30/3gccd5/55082/68476/SocialButton3_TWR_BlueOnWhite_50X75.png" data-connectorsauthtoken="1" data-imageproxyendpoint="/actions/ei" data-imageproxyid="" alt="Twitter" style="border:none; clear:both; display:block; max-width:100%; outline:0; text-decoration:none; width:20px;"> </a>
																				</th>
																				<th style="margin:0 auto; color:inherit; float:none; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-right:10px; text-align:center">
																					<a href="https://www.facebook.com/Voices-City-332687944647576/" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="margin:0; color:#17b; font-family:Helvetica,Arial,sans-serif; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; text-decoration:none" data-linkindex="6"><img data-imagetype="External" src="http://voicescity.com/static/facebook.png" originalsrc="http://go.pardot.com/l/55082/2015-09-30/3gcccp/55082/68474/SocialButton2_FB_BlueOnWhite_50X75.png" data-connectorsauthtoken="1" data-imageproxyendpoint="/actions/ei" data-imageproxyid="" alt="Facebook" style="border:none; clear:both; display:block; max-width:100%; outline:0; text-decoration:none; width:30px;"> </a>
																				</th>
																				<th style="margin:0 auto; color:inherit; float:none; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-right:10px; text-align:center">
																					<a href="https://www.linkedin.com/in/voices-city-33990a205" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="margin:0; color:#17b; font-family:Helvetica,Arial,sans-serif; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; text-decoration:none" data-linkindex="7"><img data-imagetype="External" src="http://voicescity.com/static/linkedin.png" originalsrc="http://go.pardot.com/l/55082/2015-09-30/3gccd7/55082/68478/SocialButton1_LI_BlueOnWhite_50X75.png" data-connectorsauthtoken="1" data-imageproxyendpoint="/actions/ei" data-imageproxyid="" alt="LinkedIn" style="border:none; clear:both; display:block; max-width:100%; outline:0; text-decoration:none; width:20px;"> </a>
																				</th>
																			</tr>
																		</tbody>
																	</table>
																</td>
															</tr>
														</tbody>
													</table>
												</center>
											</th>
											<th style="margin:0; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0!important; text-align:left; width:0"></th>
										</tr>
									</tbody>
								</table>
							</th>
						</tr>
					</tbody>
				</table>
			</td>
		</tr>
	</tbody>
</table>
</table>""" } ] }
                    sg = SendGridAPIClient(api_key)
                    response = sg.client.mail.send.post(request_body=data)
                    return jsonify({"success": True})
                except Exception as e:
                    return jsonify({"success": False, "error": str(e)})
            else:
                username = session.get("username")
                email = session.get("email")
                type = session.get("type")
                table = mydb["category"]
                categories = table.find({})
                error = ""
                if session.get("error"):
                    error = session.get("error")
                    session.pop("error", None)
                message = ""
                if session.get("message"):
                    message = session.get("message")
                    session.pop("message", None)
                languages, countries, dead_line, categories, delivery_options, proposals, accents = fetch_record()
                return render_template("postjob.html", username=username, email=email,
                                       type=type, categories=categories, error=error, message=message,
                                       dead_line=dead_line, delivery_options=delivery_options,
                                       languages=languages, proposals=proposals)
        else:
            return redirect("/login")
    except Exception as e:
        session["error"] = str(e) + str(".\t\tRoute: /post-job")
        return redirect(url_for("show_error"))


@app.route("/get-price", methods=["GET", "POST"])
def get_price():
    try:
        if request.method == "GET":
            selectedValues = request.args.get("selectedValues")
            selectedValues = selectedValues.split(",")
            cost = 0
            table = mydb["category"]
            cost_list = []
            data_cat = table.find({})
            for i in data_cat:
                if str(i["_id"]) in selectedValues:
                    standard_cost = i["Standard Price"]
                    price_per_word = i["Price per Word"]
                    cost_list.append({"standard_cost": standard_cost, "price_per_word": price_per_word})
            return jsonify({"success": True, "cost_list": cost_list})
        else:
            return jsonify({"success": False, "error": str("Invalid Request..")})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# Edit Post Job a new Job by the buyer.
@app.route("/edit-job", methods=["GET", "POST"])
def editjob():
    try:
        if session.get("email") and session.get("type") == "buyer" and session.get("username"):
            if request.method == "POST":
                usertype = session.get("type")
                data = request.form
                files = request.files
                project_id = data["project_id"]
                session["project_id"] = str(project_id)
                project_name = data["projectName"]
                project_description = data["projectDescription"]
                project_usage = data["projectUsage"]
                project_language = data.getlist("projectLanguage")
                project_accent = data.getlist("projectAccent")
                project_gender_age = data.getlist("projectGenderAge")
                project_length = data["projectLength"]
                project_length_type = data["projectLengthType"]
                project_script = data["inputscript"]
                project_delivery_option = data.getlist("projectDeliveryOption")
                # project_custom_audition = data["projectCustomAudition"]
                project_proposal = data.getlist("projectProposal")
                project_deadline = data.getlist("projectDeadline")
                project_budget = data["projectBudget"]
                if project_budget == "variable":
                    project_cost = data["projectCost1"]
                elif project_budget == "fixed":
                    project_cost = data["projectCost"]

                project_status_old = data["projectStatusOld"]
                if project_status_old == "draft":
                    status = "draft"
                elif project_status_old == "deposited":
                    status = "deposited"
                else:
                    status = project_status_old
                if usertype == "buyer":
                    table = mydb["buyer"]
                    buyer_id = session.get("userid")
                    if 'scriptFile' in files:
                        project_script_file = files["scriptFile"]
                        if project_script_file.filename != "":
                            # scriptFile = project_script_file.filename
                            scriptFile = secure_filename(project_script_file.filename)
                            scriptFile = str(project_name).replace("-", "") + "-" + str(scriptFile).replace("-", "")
                            project_script_file.save(os.path.join(app.config['UPLOAD_FOLDER4'], str(scriptFile)))
                        else:
                            if 'oldScriptFile' in data:
                                scriptFile = data["oldScriptFile"]
                            else:
                                scriptFile = ""
                    mydic1 = {"project_name": project_name, "project_description": project_description,
                              "project_usage": project_usage, "project_language": project_language,
                              "project_gender_age": project_gender_age, "project_length": project_length,
                              "project_length_type": project_length_type, "project_proposal": project_proposal,
                              "project_delivery_option": project_delivery_option, "project_accent": project_accent,
                              "project_deadline": project_deadline, "project_budget": project_budget,
                              "project_cost": project_cost, "timestamp": datetime.now(),
                              "project_id": ObjectId(project_id), "status": status, "paymentStatus": "unpaid"
                        , "script file": scriptFile, "script": project_script, "live":False}
                    table.update({"_id": ObjectId(buyer_id), "projects.project_id": ObjectId(project_id)},
                                 {'$set': {"projects.$": mydic1}})
                    session["message"] = "Updated successfully."
                    return redirect(url_for("editjob"))
                else:
                    session["error"] = "Invalid user type error"
                    return redirect(url_for("postjob"))
            else:
                username = session.get("username")
                email = session.get("email")
                type = session.get("type")
                buyer_id = session.get("userid")
                error = ""
                if session.get("error"):
                    error = session.get("error")
                    session.pop("error", None)
                message = ""
                if session.get("message"):
                    message = session.get("message")
                    session.pop("message", None)
                languages, countries, dead_line, categories, delivery_options, proposals, accents = fetch_record()
                project_id = request.args.get("project_id")
                if project_id is None:
                    project_id = session.get("project_id")
                    # session.pop("project_id", None)
                table = mydb["buyer"]
                job_data = table.find_one({"_id": ObjectId(buyer_id),
                                           "projects.project_id": ObjectId(str(project_id))},
                                          {"projects": {"$elemMatch": {"project_id": ObjectId(project_id)}}})
                min_date = str(datetime.now()).split(" ")[0]
                return render_template("jobedit.html", username=username, email=email,
                                       type=type, categories=categories, error=error, message=message,
                                       job_data=job_data, delivery_options=delivery_options,
                                       dead_line=dead_line, languages=languages, proposals=proposals,
                                       project_id=project_id, accents=accents, min_date=min_date)
        else:
            return redirect("/login")
    except Exception as e:
        return str(e)
        session["error"] = str(e) + str(".\t\tRoute: /edit-job")
        return redirect(url_for("show_error"))


# Edit Post Job a new Job by the buyer.
@app.route("/edit-job-payment", methods=["GET", "POST"])
def editjob_payment():
    try:
        if session.get("email") and session.get("type") == "buyer" and session.get("username"):
            if request.method == "POST":
                usertype = session.get("type")
                data = request.form
                files = request.files
                project_id = data["project_id"]
                session["project_id"] = str(project_id)
                project_name = request.form["projectName"]
                project_description = request.form["projectDescription"]
                project_usage = data["projectUsage"]
                project_language = data["projectLanguage"]
                project_language = project_language.split(',')
                project_accent = data["projectAccent"]
                project_accent = project_accent.split(',')
                project_gender_age = data["projectGenderAge"]
                project_gender_age2 = data["projectGenderAge1"]
                project_gender_age3 = data["projectGenderAge2"]
                project_gender_age = project_gender_age + "," + project_gender_age2 + "," + project_gender_age3
                project_gender_age = project_gender_age.split(',')
                project_length = data["projectLength"]
                project_length_type = data["projectLengthType"]

                project_script = data["inputscript"]
                # project_script_file = files["scriptFile"]
                project_delivery_option = data["projectDeliveryOption"]
                project_delivery_option = project_delivery_option.split(',')
                # project_custom_audition = data["projectCustomAudition"]
                project_deadline = data.getlist("projectDeadline")
                project_proposal = data.getlist("projectProposal")
                project_budget = data["projectBudget"]
                project_cost = data["projectCost"]
                project_bank = data["bankId"]
                project_account = data["bankAccount"]
                project_amount = data["bankAmount"]
                status = "draft"
                if usertype == "buyer":
                    table = mydb["buyer"]
                    buyer_id = session.get("userid")
                    if data["bankId"]:
                        if 'scriptFile' in files:
                            project_script_file = files["scriptFile"]
                            scriptFile = secure_filename(project_script_file.filename)
                            str(project_name).replace("-", "") + "-" + str(scriptFile).replace("-", "")
                            project_script_file.save(os.path.join(app.config['UPLOAD_FOLDER4'], str(scriptFile)))
                        else:
                            if 'oldScriptFile' in data:
                                scriptFile = data["oldScriptFile"]
                            else:
                                scriptFile = ""
                        mydic1 = {"project_name": project_name, "project_description": project_description,
                                  "project_usage": project_usage, "project_language": project_language,
                                  "project_gender_age": project_gender_age, "project_length": project_length,
                                  "project_length_type": project_length_type, "project_proposal": project_proposal,
                                  "project_delivery_option": project_delivery_option, "project_accent": project_accent,
                                  "project_deadline": project_deadline, "project_budget": project_budget,
                                  "project_cost": project_cost, "timestamp": datetime.now(),
                                  "project_id": ObjectId(project_id), "status": status, "paymentStatus": "unpaid"
                            , "script file": scriptFile, "script": project_script,"live":True}
                                #   "paymentDetail": {
                                #       "bank": project_bank, "account": project_account, "amount": project_amount,
                                #       "timestamp": datetime.now()
                                #   }
                                #   }
                        table.update({"_id": ObjectId(buyer_id), "projects.project_id": ObjectId(project_id)},
                                     {'$set': {"projects.$": mydic1}})
                        buyer_data = table.find_one({"_id": ObjectId(buyer_id)})
                        data = {
                            "personalizations": [
                                {
                                "to": [
                                    {
                                    "email": buyer_data["email"]
                                    }
                                ],
                                "subject": "Project Status"
                                }
                            ],
                            "from": {
                                "email": default_sender,
                                "name": "voices city"
                            },
                            "content": [
                                {
                                "type": "text/html",
                                "value": """<th style="margin:0 auto; color:#0a0a0a; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-bottom:16px; padding-left:16px; padding-right:16px; text-align:left; width:564px">
	<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
		<tbody>
			<tr style="padding:0; text-align:left; vertical-align:top">
				<th style="margin:0; color:#0a0a0a; font-family:Helvetica,Arial,sans-serif; font-size:14px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left">
					<p><strong>Your project: """ + project_name + """</strong></p>
					<p>Hello """ + buyer_data['userName'] + """,</p>
					<p>Thank you for posting a project on Voicescity!</p>
					<p>Our client success team is currently reviewing your project. You can check its status in the <a href="https://www.voicescity.com/projects" style="color:blue;"> project dashboard.</a></p>
					<p>If you have any questions, please feel free to <a href="mailto:support@voicescity.com" style="color: blue">contact us.</a></p>
					<p>Kind Regards,</p>
					<p><strong>Voicescity Team </strong>
						<p>
							<br aria-hidden="true"><strong><span style="color:#1171bb">Voicescity.com</span></strong>
							<br aria-hidden="true">+447888884150
							<br aria-hidden="true"><a href="mailto:support@voicescity.com" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" data-linkindex="3">support@voicescity.com</a> | <a href="https://voicescity.com/" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" data-linkindex="4">voicescity.com</a> </div>
				</th>
				<th style="margin:0; color:#0a0a0a; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0!important; text-align:left; width:0"></th>
			</tr>
		</tbody>
	</table>
</th>
<table style="margin:0 auto; background:#ffffff; border:1px solid #ccc; border-collapse:collapse; border-spacing:0; border:none; color:grey; float:none; margin:0 auto; padding:0; text-align:center; vertical-align:top; width:600px" align="center">
	<tbody>
		<tr style="padding:0; text-align:left; vertical-align:top">
			<td style="margin:0; border-collapse:collapse!important; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; vertical-align:top; word-wrap:break-word">
				<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
					<tbody>
						<tr style="padding:0; text-align:left; vertical-align:top">
							<td style="margin:0; border-collapse:collapse!important; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:15px; font-weight:400; line-height:15px; margin:0; padding:0; text-align:left; vertical-align:top; word-wrap:break-word" height="15px">&nbsp;</td>
						</tr>
					</tbody>
				</table>
				<table style="border-collapse:collapse; border-spacing:0; display:table; padding:0; text-align:left; vertical-align:top; width:100%">
					<tbody>
						<tr style="padding:0; text-align:left; vertical-align:top">
							<th style="margin:0 auto; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-bottom:0; padding-left:16px; padding-right:16px; text-align:left; width:564px">
								<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
									<tbody>
										<tr style="padding:0; text-align:left; vertical-align:top">
											<th style="margin:0; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left">
												<center style="min-width:532px; width:100%"><span align="center" style="font-size:12px">LET'S BE FRIENDS</span></center>
											</th>
											<th style="margin:0; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0!important; text-align:left; width:0"></th>
										</tr>
									</tbody>
								</table>
							</th>
						</tr>
					</tbody>
				</table>
				<table style="border-collapse:collapse; border-spacing:0; display:table; padding:0; text-align:left; vertical-align:top; width:100%">
					<tbody>
						<tr style="padding:0; text-align:left; vertical-align:top">
							<th style="margin:0 auto; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-left:27px; padding-right:16px; text-align:left; width:564px">
								<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
									<tbody>
										<tr style="padding:0; text-align:left; vertical-align:top">
											<th style="margin:0; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left">
												<center style="min-width:532px; width:100%">
													<table style="margin:0 auto; border-collapse:collapse; border-spacing:0; float:none; margin:0 auto; padding:0; text-align:center; vertical-align:top; width:auto!important" align="center">
														<tbody>
															<tr style="padding:0; text-align:left; vertical-align:top">
																<td style="margin:0; border-collapse:collapse!important; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; vertical-align:top; word-wrap:break-word">
																	<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
																		<tbody>
																			<tr style="padding:0; text-align:left; vertical-align:top">
																				<th style="margin:0 auto; color:inherit; float:none; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-right:10px; text-align:center">
																					<a href="https://twitter.com/VoicesCity2?s=08" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="margin:0; color:#17b; font-family:Helvetica,Arial,sans-serif; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; text-decoration:none" data-linkindex="5"><img data-imagetype="External" src="http://voicescity.com/static/twitter.png" originalsrc="http://go.pardot.com/l/55082/2015-09-30/3gccd5/55082/68476/SocialButton3_TWR_BlueOnWhite_50X75.png" data-connectorsauthtoken="1" data-imageproxyendpoint="/actions/ei" data-imageproxyid="" alt="Twitter" style="border:none; clear:both; display:block; max-width:100%; outline:0; text-decoration:none; width:20px;"> </a>
																				</th>
																				<th style="margin:0 auto; color:inherit; float:none; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-right:10px; text-align:center">
																					<a href="https://www.facebook.com/Voices-City-332687944647576/" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="margin:0; color:#17b; font-family:Helvetica,Arial,sans-serif; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; text-decoration:none" data-linkindex="6"><img data-imagetype="External" src="http://voicescity.com/static/facebook.png" originalsrc="http://go.pardot.com/l/55082/2015-09-30/3gcccp/55082/68474/SocialButton2_FB_BlueOnWhite_50X75.png" data-connectorsauthtoken="1" data-imageproxyendpoint="/actions/ei" data-imageproxyid="" alt="Facebook" style="border:none; clear:both; display:block; max-width:100%; outline:0; text-decoration:none; width:30px;"> </a>
																				</th>
																				<th style="margin:0 auto; color:inherit; float:none; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-right:10px; text-align:center">
																					<a href="https://www.linkedin.com/in/voices-city-33990a205" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="margin:0; color:#17b; font-family:Helvetica,Arial,sans-serif; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; text-decoration:none" data-linkindex="7"><img data-imagetype="External" src="http://voicescity.com/static/linkedin.png" originalsrc="http://go.pardot.com/l/55082/2015-09-30/3gccd7/55082/68478/SocialButton1_LI_BlueOnWhite_50X75.png" data-connectorsauthtoken="1" data-imageproxyendpoint="/actions/ei" data-imageproxyid="" alt="LinkedIn" style="border:none; clear:both; display:block; max-width:100%; outline:0; text-decoration:none; width:20px;"> </a>
																				</th>
																			</tr>
																		</tbody>
																	</table>
																</td>
															</tr>
														</tbody>
													</table>
												</center>
											</th>
											<th style="margin:0; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0!important; text-align:left; width:0"></th>
										</tr>
									</tbody>
								</table>
							</th>
						</tr>
					</tbody>
				</table>
			</td>
		</tr>
	</tbody>
</table>
</table>""" } ] }
                        sg = SendGridAPIClient(api_key)
                        response = sg.client.mail.send.post(request_body=data)

                        session["message"] = "Updated successfully."
                        return jsonify({"success": True})
                else:
                    session["error"] = "Invalid user type error"
                    return redirect(url_for("postjob"))
            else:
                username = session.get("username")
                email = session.get("email")
                type = session.get("type")
                table = mydb["category"]
                categories = table.find({})
                buyer_id = session.get("userid")
                error = ""
                if session.get("error"):
                    error = session.get("error")
                    session.pop("error", None)
                message = ""
                if session.get("message"):
                    message = session.get("message")
                    session.pop("message", None)
                project_id = request.args.get("project_id")
                if project_id is None:
                    project_id = session.get("project_id")
                    # session.pop("project_id", None)
                table = mydb["buyer"]
                languages, countries, dead_line, categories, delivery_options, proposals, accents = fetch_record()
                job_data = table.find_one({"_id": ObjectId(buyer_id),
                                           "projects.project_id": ObjectId(str(project_id))},
                                          {"projects": {"$elemMatch": {"project_id": ObjectId(project_id)}}})
                return render_template("jobedit.html", username=username, email=email,
                                       type=type, categories=categories, error=error, message=message,
                                       job_data=job_data, delivery_options=delivery_options,
                                       dead_line=dead_line, languages=languages, proposals=proposals,
                                       project_id=project_id)
        else:
            return redirect("/login")
    except Exception as e:
        return str(e)
        session["error"] = str(e) + str(".\t\tRoute: /edit-job")
        return redirect(url_for("show_error"))


# Job poster or list of posted projects.
@app.route("/projects", methods=["GET", "POST"])
def projects():
    try:
        if session.get("email") and session.get("type") == "buyer" and session.get("username"):
            if request.method == "POST":
                return redirect(url_for("projects"))
            else:
                username = session.get("username")
                email = session.get("email")
                type = session.get("type")
                table = mydb["category"]
                categories = table.find({})
                buyer_id = session.get("userid")
                table = mydb["buyer"]
                buyer_data = table.find_one({"_id": ObjectId(buyer_id)}, {"activateLink": 0, "passwordHash": 0,
                                                                          "password": 0})

                table = mydb["bidding"]
                bid_data1 = table.find({"buyer_id": ObjectId(buyer_id)})
                bid_data = []
                for i in bid_data1:
                    bid_data.append(i)
                error = ""
                if session.get("error"):
                    error = session.get("error")
                    session.pop("error", None)
                message = ""
                if session.get("message"):
                    message = session.get("message")
                    session.pop("message", None)
                return render_template("projects.html", username=username, email=email, type=type, error=error,
                                       message=message, buyer_data=buyer_data, bid_data=bid_data)
        else:
            return redirect('/login')
    except Exception as e:
        session["error"] = str(e) + str(".\t\tRoute: /projects")
        return redirect(url_for("show_error"))


@app.route("/project-response", methods=["GET", "POST"])
def project_responses():
    try:
        if session.get("email") and session.get("type") == "buyer" and session.get("username"):
            if request.method == "POST":
                return redirect(url_for("project_responses"))
            else:
                username = session.get("username")
                email = session.get("email")
                type = session.get("type")
                buyer_id = session.get("userid")
                project_id = request.args.get("id")
                if project_id is None:
                    project_id = session.get("projectID")
                    session.pop("projectID", None)
                table = mydb["buyer"]
                project_details = table.find_one(
                    {"_id": ObjectId(buyer_id), "projects.project_id": ObjectId(project_id)},
                    {"projects": {"$elemMatch": {"project_id": ObjectId(project_id)}}}
                )
                table = mydb["category"]
                categoriesNew = table.find({})
                categories = []
                for i in categoriesNew:
                    categories.append(i)
                table = mydb["bidding"]
                bid_data1 = table.find({"buyer_id": ObjectId(buyer_id), "project_id": ObjectId(project_id)})
                bid_data = []
                for i in bid_data1:
                    bid_data.append(i)
                error = ""
                if session.get("error"):
                    error = session.get("error")
                    session.pop("error", None)
                message = ""
                if session.get("message"):
                    message = session.get("message")
                    session.pop("message", None)
                offer_array = []
                if "acceptOffers" in project_details['projects'][0]:
                    for entry in project_details['projects'][0]['acceptOffers']:
                        offer_array.append(entry['actor_id'])
                return render_template("project_responses.html", username=username, email=email, type=type, error=error,
                                       message=message, project_details=project_details, categories=categories,
                                       project_id=project_id, bid_data=bid_data, key=stripe_keys['publishable_key'],mydata=offer_array)
        else:
            return redirect(url_for("login"))
    except Exception as e:
        session["error"] = str(e) + str(".\t\tRoute: /project-response")
        return redirect(url_for("show_error"))


# Actor profile for buyer from response page.
@app.route("/actor-profile", methods=["GET", "POST"])
def actor_profile():
    try:
        if session.get("email") and session.get("type") == "buyer" and session.get("username"):
            if request.method == "POST":
                return redirect(url_for("project_responses"))
            else:
                username = session.get("username")
                email = session.get("email")
                type = session.get("type")
                buyer_id = session.get("userid")
                actor_id = request.args.get("id")
                actorTable = mydb["actor"]
                actordata = actorTable.find_one({"_id": ObjectId(actor_id)})
                table = mydb["buyer"]
                table = mydb["category"]
                error = ""
                if session.get("error"):
                    error = session.get("error")
                    session.pop("error", None)
                message = ""
                if session.get("message"):
                    message = session.get("message")
                    session.pop("message", None)
                table = mydb["category"]
                catdata = table.find({})
                languages, countries, dead_line, categories, delivery_options, proposals, accents = fetch_record()
                return render_template("actor-profile.html", username=username, email=email, type=type, error=error,
                                       message=message, actordata=actordata,
                                       actor_id=actor_id, catdata=catdata, categories=categories)
        else:
            return redirect(url_for("login"))
    except Exception as e:
        session["error"] = str(e) + str(".\t\tRoute: /actor-profile")
        return redirect(url_for("show_error"))


# After Login
# Actors routes
# Actor Home page
@app.route("/actor-home")
def actorhome():
    try:
        job_data = ""
        if session.get("email") and session.get("type") == "actor" \
                and session.get("username"):
            if request.method == "POST":
                return redirect("/actor-home")
            else:
                username = session.get("username")
                email = session.get("email")
                type = session.get("type")
                userid = session.get("userid")
                table = mydb["buyer"]
                actor_table = mydb['actor']
                actordata = actor_table.find_one({"_id": ObjectId(userid)})
                profile_percentag = 0
                skill_status = False
                playlist_status = False
                if "profileStatus" in actordata:
                    if actordata["profileStatus"] == "completed":
                        profile_percentag = profile_percentag + 25

                if "skillStatus" in actordata:
                    if actordata["skillStatus"] == "completed":
                        skill_status = True
                        profile_percentag = profile_percentag + 25

                if "studioStatus" in actordata:
                    if actordata["studioStatus"] == "completed":
                        profile_percentag = profile_percentag + 25

                if "playlistStatus" in actordata:
                    if actordata["playlistStatus"] == "completed":
                        playlist_status = True
                        profile_percentag = profile_percentag + 25
                # if "bankStatus" in actordata:
                #     if actordata["bankStatus"] == "completed":
                #         bank_status = True
                #         profile_percentag = profile_percentag + 20
                # if profile_percentag == 0:
                #     profile_percentag = int(100 / (profile_percentag + 10))
                # else:
                #     profile_percentag = int(100 / profile_percentag)

                projcts = table.aggregate([
                    {
                        "$project": {"projects": 1}
                    },
                    {
                        "$unwind": "$projects"
                    },
                    {
                        "$match": {"projects.status": "posted"}
                    },
                    {
                        "$count": "total_project"
                    }
                ])
                for entry in projcts:
                    print(entry)
                for i in projcts:
                    job_data = i['total_project']

                if skill_status == True:
                    actor_languages = actordata['languages']
                    actor_category = actordata['catdata']
                    projcts = table.aggregate([
                        {
                            "$project": {"projects": 1}
                        },
                        {
                            "$unwind": "$projects"
                        },
                        {
                            "$match": {"projects.status": "posted"}
                        },
                        {
                            "$project": {
                                "projects": "$projects",
                                "matchesgener": {"$cond": {"if": {"$eq": [{"$size": {
                                    "$setIntersection": ["$projects.project_language",
                                                         actor_languages]}}, 0]}, "then": "NULL", "else": "True"}},
                                "matchesgender": {"$cond": {"if": {"$eq": [{"$size": {
                                    "$setIntersection": ["$projects.project_gender_age",
                                                         actor_category]}}, 0]}, "then": "NULL",
                                    "else": "True"}}
                            }
                        },
                        {
                            "$match": {
                                "$or": [{"matchesgener": {"$eq": "True"}}, {"matchesgender": {"$eq": "True"}}]}
                        }
                    ])
                    # for i in projcts:
                        # job_data = i['total_project']
                    job_data = len(list(projcts))
                playlist_length = 'No'
                if playlist_status == True:
                    playlist_length = 0
                    for entry in actordata['playlists']:
                        if "status" not in entry:
                            playlist_length = playlist_length + 1
                return render_template("profile.html", username=username, email=email,
                                       type=type, totaljobs=job_data, profile_percentag=profile_percentag,
                                       skill_status=skill_status, playlist_status=playlist_status,
                                       playlist_length=playlist_length,status=actordata['planType'])
        else:
            return redirect("/login")

    except Exception as e:
        session["error"] = str(e) + str(".\t\tRoute: /actor-profile")
        return redirect(url_for("show_error"))


# about the actor update here.
@app.route("/actor-editprofile", methods=["GET", "POST"])
def newactoreditprofile():
    try:
        if session.get("email") and session.get("type") == "actor" \
                and session.get("username"):
            actorTable = mydb["actor"]
            userid = session.get("userid")
            if request.method == "POST":
                firstName = ""
                if "firstName" in request.form:
                    firstName = request.form["firstName"]
                lastName = request.form["lastName"]
                userName = request.form["userName"]
                Location = request.form["Location"]
                Country = request.form["userCountry"]
                proHeadlines = request.form["proHeadlines"]
                moreaboutyou = request.form["moreAboutYou"]
                file = ""
                if "profilePic[]" in request.files and request.files["profilePic[]"].filename != "":
                    prifilepic = request.files["profilePic[]"]
                    file = secure_filename(prifilepic.filename)
                    file = str(userName) + "-" + str(file)
                    prifilepic.save(os.path.join(app.config['UPLOAD_FOLDER3'], str(file)))
                    newimage = Image.open(os.path.join(app.config['UPLOAD_FOLDER3'], str(file)))
                    newimage.thumbnail((421, 430))
                    newimage.save(os.path.join(UPLOAD_FOLDER, str(file)), quality=95)
                else:
                    if 'oldprofilePic[]' in request.form:
                        file = request.form["oldprofilePic[]"]
                    else:
                        file = ""
                actorTable.update_one({"_id": ObjectId(userid)},
                                      {"$set": {"userName": userName, "firstName": firstName, "lastName": lastName,
                                                "Location": Location, "Country": Country, "profilePicture": file,
                                                "proHeadlines": proHeadlines, "moreaboutyou": moreaboutyou,
                                                "profileStatus": "completed"}})
                session["message"] = "Profile update successfully"
                return redirect("/actor-editprofile")
            else:
                username = session.get("username")
                email = session.get("email")
                type = session.get("type")
                message = "NULL"
                if session.get("message"):
                    message = session.get("message")
                    session.pop("message", None)
                error = "NULL"
                if session.get("error"):
                    error = session.get("error")
                    session.pop("error", None)

                actordata = actorTable.find_one({"_id": ObjectId(userid)})
                joindate = actordata["timeStamp"]
                joindate = joindate.strftime("%b %d, %Y")

                languages, countries, dead_line, categories, delivery_options, proposals, accents = fetch_record()

                catTabledata = categories
                catTabledataedit = categories
                catTabledataPlayList = categories
                catPlayList = []
                for i in catTabledataPlayList:
                    catPlayList.append(i)
                return render_template("newedtprofile.html", username=username, email=email,
                                       type=type, actordata=actordata, message=message, error=error, joindate=joindate,
                                       languages=languages, delivery_options=delivery_options,
                                       catTabledata=catTabledata,
                                       catTabledataedit=catTabledataedit, catPlayList=catPlayList,
                                       countries=countries, accents=accents, banklistarray=banklistarray)
        else:
            return redirect("/login")

    except Exception as e:
        session["error"] = str(e) + ", Route: \t\t/actor-editprofile."
        return redirect(url_for("show_error"))


# Skills edit by the actor
@app.route("/edit-skills", methods=["POST"])
def editskills():
    try:
        if request.method == "POST":
            actorTable = mydb["actor"]
            userid = session.get("userid")
            languages = request.form.getlist("languages")
            agegender = request.form.getlist("genderAge")
            accents = request.form.getlist("accents")
            addVocalAbilities = request.form["addVocalAbilities"]
            expTrainEquip = request.form["expTrainEquip"]
            actorTable.update_one({"_id": ObjectId(userid)},
                                  {"$set": {"languages": languages, "catdata": agegender,
                                            "addVocalAbilities": addVocalAbilities,
                                            "expTrainEquip": expTrainEquip, "skillStatus": "completed",
                                            "accents": accents}})
            session["message"] = "Profile update successfully"
            return redirect("/actor-editprofile")
        else:
            session["error"] = "Opps something went wrong please try later. Worng Method "
            return redirect("/actor-editprofile")
    except Exception as e:
        session["error"] = "Opps something went wrong please try later. " + str(e)
        return redirect("/actor-editprofile")


# studio edit by the actor
@app.route("/edit-studio", methods=["POST"])
def editstudio():
    try:
        if request.method == "POST":
            actorTable = mydb["actor"]
            userid = session.get("userid")
            studio_sessions = request.form.getlist("sessions")
            studio_turnaroundtime = request.form["turnaroundtime"]
            studio_equipment = request.form["equipment"]
            studio_microphone = request.form["microphone"]
            actorTable.update_one({"_id": ObjectId(userid)},
                                  {"$set": {"studio_sessions": studio_sessions,
                                            "studio_turnaroundtime": studio_turnaroundtime,
                                            "studio_equipment": studio_equipment,
                                            "studio_microphone": studio_microphone, "studioStatus": "completed"}})
            session["message"] = "Studio Profile update successfully"
            return redirect("/actor-editprofile")
        else:
            session["error"] = "Opps something went wrong please try later. Worng Method "
            return redirect("/actor-editprofile")
    except Exception as e:
        session["error"] = "Opps something went wrong please try later. " + str(e)
        return redirect("/actor-editprofile")


# Add new play list.
@app.route('/add-playlist', methods=["POST"])
def add_playlist():
    try:
        if session.get("email") and session.get("type") == "actor" and session.get("username"):
            if request.method == "POST":
                data = request.form
                playlist_files = request.files.getlist("sampleFiles")
                playlist_name = data["playlistName"]
                playlist_language = data.getlist("playlistLanguage")
                playlist_category = data.getlist("playListCategory")
                playlist_accents = data.getlist("playlistaccents")
                playlist = []
                for eachfile in playlist_files:
                    if eachfile.filename != "":
                        file = secure_filename(eachfile.filename)
                        file = str(datetime.now()).split(".")[0].replace(":", "-") + " - " + str(file)
                        playlist.append(file)
                        eachfile.save(os.path.join(app.config['UPLOAD_FOLDER2'], str(file)))
                userid = session.get("userid")
                actorTable = mydb["actor"]
                actorTable.update_one({"_id": ObjectId(userid)},
                                      {"$addToSet": {"playlists": {"playlist_name": playlist_name,
                                                                   "playlist_language": playlist_language,
                                                                   "playlist_category": playlist_category,
                                                                   "playlist": playlist,
                                                                   "playlist_accents": playlist_accents,
                                                                   "_id": ObjectId()}}})
                actorTable.update_one({"_id": ObjectId(userid)},
                                      {"$set": {"playlistStatus": "completed"}})
                session["message"] = "Playlist added successfully"
                return redirect(url_for("newactoreditprofile"))
            else:
                session["error"] = "Invalid request received"
                return redirect(url_for("newactoreditprofile"))
        else:
            return redirect(url_for("login"))
    except Exception as e:
        return str(e)
        session["error"] = "Opps something went wrong please try later. " + str(e)
        return redirect("/actor-editprofile")


# Edit play list.
@app.route("/edit-playlist", methods=["POST"])
def edit_playlist():
    try:
        if session.get("email") and session.get("type") == "actor" and session.get("username"):
            if request.method == "POST":
                return redirect(url_for("newactoreditprofile"))
            else:
                session["error"] = "Not a valid request for the route \/edit-playlist."
        else:
            return redirect(url_for("login"))
    except Exception as e:
        session["error"] = str(e) + ", Route: \t\t/edit-playlist."


# Delete single sampale for from play list.
@app.route('/delete-sample', methods=["GET"])
def delete_sample():
    try:
        if session.get("email") and session.get("type") == "actor" and session.get("username"):
            if request.method == "GET":
                sample_name = request.args.get("name")
                playlist_id = request.args.get("id")
                userid = session.get("userid")
                actorTable = mydb["actor"]
                # actorTable.update_one({"_id": ObjectId(userid)},
                #                       {"$pull": {"playlists" : {"playlist": str(sample_name)}}})
                session["message"] = "sample deleted successfully"
                return redirect(url_for("newactoreditprofile"))
            else:
                session["error"] = "Invalid request received"
                return redirect(url_for("newactoreditprofile"))
        else:
            return redirect(url_for("login"))
    except Exception as e:
        session["error"] = "Opps something went wrong please try later. " + str(e)
        return redirect("/actor-editprofile")


# Delete Complete play list.
@app.route('/delete-plalist', methods=["GET"])
def delete_playlist():
    try:
        if session.get("email") and session.get("type") == "actor" and session.get("username"):
            if request.method == "GET":
                playlist_id = request.args.get("id")
                userid = session.get("userid")
                actorTable = mydb["actor"]
                actor_data = actorTable.find_one({"_id": ObjectId(userid),
                                                  "playlists._id": ObjectId(playlist_id)},
                                                 {"playlists": {"$elemMatch": {"_id": ObjectId(playlist_id)}}})
                mydict = {}
                mydict["status"] = "deleted"
                mydict["_id"] = actor_data["playlists"][0]["_id"]
                mydict["playlist_name"] = actor_data["playlists"][0]["playlist_name"]
                mydict["playlist_language"] = actor_data["playlists"][0]["playlist_language"]
                mydict["playlist_category"] = actor_data["playlists"][0]["playlist_category"]
                mydict["playlist"] = actor_data["playlists"][0]["playlist"]
                actorTable.update({"_id": ObjectId(userid), "playlists._id": ObjectId(playlist_id)},
                                  {'$set': {"playlists.$": mydict}})
                # actorTable.update_one({"_id": ObjectId(userid)},
                #                       {"$pull": {"playlists" : {"$elemMatch": {"_id": ObjectId(playlist_id)}}}})
                session["message"] = "Playlist deleted successfully"
                return redirect(url_for("newactoreditprofile"))
            else:
                session["error"] = "Invalid request received"
                return redirect(url_for("newactoreditprofile"))
        else:
            return redirect(url_for("login"))
    except Exception as e:
        session["error"] = "Opps something went wrong please try later. " + str(e)
        return redirect("/actor-editprofile")


# Jobs for the actor
@app.route("/jobs")
def jobs():
    try:
        total_bids = ""
        bid_package = ""
        if session.get("email") and session.get("type") == "actor" and session.get("username"):
            if request.method == "POST":
                return redirect(url_for(jobs))
            else:
                username = session.get("username")
                email = session.get("email")
                type = session.get("type")
                userid = session.get("userid")
                actor_table = mydb["actor"]
                actor_data = actor_table.find_one({"_id": ObjectId(userid)})
                actor_languages = []
                actor_accents = []
                actor_category = []
                if "languages" in actor_data:
                    actor_languages = actor_data["languages"]
                if "accents" in actor_data:
                    actor_accents = actor_data["accents"]
                if "catdata" in actor_data:
                    actor_category = actor_data["catdata"]
                buyer_table = mydb["buyer"]
                projcts = buyer_table.aggregate([
                    {
                        "$project": {"projects": 1, "userName": 1}
                    },
                    {
                        "$unwind": "$projects"
                    },
                    {
                        "$match": {"projects.status": "posted"}
                    },
                    {
                        "$project": {
                            "projects": "$projects",
                            "matchesgener": {"$cond": {"if": {"$eq": [{"$size": {
                                "$setIntersection": ["$projects.project_language",
                                                     actor_languages]}}, 0]}, "then": "NULL", "else": "True"}},
                            "matchesgender": {"$cond": {"if": {"$eq": [{"$size": {
                                "$setIntersection": ["$projects.project_gender_age",
                                                     actor_category]}}, 0]}, "then": "NULL",
                                "else": "True"}}
                            # ,
                            # "matchesaccent": {"$cond": {"if": {"$eq": [{"$size": {
                            #     "$setIntersection": ["$projects.project_accent",
                            #                          actor_accents]}}, 0]}, "then": "NULL",
                            #     "else": "True"}}
                        }
                    },
                    {
                        "$match": {
                            "$or": [{"matchesgener": {"$eq": "True"}}, {"matchesgender": {"$eq": "True"}}
                                    # ,{"matchesaccent": {"$eq": "True"}}
                                    ]}
                    }
                ])
                data_job = []
                for i in projcts:
                    i['_id'] = str(i['_id'])
                    i['projects']['project_id'] = str(i['projects']['project_id'])
                    if "responses" in i['projects']:
                        responses = len(i['projects']['responses'])
                        i['projects'].pop('responses', None)
                        i['projects'].pop('acceptOffers', None)
                        i['responses'] = responses
                    data_job.append(i)
                table = mydb["category"]
                catdata1 = table.find({})
                catdata = []
                for i in catdata1:
                    catdata.append(i)
                actordata = {}
                if session.get("userid") is not None:
                    userid = session.get("userid")
                    table = mydb["actor"]
                    actordata = table.find_one({"_id": ObjectId(userid)})
                table = mydb["actor"]
                sugestions = table.find({"active": 1},
                                        {"firstName": 1, "lastName": 1, "userName": 1})
                languages, countries, dead_line, categories, delivery_options, proposals, accents = fetch_record()
                error = ""
                if len(actor_category) == 0 and len(actor_accents) == 0 and len(actor_languages) == 0:
                    error = "Please fillout your skills section of your profile to get the matching jobs."
                elif session.get('error'):
                    error = session.get('error')
                    session.pop('error', None)
                message = ""
                if session.get('message'):
                    message = session.get('message')
                    session.pop('message', None)

                # Bidding of actor for last month.
                actorTable = mydb["actor"]
                actordata = actorTable.find_one({"_id": ObjectId(userid)})
                planDate = actordata["planDate"]
                curdata = datetime.now()
                bidTable = mydb['bidding']
                previousMonthDate = curdata - timedelta(days=30)
                current_month_bids = bidTable.find(
                    {"actor_id": ObjectId(userid), "timeStamp": {"$gte": previousMonthDate}}).count()
                print(current_month_bids)
                if actordata['planType'] == 'standard':
                    total_bids = 10
                    bid_package = 'Basic'
                elif actordata['planType'] == 'bronze':
                    if actordata["planPayment"] == 'full':
                        total_bids = 90
                        bid_package = 'Silver'
                    elif actordata["planPayment"] == 'monthly':
                        total_bids = 30
                        bid_package = 'Silver'
                    else:
                        total_bids = 25
                        bid_package = 'Silver'
                elif actordata['planType'] == 'premium':
                    total_bids = 150
                    bid_package = 'Gold'
                min_date = str(datetime.now()).split(" ")[0]
                return render_template("Jobs.html", username=username, email=email, type=type, data_job=data_job,
                                       catdata=catdata, actordata=actordata, sugestions=sugestions,
                                       actor_category=actor_category, languages=languages, categories=categories,
                                       error=error, message=message, current_month_bids=current_month_bids,
                                       total_bids=total_bids, bid_package=bid_package, min_date=min_date)
        else:
            return redirect(url_for('login'))
    except Exception as e:
        session["error"] = str(e) + ", Route: \t\t/job"
        return redirect(url_for("show_error"))


@app.route("/orders", methods=["GET", "POST"])
def joblist():
    try:
        if request.method == "POST":
            return redirect(url_for("joblist"))
        else:
            username = session.get("username")
            email = session.get("email")
            type = session.get("type")
            actor_id = session.get("userid")
            table = mydb["actor"]
            actordata = table.find_one({"_id": ObjectId(actor_id)},
                                       {"languages": 1, "catdata": 1, "profileStatus": 1,
                                        "offersReceived": 1})
            table = mydb["buyer"]
            job_data = table.find({"projects": {"$exists": True}, "projects.status": "posted"},
                                  {"projects": 1})
            data_job = []
            for i in job_data:
                data_job.append(i)
            langua = ["As", "qw", "safd"]
            table = mydb["bidding"]
            bid_data1 = table.find({"actor_id": ObjectId(actor_id)})
            bid_data = []
            cmp_data = []
            for i in bid_data1:
                buyer_table = mydb['buyer']
                records = buyer_table.aggregate([
                    {
                        "$project": {"projects": 1, "userName": 1}
                    },
                    {
                        "$unwind": "$projects"
                    },
                    {
                        "$match": {"projects.status": "posted", "projects.project_id": ObjectId(str(i['project_id']))}
                    }
                ])
                for l in records:
                    l['biddetails'] = i
                    bid_data.append(l)

                records_cmp = buyer_table.aggregate([
                    {
                        "$project": {"projects": 1, "userName": 1}
                    },
                    {
                        "$unwind": "$projects"
                    },
                    {
                        "$match": {"projects.status": "completed",
                                   "projects.project_id": ObjectId(str(i['project_id']))}
                    }
                ])
                for l in records_cmp:
                    l['biddetails'] = i
                    cmp_data.append(l)

            error = ""
            if session.get("error"):
                error = session.get("error")
                session.pop("error", None)
            message = ""
            if session.get("message"):
                message = session.get("message")
                session.pop("message", None)
            languages, countries, dead_line, categories, delivery_options, proposals, accents = fetch_record()
            if request.args.get("sendoffer"):
                return render_template("joblist.html", username=username, email=email, type=type,
                                   data_job=data_job, actordata=actordata, langua=langua,
                                   error=error, message=message, actor_id=actor_id, bid_data=bid_data,
                                   categories=categories, cmp_data=cmp_data, sendoffer = True)
            else:
                return render_template("joblist.html", username=username, email=email, type=type,
                                   data_job=data_job, actordata=actordata, langua=langua,
                                   error=error, message=message, actor_id=actor_id, bid_data=bid_data,
                                   categories=categories, cmp_data=cmp_data)
    except Exception as e:
        session["error"] = str(e)
        return redirect(url_for("show_error"))


# Job details for login and without login user
@app.route("/order-detail", methods=["GET", "POST"])
def job_detail():
    try:
        if request.method == "POST":
            return redirect(url_for(job_detail))
        else:
            username = session.get("username")
            email = session.get("email")
            type = session.get("type")
            actor_id = session.get("userid")
            table = mydb["actor"]
            actordata = table.find_one({"_id": ObjectId(actor_id)},
                                       {"languages": 1, "catdata": 1, "completed": 1, "accents": 1})
            job_id = request.args.get("jobid")
            buyer_id = request.args.get("byrid")
            table = mydb["buyer"]
            project_detail = table.find_one({"_id": ObjectId(buyer_id),
                                             "projects.project_id": ObjectId(str(job_id))},
                                            {"projects": {"$elemMatch": {"project_id": ObjectId(job_id)}}})

            data_job = project_detail
            # for i in project_detail['projects']:
            #     if str(project_detail['_id']) == str(buyer_id) and str(i['project_id']) == str(job_id):
            #         data_job.append({'_id': project_detail['_id'], 'projects': [i]})
            message = ""
            if session.get("message"):
                message = session.get("message")
                session.pop("message", None)
            error = ""
            if session.get("error"):
                error = session.get("error")
                session.pop("error", None)
            languages, countries, dead_line, categories, delivery_options, proposals, accents = fetch_record()
            langua = languages
            return render_template("job-detail.html", username=username, email=email, type=type,
                                   data_job=data_job, actordata=actordata, langua=langua,
                                   job_data=project_detail, message=message, error=error,
                                   # categories=catTabledata,
                                   categories=categories)
    except Exception as e:
        session["error"] = str(e)
        return redirect(url_for("show_error"))



# As an Actor
# Step 1:
# Send-bid by the actor to posted project..
@app.route("/send-bid", methods=["POST", "GET"])
def send_bid():
    try:
        if session.get("type") and session.get("email") and session.get("username"):
            if request.method == "POST":
                mydata = request.form
                myfile = request.files
                table = mydb["buyer"]
                data = request.form

                actor_name = data["actorName"]
                actor_id = data["actorId"]
                buyer_id = data["buyrId"]
                project_id = data["projId"]
                actor_description = data["actorDescription"]
                actor_time = data["actorCmplTime"]
                actor_sample = request.files.getlist("actorSample")

                actorTable = mydb["actor"]
                bidTable = mydb["bidding"]

                actordata = actorTable.find_one({"_id": ObjectId(actor_id)})
                planDate = actordata["planDate"]
                planPayment = actordata["planPayment"]
                curdata = datetime.now()
                previousMonthDate = curdata - timedelta(days=30)
                plandateDiff = planDate - curdata
                bidalready = bidTable.find_one({"actor_id": ObjectId(actor_id), "buyer_id":
                    ObjectId(buyer_id), "project_id": ObjectId(project_id)})
                if bidalready == None:
                    bidData = bidTable.find(
                        {"actor_id": ObjectId(actor_id), "timeStamp": {"$gte": previousMonthDate}}).count()
                    if actordata["planType"] == "standard" and bidData != None and bidData <= 10:
                        sampleslist = []
                        for samples in actor_sample:
                            if samples.filename != "":
                                file = secure_filename(samples.filename)
                                file = str(datetime.now()).split(".")[0].replace(":", "").replace("-", "") + "-" + str(
                                    file)
                                sampleslist.append(file)
                                samples.save(os.path.join(app.config['UPLOAD_FOLDER2'], str(file)))
                        bid_function(mydata, sampleslist)
                        # bidTable.insert_one({"actor_id": ObjectId(actor_id), "buyer_id":
                        #     ObjectId(buyer_id), "project_id": ObjectId(project_id),
                        #                      "timeStamp": datetime.now()})
                        # mydic1 = {"actor_name": actor_name, "actor_description": actor_description,
                        #           "job_complete": actor_time, "playlist": sampleslist, "_id": ObjectId(actor_id)}
                        #
                        #
                        # table.update({"_id": ObjectId(buyer_id), "projects.project_id": ObjectId(project_id)},
                        #              {"$push": {"projects.$.responses": mydic1}})
                        session["message"] = "Request send."
                        return redirect(url_for("jobs"))
                    elif actordata[
                        "planType"] == "silver" and bidData != None and bidData <= 30:
                        if  plandateDiff <= timedelta(days=90): #planPayment == "full" and
                            sampleslist = []
                            for samples in actor_sample:
                                if samples.filename != "":
                                    file = secure_filename(samples.filename)
                                    file = str(datetime.now()).split(".")[0].replace(":", "").replace("-",
                                                                                                      "") + "-" + str(
                                        file)
                                    sampleslist.append(file)
                                    samples.save(os.path.join(app.config['UPLOAD_FOLDER2'], str(file)))
                            bid_function(mydata, sampleslist)
                            # bidTable.insert_one({"actor_id": ObjectId(actor_id), "buyer_id":
                            #     ObjectId(buyer_id), "project_id": ObjectId(project_id),
                            #                      "timeStamp": datetime.now()})
                            # mydic1 = {"actor_name": actor_name, "actor_description": actor_description,
                            #           "job_complete": actor_time, "playlist": sampleslist, "_id": ObjectId(actor_id)}
                            # table.update({"_id": ObjectId(buyer_id), "projects.project_id": ObjectId(project_id)},
                            #              {"$push": {"projects.$.responses": mydic1}})
                            session["message"] = "Request send."
                            return redirect(url_for("jobs"))
                        elif planPayment == "monthly" and plandateDiff <= timedelta(days=30):
                            sampleslist = []
                            for samples in actor_sample:
                                if samples.filename != "":
                                    file = secure_filename(samples.filename)
                                    file = str(datetime.now()).split(".")[0].replace(":", "").replace("-",
                                                                                                      "") + "-" + str(
                                        file)
                                    sampleslist.append(file)
                                    samples.save(os.path.join(app.config['UPLOAD_FOLDER2'], str(file)))
                            bid_function(mydata, sampleslist)
                            # bidTable.insert_one({"actor_id": ObjectId(actor_id), "buyer_id":
                            #     ObjectId(buyer_id), "project_id": ObjectId(project_id),
                            #                      "timeStamp": datetime.now()})
                            # mydic1 = {"actor_name": actor_name, "actor_description": actor_description,
                            #           "job_complete": actor_time, "playlist": sampleslist, "_id": ObjectId(actor_id)}
                            # table.update({"_id": ObjectId(buyer_id), "projects.project_id": ObjectId(project_id)},
                            #              {"$push": {"projects.$.responses": mydic1}})
                            session["message"] = "Request send."
                            return redirect(url_for("jobs"))
                    elif actordata[
                        "planType"] == "premium" and bidData != None and bidData <= 150:
                        # if planPayment == "full" and plandateDiff <= timedelta(days=365):
                        sampleslist = []
                        for samples in actor_sample:
                            if samples.filename != "":
                                file = secure_filename(samples.filename)
                                file = str(datetime.now()).split(".")[0].replace(":", "").replace("-", "") + "-" + str(
                                    file)
                                sampleslist.append(file)
                                samples.save(os.path.join(app.config['UPLOAD_FOLDER2'], str(file)))
                        bid_function(mydata, sampleslist)
                        # bidTable.insert_one({"actor_id": ObjectId(actor_id), "buyer_id":
                        #     ObjectId(buyer_id), "project_id": ObjectId(project_id),
                        #                      "timeStamp": datetime.now()})
                        # mydic1 = {"actor_name": actor_name, "actor_description": actor_description,
                        #           "job_complete": actor_time, "playlist": sampleslist, "_id": ObjectId(actor_id)}
                        # table.update({"_id": ObjectId(buyer_id), "projects.project_id": ObjectId(project_id)},
                        #              {"$push": {"projects.$.responses": mydic1}})
                        session["message"] = "Request send."
                        return redirect(url_for("jobs"))
                        # elif planPayment == "monthly" and plandateDiff <= timedelta(days=30):
                        #     sampleslist = []
                        #     for samples in actor_sample:
                        #         if samples.filename != "":
                        #             file = secure_filename(samples.filename)
                        #             file = str(datetime.now()).split(".")[0].replace(":", "-") + "-" + str(file)
                        #             sampleslist.append(file)
                        #             samples.save(os.path.join(app.config['UPLOAD_FOLDER'], str(file)))
                        #     bid_function(mydata, sampleslist)
                        # bidTable.insert_one({"actor_id": ObjectId(actor_id), "buyer_id":
                        #     ObjectId(buyer_id), "project_id": ObjectId(project_id),
                        #                      "timeStamp": datetime.now()})
                        # mydic1 = {"actor_name": actor_name, "actor_description": actor_description,
                        #           "job_complete": actor_time, "playlist": sampleslist, "_id": ObjectId(actor_id)}
                        # table.update({"_id": ObjectId(buyer_id), "projects.project_id": ObjectId(project_id)},
                        #              {"$push": {"projects.$.responses": mydic1}})
                        # session["message"] = "Request send."
                        # return redirect(url_for("jobs"))
                    else:
                        session["message"] = "Your current month bidding is over kindly upgrade your package."
                        return redirect(url_for("jobs"))
                else:
                    session["message"] = "You have already bid this project."
                    return redirect(url_for("jobs"))
            else:
                session["error"] = "Method Not allowed"
                return redirect(url_for("joblist"))
        else:
            return redirect(url_for("login"))
    except Exception as e:
        session["message"] = "Request not send." + str(e)
        return redirect(url_for("jobs"))


# Step 2:
# Sent offer request to them who sent you bid.
# offer sent by the buyer to the specific project.
@app.route("/sent-offer", methods=["GET", "POST"])
def sent_offer():
     try:
        if session.get("email") and session.get("type") and session.get("username"):
            if request.method == "POST":
                data = request.form
                project_Id = data["project_Id"].replace('"', "")
                buyer_Id = data["buyer_Id"].replace('"', "")
                actor_Id = data["actor_Id"].replace('"', "")
                buyer_table = mydb["buyer"]
                actor_table = mydb["actor"]
                buyer = buyer_table.find_one({"_id": ObjectId(buyer_Id)})
                email = buyer['email']
                amount = int(data["amount"]) * 100
                token = data['token']
                table = mydb["bidding"]
                anyData = table.find_one({"actor_id": ObjectId(actor_Id), "buyer_id": ObjectId(buyer_Id),
                                          "project_id": ObjectId(project_Id)})

                if anyData is not None:
                    if 'offeraccpt' in anyData:
                        return jsonify({"success": False, "error": "Already accepted request."})
                    else:
                        try:
                            customer = stripe.Customer.create(
                                 email=email,
                                 source=token
                             )
                            stripe.Charge.create(
                                 customer=customer.id,
                                 amount=amount,
                                 currency='USD',
                                 description="project payment"
                             )
                            table = mydb["transactions"]
                            table.insert_one({"buyer_id": ObjectId(buyer_Id),
                                    "project_id": ObjectId(project_Id),
                                    "amount": amount, "timestamp": datetime.now(),
                                    "message": "newproject", "amountstatus": "deposit"})
                            table = mydb["buyer"]
                            table.update_one(
                    {"_id": ObjectId(buyer_Id), "projects.project_id": ObjectId(project_Id)},
                    {"$set" : {"projects.$.paymentStatus" : "paid"}})

                            table.update({"_id": ObjectId(buyer_Id),
                                        "projects.project_id": ObjectId(project_Id)},
                                         {"$set": {
                                             "projects.$.paymentDetail": {"bank": "stripe-bank", "account": "stripe-amount", "amount": amount/100,
                                                            "timestamp": datetime.now() }
                                                            }
                                         })                            
                        except stripe.error.CardError as e:
                            session["loginerror"] = e.user_message
                            return jsonify({"success": False, "error": "Card Declined."})
                        buyer_table.update({"_id": ObjectId(buyer_Id), "projects.project_id": ObjectId(project_Id)},
                                           {"$push": {"projects.$.acceptOffers": {"actor_id": ObjectId(actor_Id),
                                                                                  "timestamp": datetime.now(),
                                                                                  "acceptStatus": "pending"}}})
                        actor_table.update({"_id": ObjectId(actor_Id)},
                                           {"$push": {"offersReceived":
                                                          {"buyerId": ObjectId(buyer_Id),
                                                           "projectId": ObjectId(project_Id),
                                                           "timestamp": datetime.now(),
                                                           "offerstatus": "pending"}}})
                        table = mydb["bidding"]
                        table.update_one({"actor_id": ObjectId(actor_Id), "buyer_id": ObjectId(buyer_Id),
                                          "project_id": ObjectId(project_Id)},
                                         {"$set": {
                                             "offeraccpt": {"timestamp": datetime.now(), "status": "pending",
                                                            "accepttime": datetime.now(), "amount": amount}}
                                         })
                        actor_data = actor_table.find_one({"_id": ObjectId(actor_Id)})

                        # msg = Message("Job response", recipients=[actor_data['email']])
                        # msg.html = str(
                        #     """You get request for the job is accepted by the buyer. Now you can response the offer in order to job awarded to you. the .<br><br>Regards, <br>Voices City""")
                        # mail.send(msg)
                        return jsonify({"success": True})
                else:
                    return jsonify({"success": False, "error": "no record"})
            else:
                return jsonify({"success": False, "error": "INvalid Method"})
        else:
            return jsonify({"success": False, "error": "login"})
     except Exception as e:
         session["error"] = str(e) + str(".\t\tRoute: /sent-offer")
         return redirect(url_for("show_error"))


# Step 3:
# Offer accept by buyer
@app.route('/accept-offer', methods=["GET", "POST"])
def accept_offer():
    try:
        if session.get("email") and session.get("type") and session.get("username"):
            if request.method == "POST":
                return redirect(url_for("accept_offer"))
            else:
                if session.get("type") == "actor":
                    actor_Id = session.get("userid")
                    if request.args.get("actor_id") and request.args.get("buyer_id") and request.args.get("project_id"):
                        data = request.args
                        actor_id = data['actor_id']
                        buyer_id = data['buyer_id']
                        project_id = data['project_id']
                        buyer_table = mydb["buyer"]
                        actor_table = mydb["actor"]
                        bidding_table = mydb["bidding"]
                        anyData = bidding_table.find_one(
                            {"actor_id": ObjectId(actor_id), "buyer_id": ObjectId(buyer_id),
                             "project_id": ObjectId(project_id)})
                        if anyData['offeraccpt']['status'] == "pending":
                            bidding_table.update_one({"actor_id": ObjectId(actor_id),
                                                      "buyer_id": ObjectId(buyer_id),
                                                      "project_id": ObjectId(project_id)},
                                                     {"$set": {
                                                         "offeraccpt.status": "accepted",
                                                         "offeraccpt.accepttime": datetime.now()
                                                     }})

                            # buyer_table.update({"_id": ObjectId(buyer_Id),
                            #                     "projects.project_id": ObjectId(projectId),
                            #                     "projects.acceptOffers.actor_id": ObjectId(actor_Id)},
                            #                    {"$set": {"projects.acceptOffers.$$.acceptStatus": "accepted"}}, False,
                            #                    True)
                            # print("done2")
                            # actor_table.update_one({"_id": ObjectId(actor_Id),
                            #                         "offersReceived.projectId": ObjectId(projectId)},
                            #                        {"$set": {"offersReceived.$$.offerstatus": "accepted",
                            #                                  "offersReceived.$$.accpetTime": datetime.now()}})
                            # print("done3")
                            session["message"] = "offer accepted successfully."
                            return redirect(url_for("joblist"))
                        else:
                            session["error"] = "Offer already accepted."
                            return redirect(url_for("joblist"))
                    else:
                        session["error"] = "Invalid Arguments."
                        return redirect(url_for("joblist"))
                else:
                    session["error"] = "Invalid Arguments."
                    return redirect(url_for("joblist"))

                return str(True)
        else:
            return redirect(url_for("login"))
    except Exception as e:
        session["error"] = str(e) + str(".\t\tRoute: /accept-offer")
        return redirect(url_for("show_error"))


# Step 4:
# Send project to buyer after completing by the actor.
@app.route('/send-project', methods=["GET", "POST"])
def send_project():
    try:
        if session.get("email") and session.get("type") and session.get("username"):
            if request.method == "POST":
                if session.get("type") == "actor":
                    actor_Id = session.get("userid")
                    if request.form['actor_idC'] == actor_Id:
                        data = request.form
                        actor_id = data['actor_idC']
                        buyer_id = data['buyer_idC']
                        project_id = data['project_idC']
                        bidding_table = mydb["bidding"]
                        message = data["sendmessage"]
                        filename1 = ""
                        if "fiels" in request.files:
                            project_file = request.files["fiels"]
                            if project_file.filename != "":
                                filename1 = secure_filename(project_file.filename)
                                filename1 = str(datetime.now().strftime("%Y%m%d%H%M")) + "-" + str(filename1).replace(
                                    "-", "")
                                project_file.save(os.path.join(app.config['UPLOAD_FOLDER5'], filename1))
                            session["error"] = "Files required"
                        else:
                            return redirect(url_for("joblist"))
                        anyData = bidding_table.find_one(
                            {"actor_id": ObjectId(actor_id), "buyer_id": ObjectId(buyer_id),
                             "project_id": ObjectId(project_id)})
                        if anyData['offeraccpt']['status'] == "accepted":
                            bidding_table.update_one({"actor_id": ObjectId(actor_id),
                                                      "buyer_id": ObjectId(buyer_id),
                                                      "project_id": ObjectId(project_id)},
                                                     {
                                                         "$set":
                                                             {"projectSubmit": {
                                                                 "message": message,
                                                                 "timestamp": datetime.now(),
                                                                 "attachedfiles": filename1,
                                                                 "status": "waiting for approved"
                                                             }
                                                             }})

                            session["message"] = "Project submitted successfully.."
                            session["projectID"] = str(project_id)
                            session["buyerID"] = str(buyer_id)
                            return redirect(url_for("working_order"))
                        else:
                            session["error"] = "Invalid status of job"
                            session["projectID"] = str(project_id)
                            return redirect(url_for("working_order"))
                    else:
                        session["error"] = "Invalid values in form."
                        return redirect(url_for("working_order"))
                else:
                    session["error"] = "Invalid actor."
                    return redirect(url_for("working_order"))
            else:
                session["error"] = "Invalid method of request."
                return redirect(url_for("working_order"))
        else:
            return redirect(url_for("login"))
    except Exception as e:
        session["error"] = str(e) + str(".\t\tRoute: /send-revision")
        return redirect(url_for("show_error"))


# Step 5:
# Send-revision by the buyer to actor
@app.route('/send-revision', methods=["GET", "POST"])
def send_revision():
    try:
        if session.get("email") and session.get("type") and session.get("username"):
            if request.method == "POST":
                if session.get("type") == "buyer":
                    actor_Id = session.get("userid")
                    if request.form['buyer_id'] == actor_Id:
                        data = request.form
                        actor_id = data['actor_id']
                        buyer_id = data['buyer_id']
                        project_id = data['project_id']
                        bidding_table = mydb["bidding"]
                        message = data["message"]
                        anyData = bidding_table.find_one(
                            {"actor_id": ObjectId(actor_id), "buyer_id": ObjectId(buyer_id),
                             "project_id": ObjectId(project_id)})
                        if anyData['offeraccpt']['status'] == "accepted":
                            bidding_table.update_one({"actor_id": ObjectId(actor_id),
                                                      "buyer_id": ObjectId(buyer_id),
                                                      "project_id": ObjectId(project_id)},
                                                     {
                                                         "$addToSet":
                                                             {"revisions":
                                                                 {
                                                                     "message": message,
                                                                     "timestamp": datetime.now(),
                                                                     "response": "buyer"
                                                                 }
                                                             }})

                            session["message"] = "Revision submitted successfully.."
                            session["projectID"] = str(project_id)
                            return redirect(url_for("project_responses"))
                        else:
                            session["error"] = "Invalid status of job"
                            session["projectID"] = str(project_id)
                            return redirect(url_for("project_responses"))
                    else:
                        session["error"] = "Invalid values in form."
                        return redirect(url_for("joblist"))
                else:
                    session["error"] = "Invalid actor."
                    return redirect(url_for("joblist"))
            else:
                session["error"] = "Invalid method of request."
                return redirect(url_for("joblist"))
        else:
            return redirect(url_for("login"))
    except Exception as e:
        session["error"] = str(e) + str(".\t\tRoute: /send-revision")
        return redirect(url_for("show_error"))


# Step 6
# Show order to the actor against the revisions.
@app.route('/receive-revision', methods=["GET", "POST"])
def working_order():
    try:
        if session.get("email") and session.get("type") and session.get("username"):
            if request.method == "POST":
                if session.get("type") == "actor":
                    print(request.form)
                    print(request.files)
                    actor_Id = session.get("userid")
                    if request.form['actor_id'] == actor_Id:
                        data = request.form
                        actor_id = data['actor_id']
                        buyer_id = data['buyer_id']
                        project_id = data['project_id']
                        bidding_table = mydb["bidding"]
                        message = data["revisionmessage"]
                        filename1 = ""
                        if "revisionFiles" in request.files:
                            project_file = request.files["revisionFiles"]
                            if project_file.filename != "":
                                filename1 = secure_filename(project_file.filename)
                                filename1 = str(datetime.now().strftime("%Y%m%d%H%M")) + "-" + str(filename1).replace(
                                    "-", "")
                                project_file.save(os.path.join(app.config['UPLOAD_FOLDER5'], filename1))
                            session["error"] = "Files required"
                        else:
                            return redirect(url_for("working_order"))
                        anyData = bidding_table.find_one(
                            {"actor_id": ObjectId(actor_id), "buyer_id": ObjectId(buyer_id),
                             "project_id": ObjectId(project_id)})
                        if anyData['offeraccpt']['status'] == "accepted":
                            bidding_table.update_one({"actor_id": ObjectId(actor_id),
                                                      "buyer_id": ObjectId(buyer_id),
                                                      "project_id": ObjectId(project_id)},
                                                     {
                                                         "$addToSet":
                                                             {"revisions": {
                                                                 "message": message,
                                                                 "timestamp": datetime.now(),
                                                                 "attachedfiles": filename1,
                                                                 "status": "waiting for approved",
                                                                 "response": "actor"
                                                             }
                                                             }})
                            bidding_table.update_one({"actor_id": ObjectId(actor_id),
                                                      "buyer_id": ObjectId(buyer_id),
                                                      "project_id": ObjectId(project_id)},
                                                     {"$set": {"projectSubmit.status": "request for revision"}})

                            session["message"] = "Revision submitted successfully.."
                            session["projectID"] = str(project_id)
                            session["buyerID"] = str(buyer_id)
                            return redirect(url_for("working_order"))
                        else:
                            session["error"] = "Invalid status of job"
                            session["projectID"] = str(project_id)
                            return redirect(url_for("working_order"))
                    else:
                        session["error"] = "Invalid values in form."
                        return redirect(url_for("joblist"))
                else:
                    session["error"] = "Invalid actor."
                    return redirect(url_for("joblist"))
            else:
                if session.get("userid"):
                    data = request.args
                    actor_id = session.get("userid")
                    if "project_id" in data:
                        buyer_id = data['buyer_id']
                        project_id = data['project_id']
                    else:
                        buyer_id = session.get("buyerID")
                        project_id = session.get("projectID")
                        session.pop("buyerID", None)
                        session.pop("projectID", None)
                    username = session.get("username")
                    email = session.get("email")
                    type = session.get("type")

                    if project_id is None:
                        project_id = session.get("projectID")
                        session.pop("projectID", None)
                    table = mydb["buyer"]
                    project_details = table.find_one(
                        {"_id": ObjectId(buyer_id), "projects.project_id": ObjectId(project_id)},
                        {"projects": {"$elemMatch": {"project_id": ObjectId(project_id)}}}
                    )
                    table = mydb["category"]
                    categoriesNew = table.find({})
                    categories = []
                    for i in categoriesNew:
                        categories.append(i)
                    table = mydb["bidding"]
                    bid_data1 = table.find({"buyer_id": ObjectId(buyer_id), "project_id": ObjectId(project_id)})
                    bid_data = []
                    for i in bid_data1:
                        if actor_id == str(i['actor_id']):
                            bid_data.append(i)
                    error = ""
                    if session.get("error"):
                        error = session.get("error")
                        session.pop("error", None)
                    message = ""
                    if session.get("message"):
                        message = session.get("message")
                        session.pop("message", None)
                    return render_template("joblist_order.html", username=username, email=email, type=type,
                                           error=error,
                                           message=message, project_details=project_details, categories=categories,
                                           project_id=project_id, bid_data=bid_data)
        else:
            return redirect(url_for("login"))
    except Exception as e:
        session["error"] = str(e) + str(".\t\tRoute: /receive-revision")
        return redirect(url_for("show_error"))


# Step 7
# Comments and review to actor for that particular project by the buyer.
@app.route('/project-reviews', methods=["GET", "POST"])
def project_reviews():
    try:
        if session.get("email") and session.get("type") and session.get("username"):
            if request.method == "POST":
                if session.get("type") == "buyer":
                    actor_Id = session.get("userid")
                    if request.form['id_buyer'] == actor_Id:
                        data = request.form
                        actor_id = data['id_actor']
                        buyer_id = data['id_buyer']
                        project_id = data['id_project']
                        project_comment = data['comment']
                        project_review = data['review']
                        bidding_table = mydb["bidding"]
                        anyData = bidding_table.find_one(
                            {"actor_id": ObjectId(actor_id), "buyer_id": ObjectId(buyer_id),
                             "project_id": ObjectId(project_id)})
                        if anyData['offeraccpt']['status'] == "accepted":
                            bidding_table.update_one({"actor_id": ObjectId(actor_id),
                                                      "buyer_id": ObjectId(buyer_id),
                                                      "project_id": ObjectId(project_id)},
                                                     {
                                                         "$set":
                                                             {"offeraccpt.status": "completed",
                                                              "projectStataus": "completed",
                                                              "completionTime": datetime.now(),
                                                              "comments": project_comment,
                                                              "reviews": project_review
                                                              }
                                                     })
                            # buyer_table = mydb["buyer"]
                            # buyer_table.update_one({})
                            session["message"] = "You have successfull review the actor against your project."
                            session["projectID"] = str(project_id)
                            return redirect(url_for("project_responses"))
                        else:
                            session["error"] = "Invalid status of job"
                            session["projectID"] = str(project_id)
                            return redirect(url_for("project_responses"))
                    else:
                        session["error"] = "Invalid values in form."
                        return redirect(url_for("joblist"))
                else:
                    session["error"] = "Invalid actor."
                    return redirect(url_for("joblist"))
            else:
                session["error"] = "Invalid method of request."
                return redirect(url_for("joblist"))
        else:
            return redirect(url_for("login"))
    except Exception as e:
        session["error"] = str(e) + str(".\t\tRoute: /project-review")
        return redirect(url_for("show_error"))


@app.route("/payment")
def payment():
    try:
        if session.get("email") and session.get("type") and session.get("username"):
            username = session.get("username")
            email = session.get("email")
            type1 = session.get("type")
            userid = session.get("userid")
            if session.get("type") == "actor":
                table = mydb["transactions"]
                transactions1 = table.find({"actor_id": ObjectId(userid)})
                transactions_data = []
                for i in transactions1:
                    transactions_data.append(i)
                actor_bidding_data = []
                table = mydb['bidding']
                actor_bidding_data1 = table.find({"actor_id": ObjectId(userid), "offeraccpt.status": "accepted"})
                for i in actor_bidding_data1:
                    actor_bidding_data.append(i)
                print(actor_bidding_data)
                print(transactions_data)
                return render_template("payment.html", type=type1, email=email, username=username,
                                       transactions_data=transactions_data, actor_bidding_data=actor_bidding_data)
            else:
                return render_template("payment.html", type=type, email=email, username=username)
        else:
            return redirect(url_for("login"))
    except Exception as e:
        session["error"] = str(e) + "\t\t Route is /payment"
        return redirect(url_for("show_error"))




# About us route
@app.route("/about-us", methods=["GET", "POST"])
def about_us():
    try:
        if request.method == "POST":
            return redirect(url_for(about_us))
        else:
            username = session.get("username")
            email = session.get("email")
            type = session.get("type")
            return render_template("aboutus.html", username=username, email=email, type=type)
    except Exception as e:
        session["error"] = str(e)
        return redirect(url_for("show_error"))


# Contact us route
@app.route("/contact-us", methods=["GET", "POST"])
def contact_us():
    try:
        if request.method == "POST":

            fname = request.form["fname"]
            lname = request.form["lname"]
            email = request.form["email"]
            phone = request.form["phone"]
            message = request.form["message"]

            contact_info_table = mydb["contact_info"]

            contact_info_table.insert_one({"fname": fname, "lname": lname, "email": email,
                                   "phone": phone, "message": message,
                                   "planDate": datetime.now()})

            data = {
                            "personalizations": [
                                {
                                "to": [
                                    {
                                    "email": "info@voicescity.com"
                                    }
                                ],
                                "subject": "Contact Information"
                                }
                            ],
                            "from": {
                                "email": default_sender,
                                "name": "Voices City"
                            },
                            "content": [
                                {
                                "type": "text/html",
                                "value": """<p><strong>First Name: </strong> """ + fname + """</p>
                                            <p><strong>Last Name: </strong> """ + lname + """</p>
                                            <p><strong>Email: </strong> """ + email + """</p> 
                                            <p><strong>Phone: </strong> """ + phone + """</p> 
                                            <h5><strong>Message: </strong></h5>
                                            <p>"""+ message + """</p>"""} ] }
            sg = SendGridAPIClient(api_key)
            response = sg.client.mail.send.post(request_body=data)
            data = {
                            "personalizations": [
                                {
                                "to": [
                                    {
                                    "email": email
                                    }
                                ],
                                "subject": "Your Voice City support request has been created"
                                }
                            ],
                            "from": {
                                "email": default_sender,
                                "name": "Voices City"
                            },
                            "content": [
                                {
                                "type": "text/html",
                                "value": """<th style="margin:0 auto; color:#0a0a0a; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-bottom:16px; padding-left:16px; padding-right:16px; text-align:left; width:564px">
	<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
		<tbody>
			<tr style="padding:0; text-align:left; vertical-align:top">
				<th style="margin:0; color:#0a0a0a; font-family:Helvetica,Arial,sans-serif; font-size:14px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left">
					<p>Thank you for contacting Voicescity.</p>
					<p>We've received your request and will reply shortly.</p>
					<p>Kind Regards,</p>
					<p><strong>Voicescity Team </strong>
						<p>
							<br aria-hidden="true"><img data-imagetype="External" src="http://voicescity.com/static/logo1.png" height=35px;/><strong><span style="color:#1171bb">Voicescity.com</span></strong>
							<br aria-hidden="true">+447888884150
							<br aria-hidden="true"><a href="mailto:support@voicescity.com" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" data-linkindex="3">support@voicescity.com</a> | <a href="https://voicescity.com/" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" data-linkindex="4">voicescity.com</a> </div>
				</th>
				<th style="margin:0; color:#0a0a0a; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0!important; text-align:left; width:0"></th>
			</tr>
		</tbody>
	</table>
</th>
<table style="margin:0 auto; background:#ffffff; border:1px solid #ccc; border-collapse:collapse; border-spacing:0; border:none; color:grey; float:none; margin:0 auto; padding:0; text-align:center; vertical-align:top; width:600px" align="center">
	<tbody>
		<tr style="padding:0; text-align:left; vertical-align:top">
			<td style="margin:0; border-collapse:collapse!important; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; vertical-align:top; word-wrap:break-word">
				<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
					<tbody>
						<tr style="padding:0; text-align:left; vertical-align:top">
							<td style="margin:0; border-collapse:collapse!important; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:15px; font-weight:400; line-height:15px; margin:0; padding:0; text-align:left; vertical-align:top; word-wrap:break-word" height="15px">&nbsp;</td>
						</tr>
					</tbody>
				</table>
				<table style="border-collapse:collapse; border-spacing:0; display:table; padding:0; text-align:left; vertical-align:top; width:100%">
					<tbody>
						<tr style="padding:0; text-align:left; vertical-align:top">
							<th style="margin:0 auto; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-bottom:0; padding-left:16px; padding-right:16px; text-align:left; width:564px">
								<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
									<tbody>
										<tr style="padding:0; text-align:left; vertical-align:top">
											<th style="margin:0; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left">
												<center style="min-width:532px; width:100%"><span align="center" style="font-size:12px">LET'S BE FRIENDS</span></center>
											</th>
											<th style="margin:0; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0!important; text-align:left; width:0"></th>
										</tr>
									</tbody>
								</table>
							</th>
						</tr>
					</tbody>
				</table>
				<table style="border-collapse:collapse; border-spacing:0; display:table; padding:0; text-align:left; vertical-align:top; width:100%">
					<tbody>
						<tr style="padding:0; text-align:left; vertical-align:top">
							<th style="margin:0 auto; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-left:27px; padding-right:16px; text-align:left; width:564px">
								<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
									<tbody>
										<tr style="padding:0; text-align:left; vertical-align:top">
											<th style="margin:0; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left">
												<center style="min-width:532px; width:100%">
													<table style="margin:0 auto; border-collapse:collapse; border-spacing:0; float:none; margin:0 auto; padding:0; text-align:center; vertical-align:top; width:auto!important" align="center">
														<tbody>
															<tr style="padding:0; text-align:left; vertical-align:top">
																<td style="margin:0; border-collapse:collapse!important; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; vertical-align:top; word-wrap:break-word">
																	<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
																		<tbody>
																			<tr style="padding:0; text-align:left; vertical-align:top">
																				<th style="margin:0 auto; color:inherit; float:none; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-right:10px; text-align:center">
																					<a href="https://twitter.com/VoicesCity2?s=08" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="margin:0; color:#17b; font-family:Helvetica,Arial,sans-serif; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; text-decoration:none" data-linkindex="5"><img data-imagetype="External" src="http://voicescity.com/static/twitter.png" originalsrc="http://go.pardot.com/l/55082/2015-09-30/3gccd5/55082/68476/SocialButton3_TWR_BlueOnWhite_50X75.png" data-connectorsauthtoken="1" data-imageproxyendpoint="/actions/ei" data-imageproxyid="" alt="Twitter" style="border:none; clear:both; display:block; max-width:100%; outline:0; text-decoration:none; width:20px;"> </a>
																				</th>
																				<th style="margin:0 auto; color:inherit; float:none; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-right:10px; text-align:center">
																					<a href="https://www.facebook.com/Voices-City-332687944647576/" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="margin:0; color:#17b; font-family:Helvetica,Arial,sans-serif; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; text-decoration:none" data-linkindex="6"><img data-imagetype="External" src="http://voicescity.com/static/facebook.png" originalsrc="http://go.pardot.com/l/55082/2015-09-30/3gcccp/55082/68474/SocialButton2_FB_BlueOnWhite_50X75.png" data-connectorsauthtoken="1" data-imageproxyendpoint="/actions/ei" data-imageproxyid="" alt="Facebook" style="border:none; clear:both; display:block; max-width:100%; outline:0; text-decoration:none; width:30px;"> </a>
																				</th>
																				<th style="margin:0 auto; color:inherit; float:none; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-right:10px; text-align:center">
																					<a href="https://www.linkedin.com/in/voices-city-33990a205" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="margin:0; color:#17b; font-family:Helvetica,Arial,sans-serif; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; text-decoration:none" data-linkindex="7"><img data-imagetype="External" src="http://voicescity.com/static/linkedin.png" originalsrc="http://go.pardot.com/l/55082/2015-09-30/3gccd7/55082/68478/SocialButton1_LI_BlueOnWhite_50X75.png" data-connectorsauthtoken="1" data-imageproxyendpoint="/actions/ei" data-imageproxyid="" alt="LinkedIn" style="border:none; clear:both; display:block; max-width:100%; outline:0; text-decoration:none; width:20px;"> </a>
																				</th>
																			</tr>
																		</tbody>
																	</table>
																</td>
															</tr>
														</tbody>
													</table>
												</center>
											</th>
											<th style="margin:0; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0!important; text-align:left; width:0"></th>
										</tr>
									</tbody>
								</table>
							</th>
						</tr>
					</tbody>
				</table>
			</td>
		</tr>
	</tbody>
</table>
</table>"""} ] }
            sg = SendGridAPIClient(api_key)
            response = sg.client.mail.send.post(request_body=data)
            session["message"] = "Your respond has been submitted"                                
            return redirect("contact-us")
        else:
            username = session.get("username")
            email = session.get("email")
            type = session.get("type")
            message = ""
            if session.get("message"):
                message = session.get("message")
                session.pop("message", None)
            return render_template("contactus.html", username=username, email=email, type=type, message=message)
    except Exception as e:
        session["error"] = str(e)
        return redirect(url_for("show_error"))


# Career routes
@app.route("/careers", methods=["GET", "POST"])
def careers():
    try:
        if request.method == "POST":
            return redirect(url_for(about_us))
        else:
            username = session.get("username")
            email = session.get("email")
            type = session.get("type")
            return render_template("career.html", username=username, email=email, type=type)
    except Exception as e:
        session["error"] = str(e)
        return redirect(url_for("show_error"))

# Terms-Condition
@app.route("/terms-condition", methods=["GET", "POST"])
def terms_condition():
    try:
        if request.method == "POST":
            return redirect(url_for(about_us))
        else:
            username = session.get("username")
            email = session.get("email")
            type = session.get("type")
            return render_template("terms-condition.html", username=username, email=email, type=type)
    except Exception as e:
        session["error"] = str(e)
        return redirect(url_for("show_error"))


# privacy-policy
@app.route("/privacy-policy", methods=["GET", "POST"])
def privacy_policy():
    try:
        if request.method == "POST":
            return redirect(url_for(about_us))
        else:
            username = session.get("username")
            email = session.get("email")
            type = session.get("type")
            return render_template("privacy-policy.html", username=username, email=email, type=type)
    except Exception as e:
        session["error"] = str(e)
        return redirect(url_for("show_error"))


#trust-and-safety-html
@app.route("/trust-and-safety", methods=["GET", "POST"])
def trust_and_safety():
    try:
        if request.method == "POST":
            return redirect(url_for(about_us))
        else:
            username = session.get("username")
            email = session.get("email")
            type = session.get("type")
            return render_template("trust-and-safety.html", username=username, email=email, type=type)
    except Exception as e:
        session["error"] = str(e)
        return redirect(url_for("show_error"))



#How-It-Works
@app.route("/How-It-Works", methods=["GET", "POST"])
def How_it_Works():
    try:
        if request.method == "POST":
            return redirect(url_for(about_us))
        else:
            username = session.get("username")
            email = session.get("email")
            type = session.get("type")
            return render_template("How-It-Works.html", username=username, email=email, type=type)
    except Exception as e:
        session["error"] = str(e)
        return redirect(url_for("show_error"))


#faq
@app.route("/faq", methods=["GET", "POST"])
def faq():
    try:
        if request.method == "POST":
            return redirect(url_for(about_us))
        else:
            username = session.get("username")
            email = session.get("email")
            type = session.get("type")
            return render_template("faq.html", username=username, email=email, type=type)
    except Exception as e:
        session["error"] = str(e)
        return redirect(url_for("show_error"))


# Main Sectors
@app.route("/main-sector", methods=["GET", "POST"])
def Main_Sectors():
    try:
        if request.method == "POST":
            return redirect(url_for(about_us))
        else:
            username = session.get("username")
            email = session.get("email")
            type = session.get("type")
            args_category = request.args.get("sector")
            if args_category == "Voice Over":
                category = "voice over"
                args_category = "61f983868919cea182127724"
                content_display = 1
            elif args_category == "Documentaries":
                category = "documentaries"
                args_category = "61f983868919cea182127725"
                content_display = 2
            elif args_category == "Commercials":
                category = "commercials"
                args_category = "61f983868919cea182127726"
                content_display = 3
            elif args_category == "Narration":
                category = "narration"
                args_category = "61f983868919cea182127727"
                content_display = 4
            elif args_category == "Audiobooks":
                category = "audiobooks"
                args_category = "61f983878919cea182127728"
                content_display = 5
            elif args_category == "Gaming":
                category = "gaming"
                args_category = "61f983878919cea182127729"
                content_display = 6
            elif args_category == "Podcasts":
                category = "podcasts"
                args_category = "61f983878919cea18212772a"
                content_display = 7
            elif args_category == "IVRS":
                category = "ivrs"
                args_category = "61f983858919cea182127722"
                content_display = 8
            elif args_category == "Training and Explainer Videos":
                category = "training & explainer videos"
                args_category = "61f983888919cea18212772b"
                content_display = 9
            elif args_category == "Animation Films and Series":
                category = "animation films & series"
                args_category = "61f983858919cea182127721"
                content_display = 10
            elif args_category == "Tv and Radio":
                category = "tv & radio"
                args_category = "61f983888919cea18212772c"
                content_display = 11
            elif args_category == "Dubbing Movies and Dramas":
                category = "dubbing movies & dramas"
                args_category = "61f983888919cea18212772d"
                content_display = 12
            else:
                args_category = "600dc98f5e9f967f3c434601"
                content_display = 1

            args_category = args_category.split(",")
            print(args_category)

            table = mydb["category"]
            args_category_name = table.find_one({"Category Name": category})
            args_category_name = args_category_name["Category Name"]

            print(args_category_name)
            languages, countries, dead_line, categories, delivery_options, proposals, accents = fetch_record()
            table = mydb["actor"]

            the_actors = table.aggregate([
                # {"$match": {"planType": {"or": ['premium', 'gold']}}},
                {
                    "$project": {"playlists": 1, "userName": 1, "profilePicture": 1,
                                 "Location": 1}
                }
                ,
                {
                    "$unwind": "$playlists"
                }
                ,
                {
                    "$project": {
                        "playlists": "$playlists",
                        "userName": "$userName",
                        "profilePicture": "$profilePicture",
                        "profilePicture": "$profilePicture",
                        "Location": "$Location",
                        "matchesgener": {"$cond": {"if": {"$eq": [{"$size": {
                            "$setIntersection": [languages, "$playlists.playlist_language"
                                                 ]}}, 0]}, "then": "NULL", "else": "True"}},
                        "matchesgender": {"$cond": {"if": {"$eq": [{"$size": {
                            "$setIntersection": ["$playlists.playlist_category",
                                                 args_category]}}, 0]}, "then": "NULL",
                            "else": "True"}}
                    }
                },
                {
                    "$match": {
                        "$or": [{"matchesgener": {"$eq": "True"}}, {"matchesgender": {"$eq": "True"}}]}
                }
            ])
            actors = []
            for i in the_actors:
                actors.append(i)
            return render_template("main_sector.html", username=username, email=email, type=type, languages=languages,
                                   categories=categories, actors=actors, args_category=args_category, accents=accents,
                                   args_category_name=args_category_name, content_display=content_display)
    except Exception as e:
        session["error"] = str(e)
        return redirect(url_for("show_error"))


@app.route("/Main-Sectors-page-1", methods=["GET", "POST"])
def Main_Sectors1():
    try:
        if request.method == "POST":
            return redirect(url_for(about_us))
        else:
            username = session.get("username")
            email = session.get("email")
            type = session.get("type")
            languages, countries, dead_line, categories, delivery_options, proposals,accents = fetch_record()
            return render_template("Main-Sectors-page-1.html", username=username, email=email, type=type, languages=languages, categories=categories)
    except Exception as e:
        session["error"] = str(e)
        return redirect(url_for("show_error"))




@app.route("/Main-Sectors-page-2", methods=["GET", "POST"])
def Main_Sectors2():
    try:
        if request.method == "POST":
            return redirect(url_for(about_us))
        else:
            username = session.get("username")
            email = session.get("email")
            type = session.get("type")
            languages, countries, dead_line, categories, delivery_options, proposals,accents = fetch_record()
            return render_template("Main-Sectors-page-2.html", username=username, email=email, type=type, languages=languages, categories=categories)
    except Exception as e:
        session["error"] = str(e)
        return redirect(url_for("show_error"))



@app.route("/Main-Sectors-page-3", methods=["GET", "POST"])
def Main_Sectors3():
    try:
        if request.method == "POST":
            return redirect(url_for(about_us))
        else:
            username = session.get("username")
            email = session.get("email")
            type = session.get("type")
            languages, countries, dead_line, categories, delivery_options, proposals,accents = fetch_record()
            return render_template("Main-Sectors-page-3.html", username=username, email=email, type=type, languages=languages, categories=categories)
    except Exception as e:
        session["error"] = str(e)
        return redirect(url_for("show_error"))




@app.route("/Main-Sectors-page-4", methods=["GET", "POST"])
def Main_Sectors4():
    try:
        if request.method == "POST":
            return redirect(url_for(about_us))
        else:
            username = session.get("username")
            email = session.get("email")
            type = session.get("type")
            languages, countries, dead_line, categories, delivery_options, proposals,accents = fetch_record()
            return render_template("Main-Sectors-page-4.html", username=username, email=email, type=type, languages=languages, categories=categories)
    except Exception as e:
        session["error"] = str(e)
        return redirect(url_for("show_error"))




@app.route("/Main-Sectors-page-5", methods=["GET", "POST"])
def Main_Sectors5():
    try:
        if request.method == "POST":
            return redirect(url_for(about_us))
        else:
            username = session.get("username")
            email = session.get("email")
            type = session.get("type")
            languages, countries, dead_line, categories, delivery_options, proposals,accents = fetch_record()
            return render_template("Main-Sectors-page-5.html", username=username, email=email, type=type, languages=languages, categories=categories)
    except Exception as e:
        session["error"] = str(e)
        return redirect(url_for("show_error"))





@app.route("/Main-Sectors-page-6", methods=["GET", "POST"])
def Main_Sectors6():
    try:
        if request.method == "POST":
            return redirect(url_for(about_us))
        else:
            username = session.get("username")
            email = session.get("email")
            type = session.get("type")
            languages, countries, dead_line, categories, delivery_options, proposals,accents = fetch_record()
            return render_template("Main-Sectors-page-6.html", username=username, email=email, type=type, languages=languages, categories=categories)
    except Exception as e:
        session["error"] = str(e)
        return redirect(url_for("show_error"))





@app.route("/Main-Sectors-page-7", methods=["GET", "POST"])
def Main_Sectors7():
    try:
        if request.method == "POST":
            return redirect(url_for(about_us))
        else:
            username = session.get("username")
            email = session.get("email")
            type = session.get("type")
            languages, countries, dead_line, categories, delivery_options, proposals,accents = fetch_record()
            return render_template("Main-Sectors-page-7.html", username=username, email=email, type=type, languages=languages, categories=categories)
    except Exception as e:
        session["error"] = str(e)
        return redirect(url_for("show_error"))






@app.route("/Main-Sectors-page-8", methods=["GET", "POST"])
def Main_Sectors8():
    try:
        if request.method == "POST":
            return redirect(url_for(about_us))
        else:
            username = session.get("username")
            email = session.get("email")
            type = session.get("type")
            languages, countries, dead_line, categories, delivery_options, proposals,accents = fetch_record()
            return render_template("Main-Sectors-page-8.html", username=username, email=email, type=type, languages=languages, categories=categories)
    except Exception as e:
        session["error"] = str(e)
        return redirect(url_for("show_error"))






@app.route("/Main-Sectors-page-9", methods=["GET", "POST"])
def Main_Sectors9():
    try:
        if request.method == "POST":
            return redirect(url_for(about_us))
        else:
            username = session.get("username")
            email = session.get("email")
            type = session.get("type")
            languages, countries, dead_line, categories, delivery_options, proposals,accents = fetch_record()
            return render_template("Main-Sectors-page-9.html", username=username, email=email, type=type, languages=languages, categories=categories)
    except Exception as e:
        session["error"] = str(e)
        return redirect(url_for("show_error"))




@app.route("/Main-Sectors-page-10", methods=["GET", "POST"])
def Main_Sectors10():
    try:
        if request.method == "POST":
            return redirect(url_for(about_us))
        else:
            username = session.get("username")
            email = session.get("email")
            type = session.get("type")
            languages, countries, dead_line, categories, delivery_options, proposals,accents = fetch_record()
            return render_template("Main-Sectors-page-10.html", username=username, email=email, type=type, languages=languages, categories=categories)
    except Exception as e:
        session["error"] = str(e)
        return redirect(url_for("show_error"))





@app.route("/Main-Sectors-page-11", methods=["GET", "POST"])
def Main_Sectors11():
    try:
        if request.method == "POST":
            return redirect(url_for(about_us))
        else:
            username = session.get("username")
            email = session.get("email")
            type = session.get("type")
            languages, countries, dead_line, categories, delivery_options, proposals,accents = fetch_record()
            return render_template("Main-Sectors-page-11.html", username=username, email=email, type=type, languages=languages, categories=categories)
    except Exception as e:
        session["error"] = str(e)
        return redirect(url_for("show_error"))




@app.route("/Main-Sectors-page-12", methods=["GET", "POST"])
def Main_Sectors12():
    try:
        if request.method == "POST":
            return redirect(url_for(about_us))
        else:
            username = session.get("username")
            email = session.get("email")
            type = session.get("type")
            languages, countries, dead_line, categories, delivery_options, proposals,accents = fetch_record()
            return render_template("Main-Sectors-page-12.html", username=username, email=email, type=type, languages=languages, categories=categories)
    except Exception as e:
        session["error"] = str(e)
        return redirect(url_for("show_error"))




# Error Route
@app.route("/something-went-wrong", methods=["GET", "POST"])
def show_error():
    if session.get("error"):
        error = session.get("error")
        session["errors"] = error
        session.pop("error", None)
    else:
        error = session.get("errors")
        if error == None:
            error = ""
    username = session.get("username")
    email = session.get("email")
    type = session.get("type")
    return render_template("error.html", error=error, username=username, email=email, type=type)



@app.route("/profile")
def profile():
    username = session.get("username")
    email = session.get("email")
    type = session.get("type")
    return render_template("profile.html", username=username, email=email, type=type)


# @app.route("/chat")
# def chat():
#     username = session.get("username")
#     email = session.get("email")
#     type = session.get("type")
#     return render_template("chat.html", username=username, email=email, type=type)


@app.route("/order")
def order():
    return render_template("order.html")


@app.route("/gig")
def gig():
    return render_template("Gig.html")


@app.route("/demo")
def demo():
    return render_template("demo.html")


@app.route("/demoedit")
def demoedit():
    return render_template("demoedit.html")


# new pages
@app.route("/teaminvite")
def teaminvite():
    return render_template("teaminvite.html")


@app.route("/manageteam")
def manageteam():
    return render_template("manageteam.html")


@app.route("/hired-actors")
def hiredactors():
    return render_template("hired-actors.html")



@app.route("/category")
def category():
    return render_template("category.html")


@app.route('/voiceover-rates', methods=["GET", "POST"])
def voiceover_rates():
    try:
        if request.method == "POST":
            languages, countries, dead_line, categories, delivery_options, proposals, accents = fetch_record()
            langauge = languages
            catego1 = request.form.getlist('age')
            table = mydb['actor']
            the_actors = table.aggregate([
                {
                    "$project": {"playlists": 1, "userName": 1, "profilePicture": 1,
                                 "Location": 1}
                }
                ,
                {
                    "$unwind": "$playlists"
                }
                ,
                {
                    "$project": {
                        "playlists": "$playlists",
                        "userName": "$userName",
                        "profilePicture": "$profilePicture",
                        "profilePicture": "$profilePicture",
                        "Location": "$Location",
                        "matchesgener": {"$cond": {"if": {"$eq": [{"$size": {
                            "$setIntersection": [langauge, "$playlists.playlist_language"
                                                 ]}}, 0]}, "then": "NULL", "else": "True"}},
                        "matchesgender": {"$cond": {"if": {"$eq": [{"$size": {
                            "$setIntersection": ["$playlists.playlist_category",
                                                 catego1]}}, 0]}, "then": "NULL",
                            "else": "True"}}
                    }
                },
                {
                    "$match": {
                        "$or": [{"matchesgener": {"$eq": "True"}}, {"matchesgender": {"$eq": "True"}}]}
                }
            ])
            actors = []
            for i in the_actors:
                actors.append(i)
            return jsonify({"success": True, "data": actors})
        else:
            languages, countries, dead_line, categories, delivery_options, proposals, accents = fetch_record()
            type1 = session.get("type")
            email = session.get("email")
            username = session.get("username")
            userid = session.get("userid")
            return render_template('voiceover_rates.html', type=type1, email=email, username=username,
                                   languages=languages, categories=categories, accents=accents)
    except Exception as e:
        session['error'] = str(e) + "\t\t Route /voiceover-rates"
        return redirect(url_for('show_error'))


@app.route('/voiceover-actors', methods=["GET", "POST"])
def voiceover_actors():
    try:
        if request.method == "POST":

            return redirect(url_for('voiceover_rates'))
        else:
            languages, countries, dead_line, categories, delivery_options, proposals, accents = fetch_record()
            langauge = languages
            catego1 = request.args.getlist('age')
            table = mydb['actor']
            the_actors = table.aggregate([
                {
                    "$project": {"playlists": 1, "userName": 1, "profilePicture": 1,
                                 "Location": 1}
                }
                ,
                {
                    "$unwind": "$playlists"
                }
                ,
                {
                    "$project": {
                        "playlists": "$playlists",
                        "userName": "$userName",
                        "profilePicture": "$profilePicture",
                        "profilePicture": "$profilePicture",
                        "Location": "$Location",
                        "matchesgener": {"$cond": {"if": {"$eq": [{"$size": {
                            "$setIntersection": [langauge, "$playlists.playlist_language"
                                                 ]}}, 0]}, "then": "NULL", "else": "True"}},
                        "matchesgender": {"$cond": {"if": {"$eq": [{"$size": {
                            "$setIntersection": ["$playlists.playlist_category",
                                                 catego1]}}, 0]}, "then": "NULL",
                            "else": "True"}}
                    }
                },
                {
                    "$match": {
                        "$or": [{"matchesgener": {"$eq": "True"}}, {"matchesgender": {"$eq": "True"}}]}
                }
            ])
            actors = []
            for i in the_actors:
                actors.append(i)
            return render_template('voiceover_actors.html', actors=actors, languages=languages, categories=categories)
    except Exception as e:
        session['error'] = str(e) + "\t\t Route /voiceover-rates"
        return redirect(url_for('show_error'))


@app.route("/logout")
def logout():
    session.pop("email", None)
    session.pop("username", None)
    session.pop("type", None)
    session.pop("_id", None)
    return redirect("/")

# Admin
@app.route("/admin/logout")
def adminlogout():
    session.pop("adminemail", None)
    session.pop("adminusername", None)
    session.pop("admintype", None)
    return redirect("/admin/login")


@app.route('/admin')
def superadmin():
    return redirect(url_for("adminlogin"))


@app.route("/admin/login", methods=["GET", "POST"])
def adminlogin():
    try:
        if session.get("admintype") == "admin" and session.get("adminemail") and session.get("adminusername"):
            return redirect("/admin/home")
        else:
            if request.method == "POST":
                email = request.form["email"]
                password = request.form["password"]
                admintable = mydb["admin"]
                admindata = admintable.find_one({"email": email})
                if admindata != None:
                    if check_password_hash(admindata["password_hash"], password):
                        session["adminemail"] = email
                        session["adminusername"] = admindata["username"]
                        session["admintype"] = "admin"
                        return redirect("/admin/home")
                    else:
                        session["adminloginerror"] = "Password is incorrect."
                        return redirect("/admin/login")
                else:
                    session["adminloginerror"] = "Email is incorrect."
                    return redirect("/admin/login")
            else:
                loginerror = "NULL"
                if session.get("adminloginerror"):
                    loginerror = session.get("adminloginerror")
                    session.pop("adminloginerror", None)
                return render_template("adminlogin.html", loginerror=loginerror)
    except Exception as e:
        session["adminloginerror"] = "Email or password is incorrect.Or " + str(e)
        return redirect("/admin/login")


@app.route("/admin/home", methods=["GET", "POST"])
def adminhome():
    try:
        if session.get("admintype") == "admin" and session.get("adminemail") and session.get("adminusername"):
            if request.method == "POST":
                return redirect("/admin/home")
            else:
                actortable = mydb["actor"]
                data_actor = actortable.find({})
                total_actor = data_actor.count()
                totalPremiumActors = actortable.find({"planType": "premium"}).count()
                totalBronzeActors = actortable.find({"planType": "bronze"}).count()
                table = mydb["buyer"]
                total_buyer = table.find({}).count()
                total_projects = table.aggregate([
                    {"$unwind": "$projects"},
                    {
                        "$project": {
                            "projects.status": 1,
                            "projects.project_cost": 1
                        }
                    },
                    {
                        "$group": {
                            "_id": "$projects.status",
                            "count": {"$sum": 1},
                            "sum": {"$sum": "$project_cost"}
                        }
                    }
                ])

                curdate = datetime.now()
                lastweekdays = []
                lastweekdaysStr = []
                for i in range(8):
                    print(i)
                    newdate = curdate - timedelta(days=7 - i)
                    newdate = newdate.strftime("%Y-%m-%d")
                    lastweekdaysStr.append(newdate)
                    lastweekdays.append(datetime.strptime(newdate, '%Y-%m-%d'))
                print(lastweekdays)
                totalActorSignups = actortable.aggregate([
                    {
                        "$match": {
                            "timeStamp": {"$gte": lastweekdays[0]}
                        }
                    },
                    {
                        "$project": {"_id": "$_id",
                                     "timeStamp": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timeStamp",
                                                                     "timezone": "Asia/Karachi"}},
                                     }

                    },
                    {
                        "$group": {

                            "_id": "$timeStamp",
                            "count": {"$sum": 1}
                        }
                    },
                    {
                        "$sort": {"_id": 1}
                    }
                ])
                totalActorSignupsnew = []
                for data in totalActorSignups:
                    totalActorSignupsnew.append(data)

                totalBuyerSignups = table.aggregate([
                    {
                        "$match": {
                            "timeStamp": {"$gte": lastweekdays[0]}
                        }
                    },
                    {
                        "$project": {"_id": "$_id",
                                     "timeStamp": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timeStamp",
                                                                     "timezone": "Asia/Karachi"}},
                                     }

                    },
                    {
                        "$group": {

                            "_id": "$timeStamp",
                            "count": {"$sum": 1}
                        }
                    },
                    {
                        "$sort": {"_id": 1}
                    }
                ])
                totalbuyerSignupsnew = []
                for data in totalBuyerSignups:
                    totalbuyerSignupsnew.append(data)
                return render_template("admin_home.html", total_buyer=total_buyer, total_actor=total_actor,
                                       total_projects=total_projects, totalPremiumActors=totalPremiumActors,
                                       totalBronzeActors=totalBronzeActors, totalActorSignups=totalActorSignupsnew,
                                       lastweekdays=lastweekdaysStr, totalBuyerSignups=totalbuyerSignupsnew)
        else:
            return redirect("/admin/login")
    except Exception as e:
        return str(e)


@app.route("/admin/category-price", methods=["GET", "POST"])
def admincategory():
    try:
        if session.get("admintype") == "admin" and session.get("adminemail") and session.get("adminusername"):
            if request.method == "POST":
                categorytable = mydb["category"]
                catname = request.form["catname"]
                stprice = request.form["stprice"]
                wprice = request.form["wprice"]
                catname = str(catname).lower()
                catType = request.form["catType"]

                olddata = categorytable.find_one({"Category Name": catname})
                if olddata == None:
                    data = {"Category Name": catname, "Standard Price": float(stprice), "Price per Word": float(wprice),
                            "timeStamp": datetime.now(), "Type": catType}
                    categorytable.insert_one(data)
                    session["catupdate"] = "New " + catType + " successfully added."
                    return redirect("/admin/category-price")
                else:
                    if olddata["Type"] != catType:
                        data = {"Category Name": catname, "Standard Price": float(stprice),
                                "Price per Word": float(wprice),
                                "timeStamp": datetime.now(), "Type": catType}
                        categorytable.insert_one(data)
                        session["catupdate"] = "New " + catType + " successfully added."
                        return redirect("/admin/category-price")
                    else:
                        session["error"] = str(catType).lower() + " with this " + catname + " name is already exists."
                        return redirect("/admin/category-price")
            else:
                categorytable = mydb["category"]
                catupdate = "NULL"
                if session.get("catupdate"):
                    catupdate = session.get("catupdate")
                    session.pop("catupdate", None)
                error = ""
                if session.get("error"):
                    error = session.get("error")
                    session.pop("error", None)
                catdata = categorytable.find({})
                catdata2 = []
                for data in catdata:
                    catdata2.append(data)
                titles = ["Category Name", "Type", "Standard Price", "Price per Word"]
                return render_template("admincategory.html", catdata=catdata2, title="category-price",
                                       catupdate=catupdate, titles=titles, error=error)
        else:
            return redirect("/admin/login")
    except Exception as e:
        session["error"] = "Some thing went worng please try later. " + str(e)
        return redirect("/admin/category-price")

@app.route("/editcat")
def catdata():
    catid = request.args.get("id")
    cattable = mydb["category"]
    catdata = cattable.find_one({"_id": ObjectId(catid)})
    if "Type" in catdata:
        Type = catdata["Type"]
    else:
        Type = ""
    if catdata != None:
        return jsonify({"id": catid, "Category Name": catdata["Category Name"],
                        "Type": Type, "Standard Price": catdata["Standard Price"],
                        "Price per Word": catdata["Price per Word"]})
    else:
        return "None"


@app.route("/updatecategory", methods=["POST"])
def updatecategory():
    try:
        if session.get("admintype") == "admin" and session.get("adminemail") and session.get("adminusername"):
            if request.method == "POST":
                categorytable = mydb["category"]
                catname = request.form["catnames"]
                stprice = request.form["stprices"]
                wprice = request.form["wprices"]
                catid = request.form["catidEdit"]
                cattype = request.form["catTypes"]
                catname = str(catname).lower()
                print(cattype)
                olddata = categorytable.find_one({"Category Name": catname, "Type": str(cattype).lower()})
                if olddata is None:
                    categorytable.update_one({"_id": ObjectId(catid)}, {"$set": {
                        "Category Name": catname, "Standard Price": float(stprice), "Price per Word": float(wprice),
                        "timeStamp": datetime.now(), "Type": cattype
                    }})
                    session["catupdate"] = "Category successfully updated."
                    return redirect("/admin/category-price")
                elif str(olddata["_id"]) == catid:
                    categorytable.update_one({"_id": ObjectId(catid)}, {"$set": {
                        "Category Name": catname, "Standard Price": float(stprice), "Price per Word": float(wprice),
                        "timeStamp": datetime.now(), "Type": cattype
                    }})
                    session["catupdate"] = "Category successfully updated."
                    return redirect("/admin/category-price")
                else:
                    session["catupdate"] = cattype + " with this " + catname + " is already exists."
                    return redirect("/admin/category-price")

            else:
                return redirect("/admin/category-price")
        else:
            return redirect("/admin/login")
    except Exception as e:
        session["catupdate"] = "Some thing went worng please try later. " + str(e)
        return redirect("/admin/category-price")


@app.route("/deletecategory", methods=["POST"])
def deletecategory():
    try:
        if session.get("admintype") == "admin" and session.get("adminemail") and session.get("adminusername"):
            if request.method == "POST":
                categorytable = mydb["category"]
                catid = request.form["catiddel"]
                categorytable.remove({"_id": ObjectId(catid)})
                session["catupdate"] = "Category deleted successfully."
                return redirect("/admin/category-price")
            else:
                return redirect("/admin/category-price")
        else:
            return redirect("/admin/login")
    except Exception as e:
        session["catupdate"] = "Some thing went worng please try later. " + str(e)
        return redirect("/admin/category-price")


@app.route("/admin/actors", methods=["POST", "GET"])
def admin_actors():
    try:
        if session.get("admintype") == "admin" and session.get("adminemail") and session.get("adminusername"):
            if request.method == "POST":
                return redirect("/admin/actors")
            else:
                table = mydb["actor"]
                # actor_data = table.find({"active": 1})
                actorType = "NULL"
                if request.args.get("type"):
                    actorType = request.args.get("type")
                if actorType != "NULL":
                    actor_data = table.find({"active": 1, "planType": actorType})
                else:
                    actor_data = table.find({"active": 1})
                error = ""
                if session.get("error"):
                    error = session.get("error")
                    session.pop("error", None)
                message = ""
                if session.get("message"):
                    message = session.get("message")
                    session.pop("message", None)
                titles1 = ["userName", "email", "phoneNo", "timeStamp"]
                titles = ["Name", "Email", "Contact", "Joined"]
                return render_template("admin_actors.html", actor_data=actor_data, titles=titles,
                                       error=error, titles1=titles1, message=message)
        else:
            return redirect("/admin/login")
    except Exception as e:
        return e


@app.route("/admin/actor-detail", methods=["POST", "GET"])
def admin_actors_detail():
    try:
        if session.get("admintype") == "admin" and session.get("adminemail") and session.get("adminusername"):
            if request.method == "POST":
                data = request.form
                actor_ids = data["actorids"]
                actor_statuss = data["actorstatuss"]
                table = mydb["actor"]
                table.update_one({"_id": ObjectId(actor_ids)}, {"$set": {"actorstatus": actor_statuss}})
                session["message"] = "Status Updated successfully for the actor."
                return redirect("/admin/actors")
            else:
                actor_id = request.cookies.get("idActor")
                if actor_id is None:
                    actor_id = request.args.get("idd")
                elif actor_id is not None and request.args.get("idd") is None:
                    actor_id = request.cookies.get("idActor")
                else:
                    actor_id = request.args.get("idd")

                table = mydb["actor"]
                actor_data = table.find_one({"_id": ObjectId(actor_id), "active": 1})
                total_projects = table.aggregate([
                    {"$match": {"_id": ObjectId(actor_id)}},
                    {"$unwind": "$projects_progress"},
                    {
                        "$project": {
                            "projects_progress.status": 1,
                            "projects_progress.project_cost": 1
                        }
                    },
                    {
                        "$group": {
                            "_id": "status",
                            "count": {"$sum": 1},
                            "sum": {"$sum": "$project_cost"}
                        }
                    }
                ])

                table = mydb["category"]
                cat_data = table.find({})

                table = mydb["transactions"]
                transactions1 = table.find({"actor_id": ObjectId(actor_id)})
                transactions = []
                for i in transactions1:
                    transactions.append(i)
                error = ""
                if session.get("error"):
                    error = session.get("error")
                    session.pop("error", None)
                message = ""
                if session.get("message"):
                    message = session.get("message")
                    session.pop("message", None)
                titles1 = ["firstName", "lastName", "email", "phoneNo", "Location", "Country", "proHeadlines",
                           "languages", "catdata", "addVocalAbilities", "expTrainEquip", "timeStamp", "accents",
                           "catdata", "catdata"]
                titles = ["Name", "Name", "Email", "Contact", "City", "Country", "Title",
                          "Languages", "Ages", "Vocal Abilities", "Experiance", "Joined", "Accents",
                          "Gender", "Category"]
                languages, countries, dead_line, categories, delivery_options, proposals, accents = fetch_record()
                return render_template("admin_actor_detail.html", actor_data=actor_data, titles=titles,
                                       error=error, titles1=titles1, message=message, cat_data=cat_data,
                                       title="admin/actors", total_projects=total_projects,
                                       transactions=transactions, categories=categories)
        else:
            return redirect("/admin/login")
    except Exception as e:
        return str(e)


@app.route("/admin/buyers", methods=["POST", "GET"])
def admin_buyers():
    try:
        if session.get("admintype") == "admin" and session.get("adminemail") and session.get("adminusername"):
            if request.method == "POST":
                return redirect("/admin/buyers")
            else:
                table = mydb["buyer"]
                actor_data = table.find({"active": 1})
                error = ""
                if session.get("error"):
                    error = session.get("error")
                    session.pop("error", None)
                message = ""
                if session.get("message"):
                    message = session.get("message")
                    session.pop("message", None)
                titles1 = ["userName", "email", "user_contact", "timeStamp"]
                titles = ["Name", "Email", "Contact", "Joined"]
                return render_template("admin_buyers.html", actor_data=actor_data, titles=titles,
                                       error=error, titles1=titles1, message=message)
        else:
            return redirect("/admin/login")
    except Exception as e:
        return str(e)


@app.route("/admin/buyer-detail", methods=["POST", "GET"])
def admin_buyers_detail():
    try:
        if session.get("admintype") == "admin" and session.get("adminemail") and session.get("adminusername"):
            if request.method == "POST":
                return redirect("/admin/actors")
            else:
                buyer_id = request.cookies.get("idActor")
                table = mydb["buyer"]
                buyer_data = table.find_one({"_id": ObjectId(buyer_id)})
                table = mydb["category"]
                cat_data = table.find({})
                error = ""
                if session.get("error"):
                    error = session.get("error")
                    session.pop("error", None)
                message = ""
                if session.get("message"):
                    message = session.get("message")
                    session.pop("message", None)
                titles1 = ["userName", "userName", "email", "user_contact", "user_city", "user_country", "companyName",
                           "languages", "catdata", "addVocalAbilities", "expTrainEquip", "userImage", "timeStamp"]
                titles = ["Name", "Name", "Email", "Contact", "City", "Country", "Company Name",
                          "Languages", "Category", "Vocal Abilities", "Experiance", "Image", "Member"]
                return render_template("admin_buyer_detail.html", buyer_data=buyer_data, titles=titles,
                                       error=error, titles1=titles1, message=message, cat_data=cat_data)
        else:
            return redirect("/admin/login")
    except Exception as e:
        return str(e)


@app.route("/admin/buyers-projets", methods=["POST", "GET"])
def admin_buyer_projects():
    try:
        if session.get("admintype") == "admin" and session.get("adminemail") and session.get("adminusername"):
            if request.method == "POST":
                return redirect("/admin/actors")
            else:
                table = mydb["buyer"]
                actor_data1 = table.find({}, {"projects": 1})
                actor_data = []
                for i in actor_data1:
                    actor_data.append(i)
                table = mydb["category"]
                cat_data = table.find({})
                error = ""
                if session.get("error"):
                    error = session.get("error")
                    session.pop("error", None)
                message = ""
                if session.get("message"):
                    message = session.get("message")
                    session.pop("message", None)
                titles1 = ["project_name", "project_description", "project_usage", "project_language",
                           "project_gender_age", "project_length", "project_length_type", "project_deadline",
                           "project_proposal", "project_budget", "project_cost", "timestamp",
                           "status", "project_id"]
                titles = ["Name", "Description", "Usage", "Language", "Category", "Script Length", "Script Type",
                          "Proposals", "Budget Type", "Budget", "Experiance", "Posted Time", "Status", "project_id"]

                titles1 = ["project_name", "project_description", "project_deadline", "project_cost",
                           "status", "project_id"]
                titles = ["Name", "Description", "Deadline", "Budget", "Status", "project_id"]
                return render_template("admin_buyer_projects.html", actor_data=actor_data, titles=titles,
                                       error=error, titles1=titles1, message=message, cat_data=cat_data)
        else:
            return redirect("/admin/login")
    except Exception as e:
        return str(e)


@app.route("/admin/project-detail", methods=["POST", "GET"])
def admin_buyer_projects_details():
    try:
        if session.get("admintype") == "admin" and session.get("adminemail") and session.get("adminusername"):
            if request.method == "POST":
                idBuyer = None
                return redirect("/admin/actors")
            else:
                idproject = request.cookies.get("idproject")
                idBuyer = request.cookies.get("idBuyer")
                table = mydb["buyer"]
                project_details = table.find_one(
                    {"_id": ObjectId(idBuyer), "projects.project_id": ObjectId(idproject)},
                    {"projects": {"$elemMatch": {"project_id": ObjectId(idproject)}}}
                )
                table = mydb["category"]
                cat_data = table.find({})

                table = mydb["bidding"]
                bid_data1 = table.find({})
                bid_data = []
                for i in bid_data1:
                    bid_data.append(i)
                error = ""
                if session.get("error"):
                    error = session.get("error")
                    session.pop("error", None)
                message = ""
                if session.get("message"):
                    message = session.get("message")
                    session.pop("message", None)
                return render_template("admin_prjct_rspns.html", project_details=project_details,
                                       message=message, cat_data=cat_data, error=error, bid_data=bid_data, idBuyer=idBuyer)
        else:
            return redirect("/admin/login")
    except Exception as e:
        return str(e)


@app.route("/admin/payments", methods=["POST", "GET"])
def admin_payments():
    try:
        titles = []
        if session.get("admintype") == "admin" and session.get("adminemail") and session.get("adminusername"):
            if request.method == "POST":
                return redirect(url_for("admin_payments"))
            else:

                table = mydb['transactions']
                actor_data = table.aggregate([
                    {
                        "$lookup":
                            {
                                "from": "actor",
                                "localField": "actor_id",
                                "foreignField": "_id",
                                "as": "actordetails"
                            }
                    },
                    {
                        "$group":
                            {
                                "_id": {
                                    "actor_id": "$actor_id",
                                    "message": "$message",
                                    "status": "$amountstatus"
                                },
                                "totalSaleAmount": {"$sum": "$amount"}
                            }
                    }
                ])

                buyer_table = mydb["buyer"]
                projcts = buyer_table.aggregate([
                    {
                        "$project": {"projects": 1}
                    },
                    {
                        "$unwind": "$projects"
                    },
                    {
                        "$match": {"projects.status": {"$in": ["posted", "completed", "cancelled"]}}
                    }
                ])
                prjcts = []
                for i in projcts:
                    i['_id'] = str(i['_id'])
                    i['projects']['project_id'] = str(i['projects']['project_id'])
                    if "responses" in i['projects']:
                        i['projects'].pop('responses', None)
                        i['projects'].pop('acceptOffers', None)
                    prjcts.append(i)
                buyer_data = prjcts
                table = mydb["bidding"]
                bidding_data = table.find({})

                # table = mydb["actor"]
                # actor_data = table.find({})

                arg_type = None
                if request.args.get('type') is not None:
                    arg_type = request.args.get('type')
                arg_type = "buyers"
                # Actors
                if arg_type == "actors":
                    titles = ["SNo.", "Actor ID", "Message", "Amount", "Status"]
                elif arg_type == "buyers":
                    titles = ["SNo.", "Name", "Description", "Date", "Budget", "Status"]
                elif arg_type == "projects":
                    titles = ["SNo.", "Name", "Description", "Budget", "Date", "Status"]

                # Projects
                error = ""
                if session.get("error"):
                    error = session.get("error")
                    session.pop("error", None)
                message = ""
                if session.get("message"):
                    message = session.get("message")
                    session.pop("message", None)
                return render_template("admin_payment.html", buyer_data=buyer_data, bidding_data=bidding_data,
                                       titles=titles, error=error, message=message, actor_data=actor_data,
                                       arg_type=arg_type)
        else:
            return redirect(url_for("login"))
    except Exception as e:
        return str(e)

@app.route("/chat", methods=["GET", "POST"])
def userchat():

    if session.get("userid") and session.get("username") and session.get("email") and session.get("type"):
        if request.method == "PSOT":
            return redirect("/chat")
        else:
            print("the get req")
            username = session.get("username")
            email = session.get("email")
            status = session.get("type")
            userid = session.get("userid")
            chatTable = mydb["chat"]
            buyerTable = mydb["buyer"]
            actorTable = mydb["actor"]
            print(email,status,userid,username)
            if status == "actor":
                buyerid = "None"
                if request.args.get("buyerid"):
                    buyerid = request.args.get("buyerid")
                    buyerdata = buyerTable.find_one({"_id":ObjectId(buyerid)})
                    findactorchat = chatTable.find_one({
                        "actorid":ObjectId(userid), "buyerid":ObjectId(buyerid)
                    })
                    if findactorchat == None:
                        roomname = id_generator()
                        chatTable.insert_one({"actorid": ObjectId(userid), "actorName": username, "buyerid":
                            ObjectId(buyerid), "buyerName": buyerdata["userName"], "lastmessagecount": 0, "roomname": roomname,
                                              "lastmessagetime": datetime.now(), "messages": []})

                data = chatTable.aggregate([
                    {"$match": {"actorid": ObjectId(userid)}},
                    {"$sort": {"lastmessagetime": -1}}
                ])
                return render_template("chat.html", data=data, username=username, userid=userid,
                                       status=status, type=status, buyerid=buyerid, email=email)
            elif status == "buyer":
                actorid = "None"
                if request.args.get("actorid"):
                    actorid = request.args.get("actorid")
                    actordata = actorTable.find_one({"_id": ObjectId(actorid)})
                    findbuyerchat = chatTable.find_one({
                        "actorid": ObjectId(actorid), "buyerid": ObjectId(userid)
                    })
                    if findbuyerchat == None:
                        roomname = id_generator()
                        chatTable.insert_one({"actorid": ObjectId(actorid), "actorName": actordata["userName"], "buyerid":
                            ObjectId(userid), "buyerName": username, "lastmessagecount": 0,
                                              "roomname": roomname,
                                              "lastmessagetime": datetime.now(), "messages": []})

                data = chatTable.aggregate([
                    {"$match": {"buyerid": ObjectId(userid)}},
                    {"$sort": {"lastmessagetime": -1}}
                ])
                print(userid)
                return render_template("buyerchat.html", data=data,username=username,userid=userid,
                                   status=status, type=status, actorid=actorid, email=email)
    else:
        return redirect("/login")


@app.route("/getmessages", methods=["GET"])
def getmessages():
    actorid = request.args.get("actorid")
    buyerid = request.args.get("buyerid")
    print(actorid, buyerid)
    chatTable = mydb["chat"]
    status = session.get("type")

    print(status)
    messages = ""
    if status == "buyer":
        messages = chatTable.find_one({"actorid": ObjectId(actorid), "buyerid": ObjectId(buyerid)})
    elif status == "actor":
        messages = chatTable.find_one({"actorid": ObjectId(actorid), "buyerid": ObjectId(buyerid)})

    print(messages)
    if messages is not None:
        messages = messages["messages"]
    elif messages is None:
        messages = []
    print(messages)

    # if messages != None:
    #     messages = str(messages[0]).replace("[","")
    #     messages = messages.replace("]","")
    #
    #     print(messages)
    # messages = """{"status": "doctor", "message": "hello", "type": "text", "time": "17:10"}&&
    #             {"status": "doctor", "message": "hello", "type": "text", "time": "17:11"}&&
    #             {"status": "patient", "message": "hello", "type": "text", "time": "17:14"}&&
    #             {"status": "patient", "message": "app.txt", "type": "file", "time": "17:17"}&&
    #             {"status": "patient", "message": "a71.jpg", "type": "image", "time": "17:19"}&&
    #             {"status": "doctor", "message": "app.txt", "type": "file", "time": "17:17"}&&
    #             {"status": "doctor", "message": "a71.jpg", "type": "image", "time": "17:19"}"""

    return jsonify({"messages": messages})


def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')


@app.route("/uploadimage", methods=["POST"])
def uploadimages():
    print(request.files)

    if "file" in request.files:
        image = request.files["file"]
        file = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER1'], file))
        newimage = Image.open(os.path.join(app.config['UPLOAD_FOLDER1'], str(file)))
        newimage.thumbnail((1920, 720))
        newimage.save(os.path.join(UPLOAD_FOLDER1, str(file)), quality=95)

        filename = file

    else:
        filename = ""
        print("0")
    return jsonify({"filename": filename})


@app.route("/uploadfiles", methods=["POST"])
def uploadfiles():
    print(request.files)

    if "file" in request.files:
        image = request.files["file"]
        file = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER1'], file))


        filename = file

    else:
        filename = ""
        print("0")
    return jsonify({"filename": filename})


@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    username = ""
    if "user_name" in json:
        username = json["user_name"]
    curuser = ""
    if session.get("username"):
        curuser = session.get("username")
    print(curuser)
    roomname = ""
    if "roomname" in json:
        roomname = json["roomname"]
        join_room(roomname)
    status = session.get("type")
    chatTable = mydb["chat"]
    print(json["message"])
    if json["message"] != "connected":
        chatTable.update(
            {"roomname": roomname},
            {"$set": {"lastmessagetime": datetime.now().time().strftime("%H:%M:%S:%f")}}
        )
        chatTable.update({"roomname": roomname},
                         {"$addToSet": {"messages": {"status": status, "message": json["message"], "type": "text",
                                                     "timeStamp": datetime.now().time().strftime("%H:%M:%S:%f"),
                                                     "time": datetime.now().time().strftime("%H:%M")}}})

    if status == "actor":
        socketio.emit('my response', json, room=roomname, callback=json, usernamess=str(username),
                      username22=str(curuser))
    else:
        socketio.emit('doctor response', json, room=roomname, callback=json, usernamess=str(username),
                      username22=str(curuser))


@socketio.on('disconnect event')
def handle_my_disconnect_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    disconnect()
    print(json["roomname"])
    leave_room(json["roomname"])
    return "True"


@socketio.on('my fileevent')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    if session.get("type") and session.get("userid") and session.get("email"):
        print('received my event: '+ str(json))
        if "user_name" in json:
            username = json["user_name"]
        curuser = ""
        if session.get("username"):
            curuser = session.get("username")
        roomname = ""
        if "roomname" in json:
            roomname = json["roomname"]
            join_room(roomname)
        status = session.get("type")
        chatTable = mydb["chat"]
        if json["message"] != "connected":
            chatTable.update(
                {"roomname": roomname},
                {"$set": {"lastmessagetime": datetime.now().time().strftime("%H:%M:%S:%f")}}
            )
            chatTable.update({"roomname": roomname},
                             {"$addToSet": {"messages": {"status": status, "message": json["message"], "type": "file",
                                                         "timeStamp": datetime.now().time().strftime("%H:%M:%S:%f"),
                                                         "time": datetime.now().time().strftime("%H:%M")}}})

        print("file event")
        if status == "actor":
            socketio.emit('my file', json,room=roomname, callback=messageReceived, usernamess = str(username), username22 = str(curuser))
        else:
            socketio.emit('doctor file', json,room=roomname, callback=messageReceived, usernamess = str(username), username22 = str(curuser))
    else:
        return redirect(url_for("home"))

@app.route("/downloadfile/<filename>", methods=["GET"])
def downloadfile(filename):


    return send_file(os.path.join(app.config['UPLOAD_FOLDER1'], filename))

@socketio.on('my imageevent')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    if "user_name" in json:
        username = json["user_name"]
    curuser = ""
    if session.get("username"):
        curuser = session.get("username")
    roomname = ""
    if "roomname" in json:
        roomname = json["roomname"]
        join_room(roomname)
    status = session.get("type")
    print(status)
    chatTable = mydb["chat"]
    if json["message"] != "connected":
        chatTable.update(
            {"roomname": roomname},
            {"$set": {"lastmessagetime": datetime.now().time().strftime("%H:%M:%S:%f")}}
        )
        chatTable.update({"roomname": roomname},
                         {"$addToSet": {"messages": {"status": status, "message": json["message"], "type": "image",
                                                     "timeStamp": datetime.now().time().strftime("%H:%M:%S:%f"),
                                                     "time": datetime.now().time().strftime("%H:%M")}}})

    if status == "actor":
        socketio.emit('my picture', json, room=roomname, usernamess=str(username), username22=str(curuser))
    else:
        socketio.emit('doctor picture', json, room=roomname, usernamess=str(username), username22=str(curuser))



# Mobile API's

@app.route('/languages-api', methods=["GET", "POST"])
def languages_api():
    languages, countries, dead_line, categories, delivery_options, proposals, accents = fetch_record()
    print(languages)
    return jsonify({"success": True, "languages": languages})


@app.route('/countries-api', methods=["GET", "POST"])
def countries_api():
    languages, countries, dead_line, categories, delivery_options, proposals, accents = fetch_record()
    return jsonify({"success": True, "countries": countries})


@app.route('/deadline-api', methods=["GET", "POST"])
def dead_line_api():
    languages, countries, dead_line, categories, delivery_options, proposals, accents = fetch_record()
    return jsonify({"success": True, "dead_line": dead_line})


@app.route('/delivery-options-api', methods=["GET", "POST"])
def delivery_options_api():
    languages, countries, dead_line, categories, delivery_options, proposals, accents = fetch_record()
    return jsonify({"success": True, "delivery_options": delivery_options})


@app.route('/proposals-api', methods=["GET", "POST"])
def proposals_api():
    languages, countries, dead_line, categories, delivery_options, proposals, accents = fetch_record()
    return jsonify({"success": True, "proposals": proposals})


@app.route('/categories-api', methods=["GET", "POST"])
def categories_api():
    table = mydb['category']
    category_data = table.find({})
    gender = [{"Category Name": "Select Gender",
               "Price per Word": 0.0,
               "Standard Price": 0.0,
               "Type": "gender",
               "_id": "0",
               "timeStamp": "Sun, 24 Jan 2021 23:44:14 GMT"}]
    category = [{"Category Name": "Select Category(s)",
                 "Price per Word": 0.0,
                 "Standard Price": 0.0,
                 "Type": "gender",
                 "_id": "0",
                 "timeStamp": "Sun, 24 Jan 2021 23:44:14 GMT"}]
    age = [{"Category Name": "Select age(s)",
            "Price per Word": 0.0,
            "Standard Price": 0.0,
            "Type": "gender",
            "_id": "0",
            "timeStamp": "Sun, 24 Jan 2021 23:44:14 GMT"}]

    for each_category in category_data:
        if each_category['Type'] == 'age':
            each_category['_id'] = str(each_category['_id'])
            age.append(each_category)
        elif each_category['Type'] == 'gender':
            each_category['_id'] = str(each_category['_id'])
            gender.append(each_category)
        elif each_category['Type'] == 'category':
            each_category['_id'] = str(each_category['_id'])
            category.append(each_category)
    return jsonify({"success": True, "categories": category, "ages": age, "gender": gender})


@app.route('/accents-api', methods=["GET", "POST"])
def accents_api():
    languages, countries, dead_line, categories, delivery_options, proposals, accents = fetch_record()
    return jsonify({"success": True, "accents": accents})


def fetch_category():
    table = mydb['category']
    category_data = table.find({})
    gender = [{ "Category Name": "Select Gender",
                "Price per Word": 0.0,
                "Standard Price": 0.0,
                "Type": "gender",
                "_id": "0",
                "timeStamp": "Sun, 24 Jan 2021 23:44:14 GMT"}]
    category = [{ "Category Name": "Select Category(s)",
                "Price per Word": 0.0,
                "Standard Price": 0.0,
                "Type": "gender",
                "_id": "0",
                "timeStamp": "Sun, 24 Jan 2021 23:44:14 GMT"}]
    age = [{ "Category Name": "Select age(s)",
                "Price per Word": 0.0,
                "Standard Price": 0.0,
                "Type": "gender",
                "_id": "0",
                "timeStamp": "Sun, 24 Jan 2021 23:44:14 GMT"}]

    for each_category in category_data:
        if each_category['Type'] == 'age':
            each_category['_id'] = str(each_category['_id'])
            age.append(each_category)
        elif each_category['Type'] == 'gender':
            each_category['_id'] = str(each_category['_id'])
            gender.append(each_category)
        elif each_category['Type'] == 'category':
            each_category['_id'] = str(each_category['_id'])
            category.append(each_category)
    return age, gender, category



# Job seeker
@app.route("/worksignup-api", methods=["GET", "POST"])
def worksignup_api():
    try:
        print(request.data)
        print(request.get_json())
        print(type(request.get_json()))
        if request.is_json:
            if request.method == "POST":
                data = request.get_json()
                print(data)
                email = data["email"]
                username = data["username"]
                password = data["password"]
                phoneno = data["phone"]
                planType = data["plantype"]
                amount = 100
                planPayment = "None"
                if planType.lower == "silver":
                    planPayment = data["planPayment"]
                password_hash = generate_password_hash(password)
                linkhash = generate_password_hash(password + email)
                buyertable = mydb["buyer"]
                actorTable = mydb["actor"]
                oldrecordbuyer = buyertable.find_one({"emai": email})
                oldrecordactor = actorTable.find_one({"email": email})
                if oldrecordbuyer == None and oldrecordactor == None:
                    actorid = actorTable.insert_one({"email": email, "userName": username, "phoneNo": phoneno,
                                                     "password": password, "passwordHash": password_hash,
                                                     "type": "actor",
                                                     "timeStamp": datetime.now(), "active": 0, "activateLink": linkhash,
                                                     "planPayment": planPayment, "planType": planType,
                                                     "planDate": datetime.now()})
                    print(actorid.inserted_id)

                    msg = Message("Signup Voices City", recipients=[email])
                    msg.html = """Dear """ + username + """, <br> 
                     Thank you for signup with Voices City. Please click below link to activate your account.<br>
                     <a href='https://voiceover.web-designpakistan.com/activate?code=""" + email + """&hashkey=""" + linkhash + """'>link</a>
                     <br><br> Regards, <br>Voices City"""
                    mail.send(msg)
                    table = mydb["transactions"]
                    table.insert_one({"actor_id": ObjectId(actorid.inserted_id),
                                      "plantype": planType, "planpayment": planPayment,
                                      "amount": amount, "timestamp": datetime.now(),
                                      "message": "newplan", "amountstatus": "deposit"})
                    return jsonify({"success": True, "message": "Please check your email to activate your account."})
                else:
                    if oldrecordactor['active'] == 0:
                        msg = Message("Signup Voices City", recipients=[email])
                        msg.html = """Dear """ + username + """, <br> 
                                             Thank you for signup with Voices City. Please click below link to activate your account.<br>
                                             <a href='https://voiceover.web-designpakistan.com/activate?code=""" + email + """&hashkey=""" + linkhash + """'>link</a>
                                             <br><br> Regards, <br>Voices City"""
                        mail.send(msg)
                        return jsonify(
                            {"success": True, "message": "Please check your email to activate your account."})
                    else:
                        return jsonify({"success": False, "message": "Account with this email address already exists."})
            else:
                return jsonify({"success": False, "message": "Invalid Post Request"})
        else:
            return jsonify({"success": False, "message": "Invalid Json Request"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


# Recruiter
# As an company or person to hire and post job. (buyer).
@app.route("/hiresignup-api", methods=["GET", "POST"])
def hiresignup_api():
    try:
        if request.is_json:
            if request.method == "POST":
                data = request.get_json()
                print(data)
                email = data["email"]
                username = data["username"]
                companyname = data["companyname"]
                password = data["password"]
                password_hash = generate_password_hash(password)
                linkhash = generate_password_hash(password + email)
                buyertable = mydb["buyer"]
                actorTable = mydb["actor"]
                oldrecordbuyer = buyertable.find_one({"email": email})
                oldrecordactor = actorTable.find_one({"email": email})
                if oldrecordbuyer == None and oldrecordactor == None:
                    buyertable.insert_one({"email": email, "userName": username, "companyName": companyname,
                                           "password": password, "passwordHash": password_hash, "type": "buyer",
                                           "timeStamp": datetime.now(), "active": 0, "activateLink": linkhash})

                    msg = Message("Signup Voices City", recipients=[email])
                    msg.html = """Dear """ + username + """, <br> 
                                         Thank you for signup with Voices City. Please click below link to activate your account.<br>
                                         <a href='https://voiceover.web-designpakistan.com/activate?code=""" + email + """&hashkey=""" + linkhash + """'>link</a>
                                         <br><br> Regards, <br>Voices City"""
                    mail.send(msg)
                    return jsonify({"success": True, "message": "Please check your email to activate your account."})
                else:
                    return jsonify({"success": False, "message": "Account with this email address already exists."})
            else:
                return jsonify({"success": False, "message": "Invalid Post Request"})
        else:
            return jsonify({"success": False, "message": "Invalid Json Request"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


# Normal login
@app.route("/login-api", methods=["GET", "POST"])
def login_api():
    try:
        print(request.get_json())
        if request.is_json:
            if request.method == "POST":
                data = request.get_json()
                print(data)
                email = data["email"]
                password = data["password"]
                buyerTable = mydb["buyer"]
                actorTable = mydb["actor"]
                buyerdata = buyerTable.find_one({"email": email})
                actordata = actorTable.find_one({"email": email})
                print(buyerdata)
                print(actordata)
                if buyerdata != None and actordata == None:
                    if int(buyerdata["active"]) == 1:
                        if "user_city" in buyerdata:
                            if buyerdata["user_city"] != "":
                                profile_status = True
                            else:
                                profile_status = False
                        else:
                            profile_status = False
                        if check_password_hash(buyerdata["passwordHash"], password):
                            print(buyerdata)
                            return jsonify({"success": True, "data":
                                {"email": email, "username": buyerdata["userName"], "type": "buyer",
                                 "userid": str(buyerdata["_id"]), "profile_status": profile_status}})
                        else:
                            return jsonify({"success": False, "message": "Password is incorrect."})
                    else:
                        return jsonify({"success": False, "message": "Your account is not active."})
                elif actordata != None and buyerdata == None:
                    if int(actordata["active"]) == 1:
                        if "profileStatus" in actordata:
                            if actordata["profileStatus"] == "completed":
                                profile_status = True
                            else:
                                profile_status = False
                        else:
                            profile_status = False

                        if "skillStatus" in actordata:
                            if actordata["skillStatus"] == "completed":
                                skill_status = True
                            else:
                                skill_status = False
                        else:
                            skill_status = False
                        if "studioStatus" in actordata:
                            if actordata["studioStatus"] == "completed":
                                studio_status = True
                            else:
                                studio_status = False
                        else:
                            studio_status = False

                        if "playlistStatus" in actordata:
                            if actordata["playlistStatus"] == "completed":
                                playlist_status = True
                            else:
                                playlist_status = False
                        else:
                            playlist_status = False
                        if check_password_hash(actordata["passwordHash"], password):
                            return jsonify({"success": True, "data":
                                {"email": email, "username": actordata["userName"], "type": "actor",
                                 "userid": str(actordata["_id"]), "profile_status": profile_status,
                                 "skill_status": skill_status, "studio_status": studio_status,
                                 "playlist_status": playlist_status}})
                        else:
                            return jsonify({"success": False, "message": "Password is incorrect."})
                    else:
                        return jsonify({"success": False, "message": "Your account is not active."})
                else:
                    return jsonify({"success": False, "message": "Email or Password is incorrect."})
            else:
                return jsonify({"success": False, "message": "Invalid Post Request"})
        else:
            return jsonify({"success": False, "message": "Invalid Json Request"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


# Normal login
@app.route("/login-check-api", methods=["GET", "POST"])
def login_check_api():
    try:
        if request.is_json:
            if request.method == "POST":
                data = request.get_json()
                print(data)
                user_id = data["userid"]
                user_type = data["type"]
                buyerTable = mydb["buyer"]
                actorTable = mydb["actor"]
                buyerdata = buyerTable.find_one({"_id": ObjectId(user_id)})
                actordata = actorTable.find_one({"_id": ObjectId(user_id)})
                if buyerdata != None and actordata == None:
                    if user_type == buyerdata["type"]:
                        if "user_city" in buyerdata:
                            if buyerdata["user_city"] != "":
                                profile_status = True
                            else:
                                profile_status = False
                        else:
                            profile_status = False
                            return jsonify({"success": True, "data":
                                {"email": buyerdata["email"], "username": buyerdata["userName"], "type": "buyer",
                                 "userid": str(buyerdata["_id"]), "profile_status": profile_status}})
                    else:
                        return jsonify({"success": False, "message": "invalid user or id"})
                elif actordata != None and buyerdata == None:
                    if user_type == actordata["type"]:
                        if "profileStatus" in actordata:
                            if actordata["profileStatus"] == "completed":
                                profile_status = True
                            else:
                                profile_status = False
                        else:
                            profile_status = False
                        return jsonify({"success": True, "data":
                            {"email": actordata["email"], "username": actordata["userName"], "type": "actor",
                             "userid": str(actordata["_id"]), "profile_status": profile_status}})
                    else:
                        return jsonify({"success": False, "message": "invalid user or id"})
                else:
                    return jsonify({"success": False, "message": "Email or Password is incorrect."})
            else:
                return jsonify({"success": False, "message": "Invalid Get Request"})
        else:
            return jsonify({"success": False, "message": "Invalid Json Request"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route('/forget-password-api', methods=["GET", "POST"])
def forget_password_api():
    try:
        if request.is_json:
            if request.method == "POST":
                data = request.get_json()
                print(data)
                email = data["email"]
                user_type = data["type"]
                buyerTable = mydb["buyer"]
                actorTable = mydb["actor"]
                buyerdata = buyerTable.find_one({"email": email})
                actordata = actorTable.find_one({"email": email})
                if buyerdata != None and actordata == None:
                    code = id_generator()
                    msg = Message("Forgot Password", recipients=[email])
                    linkhash = generate_password_hash(code + email)
                    msg = Message("Forgot Password! Voices City", recipients=[email])
                    msg.html = """Dear """ + buyerdata['userName'] + """, <br> 
                            Use the following link to change password of your account.<br>
                            <a href='https://voiceover.web-designpakistan.com/changePassword?code=""" + buyerdata['_id'] + """&hashkey=""" + linkhash + """'>link</a>
                            <br><br> Regards, <br>Voices City"""
                    mail.send(msg)
                    profile_status = False
                    return jsonify({"success": True, "data":
                        {"email": buyerdata["email"], "username": buyerdata["userName"], "type": "buyer",
                         "userid": str(buyerdata["_id"]), "profile_status": profile_status}})

                elif actordata != None and buyerdata == None:
                    code = id_generator()
                    msg = Message("Forgot Password! Voices City", recipients=[email])
                    msg.html = """Dear """ + actordata['userName'] + """, <br> 
                                                Use the following code to change password of your account.The code is : """ + code + """<br>
                                                <br><br> Regards, <br>Voices City"""
                    mail.send(msg)
                    profile_status = False
                    return jsonify({"success": True, "data":
                        {"email": actordata["email"], "username": actordata["userName"], "type": "actor",
                         "userid": str(actordata["_id"]), "profile_status": profile_status}})
                else:
                    return jsonify({"success": False, "message": "No user with this email exist."})
            else:
                return jsonify({"success": False, "message": "Invalid Get Request"})
        else:
            return jsonify({"success": False, "message": "Invalid Json Request"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route('/change-password-api', methods=["GET", "POST"])
def change_password_api():
    try:
        if request.is_json:
            if request.method == "POST":
                data = request.get_json()
                print(data)
                userid = data["userid"]
                email = data["email"]
                password = data["password"]
                user_type = data["type"]
                buyerTable = mydb["buyer"]
                actorTable = mydb["actor"]
                buyerdata = buyerTable.find_one({"_id": ObjectId(userid)})
                actordata = actorTable.find_one({"_id": ObjectId(userid)})
                if buyerdata != None and actordata == None:
                    hash_password = generate_password_hash(password)
                    buyerTable.update_one({"_id": ObjectId(userid), "email": email},
                                          {"$set": {"password": password, "passwordHash": hash_password}})
                    profile_status = False
                    if "user_city" in buyerdata:
                        if buyerdata["user_city"] != "":
                            profile_status = True
                        return jsonify({"success": True, "data":
                            {"email": buyerdata["email"], "username": buyerdata["userName"], "type": "buyer",
                             "userid": str(buyerdata["_id"]), "profile_status": profile_status}})

                elif actordata != None and buyerdata == None:
                    code = id_generator()
                    msg = Message("Forgot Password! Voices City", recipients=[email])
                    msg.html = """Dear """ + actordata['userName'] + """, <br> 
                                                Use the following code to change password of your account.The code is : """ + code + """<br>
                                                <br><br> Regards, <br>Voices City"""
                    mail.send(msg)
                    profile_status = False
                    if "profileStatus" in actordata:
                        if actordata["profileStatus"] == "completed":
                            profile_status = True
                    return jsonify({"success": True, "data":
                        {"email": actordata["email"], "username": actordata["userName"], "type": "actor",
                         "userid": str(actordata["_id"]), "profile_status": profile_status}})
                else:
                    return jsonify({"success": False, "message": "No user with this email exist."})
            else:
                return jsonify({"success": False, "message": "Invalid Get Request"})
        else:
            return jsonify({"success": False, "message": "Invalid Json Request"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


# Buyer Profile API's
# Buyer Profile edit.
@app.route("/editprofile-api", methods=["GET", "POST"])
def editprofile_api():
    try:
        if request.is_json:
            if request.method == "POST":
                data = request.get_json()
                email = data["email"]
                type = data["type"]
                userid = data["userid"]
                if type == "buyer":
                    table = mydb["buyer"]
                else:
                    return jsonify({"success": False, "error": "Invalid user type"})
                user_name = data["userName"]
                user_email = data["userEmail"]
                user_contact = data["userContact"]
                user_password = data["userPassword"]
                user_company = data["userCompany"]
                user_city = data["userCity"]
                user_country = data["userCountry"]
                user_file = request.files["userImage"]
                print(request.files)
                if user_email == email:
                    hashpassword = generate_password_hash(user_password)
                    filename1 = ""
                    if user_file.filename != "":
                        filename1 = secure_filename(user_file.filename)
                        filename1 = str(datetime.now().strftime("%Y%m%d-%H%M")) + "_" + filename1
                        user_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
                    table.update_one({"email": email, "_id": ObjectId(userid)},
                                     {"$set":
                                          {"userName": user_name, "companyName": user_company,
                                           "password": user_password,
                                           "passwordHash": hashpassword, "user_city": user_city,
                                           "user_country": user_country, "user_contact": user_contact,
                                           "userImage": filename1}
                                      })
                    return jsonify({"success": True, "message": "Profile Updated successfully."})
                else:
                    session["error"] = "Email not matched."
                    return jsonify({"success": False, "message": "Email not matched."})
            # Get request
            else:
                data = request.get_json()
                email = data["email"]
                type = data["type"]
                userid = data["userid"]

                if type == "buyer":
                    buyerTable = mydb["buyer"]
                    buyer_data = buyerTable.find_one({"_id": ObjectId(userid), "email": email})
                    if buyer_data != None and buyer_data != ():
                        name_user = buyer_data["userName"]
                        email_user = buyer_data["email"]
                        password_user = buyer_data["password"]
                        company_user = buyer_data["companyName"]
                        if "user_contact" in buyer_data and "user_country" in buyer_data and \
                                "user_city" in buyer_data and "userImage" in buyer_data:
                            city_user = buyer_data["user_city"]
                            country_user = buyer_data["user_country"]
                            contact_user = buyer_data["user_contact"]
                            image_user = buyer_data["userImage"]
                        else:
                            city_user = ""
                            country_user = ""
                            contact_user = ""
                            image_user = ""
                        return jsonify({"succes": True, "userid": userid, "data":
                            {"name_user": name_user, "email_user": email_user, "password_user": password_user,
                             "company_user": company_user, "city_user": city_user,
                             "country_user": country_user, "contact_user": contact_user,
                             "image_user": image_user
                             }})
                    else:
                        return jsonify({"success": False, "message": "User with this record not found."})
                else:
                    return jsonify({"success": False, "message": "Invalid user type"})
                    # languages, countries, dead_line, categories, delivery_options, proposals, accents = fetch_record()
        else:
            return jsonify({"success": False, "message": "Invalid Json Request"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


# Post a new Job by the buyer. as a draft.
@app.route("/post-job-api", methods=["GET", "POST"])
def postjob_api():
    try:
        if session.get("email") and session.get("type") == "buyer" and session.get("username"):
            if request.method == "POST":
                print(request.form)
                files = request.files
                print(files)
                email = session.get("email")
                usertype = session.get("type")
                data = request.form
                project_name = data["projectName"]
                project_description = data["projectDescription"]
                project_usage = data["projectUsage"]
                project_language = data.getlist("projectLanguage")
                project_gender_age = data.getlist("projectGenderAge")
                project_length = data["projectLength"]
                project_length_type = data["projectLengthType"]
                project_delivery_option = data.getlist("projectDeliveryOption")
                project_script = data["inputscript"]
                project_script_file = files["scriptFile"]
                # project_custom_audition = data["projectCustomAudition"]
                project_deadline = data.getlist("projectDeadline")
                project_proposal = data.getlist("projectProposal")
                project_budget = data["projectBudget"]

                if project_budget == "variable":
                    project_cost = data["projectCost1"]
                elif project_budget == "fixed":
                    project_cost = data["projectCost"]
                if usertype == "buyer":
                    table = mydb["buyer"]
                else:
                    session["error"] = "Invalid user type error"
                    return redirect(url_for("postjob"))
                buyer_id = session.get("userid")
                scriptFile = ""
                if project_script_file.filename != "":
                    # scriptFile = project_script_file.filename
                    scriptFile = secure_filename(project_script_file.filename)
                    scriptFile = str(project_name) + " - " + str(scriptFile)
                    project_script_file.save(os.path.join(app.config['UPLOAD_FOLDER4'], str(scriptFile)))
                mydic1 = {"project_name": project_name, "project_description": project_description,
                          "project_usage": project_usage, "project_language": project_language,
                          "project_gender_age": project_gender_age, "project_length": project_length,
                          "project_length_type": project_length_type,
                          "project_delivery_option": project_delivery_option,
                          "project_deadline": project_deadline, "project_proposal": project_proposal,
                          "project_budget": project_budget, "project_cost": project_cost,
                          "timestamp": datetime.now(), "status": "draft", "project_id": ObjectId(),
                          "paymentStatus": "unpaid", "script file": scriptFile, "script": project_script}
                table.update({"_id": ObjectId(buyer_id)},
                             {'$addToSet': {"projects": mydic1}})
                table.update_one({"_id": ObjectId(buyer_id)},
                                 {"$inc": {"scout_payment": int(project_cost)}})
                session["message"] = "Added successfully."
                return redirect(url_for("projects"))
            else:
                username = session.get("username")
                email = session.get("email")
                type = session.get("type")
                table = mydb["category"]
                categories = table.find({})
                error = ""
                if session.get("error"):
                    error = session.get("error")
                    session.pop("error", None)
                message = ""
                if session.get("message"):
                    message = session.get("message")
                    session.pop("message", None)
                languages, countries, dead_line, categories, delivery_options, proposals, accents = fetch_record()
                return render_template("postjob.html", username=username, email=email,
                                       type=type, categories=categories, error=error, message=message,
                                       dead_line=dead_line, delivery_options=delivery_options,
                                       languages=languages, proposals=proposals)
        else:
            return redirect("/login")
    except Exception as e:
        session["error"] = str(e) + str(".\t\tRoute: /post-job")
        return redirect(url_for("show_error"))


# Actor API's
# about the actor update here.
@app.route("/actor-profile-api", methods=["GET", "POST"])
def actorprofile_api():
    try:
        print("file", request.files)
        print("args ", request.args)
        print("data ", request.data)
        print("json ", request.get_json())
        print("form ", request.form)
        if request.is_json or request.args or request.form:
            actorTable = mydb["actor"]
            if request.method == "POST":
                data = request.get_json()
                if data is None:
                    data = request.form
                print("New data is ",data)
                print("the  datagfa is", data)
                print(data['data[city]'])
                print(data['data[firstname]'])
                print(data['data[lastname]'])
                firstName = data['data[firstname]']
                lastName = data['data[lastname]']
                userName = data['data[username]']
                Location = data['data[city]']
                Country = data['data[country]']
                proHeadlines = data['data[professionalHeadline]']
                moreaboutyou = data['data[moreAboutYou]']

                email = data["data[email]"]
                userid = data["data[userid]"]
                type = data["data[type]"]
                print(data)
                print(request.files)
                if "pic" in request.files and request.files["pic"].filename != "":
                    print("1")
                    prifilepic = request.files["pic"]
                    file = secure_filename(prifilepic.filename)
                    file = str(userName) + "-" + str(file)
                    prifilepic.save(os.path.join(app.config['UPLOAD_FOLDER3'], str(file)))
                    newimage = Image.open(os.path.join(app.config['UPLOAD_FOLDER3'], str(file)))
                    newimage.thumbnail((421, 430))
                    newimage.save(os.path.join(UPLOAD_FOLDER, str(file)), quality=95)
                else:
                    file = ""
                actorTable.update_one({"_id": ObjectId(userid)},
                                      {"$set": {"userName": userName, "firstName": firstName, "lastName": lastName,
                                                "Location": Location, "Country": Country, "profilePicture": file,
                                                "proHeadlines": proHeadlines, "moreaboutyou": moreaboutyou,
                                                "profileStatus": "completed"}})
                return jsonify({"success": True, "message": "Profile update successfully",
                                "userid": userid, "username": userName, "type": type})
            else:
                data = request.get_json()
                if data is None:
                    data = request.args
                print(data)
                email = data["email"]
                userid = data["userid"]
                type = data["type"]
                if type == "actor":
                    actordata = actorTable.find_one({"_id": ObjectId(userid)})
                    username = actordata["userName"]
                    email = actordata["email"]
                    password = actordata["password"]
                    phoneNo = actordata["phoneNo"]
                    joinedDate = actordata["timeStamp"].strftime("%b %d, %Y")
                    if "firstName" in actordata and "lastName" in actordata:
                        firstname = actordata["firstName"]
                        lastname = actordata["lastName"]
                        professionalHeadline = actordata["proHeadlines"]
                        city = actordata["Location"]
                        country = actordata["Country"]
                        profilePic = actordata["profilePicture"]
                        if profilePic == "":
                            profilePic = "defaultPic.jpeg"
                        profilePic = "/static/profileImages/"+profilePic
                        print("the pc ", profilePic)
                    else:
                        firstname = ""
                        lastname = ""
                        professionalHeadline = ""
                        city = ""
                        country = ""
                        profilePic = "/static/profileImages/defaultPic.jpeg"
                    moreAboutYou = ""
                    if "moreaboutyou" in actordata:
                        moreAboutYou = actordata["moreaboutyou"]
                    return jsonify({"success": True, "userid": userid, "type": "type",
                                    "data": {
                                        "username": username, "firstname": firstname, "lastname": lastname,
                                        "professionalHeadline": professionalHeadline,
                                        "moreAboutYou": moreAboutYou, "city": city, "country": country,
                                        "profilePic": profilePic, "email": email, "password": password,
                                        "phoneNo": phoneNo, "joinedDate": joinedDate
                                    }})
                else:
                    return jsonify({"success": False, "message": "User type not matched"})
        else:
            return jsonify({"success": False, "message": "Not a json type request"})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


# Skills edit by the actor
@app.route("/actor-skills-api", methods=["POST", "GET"])
def actorskills_api():
    try:
        if request.is_json or request.args:
            if request.method == "POST":
                data = request.get_json()
                print(data)
                userid = data["userid"]
                email = data["email"]
                type = data["type"]
                lanaguages = data["lanaguage"]
                accent = data["actor_accents"]
                category_id = data["category_id"]
                vacal_abilities = data["vacal_abilities"]
                exp_train_equip = data["exp_train_equip"]
                if type == "actor":
                    actorTable = mydb["actor"]
                    actorTable.update_one({"_id": ObjectId(userid)},
                                          {"$set": {"languages": lanaguages, "catdata": category_id,
                                                    "addVocalAbilities": vacal_abilities,
                                                    "expTrainEquip": exp_train_equip,
                                                    "skillStatus": "completed",
                                                    "accents": accent}})
                    return jsonify({"success": True, "message": "Skills update successfully"})
                else:
                    return jsonify({"success": False, "message": "type of user not match."})
            else:
                data = request.get_json()
                if data is None:
                    data = request.args
                userid = data["userid"]
                type1 = data["type"]
                email = data["email"]
                if type1 == "actor":
                    table = mydb["actor"]
                    actor_skills = table.find_one({"_id": ObjectId(userid)})
                    if "languages" in actor_skills:
                        lanaguage = actor_skills["languages"]
                        category_id = actor_skills["catdata"]
                        vacal_abilities = actor_skills["addVocalAbilities"]
                        exp_train_equip = actor_skills["expTrainEquip"]
                        actor_accents = actor_skills["accents"]

                    else:
                        lanaguage = ""
                        category_id = ""
                        vacal_abilities = ""
                        exp_train_equip = ""
                        actor_accents =""
                    age_list, gender_list, category_list = fetch_category()
                    languages, countries, dead_line, categories, delivery_options, proposals, accents = fetch_record()
                    return jsonify({"success": True, "userid": userid, "type": type1,
                                    "data": {"lanaguage": lanaguage, "category_id": category_id,
                                             "vacal_abilities": vacal_abilities,
                                             "exp_train_equip": exp_train_equip,
                                             "actor_accents": actor_accents},
                                    "data_list": {"age_list":age_list,
                                                  "gender_list": gender_list,
                                                  "category_list": category_list,
                                                  "languages": languages,
                                                  "accents": accents}})
                else:
                    return jsonify({"success": False, "message": "type of user not match."})
        else:
            return jsonify({"success": False, "message": "Not a json type request"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


# Skills edit by the actor
@app.route("/actor-studio-api", methods=["GET", "POST"])
def actorstudio_api():
    try:
        if request.is_json:
            if request.method == "POST":
                data = request.get_json()
                print(data)
                actorTable = mydb["actor"]
                userid = session.get("userid")
                studio_sessions = data["sessions"]
                studio_turnaroundtime = data["turnaround"]
                studio_equipment = data["equipment"]
                studio_microphone = data["microphone"]
                actorTable.update_one({"_id": ObjectId(userid)},
                                      {"$set": {"studio_sessions": studio_sessions,
                                                "studio_turnaroundtime": studio_turnaroundtime,
                                                "studio_equipment": studio_equipment,
                                                "studio_microphone": studio_microphone}})
                return jsonify({"success": True, "message": "Studio Profile update successfully"})
            else:
                data = request.get_json()
                userid = data["userid"]
                type = data["type"]
                email = data["email"]
                if type == "actor":
                    table = mydb["actor"]
                    actor_skills = table.find_one({"_id": ObjectId(userid)})
                    if "studio_equipment" in actor_skills:
                        studio_equip = actor_skills["studio_equipment"]
                        studio_microphone = actor_skills["studio_microphone"]
                        studio_session = actor_skills["studio_sessions"]
                        turnaround_time = actor_skills["studio_turnaroundtime"]
                    else:
                        studio_equip = ""
                        studio_microphone = ""
                        studio_session = ""
                        turnaround_time = ""
                    return jsonify({"success": True, "userid": userid, "type": type,
                                    "data": {"equipment": studio_equip,
                                             "microphone": studio_microphone,
                                             "sessions": studio_session,
                                             "turnaround": turnaround_time}})
                else:
                    return jsonify({"success": False, "message": "type of user not match."})
        else:
            return jsonify({"success": False, "message": "Not a json type request"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


# Add new play list.
@app.route('/add-playlist-api', methods=["POST", "GET"])
def add_playlist_api():
    try:
        if request.is_json:
            if request.method == "POST":
                data = request.get_json()
                playlist_name = data["playlistName"]
                playlist_language = data["playlistLanguage"]
                playlist_accent = data["playlistAccent"]
                playlist_category = data["playListCategory"]
                userid = data["userid"]
                type = data["type"]
                email = data["email"]
                if type == "actor":
                    if "sampleFiles" in request.files:
                        playlist_files = request.files.getlist("sampleFiles")
                        print(playlist_files)
                        playlist = []
                        for eachfile in playlist_files:
                            if eachfile.filename != "":
                                file = secure_filename(eachfile.filename)
                                file = str(datetime.now()).split(".")[0].replace(":", "-") + " - " + str(file)
                                playlist.append(file)
                                eachfile.save(os.path.join(app.config['UPLOAD_FOLDER2'], str(file)))
                        actorTable = mydb["actor"]
                        actorTable.update_one({"_id": ObjectId(userid)},
                                              {"$addToSet": {"playlists": {"playlist_name": playlist_name,
                                                                           "playlist_language": playlist_language,
                                                                           "playlist_category": playlist_category,
                                                                           "playlist": playlist,
                                                                           "_id": ObjectId(),
                                                                           "playlist_accents": playlist_accent}}})
                        return jsonify({"success": True, "message": "Playlist added successfully"})
                else:
                    return jsonify({"success": True, "message": "No samples attached"})
            else:
                data = request.get_json()
                userid = data["userid"]
                type = data["type"]
                email = data["email"]
                if type == "actor":
                    table = mydb["actor"]
                    actor_skills = table.find_one({"_id": ObjectId(userid)})
                    if "playlists" in actor_skills:
                        playlists1 = actor_skills["playlists"]
                        playlists = []
                        for each_playlist in playlists1:
                            each_playlist["_id"] = str(each_playlist["_id"])
                            playlists.append(each_playlist)
                    else:
                        playlists = []
                    return jsonify({"success": True, "userid": userid, "type": type,
                                    "data": {"playlists": playlists}})
                else:
                    return jsonify({"success": False, "message": "type of user not match."})
        else:
            return jsonify({"success": False, "message": "Not a json type request"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


# Jobs for the actor
@app.route("/projects-api", methods=["GET", "POST"])
def jobs_api():
    try:
        if request.is_json:
            if request.method == "POST":
                return redirect(url_for(about_us))
            else:
                data = request.get_json()
                userid = data["userid"]
                email = data["email"]
                type1 = data["type"]
                if type1 == "actor":
                    actor_table = mydb["actor"]
                    actor_data = actor_table.find_one({"_id": ObjectId(userid)})
                    if "languages" in actor_data:
                        actor_languages = actor_data["languages"]
                        actor_accents = actor_data["accents"]
                        actor_category = actor_data["catdata"]

                        buyer_table = mydb["buyer"]
                        projcts = buyer_table.aggregate([
                            {
                                "$project": {"projects": 1}
                            },
                            {
                                "$unwind": "$projects"
                            },
                            {
                                "$match": {"projects.status": "posted"}
                            },
                            {
                                "$project": {
                                    "projects": "$projects",
                                    "matchesgener": {"$cond": {"if": {"$eq": [{"$size": {
                                        "$setIntersection": ["$projects.project_language",
                                                             actor_languages]}}, 0]}, "then": "NULL", "else": "True"}},
                                    "matchesgender": {"$cond": {"if": {"$eq": [{"$size": {
                                        "$setIntersection": ["$projects.project_gender_age",
                                                             actor_category]}}, 0]}, "then": "NULL",
                                        "else": "True"}}
                                }
                            },
                            {
                                "$match": {
                                    "$or": [{"matchesgener": {"$eq": "True"}}, {"matchesgender": {"$eq": "True"}}]}
                            }
                        ])
                        prjcts = []
                        for i in projcts:
                            i['_id'] = str(i['_id'])
                            i['projects']['project_id'] = str(i['projects']['project_id'])
                            if "responses" in i['projects']:
                                i['projects'].pop('responses', None)
                                i['projects'].pop('acceptOffers', None)

                            prjcts.append(i)
                        if len(prjcts) > 0:
                            return jsonify({"success": True, "jobs":prjcts})
                        else:
                            return jsonify({"success": False, "message": "No matching projects found"})
                    return jsonify({"success": False, "message": "Please complete your skills or profile to view related jobs.,"})
                else:
                    return jsonify({"success": False, "message": "Invalid Json Request"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


# Send-bid by the actor to posted project..
@app.route("/send-bid-api", methods=["POST"])
def send_bid_api():
    try:
        if request.is_json or request.form:
            if request.method == "POST":
                mydata = request.get_json()
                if mydata is None:
                    mydata = request.form
                data = mydata
                print(data)
                actor_id = data["user[userid]"]
                buyer_id = data["_id"]
                project_id = data["project_id"]
                actor_sample = request.files.getlist("File")

                actorTable = mydb["actor"]
                bidTable = mydb["bidding"]

                actordata = actorTable.find_one({"_id": ObjectId(actor_id)})
                planDate = actordata["planDate"]
                planPayment = actordata["planPayment"]
                curdata = datetime.now()
                previousMonthDate = curdata - timedelta(days=30)
                plandateDiff = planDate - curdata
                bidalready = bidTable.find_one({"actor_id": ObjectId(actor_id), "buyer_id":
                    ObjectId(buyer_id), "project_id": ObjectId(project_id)})
                if bidalready == None:
                    bidData = bidTable.find(
                        {"actor_id": ObjectId(actor_id), "timeStamp": {"$gte": previousMonthDate}}).count()
                    if (actordata["planType"] == "standard" or actordata[
                        "planType"] == "Basic") and bidData != None and bidData <= 10:
                        sampleslist = []
                        for samples in actor_sample:
                            if samples.filename != "":
                                file = secure_filename(samples.filename)
                                file = str(datetime.now()).split(".")[0].replace(":", "").replace("-", "") + "-" + str(
                                    file)
                                sampleslist.append(file)
                                samples.save(os.path.join(app.config['UPLOAD_FOLDER2'], str(file)))
                        bid_function_api(mydata, sampleslist)
                        return jsonify({"success": True, "message": "Request successfully send."})
                    elif (actordata["planType"] == "bronze" or actordata[
                        "planType"] == "Silver") and bidData != None and bidData <= 30:
                        if planPayment == "full" and plandateDiff <= timedelta(days=90):
                            sampleslist = []
                            for samples in actor_sample:
                                if samples.filename != "":
                                    file = secure_filename(samples.filename)
                                    file = str(datetime.now()).split(".")[0].replace(":", "").replace("-",
                                                                                                      "") + "-" + str(
                                        file)
                                    sampleslist.append(file)
                                    samples.save(os.path.join(app.config['UPLOAD_FOLDER2'], str(file)))
                            bid_function(mydata, sampleslist)
                            return jsonify({"success": True, "message": "Request successfully send."})
                        elif planPayment == "monthly" and plandateDiff <= timedelta(days=30):
                            sampleslist = []
                            for samples in actor_sample:
                                if samples.filename != "":
                                    file = secure_filename(samples.filename)
                                    file = str(datetime.now()).split(".")[0].replace(":", "").replace("-",
                                                                                                      "") + "-" + str(
                                        file)
                                    sampleslist.append(file)
                                    samples.save(os.path.join(app.config['UPLOAD_FOLDER2'], str(file)))
                            bid_function_api(mydata, sampleslist)
                            return jsonify({"success": True, "message": "Request successfully send."})
                    elif actordata[
                        "planType"] == "premium" and bidData != None and bidData <= 150:
                        if planPayment == "full" and plandateDiff <= timedelta(days=365):
                            sampleslist = []
                            for samples in actor_sample:
                                if samples.filename != "":
                                    file = secure_filename(samples.filename)
                                    file = str(datetime.now()).split(".")[0].replace(":", "").replace("-",
                                                                                                      "") + "-" + str(
                                        file)
                                    sampleslist.append(file)
                                    samples.save(os.path.join(app.config['UPLOAD_FOLDER2'], str(file)))
                            bid_function_api(mydata, sampleslist)
                            return jsonify({"success": True, "message": "Request successfully send."})
                        elif planPayment == "monthly" and plandateDiff <= timedelta(days=30):
                            sampleslist = []
                            for samples in actor_sample:
                                if samples.filename != "":
                                    file = secure_filename(samples.filename)
                                    file = str(datetime.now()).split(".")[0].replace(":", "").replace("-",
                                                                                                      "") + "-" + str(
                                        file)
                                    sampleslist.append(file)
                                    samples.save(os.path.join(app.config['UPLOAD_FOLDER2'], str(file)))
                            bid_function_api(mydata, sampleslist)
                            return jsonify({"success": True, "message": "Request successfully send."})
                    else:
                        return jsonify({"success": False,
                                        "message": "Your current month bidding is over kindly upgrade your package."})
                else:
                    return jsonify({"success": False, "message": "You have already bid this project."})
            else:
                return jsonify({"success": False, "message": "Method Not allowed."})
        else:
            return jsonify({"success": False, "message": "Not a Jsoin request."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


# Sent offer request to them who sent you bid.
# offer sent by the buyer to the reply for specific project.
@app.route("/sent-offer-api", methods=["GET", "POST"])
def sent_offer_api():
    try:
        if session.get("email") and session.get("type") and session.get("username"):
            if request.method == "POST":
                data = request.form
                project_Id = data["project_Id"].replace('"', "")
                buyer_Id = data["buyer_Id"].replace('"', "")
                actor_Id = data["actor_Id"].replace('"', "")

                buyer_table = mydb["buyer"]
                actor_table = mydb["actor"]

                table = mydb["bidding"]
                anyData = table.find_one({"actor_id": ObjectId(actor_Id), "buyer_id": ObjectId(buyer_Id),
                                          "project_id": ObjectId(project_Id)})
                if anyData is not None:
                    if anyData["offeraccpt"]:
                        return jsonify({"success": False, "error": "Already accpet request."})
                    else:
                        buyer_table.update({"_id": ObjectId(buyer_Id), "projects.project_id": ObjectId(project_Id)},
                                           {"$push": {"projects.$.acceptOffers": {"actor_id": ObjectId(actor_Id),
                                                                                  "timestamp": datetime.now(),
                                                                                  "acceptStatus": "pending"}}})
                        actor_table.update({"_id": ObjectId(actor_Id)},
                                           {"$push": {"offersReceived":
                                                          {"buyerId": ObjectId(buyer_Id),
                                                           "projectId": ObjectId(project_Id),
                                                           "timestamp": datetime.now(),
                                                           "offerstatus": "pending"}}})
                        table = mydb["bidding"]
                        table.update_one({"actor_id": ObjectId(actor_Id), "buyer_id": ObjectId(buyer_Id),
                                          "project_id": ObjectId(project_Id)},
                                         {"$set": {
                                             "offeraccpt": {"timestamp": datetime.now(), "status": "pending"}}
                                         })
                        return jsonify({"success": True})
                else:
                    return jsonify({"success": False, "error": "no record"})
            else:
                return jsonify({"success": False, "error": "INvalid Method"})
        else:
            return jsonify({"success": False, "error": "login"})
    except Exception as e:
        session["error"] = str(e) + str(".\t\tRoute: /sent-offer")
        return redirect(url_for("show_error"))


@app.route('/accept-offer-api', methods=["GET", "POST"])
def accept_offer_api():
    try:
        if request.is_json:
            if request.method == "POST":
                return jsonify({"success": False, "message": "Invalid Post request"})
            else:
                data = request.get_json
                if data is None:
                    data = request.args()
                type1 = data['type']
                actor_Id = data['userid']
                if type1 == "actor":
                    actor_Id = data['userid']
                    if request.args.get("jobId"):
                        projectId = request.args.get("jobId")
                        buyer_Id = request.args.get("buyer")
                        buyer_table = mydb["buyer"]
                        actor_table = mydb["actor"]
                        bidding_table = mydb["bidding"]
                        anyData = bidding_table.find_one(
                            {"actor_id": ObjectId(actor_Id), "buyer_id": ObjectId(buyer_Id),
                             "project_id": ObjectId(projectId)})
                        if anyData['offeraccpt']['status'] == "pending":
                            bidding_table.update_one({"actor_id": ObjectId(actor_Id),
                                                      "buyer_id": ObjectId(buyer_Id),
                                                      "project_id": ObjectId(projectId)},
                                                     {"$set": {
                                                         "offeraccpt.status": "accepted",
                                                         "offeraccpt.accepttime": datetime.now()
                                                     }})
                            print("done1")
                            # buyer_table.update({"_id": ObjectId(buyer_Id),
                            #                     "projects.project_id": ObjectId(projectId),
                            #                     "projects.acceptOffers.actor_id": ObjectId(actor_Id)},
                            #                    {"$set": {"projects.acceptOffers.$$.acceptStatus": "accepted"}}, False,
                            #                    True)
                            # print("done2")
                            # actor_table.update_one({"_id": ObjectId(actor_Id),
                            #                         "offersReceived.projectId": ObjectId(projectId)},
                            #                        {"$set": {"offersReceived.$$.offerstatus": "accepted",
                            #                                  "offersReceived.$$.accpetTime": datetime.now()}})
                            # print("done3")
                            return jsonify({"success": True, "message": "offer accepted successfully."})
                        else:
                            return jsonify({"success": False, "message": "Offer already accepted."})
                    else:
                        return jsonify({"success": False, "message": "Invalid Arguments."})
                else:
                    return jsonify({"success": False, "message": "Type not matching."})
        else:
            return jsonify({"success": False, "message": "Not a Json request."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


# Test Post api
@app.route("/test-api", methods=["GET", "POST"])
def test_api():
    print(request.args)
    try:
        print(request.data)
        print(request.get_json())
        print(type(request.get_json()))
        # if request.is_json:
        if request.method == "POST":
            table = mydb["actor"]
            actor_data = table.find({"_id" : ObjectId("5fdcc160eb2b05979a99e855")})
            return jsonify({"success": True, "data": actor_data})
        else:
            print(request.args)
            table = mydb["actor"]
            actor_data = table.find({"_id": ObjectId("5fdcc160eb2b05979a99e855")})
            return jsonify({"success": True, "data": actor_data})
            # return jsonify({"success": False})
        # return jsonify({"success": False})
    except Exception as e:
        return jsonify({"success": True, "error": str(e)})

# Email check
@app.route("/email-check", methods=["POST"])
def emailCheck():
    try:
        email = request.json["email"]
        buyertable = mydb["buyer"]
        actorTable = mydb["actor"]
        oldrecordbuyer = buyertable.find_one({"email": email})
        oldrecordactor = actorTable.find_one({"email": email})
        if oldrecordbuyer == None and oldrecordactor == None:
            return "Success"
        else:
            session["loginerror"] = """Account with this email address already exists."""
            return "Failure", 422
    except Exception as e:
        session["loginerror"] = str(
            e) + "/ Some thing went wrong please try later. Or you can write to us any time if you face any problem from contact us tab."
        return redirect("/worksignup")


@app.route("/change-job-status", methods=["GET", "POST"])
def changejob_status():
    try:
        if session.get("admintype") == "admin" and session.get("adminemail") and session.get("adminusername"):
            if request.method == "POST":
                try:
                    email = session.get("email")
                    usertype = session.get("type")      
                    print(email)
                    print(usertype)
                    data = request.form
                    project_Id = data["project_Id"].replace('"', "")
                    buyer_Id = data["buyer_Id"].replace('"', "")
                    action = data["action"].replace('"', "")
                    print(project_Id)
                    print(buyer_Id)
                    table = mydb["buyer"]
                    if action != 'deleted':
                        project_details = table.update_one(
                    {"_id": ObjectId(buyer_Id), "projects.project_id": ObjectId(project_Id)},
                    {"$set" : {"projects.$.status" : action}}
                )   
                    else:
                        print(project_Id)
                        project_details = table.update(
                    {},
                    {"$pull" : {"projects" : {"project_id": ObjectId(project_Id)}}},multi=True
                )                         
                    buyer_details = table.find_one({"_id": ObjectId(buyer_Id)})
                    buyer_email = buyer_details['email']
                    buyer_username  = buyer_details['userName']
                    for entry in buyer_details['projects']:
                        if entry['project_id'] == ObjectId(project_Id):
                            project_name = entry['project_name']
                    if action != 'deleted':
                        if action == 'posted':
                            data = {
                            "personalizations": [
                                {
                                "to": [
                                    {
                                    "email": buyer_email
                                    }
                                ],
                                "subject": "Project Status"
                                }
                            ],
                            "from": {
                                "email": default_sender,
                                "name": "voices city"
                            },
                            "content": [
                                {
                                "type": "text/html",
                                "value": """<th style="margin:0 auto; color:#0a0a0a; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-bottom:16px; padding-left:16px; padding-right:16px; text-align:left; width:564px">
	<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
		<tbody>
			<tr style="padding:0; text-align:left; vertical-align:top">
				<th style="margin:0; color:#0a0a0a; font-family:Helvetica,Arial,sans-serif; font-size:14px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left">
					<p><strong>Your project: """ + project_name + """</strong></p>
					<p>Hello """ + buyer_username + """,</p>
					<p>Thank you for posting a project on Voicescity!</p>
					<p>Our client success team has reviewed your project. We are glad to inform you that it has been successfully posted. You can check status of all projects in the <a href="https://www.voicescity.com/projects" style="color:blue;"> project dashboard.</a></p>
					<p>If you have any questions, please feel free to <a href="mailto:support@voicescity.com" style="color: blue">contact us.</a></p>
					<p>Kind Regards,</p>
					<p><strong>Voicescity Team </strong>
						<p>
							<br aria-hidden="true"><strong><span style="color:#1171bb">Voicescity.com</span></strong>
							<br aria-hidden="true">+447888884150
							<br aria-hidden="true"><a href="mailto:support@voicescity.com" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" data-linkindex="3">support@voicescity.com</a> | <a href="https://voicescity.com/" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" data-linkindex="4">voicescity.com</a> </div>
				</th>
				<th style="margin:0; color:#0a0a0a; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0!important; text-align:left; width:0"></th>
			</tr>
		</tbody>
	</table>
</th>
<table style="margin:0 auto; background:#ffffff; border:1px solid #ccc; border-collapse:collapse; border-spacing:0; border:none; color:grey; float:none; margin:0 auto; padding:0; text-align:center; vertical-align:top; width:600px" align="center">
	<tbody>
		<tr style="padding:0; text-align:left; vertical-align:top">
			<td style="margin:0; border-collapse:collapse!important; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; vertical-align:top; word-wrap:break-word">
				<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
					<tbody>
						<tr style="padding:0; text-align:left; vertical-align:top">
							<td style="margin:0; border-collapse:collapse!important; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:15px; font-weight:400; line-height:15px; margin:0; padding:0; text-align:left; vertical-align:top; word-wrap:break-word" height="15px">&nbsp;</td>
						</tr>
					</tbody>
				</table>
				<table style="border-collapse:collapse; border-spacing:0; display:table; padding:0; text-align:left; vertical-align:top; width:100%">
					<tbody>
						<tr style="padding:0; text-align:left; vertical-align:top">
							<th style="margin:0 auto; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-bottom:0; padding-left:16px; padding-right:16px; text-align:left; width:564px">
								<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
									<tbody>
										<tr style="padding:0; text-align:left; vertical-align:top">
											<th style="margin:0; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left">
												<center style="min-width:532px; width:100%"><span align="center" style="font-size:12px">LET'S BE FRIENDS</span></center>
											</th>
											<th style="margin:0; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0!important; text-align:left; width:0"></th>
										</tr>
									</tbody>
								</table>
							</th>
						</tr>
					</tbody>
				</table>
				<table style="border-collapse:collapse; border-spacing:0; display:table; padding:0; text-align:left; vertical-align:top; width:100%">
					<tbody>
						<tr style="padding:0; text-align:left; vertical-align:top">
							<th style="margin:0 auto; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-left:27px; padding-right:16px; text-align:left; width:564px">
								<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
									<tbody>
										<tr style="padding:0; text-align:left; vertical-align:top">
											<th style="margin:0; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left">
												<center style="min-width:532px; width:100%">
													<table style="margin:0 auto; border-collapse:collapse; border-spacing:0; float:none; margin:0 auto; padding:0; text-align:center; vertical-align:top; width:auto!important" align="center">
														<tbody>
															<tr style="padding:0; text-align:left; vertical-align:top">
																<td style="margin:0; border-collapse:collapse!important; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; vertical-align:top; word-wrap:break-word">
																	<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
																		<tbody>
																			<tr style="padding:0; text-align:left; vertical-align:top">
																				<th style="margin:0 auto; color:inherit; float:none; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-right:10px; text-align:center">
																					<a href="https://twitter.com/VoicesCity2?s=08" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="margin:0; color:#17b; font-family:Helvetica,Arial,sans-serif; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; text-decoration:none" data-linkindex="5"><img data-imagetype="External" src="http://voicescity.com/static/twitter.png" originalsrc="http://go.pardot.com/l/55082/2015-09-30/3gccd5/55082/68476/SocialButton3_TWR_BlueOnWhite_50X75.png" data-connectorsauthtoken="1" data-imageproxyendpoint="/actions/ei" data-imageproxyid="" alt="Twitter" style="border:none; clear:both; display:block; max-width:100%; outline:0; text-decoration:none; width:20px;"> </a>
																				</th>
																				<th style="margin:0 auto; color:inherit; float:none; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-right:10px; text-align:center">
																					<a href="https://www.facebook.com/Voices-City-332687944647576/" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="margin:0; color:#17b; font-family:Helvetica,Arial,sans-serif; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; text-decoration:none" data-linkindex="6"><img data-imagetype="External" src="http://voicescity.com/static/facebook.png" originalsrc="http://go.pardot.com/l/55082/2015-09-30/3gcccp/55082/68474/SocialButton2_FB_BlueOnWhite_50X75.png" data-connectorsauthtoken="1" data-imageproxyendpoint="/actions/ei" data-imageproxyid="" alt="Facebook" style="border:none; clear:both; display:block; max-width:100%; outline:0; text-decoration:none; width:30px;"> </a>
																				</th>
																				<th style="margin:0 auto; color:inherit; float:none; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-right:10px; text-align:center">
																					<a href="https://www.linkedin.com/in/voices-city-33990a205" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="margin:0; color:#17b; font-family:Helvetica,Arial,sans-serif; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; text-decoration:none" data-linkindex="7"><img data-imagetype="External" src="http://voicescity.com/static/linkedin.png" originalsrc="http://go.pardot.com/l/55082/2015-09-30/3gccd7/55082/68478/SocialButton1_LI_BlueOnWhite_50X75.png" data-connectorsauthtoken="1" data-imageproxyendpoint="/actions/ei" data-imageproxyid="" alt="LinkedIn" style="border:none; clear:both; display:block; max-width:100%; outline:0; text-decoration:none; width:20px;"> </a>
																				</th>
																			</tr>
																		</tbody>
																	</table>
																</td>
															</tr>
														</tbody>
													</table>
												</center>
											</th>
											<th style="margin:0; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0!important; text-align:left; width:0"></th>
										</tr>
									</tbody>
								</table>
							</th>
						</tr>
					</tbody>
				</table>
			</td>
		</tr>
	</tbody>
</table>
</table>""" } ] }
                            print(project_details)
                            sg = SendGridAPIClient(api_key)
                            response = sg.client.mail.send.post(request_body=data)
                        if action == 'cancelled':
                            data = {
                            "personalizations": [
                                {
                                "to": [
                                    {
                                    "email": buyer_email
                                    }
                                ],
                                "subject": "Project Status"
                                }
                            ],
                            "from": {
                                "email": default_sender,
                                "name": "voices city"
                            },
                            "content": [
                                {
                                "type": "text/html",
                                "value": """<th style="margin:0 auto; color:#0a0a0a; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-bottom:16px; padding-left:16px; padding-right:16px; text-align:left; width:564px">
	<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
		<tbody>
			<tr style="padding:0; text-align:left; vertical-align:top">
				<th style="margin:0; color:#0a0a0a; font-family:Helvetica,Arial,sans-serif; font-size:14px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left">
					<p><strong>Your project: """ + project_name + """</strong></p>
					<p>Hello """ + buyer_username + """,</p>
					<p>Thank you for posting a project on Voicescity!</p>
					<p>Our client success team has reviewed your project. We are sorry to inform you that it has been rejected as it does not meet our policies. You can check status of all projects in the <a href="https://www.voicescity.com/projects" style="color:blue;"> project dashboard.</a></p>
					<p>If you have any questions, please feel free to <a href="mailto:support@voicescity.com" style="color: blue">contact us.</a></p>
					<p>Kind Regards,</p>
					<p><strong>Voicescity Team </strong>
						<p>
							<br aria-hidden="true"><strong><span style="color:#1171bb">Voicescity.com</span></strong>
							<br aria-hidden="true">+447888884150
							<br aria-hidden="true"><a href="mailto:support@voicescity.com" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" data-linkindex="3">support@voicescity.com</a> | <a href="https://voicescity.com/" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" data-linkindex="4">voicescity.com</a> </div>
				</th>
				<th style="margin:0; color:#0a0a0a; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0!important; text-align:left; width:0"></th>
			</tr>
		</tbody>
	</table>
</th>
<table style="margin:0 auto; background:#ffffff; border:1px solid #ccc; border-collapse:collapse; border-spacing:0; border:none; color:grey; float:none; margin:0 auto; padding:0; text-align:center; vertical-align:top; width:600px" align="center">
	<tbody>
		<tr style="padding:0; text-align:left; vertical-align:top">
			<td style="margin:0; border-collapse:collapse!important; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; vertical-align:top; word-wrap:break-word">
				<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
					<tbody>
						<tr style="padding:0; text-align:left; vertical-align:top">
							<td style="margin:0; border-collapse:collapse!important; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:15px; font-weight:400; line-height:15px; margin:0; padding:0; text-align:left; vertical-align:top; word-wrap:break-word" height="15px">&nbsp;</td>
						</tr>
					</tbody>
				</table>
				<table style="border-collapse:collapse; border-spacing:0; display:table; padding:0; text-align:left; vertical-align:top; width:100%">
					<tbody>
						<tr style="padding:0; text-align:left; vertical-align:top">
							<th style="margin:0 auto; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-bottom:0; padding-left:16px; padding-right:16px; text-align:left; width:564px">
								<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
									<tbody>
										<tr style="padding:0; text-align:left; vertical-align:top">
											<th style="margin:0; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left">
												<center style="min-width:532px; width:100%"><span align="center" style="font-size:12px">LET'S BE FRIENDS</span></center>
											</th>
											<th style="margin:0; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0!important; text-align:left; width:0"></th>
										</tr>
									</tbody>
								</table>
							</th>
						</tr>
					</tbody>
				</table>
				<table style="border-collapse:collapse; border-spacing:0; display:table; padding:0; text-align:left; vertical-align:top; width:100%">
					<tbody>
						<tr style="padding:0; text-align:left; vertical-align:top">
							<th style="margin:0 auto; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-left:27px; padding-right:16px; text-align:left; width:564px">
								<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
									<tbody>
										<tr style="padding:0; text-align:left; vertical-align:top">
											<th style="margin:0; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left">
												<center style="min-width:532px; width:100%">
													<table style="margin:0 auto; border-collapse:collapse; border-spacing:0; float:none; margin:0 auto; padding:0; text-align:center; vertical-align:top; width:auto!important" align="center">
														<tbody>
															<tr style="padding:0; text-align:left; vertical-align:top">
																<td style="margin:0; border-collapse:collapse!important; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; vertical-align:top; word-wrap:break-word">
																	<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
																		<tbody>
																			<tr style="padding:0; text-align:left; vertical-align:top">
																				<th style="margin:0 auto; color:inherit; float:none; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-right:10px; text-align:center">
																					<a href="https://twitter.com/VoicesCity2?s=08" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="margin:0; color:#17b; font-family:Helvetica,Arial,sans-serif; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; text-decoration:none" data-linkindex="5"><img data-imagetype="External" src="http://voicescity.com/static/twitter.png" originalsrc="http://go.pardot.com/l/55082/2015-09-30/3gccd5/55082/68476/SocialButton3_TWR_BlueOnWhite_50X75.png" data-connectorsauthtoken="1" data-imageproxyendpoint="/actions/ei" data-imageproxyid="" alt="Twitter" style="border:none; clear:both; display:block; max-width:100%; outline:0; text-decoration:none; width:20px;"> </a>
																				</th>
																				<th style="margin:0 auto; color:inherit; float:none; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-right:10px; text-align:center">
																					<a href="https://www.facebook.com/Voices-City-332687944647576/" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="margin:0; color:#17b; font-family:Helvetica,Arial,sans-serif; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; text-decoration:none" data-linkindex="6"><img data-imagetype="External" src="http://voicescity.com/static/facebook.png" originalsrc="http://go.pardot.com/l/55082/2015-09-30/3gcccp/55082/68474/SocialButton2_FB_BlueOnWhite_50X75.png" data-connectorsauthtoken="1" data-imageproxyendpoint="/actions/ei" data-imageproxyid="" alt="Facebook" style="border:none; clear:both; display:block; max-width:100%; outline:0; text-decoration:none; width:30px;"> </a>
																				</th>
																				<th style="margin:0 auto; color:inherit; float:none; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-right:10px; text-align:center">
																					<a href="https://www.linkedin.com/in/voices-city-33990a205" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="margin:0; color:#17b; font-family:Helvetica,Arial,sans-serif; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; text-decoration:none" data-linkindex="7"><img data-imagetype="External" src="http://voicescity.com/static/linkedin.png" originalsrc="http://go.pardot.com/l/55082/2015-09-30/3gccd7/55082/68478/SocialButton1_LI_BlueOnWhite_50X75.png" data-connectorsauthtoken="1" data-imageproxyendpoint="/actions/ei" data-imageproxyid="" alt="LinkedIn" style="border:none; clear:both; display:block; max-width:100%; outline:0; text-decoration:none; width:20px;"> </a>
																				</th>
																			</tr>
																		</tbody>
																	</table>
																</td>
															</tr>
														</tbody>
													</table>
												</center>
											</th>
											<th style="margin:0; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0!important; text-align:left; width:0"></th>
										</tr>
									</tbody>
								</table>
							</th>
						</tr>
					</tbody>
				</table>
			</td>
		</tr>
	</tbody>
</table>
</table>""" } ] }
                            print(project_details)
                            sg = SendGridAPIClient(api_key)
                            response = sg.client.mail.send.post(request_body=data)
                    # if action == 'posted':
                    #     buyer_projects = table.aggregate([
                    #     {
                    #         "$project": {"projects": 1}
                    #     },
                    #     {
                    #         "$unwind": "$projects"
                    #     },
                    #     {
                    #         "$match": {"_id": ObjectId(buyer_Id), "projects.status": "posted",
                    #                    "projects.project_id": ObjectId(project_Id)}
                    #     }
                    # ])
                    #     proId = ""
                    #     act_lang = ""
                    #     act_cat = ""
                    #     for i in buyer_projects:
                    #         proId = str(i['projects']['project_id'])
                    #         act_lang = i['projects']['project_language']
                    #         act_cat = i['projects']['project_gender_age']

                    #     table = mydb['actor']
                    #     the_actors = table.aggregate([
                    #         {"$project": {"email": 1, "userName": 1, "languages": 1, "catdata": 1,
                    #                     "commonToLang": {"$setIntersection": ["$languages", act_lang]},
                    #                     "commonToCat": {"$setIntersection": ["$catdata", act_cat]}
                    #                     }},
                    #         {
                    #             "$match": {
                    #                 "$or": [{"commonToLang": {"$ne": {"$or": ["None", []]}}},
                    #                         {"commonToCat": {"$ne": {"$or": ["None", []]}}}]}
                    #         }
                    #     ])
                    #     actors = []
                    #     actors_user = []
                    #     for i in the_actors:
                    #         if i['commonToLang'] != None and i['commonToCat'] != None:
                    #             actors.append(i['email'])
                    #             actors_user.append(i['userName'])

                    #     for i, mails in enumerate(actors):
                    #         try:
                    #             data = {
                    #         "personalizations": [
                    #             {
                    #             "to": [
                    #                 {
                    #                 "email": mails
                    #                 }
                    #             ],
                    #             "subject": "New Job Notification"
                    #             }
                    #         ],
                    #         "from": {
                    #             "email": default_sender,
                    #             "name": "voices city"
                    #         },
                    #         "content": [
                    #             {
                    #             "type": "text/html",
                    #             "value":"""Dear """ + actors_user[i] + """, <br>
                    #                     A new projected posted which project requiremnt is best matching according to your skill set.<br>
                    #                     Reply to project and get the chance of project awarded to you.
                    #                     <br><br> Regards, <br>Voices City""" } ] }
                    #             sg = SendGridAPIClient(api_key)
                    #             response = sg.client.mail.send.post(request_body=data)
                    #         except Exception as e:
                    #             print(i, str(e))
                except Exception as e:
                    session["error"] = str(e) + str(".\t\tRoute: /change-job-status")
                    return redirect(url_for("show_error"))

            return jsonify({"success": True})
    except Exception as e:
        session["error"] = str(e) + str(".\t\tRoute: /change-job-status")
        return redirect(url_for("show_error"))

@app.route("/help")
def showHelp():
    return render_template("help.html",type=None)

@app.route("/help-equipment")
def showHelpequipment():
    return render_template("help_equipment.html",type=None)

@app.route("/help-f2f")
def showHelpf2f():
    return render_template("help_f2f.html",type=None)

@app.route("/help-wcc")
def showHelpwcc():
    return render_template("help_wcc.html",type=None)

@app.route("/help-safebox")
def showHelpsafebox():
    return render_template("help_safebox.html",type=None)

@app.route("/help-sim")
def showHelpsim():
    return render_template("help_sim.html",type=None)

@app.route("/help-ftp")
def showHelpftp():
    return render_template("help_ftp.html",type=None)

@app.route("/help-do")
def showHelpdo():
    return render_template("help_do.html",type=None)

@app.route("/help-scammers")
def showHelpscammers():
    return render_template("help_scammers.html",type=None)

@app.route("/help-member")
def showHelpmember():
    return render_template("help_member.html",type=None)

@app.route('/resend_verification',methods=["GET", "POST"])
def resend_verification():
    try:
        if request.method == "POST":
            data = request.form
            email = data["email"]
            # number = data["number"]
            buyerTable = mydb["buyer"]
            actorTable = mydb["actor"]
            buyerdata = buyerTable.find_one({"email": email})
            actordata = actorTable.find_one({"email": email})
            # print("buyerdata", buyerdata)
            # print("actordata", actordata)
            # print(type(email),email)

            if buyerdata != None and actordata == None:
                if int(buyerdata["active"]) == 0:
                    username = buyerdata['userName']
                    linkhash = buyerdata['activateLink']
                    data = {
                            "personalizations": [
                                {
                                "to": [
                                    {
                                    "email": email
                                    }
                                ],
                                "subject": username + ", please confirm your email address"
                                }
                            ],
                            "from": {
                                "email": default_sender,
                                "name": "voices city"
                            },
                            "content": [
                                {
                                "type": "text/html",
                                "value": """<th style="margin:0 auto; color:#0a0a0a; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-bottom:16px; padding-left:16px; padding-right:16px; text-align:left; width:564px">
	<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
		<tbody>
			<tr style="padding:0; text-align:left; vertical-align:top">
				<th style="margin:0; color:#0a0a0a; font-family:Helvetica,Arial,sans-serif; font-size:14px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left">
					<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
						<tbody>
							<tr style="padding:0; text-align:left; vertical-align:top">
								<td style="margin:0; border-collapse:collapse!important; color:#0a0a0a; font-family:Helvetica,Arial,sans-serif; font-size:32px; font-weight:400; line-height:10px; margin:0; padding:0; text-align:left; vertical-align:top; word-wrap:break-word" height="10px">&nbsp;</td>
							</tr>
						</tbody>
					</table>
					<p style="margin:22px 0 0"><img data-imagetype="External" src=\"""" + base_url + """/static/mail.png" title="Mail Icon" alt="Mail Icon" style="margin:auto; display:block; width:80px"> </p>
					<h4 style="width:221px; height:25px; font-size:20px; font-weight:500; line-height:1.25; letter-spacing:normal; text-align:center; margin:24px auto auto">Let's confirm your email! </h4>
					<hr style="width:520px; height:1px; background-color:#c9d0d9; border:none; margin-top:40px">
					<div style="padding:0 24px">
						<p style="font-size:16px; font-weight:normal; font-stretch:normal; font-style:normal; line-height:1.5; letter-spacing:normal; color:#4f5963; margin-top:30px; margin-bottom:30px">Hi """ + username + """,</p>
						<p style="font-size:16px; font-weight:normal; font-stretch:normal; font-style:normal; line-height:1.5; letter-spacing:normal; color:#4f5963; margin-top:30px; margin-bottom:30px">Thank you for creating a Voicescity.com account. In order to complete the registration process, please click the button below to verify your email address: </p><a href='""" + base_url + """/activate?code=""" + email + """&hashkey=""" + linkhash + """' target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="border-radius:4px; background-color:#1171bb; font-size:18px; padding:12px 24px; color:white; margin:10px 0; display:inline-block; text-decoration:none" data-linkindex="1">Verify Your Email </a>
						<p style="font-size:16px; font-weight:normal; font-stretch:normal; font-style:normal; line-height:1.5; letter-spacing:normal; color:#4f5963; margin-top:30px; margin-bottom:30px">Once you’ve verified your email you’ll gain full access to your Voicescity.com account. The verification link will expire 24 hours after your original registration request was submitted. </p>
						<p style="font-size:16px; font-weight:normal; font-stretch:normal; font-style:normal; line-height:1.5; letter-spacing:normal; color:#4f5963; margin-top:30px; margin-bottom:30px">If you experience any issues or have questions regarding your Voicescity.com account, please contact us at <a href="mailto:support@voicescity.com" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="color:#1171bb" data-linkindex="2">support@voicescity.com</a>, or at <span style="color:#1171bb">+447888884150</span> (Monday to Friday, 8:00 AM to 8:00 PM EST). </p>
						<p style="font-size:16px; font-weight:normal; font-stretch:normal; font-style:normal; line-height:1.5; letter-spacing:normal; color:#4f5963; margin-top:30px; margin-bottom:30px">Thank You.</p><strong><span style="color:#000066">Customer Support Team</span></strong>
						<br aria-hidden="true"><strong><span style="color:#1171bb">Voicescity.com</span></strong>
						<br aria-hidden="true">+447888884150
						<br aria-hidden="true"><a href="mailto:support@voicescity.com" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" data-linkindex="3">support@voicescity.com</a> | <a href="https://voicescity.com/" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" data-linkindex="4">voicescity.com</a> </div>
				</th>
				<th style="margin:0; color:#0a0a0a; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0!important; text-align:left; width:0"></th>
			</tr>
		</tbody>
	</table>
</th>
<table style="margin:0 auto; background:#ffffff; border:1px solid #ccc; border-collapse:collapse; border-spacing:0; border:none; color:grey; float:none; margin:0 auto; padding:0; text-align:center; vertical-align:top; width:600px" align="center">
	<tbody>
		<tr style="padding:0; text-align:left; vertical-align:top">
			<td style="margin:0; border-collapse:collapse!important; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; vertical-align:top; word-wrap:break-word">
				<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
					<tbody>
						<tr style="padding:0; text-align:left; vertical-align:top">
							<td style="margin:0; border-collapse:collapse!important; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:15px; font-weight:400; line-height:15px; margin:0; padding:0; text-align:left; vertical-align:top; word-wrap:break-word" height="15px">&nbsp;</td>
						</tr>
					</tbody>
				</table>
				<table style="border-collapse:collapse; border-spacing:0; display:table; padding:0; text-align:left; vertical-align:top; width:100%">
					<tbody>
						<tr style="padding:0; text-align:left; vertical-align:top">
							<th style="margin:0 auto; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-bottom:0; padding-left:16px; padding-right:16px; text-align:left; width:564px">
								<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
									<tbody>
										<tr style="padding:0; text-align:left; vertical-align:top">
											<th style="margin:0; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left">
												<center style="min-width:532px; width:100%"><span align="center" style="font-size:12px">LET'S BE FRIENDS</span></center>
											</th>
											<th style="margin:0; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0!important; text-align:left; width:0"></th>
										</tr>
									</tbody>
								</table>
							</th>
						</tr>
					</tbody>
				</table>
				<table style="border-collapse:collapse; border-spacing:0; display:table; padding:0; text-align:left; vertical-align:top; width:100%">
					<tbody>
						<tr style="padding:0; text-align:left; vertical-align:top">
							<th style="margin:0 auto; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-left:27px; padding-right:16px; text-align:left; width:564px">
								<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
									<tbody>
										<tr style="padding:0; text-align:left; vertical-align:top">
											<th style="margin:0; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left">
												<center style="min-width:532px; width:100%">
													<table style="margin:0 auto; border-collapse:collapse; border-spacing:0; float:none; margin:0 auto; padding:0; text-align:center; vertical-align:top; width:auto!important" align="center">
														<tbody>
															<tr style="padding:0; text-align:left; vertical-align:top">
																<td style="margin:0; border-collapse:collapse!important; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; vertical-align:top; word-wrap:break-word">
																	<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
																		<tbody>
																			<tr style="padding:0; text-align:left; vertical-align:top">
																				<th style="margin:0 auto; color:inherit; float:none; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-right:10px; text-align:center">
																					<a href="https://twitter.com/VoicesCity2?s=08" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="margin:0; color:#17b; font-family:Helvetica,Arial,sans-serif; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; text-decoration:none" data-linkindex="5"><img data-imagetype="External" src="http://voicescity.com/static/twitter.png" originalsrc="http://go.pardot.com/l/55082/2015-09-30/3gccd5/55082/68476/SocialButton3_TWR_BlueOnWhite_50X75.png" data-connectorsauthtoken="1" data-imageproxyendpoint="/actions/ei" data-imageproxyid="" alt="Twitter" style="border:none; clear:both; display:block; max-width:100%; outline:0; text-decoration:none; width:20px;"> </a>
																				</th>	
																				<th style="margin:0 auto; color:inherit; float:none; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-right:10px; text-align:center">
																					<a href="https://www.facebook.com/Voices-City-332687944647576/" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="margin:0; color:#17b; font-family:Helvetica,Arial,sans-serif; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; text-decoration:none" data-linkindex="6"><img data-imagetype="External" src="http://voicescity.com/static/facebook.png" originalsrc="http://go.pardot.com/l/55082/2015-09-30/3gcccp/55082/68474/SocialButton2_FB_BlueOnWhite_50X75.png" data-connectorsauthtoken="1" data-imageproxyendpoint="/actions/ei" data-imageproxyid="" alt="Facebook" style="border:none; clear:both; display:block; max-width:100%; outline:0; text-decoration:none; width:30px;"> </a>
																				</th>
																				<th style="margin:0 auto; color:inherit; float:none; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-right:10px; text-align:center">
																					<a href="https://www.linkedin.com/in/voices-city-33990a205" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="margin:0; color:#17b; font-family:Helvetica,Arial,sans-serif; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; text-decoration:none" data-linkindex="7"><img data-imagetype="External" src="http://voicescity.com/static/linkedin.png" originalsrc="http://go.pardot.com/l/55082/2015-09-30/3gccd7/55082/68478/SocialButton1_LI_BlueOnWhite_50X75.png" data-connectorsauthtoken="1" data-imageproxyendpoint="/actions/ei" data-imageproxyid="" alt="LinkedIn" style="border:none; clear:both; display:block; max-width:100%; outline:0; text-decoration:none; width:20px;"> </a>
																				</th>
																			</tr>
																		</tbody>
																	</table>
																</td>
															</tr>
														</tbody>
													</table>
												</center>
											</th>
											<th style="margin:0; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0!important; text-align:left; width:0"></th>
										</tr>
									</tbody>
								</table>
							</th>
						</tr>
					</tbody>
				</table>
			</td>
		</tr>
	</tbody>
</table>
</table>""" }
                            ]
                            }
                    # msg = Message("Reset Password", recipients=[email])

                    # msg.html = """Hi, <br>You can find you new password below:<br><br> <strong>Password: """ + str(
                    #     newpass) + """</strong> 
                    #         <br><br> Regards, <br>Voices City"""
                    # mail.send(msg)
                    sg = SendGridAPIClient(api_key)
                    response = sg.client.mail.send.post(request_body=data)
                    session["message"] = "Please check your email for verification link."
                    return redirect("/resend_verification")
                else:
                    session["loginerror"] = "Your account is already active"
                    return redirect("/resend_verification")

            elif actordata != None and buyerdata == None:
                if int(actordata["active"]) == 0:
                    username = actordata['userName']
                    linkhash = actordata['activateLink'] 
                    data = {
                            "personalizations": [
                                {
                                "to": [
                                    {
                                    "email": email
                                    }
                                ],
                                "subject": username + ", please confirm your email address"
                                }
                            ],
                            "from": {
                                "email": default_sender,
                                "name": "voices city"
                            },
                            "content": [
                                {
                                "type": "text/html",
                                "value": """<th style="margin:0 auto; color:#0a0a0a; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-bottom:16px; padding-left:16px; padding-right:16px; text-align:left; width:564px">
	<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
		<tbody>
			<tr style="padding:0; text-align:left; vertical-align:top">
				<th style="margin:0; color:#0a0a0a; font-family:Helvetica,Arial,sans-serif; font-size:14px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left">
					<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
						<tbody>
							<tr style="padding:0; text-align:left; vertical-align:top">
								<td style="margin:0; border-collapse:collapse!important; color:#0a0a0a; font-family:Helvetica,Arial,sans-serif; font-size:32px; font-weight:400; line-height:10px; margin:0; padding:0; text-align:left; vertical-align:top; word-wrap:break-word" height="10px">&nbsp;</td>
							</tr>
						</tbody>
					</table>
					<p style="margin:22px 0 0"><img data-imagetype="External" src=\"""" + base_url + """/static/mail.png" title="Mail Icon" alt="Mail Icon" style="margin:auto; display:block; width:80px"> </p>
					<h4 style="width:221px; height:25px; font-size:20px; font-weight:500; line-height:1.25; letter-spacing:normal; text-align:center; margin:24px auto auto">Let's confirm your email! </h4>
					<hr style="width:520px; height:1px; background-color:#c9d0d9; border:none; margin-top:40px">
					<div style="padding:0 24px">
						<p style="font-size:16px; font-weight:normal; font-stretch:normal; font-style:normal; line-height:1.5; letter-spacing:normal; color:#4f5963; margin-top:30px; margin-bottom:30px">Hi """ + username + """,</p>
						<p style="font-size:16px; font-weight:normal; font-stretch:normal; font-style:normal; line-height:1.5; letter-spacing:normal; color:#4f5963; margin-top:30px; margin-bottom:30px">Thank you for creating a Voicescity.com account. In order to complete the registration process, please click the button below to verify your email address: </p><a href='""" + base_url + """/activate?code=""" + email + """&hashkey=""" + linkhash + """' target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="border-radius:4px; background-color:#1171bb; font-size:18px; padding:12px 24px; color:white; margin:10px 0; display:inline-block; text-decoration:none" data-linkindex="1">Verify Your Email </a>
						<p style="font-size:16px; font-weight:normal; font-stretch:normal; font-style:normal; line-height:1.5; letter-spacing:normal; color:#4f5963; margin-top:30px; margin-bottom:30px">Once you’ve verified your email you’ll gain full access to your Voicescity.com account. The verification link will expire 24 hours after your original registration request was submitted. </p>
						<p style="font-size:16px; font-weight:normal; font-stretch:normal; font-style:normal; line-height:1.5; letter-spacing:normal; color:#4f5963; margin-top:30px; margin-bottom:30px">If you experience any issues or have questions regarding your Voicescity.com account, please contact us at <a href="mailto:support@voicescity.com" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="color:#1171bb" data-linkindex="2">support@voicescity.com</a>, or at <span style="color:#1171bb">+447888884150</span> (Monday to Friday, 8:00 AM to 8:00 PM EST). </p>
						<p style="font-size:16px; font-weight:normal; font-stretch:normal; font-style:normal; line-height:1.5; letter-spacing:normal; color:#4f5963; margin-top:30px; margin-bottom:30px">Thank You.</p><strong><span style="color:#000066">Customer Support Team</span></strong>
						<br aria-hidden="true"><strong><span style="color:#1171bb">Voicescity.com</span></strong>
						<br aria-hidden="true">+447888884150
						<br aria-hidden="true"><a href="mailto:support@voicescity.com" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" data-linkindex="3">support@voicescity.com</a> | <a href="https://voicescity.com/" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" data-linkindex="4">voicescity.com</a> </div>
				</th>
				<th style="margin:0; color:#0a0a0a; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0!important; text-align:left; width:0"></th>
			</tr>
		</tbody>
	</table>
</th>
<table style="margin:0 auto; background:#ffffff; border:1px solid #ccc; border-collapse:collapse; border-spacing:0; border:none; color:grey; float:none; margin:0 auto; padding:0; text-align:center; vertical-align:top; width:600px" align="center">
	<tbody>
		<tr style="padding:0; text-align:left; vertical-align:top">
			<td style="margin:0; border-collapse:collapse!important; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; vertical-align:top; word-wrap:break-word">
				<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
					<tbody>
						<tr style="padding:0; text-align:left; vertical-align:top">
							<td style="margin:0; border-collapse:collapse!important; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:15px; font-weight:400; line-height:15px; margin:0; padding:0; text-align:left; vertical-align:top; word-wrap:break-word" height="15px">&nbsp;</td>
						</tr>
					</tbody>
				</table>
				<table style="border-collapse:collapse; border-spacing:0; display:table; padding:0; text-align:left; vertical-align:top; width:100%">
					<tbody>
						<tr style="padding:0; text-align:left; vertical-align:top">
							<th style="margin:0 auto; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-bottom:0; padding-left:16px; padding-right:16px; text-align:left; width:564px">
								<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
									<tbody>
										<tr style="padding:0; text-align:left; vertical-align:top">
											<th style="margin:0; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left">
												<center style="min-width:532px; width:100%"><span align="center" style="font-size:12px">LET'S BE FRIENDS</span></center>
											</th>
											<th style="margin:0; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0!important; text-align:left; width:0"></th>
										</tr>
									</tbody>
								</table>
							</th>
						</tr>
					</tbody>
				</table>
				<table style="border-collapse:collapse; border-spacing:0; display:table; padding:0; text-align:left; vertical-align:top; width:100%">
					<tbody>
						<tr style="padding:0; text-align:left; vertical-align:top">
							<th style="margin:0 auto; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-left:27px; padding-right:16px; text-align:left; width:564px">
								<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
									<tbody>
										<tr style="padding:0; text-align:left; vertical-align:top">
											<th style="margin:0; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left">
												<center style="min-width:532px; width:100%">
													<table style="margin:0 auto; border-collapse:collapse; border-spacing:0; float:none; margin:0 auto; padding:0; text-align:center; vertical-align:top; width:auto!important" align="center">
														<tbody>
															<tr style="padding:0; text-align:left; vertical-align:top">
																<td style="margin:0; border-collapse:collapse!important; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; vertical-align:top; word-wrap:break-word">
																	<table style="border-collapse:collapse; border-spacing:0; padding:0; text-align:left; vertical-align:top; width:100%">
																		<tbody>
																			<tr style="padding:0; text-align:left; vertical-align:top">
																				<th style="margin:0 auto; color:inherit; float:none; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-right:10px; text-align:center">
																					<a href="https://twitter.com/VoicesCity2?s=08" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="margin:0; color:#17b; font-family:Helvetica,Arial,sans-serif; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; text-decoration:none" data-linkindex="5"><img data-imagetype="External" src="http://voicescity.com/static/twitter.png" originalsrc="http://go.pardot.com/l/55082/2015-09-30/3gccd5/55082/68476/SocialButton3_TWR_BlueOnWhite_50X75.png" data-connectorsauthtoken="1" data-imageproxyendpoint="/actions/ei" data-imageproxyid="" alt="Twitter" style="border:none; clear:both; display:block; max-width:100%; outline:0; text-decoration:none; width:20px;"> </a>
																				</th>	
																				<th style="margin:0 auto; color:inherit; float:none; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-right:10px; text-align:center">
																					<a href="https://www.facebook.com/Voices-City-332687944647576/" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="margin:0; color:#17b; font-family:Helvetica,Arial,sans-serif; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; text-decoration:none" data-linkindex="6"><img data-imagetype="External" src="http://voicescity.com/static/facebook.png" originalsrc="http://go.pardot.com/l/55082/2015-09-30/3gcccp/55082/68474/SocialButton2_FB_BlueOnWhite_50X75.png" data-connectorsauthtoken="1" data-imageproxyendpoint="/actions/ei" data-imageproxyid="" alt="Facebook" style="border:none; clear:both; display:block; max-width:100%; outline:0; text-decoration:none; width:30px;"> </a>
																				</th>
																				<th style="margin:0 auto; color:inherit; float:none; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0 auto; padding:0; padding-right:10px; text-align:center">
																					<a href="https://www.linkedin.com/in/voices-city-33990a205" target="_blank" rel="noreferrer noopener" data-auth="NotApplicable" style="margin:0; color:#17b; font-family:Helvetica,Arial,sans-serif; font-weight:400; line-height:1.3; margin:0; padding:0; text-align:left; text-decoration:none" data-linkindex="7"><img data-imagetype="External" src="http://voicescity.com/static/linkedin.png" originalsrc="http://go.pardot.com/l/55082/2015-09-30/3gccd7/55082/68478/SocialButton1_LI_BlueOnWhite_50X75.png" data-connectorsauthtoken="1" data-imageproxyendpoint="/actions/ei" data-imageproxyid="" alt="LinkedIn" style="border:none; clear:both; display:block; max-width:100%; outline:0; text-decoration:none; width:20px;"> </a>
																				</th>
																			</tr>
																		</tbody>
																	</table>
																</td>
															</tr>
														</tbody>
													</table>
												</center>
											</th>
											<th style="margin:0; color:inherit; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:400; line-height:1.3; margin:0; padding:0!important; text-align:left; width:0"></th>
										</tr>
									</tbody>
								</table>
							</th>
						</tr>
					</tbody>
				</table>
			</td>
		</tr>
	</tbody>
</table>
</table>""" }
                            ]
                            }
                    # msg = Message("Reset Password", recipients=[email])

                    # msg.html = """Hi, <br>You can find you new password below:<br><br> <strong>Password: """ + str(
                    #     newpass) + """</strong> 
                    #         <br><br> Regards, <br>Voices City"""
                    # mail.send(msg)
                    sg = SendGridAPIClient(api_key)
                    response = sg.client.mail.send.post(request_body=data)
                    session["message"] = "Please check your email for activation link."
                    return redirect("/resend_verification")

                else:
                    session["loginerror"] = "Your account is already active."
                    return redirect("/resend_verification")
            else:
                session["loginerror"] = "Email or Password is incorrect."
                return redirect("/resend_verification")
        else:
            loginerror = "NULL"
            if session.get("loginerror"):
                loginerror = session.get("loginerror")
                session.pop("loginerror", None)
            loginemail = ""
            if session.get("loginemail"):
                loginemail = session.get("loginemail")
                session.pop("loginemail", None)
            message = ""
            if session.get("message"):
                message = session.get("message")
                session.pop("message", None)
            return render_template("resend_verification.html", loginerror=loginerror, loginemail=loginemail, message=message,
                                   type=None)
    except Exception as e:
        session["loginerror"] = str(
            e) + "/ Some thing went wrong please try later. Or you can write to us any time if you face any problem from contact us tab."
        return redirect("/forget_password")


@app.route('/change_password',methods=["GET", "POST"])
def change_password():
    try:
        if request.method == "POST":
            data = request.form
            email = data["email"]
            old_password = data['old_password']
            new_password = data['new_password']
            buyerTable = mydb["buyer"]
            actorTable = mydb["actor"]
            buyerdata = buyerTable.find_one({"email": email, "password": old_password})
            actordata = actorTable.find_one({"email": email, "password": old_password})
            # print("buyerdata", buyerdata)
            # print("actordata", actordata)
            # print(type(email),email)

            if buyerdata != None and actordata == None:
                if int(buyerdata["active"]) == 1:
                    hashpassword = generate_password_hash(new_password)
                    buyerTable.update_one({"email": email}, {"$set": {"password": new_password,"passwordHash":hashpassword}})
                    session["message"] = "Your password has been updated."
                    return redirect("/change_password")
                else:
                    return redirect("/change_password")

            elif actordata != None and buyerdata == None:
                if int(actordata["active"]) == 1:
                    hashpassword = generate_password_hash(new_password)
                    actorTable.update_one({"email": email}, {"$set": {"password": new_password,"passwordHash": hashpassword}})
                    session["message"] = "Your password has been updated."
                    return redirect("/change_password")

                else:
                    session["loginerror"] = "Your account is not active.Please check your email to activate your account."
                    return redirect("/change_password")
            else:
                session["loginerror"] = "Email or Old password does not match."
                return redirect("/change_password")
        else:
            loginerror = "NULL"
            if session.get("loginerror"):
                loginerror = session.get("loginerror")
                session.pop("loginerror", None)
            loginemail = ""
            if session.get("loginemail"):
                loginemail = session.get("loginemail")
                session.pop("loginemail", None)
            message = ""
            if session.get("message"):
                message = session.get("message")
                session.pop("message", None)
            return render_template("change_password.html", loginerror=loginerror, loginemail=loginemail, message=message,
                                   type=None)
    except Exception as e:
        session["loginerror"] = str(
            e) + "/ Some thing went wrong please try later. Or you can write to us any time if you face any problem from contact us tab."
        return redirect("/change_password")



if __name__ == "__main__":
    socketio.run(app, debug=True)
