from flask import Flask, render_template
import pandas as pd
import plotly.express as px
import plotly.io as pio
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import numpy as np

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

@app.route('/')
def index():
    # Load data
    data = load_data()
    
    # Train model and make predictions
    model, X, y = train_model(data)
    future_data = predict_future(model, X)
    
    # Determine the next time air pollution will be detected
    next_pollution_time = predict_next_pollution_time(future_data)
    
    # Write the next pollution time to a text file
    if next_pollution_time:
        with open('next_pollution_time.txt', 'w') as f:
            f.write(f"Next predicted air pollution time: {next_pollution_time}")
    else:
        with open('next_pollution_time.txt', 'w') as f:
            f.write("No air pollution predicted in the next 24 hours.")
    
    # Create Plotly figures
    fig_historical = px.line(data, x='Timestamp', y='Air Quality', title='Historical Air Quality Data', 
                             labels={'Timestamp': 'Timestamp', 'Air Quality': 'Air Quality Index'})
    fig_predicted = px.line(future_data, x='Timestamp', y='Air Quality', title='Predicted Air Quality Data',
                            labels={'Timestamp': 'Timestamp', 'Air Quality': 'Air Quality Index'})
    
    # Convert figures to HTML
    graph_historical_html = pio.to_html(fig_historical, full_html=False)
    graph_predicted_html = pio.to_html(fig_predicted, full_html=False)
    
    return render_template('index.html', graph_historical=graph_historical_html, graph_predicted=graph_predicted_html)

if __name__ == '__main__':
    app.run(debug=True)
