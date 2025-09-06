import pickle
import os
import time
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from fitness_evaluation import evaluate_fitness  # Import the fitness evaluation function

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = [
    'https://www.googleapis.com/auth/fitness.activity.read',
    'https://www.googleapis.com/auth/fitness.body.read',
    'https://www.googleapis.com/auth/fitness.location.read',
    'https://www.googleapis.com/auth/fitness.sleep.read'  # Added sleep scope
]

# Function to get credentials
def get_credentials():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=50803)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

# Function to get Google Fit data
def get_google_fit_data(credentials):
    service = build('fitness', 'v1', credentials=credentials)

    # Define the time range for the data request
    end_time = int(time.time() * 1e9)  # Current time in nanoseconds
    start_time = end_time - 24 * 60 * 60 * 1e9  # 24 hours ago

    # Prepare the dataset ID
    dataset_id = f"{int(start_time)}-{int(end_time)}"  # Ensure dataset_id is in integer format

    # Initialize a dictionary for fitness data
    fitness_data = {
        'steps': 0,
        'calories_burned': 0,
        'weight': 0,
        'sleep_duration': 0,
        'heart_rate': 0,
        'vigorous_activity_minutes': 0,
        'distance_traveled': 0,
        'body_fat_percentage': 0,
        'heart_points': 0,
        'energy_expended': 0
    }

    # Function to fetch data from a specific data source
    def fetch_data(source_id, metric):
        try:
            response = service.users().dataSources().datasets().get(
                userId='me',
                dataSourceId=source_id,
                datasetId=dataset_id
            ).execute()
            return sum(point['value'][0]['fpVal'] if 'fpVal' in point['value'][0] else point['value'][0]['intVal'] for point in response['point'])
        except HttpError as e:
            print(f"Error fetching {metric} data: {e}")
            return 0

    # Fetch different metrics using the helper function
    fitness_data['steps'] = fetch_data('derived:com.google.step_count.delta:com.google.android.gms:estimated_steps', 'steps')
    fitness_data['calories_burned'] = fetch_data('derived:com.google.calories.expended:com.google.android.gms:merge_calories_expended', 'calories burned')
    fitness_data['heart_points'] = fetch_data('derived:com.google.heart_minutes:com.google.android.gms:merge_heart_minutes', 'heart points')
    fitness_data['energy_expended'] = fetch_data('derived:com.google.heart_minutes:com.google.android.gms:merge_calories_expended', 'energy expended')
    fitness_data['weight'] = fetch_data('derived:com.google.weight:com.google.android.gms:merge_weight', 'weight')
    
    # Fetch sleep duration in hours
    fitness_data['sleep_duration'] = fetch_data('derived:com.google.sleep.segment:com.google.android.gms:merge_sleep', 'sleep') / 60

    # Prompt user for additional metrics not available from the API
    fitness_data['heart_rate'] = float(input("Enter your average heart rate (bpm): ")) if not fitness_data['heart_rate'] else fitness_data['heart_rate']
    fitness_data['vigorous_activity_minutes'] = float(input("Enter your vigorous activity minutes: ")) if not fitness_data['vigorous_activity_minutes'] else fitness_data['vigorous_activity_minutes']
    fitness_data['distance_traveled'] = float(input("Enter the distance traveled in kilometers: ")) if not fitness_data['distance_traveled'] else fitness_data['distance_traveled']
    fitness_data['body_fat_percentage'] = float(input("Enter your body fat percentage: ")) if not fitness_data['body_fat_percentage'] else fitness_data['body_fat_percentage']

    # Evaluate fitness data and add verdict
    fitness_data['verdict'] = evaluate_fitness(fitness_data)  # Call the imported fitness evaluation function

    return fitness_data

# Main function to handle the entire process
def main():
    credentials = get_credentials()  # Get credentials
    fitness_data = get_google_fit_data(credentials)  # Get fitness data

    # Display all collected fitness parameters
    print("\n\nFITNESS DATA")
    for key, value in fitness_data.items():
        print(f"{key.capitalize()}: {value}")

    # Improved formatting for recommendations and positive aspects in the verdict
    verdict = fitness_data.get('verdict', '')


if __name__ == '__main__':
    main()
