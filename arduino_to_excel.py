import serial
import pandas as pd
from datetime import datetime
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Configure the serial port
ser = serial.Serial('COM5', 9600)  # Update 'COM5' with your Arduino's serial port

# File path
file_path = 'air.xlsx'

# Check if the file exists
if os.path.exists(file_path):
    # Load existing data
    data = pd.read_excel(file_path)
else:
    # Create an empty DataFrame to store data
    data = pd.DataFrame(columns=['Air Quality', 'Timestamp'])

# Email configurations
sender_email = 'akda2003a@gmail.com'  # Replace with your email address
sender_password = 'qCAUIdkctag7619b'  # Replace with your email password
receiver_emails = ['akda2003k@gmail.com', 'aswin1372004@gmail.com']  # Replace with recipient email addresses

def assess_air_quality(air_quality):
    if air_quality <= 10:
        return "Good"
    elif air_quality <= 50:
        return "Moderate"
    elif air_quality <= 100:
        return "Unhealthy for sensitive groups"
    elif air_quality <= 150:
        return "Unhealthy"
    elif air_quality <= 200:
        return "Very unhealthy"
    else:
        return "Hazardous"

def send_email(new_data):
    # Prepare message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['Subject'] = 'New Air Quality Data Added'

    # Extract the latest data
    latest_data = new_data.iloc[-1:]

    # Determine air quality assessment
    latest_air_quality = latest_data['Air Quality'].iloc[0]
    air_quality_assessment = assess_air_quality(latest_air_quality)

    # Create HTML content for the email
    html_content = """
    <html>
    <body>
        <h2>Latest Air Quality Data</h2>
        <div>
            <p><strong>Air Quality:</strong> {aq}</p>
            <p><strong>Timestamp:</strong> {ts}</p>
            <p><strong>Assessment:</strong> {assessment}</p>
        </div>
        
        <div class="precautions">
            <h3>Precautions for Air Quality</h3>
            <ul>
                <li>Avoid outdoor activities during high pollution times.</li>
                <li>Use air purifiers indoors to reduce exposure.</li>
                <li>Keep windows closed during high pollution periods.</li>
            </ul>
        </div>
        
        <div class="best-worst">
            <h3>Best and Worst Air Quality Standards</h3>
            <p>According to WHO standards:</p>
            <ul>
                <li>Best air quality: PM2.5 ≤ 10 µg/m³</li>
                <li>Worst air quality: PM2.5 ≥ 250 µg/m³</li>
            </ul>
        </div>
    </body>
    </html>
    """.format(aq=latest_air_quality, ts=latest_data['Timestamp'].iloc[0], assessment=air_quality_assessment)

    msg.attach(MIMEText(html_content, 'html'))

    # SMTP session for sending the mail
    try:
        server = smtplib.SMTP('smtp-relay.brevo.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)

        for receiver_email in receiver_emails:
            msg['To'] = receiver_email
            server.sendmail(sender_email, receiver_email, msg.as_string())
            print(f'Email sent successfully to {receiver_email}!')

    except Exception as e:
        print(f'Failed to send email. Error: {str(e)}')
    finally:
        server.quit()

try:
    while True:
        # Read data from Arduino
        line = ser.readline().decode('utf-8').strip()
        
        if line.startswith('DATA,'):
            # Extract air quality and timestamp
            _, air_quality, timestamp = line.split(',')
            
            # Convert timestamp to datetime object
            timestamp = datetime.fromtimestamp(int(timestamp) / 1000.0)
            
            # Create a new DataFrame row
            new_data = pd.DataFrame({'Air Quality': [int(air_quality)], 'Timestamp': [timestamp]})
            
            # Append new data to the main DataFrame
            data = pd.concat([data, new_data], ignore_index=True)
            
            # Save DataFrame to Excel file
            data.to_excel(file_path, index=False)
            print(f"Data saved to {file_path}")
            
            # Send email with new data
            send_email(new_data)

except KeyboardInterrupt:
    print("Data logging stopped.")
    ser.close()
