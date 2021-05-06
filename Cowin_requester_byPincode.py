import urllib.request, urllib.parse, urllib.error
import datetime
import json
import time
import smtplib, ssl
import getpass

# date_tomorrow = datetime.date.today() + datetime.timedelta(days=1)
# date = date_tomorrow.strftime('%d-%m-%Y')
date = datetime.today().strftime('%d-%m-%Y')
port = 587
sender_email = input("Enter sender outlook email address: ")
password = getpass.getpass(prompt="Enter your password: ")
smtp_server = "smtp.outlook.com"
receiver_email = input("Enter receiver email address: ")
cc = input("Enter cc address: ")
SUBJECT = "COVID VACCINE AVAILABILITY"
context = ssl.create_default_context()

#Pune District code = 363
pincodes = ['411057', '411033', '411027', '411045'] # Wakad, Chinchwadgaon, Aundh, Baner

serviceurl = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?"
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
headers = {"User-Agent":user_agent}

while(True):
    avail_centers = list()
    for pincode in pincodes:
        parms = {"pincode": pincode, "date": date}
        url = serviceurl + urllib.parse.urlencode(parms)
        
        request = urllib.request.Request(url,headers=headers)
        try:
            response = urllib.request.urlopen(request)
        except urllib.error.HTTPError as e:
            print("HTTP Error:", e.code)
            time.sleep(60)
            continue
        data = response.read().decode()
        js = json.loads(data)

        for center in js["centers"]:
            sessions = center["sessions"]
            for session in sessions:
                if  session["min_age_limit"] == 18 and session["available_capacity"] != 0 and session["vaccine"] == "COVAXIN":
                    avail_centers.append({"name": center["name"], "available_capacity": session["available_capacity"],  "date": session["date"], "fee_type": center["fee_type"], "address": center["address"], "slots": session["slots"], "vaccine": session["vaccine"]})
                
                if  session["min_age_limit"] == 45 and session["available_capacity"] != 0 and session["vaccine"] == "COVISHIELD":
                    avail_centers.append({"name": center["name"], "available_capacity": session["available_capacity"],  "date": session["date"], "fee_type": center["fee_type"], "address": center["address"], "slots": session["slots"], "vaccine": session["vaccine"]})

        time.sleep(3)        
    TEXT = "Following centers are available:\n\n"
    for center in avail_centers:
        TEXT = TEXT + json.dumps(center) + "\n"

    message = "To: {}\r\n".format(receiver_email) + "CC: {}\r\n".format(cc) +  "Subject: {}\n\n{}".format(SUBJECT, TEXT)

    if not bool(avail_centers):
        print("Sleep")
        time.sleep(10)

    else:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls(context=context)
            try:
                server.login(sender_email, password)
            except smtplib.SMTPAuthenticationError as e:
                error_code = e.smtp_code
                error_message = e.smtp_error
                print("\n" + error_message)
                print("Abort!")
                exit(0)
            try:
                server.sendmail(sender_email, [receiver_email]+[cc], message)
                server.quit()
            except smtplib.SMTPResponseException as e:
                error_code = e.smtp_code
                error_message = e.smtp_error
                print("\n" + error_message)
                print("Abort!")
                exit(0)
        print("Slots found. Sending email. Sleep for 1hr")
        time.sleep(3600)
        print("Restarting")
    
