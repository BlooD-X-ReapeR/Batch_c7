from flask import Flask, render_template
import pandas as pd
import plotly.express as px
import plotly.io as pio
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime

app = Flask(__name__)

# Load data from Excel file
def load_data():
    file_path = 'air.xlsx'
    data = pd.read_excel(file_path)
    return data

# Train a regression model
def train_model(data):
    # Convert timestamp to numeric
    data['Timestamp'] = pd.to_datetime(data['Timestamp'])
    data['Timestamp'] = data['Timestamp'].astype('int64') // 10**9  # Convert to seconds
    
    # Prepare features and target
    X = data['Timestamp'].values.reshape(-1, 1)
    y = data['Air Quality'].values
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train the model
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    return model, X, y

# Predict future air quality
def predict_future(model, X):
    X_future = np.arange(X[-1], X[-1] + 86400, 3600).reshape(-1, 1)  # Predict for the next 24 hours, every hour
    y_future = model.predict(X_future)
    
    # Convert predictions to a DataFrame
    future_data = pd.DataFrame({
        'Timestamp': pd.to_datetime(X_future.flatten(), unit='s'),
        'Air Quality': y_future
    })
    
    return future_data

# Determine the next time air pollution will be detected
def predict_next_pollution_time(future_data, threshold=300):
    pollution_times = future_data[future_data['Air Quality'] > threshold]
    if not pollution_times.empty:
        next_pollution_time = pollution_times['Timestamp'].iloc[0]
        return next_pollution_time
    else:
        return None
# Add this new route to your existing app.py
@app.route('/impacts')
def impacts():
    impacts_data = {
        'health': [
            {'level': 'Good (0-50)', 'effects': 'Minimal impact'},
            {'level': 'Moderate (51-100)', 'effects': 'Possible irritation for sensitive individuals'},
            {'level': 'Unhealthy for Sensitive Groups (101-150)', 'effects': 'Increased likelihood of respiratory symptoms'},
            {'level': 'Unhealthy (151-200)', 'effects': 'Increased aggravation of heart or lung disease'},
            {'level': 'Very Unhealthy (201-300)', 'effects': 'Significant health effects for everyone'},
            {'level': 'Hazardous (301+)', 'effects': 'Serious health effects and emergency conditions'}
        ],
        'environment': [
            'Damage to vegetation and reduced crop yields',
            'Acid rain formation',
            'Eutrophication of water bodies',
            'Damage to buildings and monuments',
            'Reduced visibility (haze)'
        ],
        'economic': [
            'Increased healthcare costs',
            'Reduced worker productivity',
            'Damage to agricultural production',
            'Increased maintenance costs for buildings',
            'Impact on tourism'
        ]
    }
    
    return render_template('impacts.html', impacts=impacts_data)

@app.route('/analysis')
def analysis():
    # Load data
    data = load_data()
    
    # Train model and make predictions
    model, X, y = train_model(data)
    future_data = predict_future(model, X)
    
    # Create Plotly figures with dark theme
    fig_historical = px.line(data, x='Timestamp', y='Air Quality', title='Historical Air Quality Data', 
                             labels={'Timestamp': 'Timestamp', 'Air Quality': 'Air Quality Index'},
                             template='plotly_dark')
    fig_predicted = px.line(future_data, x='Timestamp', y='Air Quality', title='Predicted Air Quality Data',
                            labels={'Timestamp': 'Timestamp', 'Air Quality': 'Air Quality Index'},
                            template='plotly_dark')
    
    # Convert figures to HTML
    graph_historical_html = pio.to_html(fig_historical, full_html=False)
    graph_predicted_html = pio.to_html(fig_predicted, full_html=False)
    
    return render_template('analysis.html', 
                           graph_historical=graph_historical_html,
                           graph_predicted=graph_predicted_html)


@app.route('/')
def index():
    # Load data
    data = load_data()
    
    # Train model and make predictions
    model, X, y = train_model(data)
    future_data = predict_future(model, X)
    
    # Determine the next time air pollution will be detected
    next_pollution_time = predict_next_pollution_time(future_data)
    
    # Prepare prediction message
    if next_pollution_time:
        prediction_message = f"Next air pollution predicted at: {next_pollution_time.strftime('%Y-%m-%d %H:%M:%S')}"
        alert_class = "alert-danger"
    else:
        prediction_message = "No air pollution predicted in the next 24 hours"
        alert_class = "alert-success"
    
    # Current air quality status
    current_quality = data['Air Quality'].iloc[-1]
    if current_quality > 300:
        current_status = "Poor"
        status_class = "text-danger"
    elif current_quality > 150:
        current_status = "Moderate"
        status_class = "text-warning"
    else:
        current_status = "Good"
        status_class = "text-success"
    
    # Create Plotly figures with dark theme
    fig_historical = px.line(data, x='Timestamp', y='Air Quality', title='Historical Air Quality Data', 
                             labels={'Timestamp': 'Timestamp', 'Air Quality': 'Air Quality Index'},
                             template='plotly_dark')
    fig_predicted = px.line(future_data, x='Timestamp', y='Air Quality', title='Predicted Air Quality Data',
                            labels={'Timestamp': 'Timestamp', 'Air Quality': 'Air Quality Index'},
                            template='plotly_dark')
    
    # Convert figures to HTML
    graph_historical_html = pio.to_html(fig_historical, full_html=False)
    graph_predicted_html = pio.to_html(fig_predicted, full_html=False)
    
    return render_template('index.html', 
                         graph_historical=graph_historical_html,
                         graph_predicted=graph_predicted_html,
                         prediction_message=prediction_message,
                         alert_class=alert_class,
                         current_quality=current_quality,
                         current_status=current_status,
                         status_class=status_class,
                         last_update=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

if __name__ == '__main__':
    app.run(debug=True)