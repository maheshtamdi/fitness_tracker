
import pickle
import os
import time
import tkinter as tk
from tkinter import messagebox, simpledialog
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from fitness_evaluation import evaluate_fitness  # Import the fitness evaluation function
from firebase_config import initialize_firebase  # Import Firebase initialization

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = [
    'https://www.googleapis.com/auth/fitness.activity.read',
    'https://www.googleapis.com/auth/fitness.body.read',
    'https://www.googleapis.com/auth/fitness.location.read',
    'https://www.googleapis.com/auth/fitness.sleep.read'  # Added sleep scope
]

class FitnessApp:
    def __init__(self, master):
        self.master = master
        master.title("Fitness Data Evaluation")

        # Initialize Firebase
        self.db = initialize_firebase()

        # Create buttons for actions
        self.get_data_button = tk.Button(master, text="Get Google Fit Data", command=self.get_google_fit_data)
        self.get_data_button.pack(pady=20)

        self.quit_button = tk.Button(master, text="Quit", command=master.quit)
        self.quit_button.pack(pady=20)

    # Function to get credentials
    def get_credentials(self):
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

    # Function to fetch Google Fit data
    def get_google_fit_data(self):
        credentials = self.get_credentials()  # Get credentials
        service = build('fitness', 'v1', credentials=credentials)

        # Define the time range for the data request
        end_time = int(time.time() * 1e9)  # Current time in nanoseconds
        start_time = end_time - 24 * 60 * 60 * 1e9  # 24 hours ago

        # Prepare the dataset ID
        dataset_id = f"{int(start_time)}-{int(end_time)}"

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

        # Create a new window for additional inputs
        self.input_window = tk.Toplevel(self.master)
        self.input_window.title("Additional Fitness Metrics")

        # Labels and entry fields for additional metrics
        tk.Label(self.input_window, text="Average Heart Rate (bpm):").grid(row=0, column=0)
        self.heart_rate_entry = tk.Entry(self.input_window)
        self.heart_rate_entry.grid(row=0, column=1)

        tk.Label(self.input_window, text="Vigorous Activity Minutes:").grid(row=1, column=0)
        self.vigorous_activity_entry = tk.Entry(self.input_window)
        self.vigorous_activity_entry.grid(row=1, column=1)

        tk.Label(self.input_window, text="Distance Traveled (km):").grid(row=2, column=0)
        self.distance_traveled_entry = tk.Entry(self.input_window)
        self.distance_traveled_entry.grid(row=2, column=1)

        tk.Label(self.input_window, text="Body Fat Percentage:").grid(row=3, column=0)
        self.body_fat_percentage_entry = tk.Entry(self.input_window)
        self.body_fat_percentage_entry.grid(row=3, column=1)

        # Submit button to process the inputs
        submit_button = tk.Button(self.input_window, text="Submit", command=lambda: self.process_inputs(fitness_data))
        submit_button.grid(row=4, columnspan=2, pady=20)

    def process_inputs(self, fitness_data):
        # Retrieve values from the entry fields
        try:
            fitness_data['heart_rate'] = float(self.heart_rate_entry.get())
            fitness_data['vigorous_activity_minutes'] = float(self.vigorous_activity_entry.get())
            fitness_data['distance_traveled'] = float(self.distance_traveled_entry.get())
            fitness_data['body_fat_percentage'] = float(self.body_fat_percentage_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for all metrics.")
            return
        # Add timestamp for plotting later
        fitness_data['timestamp'] = time.time() 
        # Evaluate fitness data and add verdict
        fitness_data['verdict'] = evaluate_fitness(fitness_data)

        # Store the fitness data in Firestore
        self.store_fitness_data(fitness_data)

        # Display results
        self.display_results(fitness_data)

    def display_results(self, fitness_data):
        results = "\n".join(f"{key.capitalize()}: {value}" for key, value in fitness_data.items())
        messagebox.showinfo("Fitness Data", results)

        
    # Store fitness data in Firebase Firestore
    def store_fitness_data(self, fitness_data):
        # Firestore document reference (You can use a user's ID or timestamp as the document name)
        doc_ref = self.db.collection('fitness_data').document(str(time.time()))

        # Store the fitness data
        try:
            doc_ref.set(fitness_data)
            print("Fitness data successfully saved to Firestore.")
        except Exception as e:
            print(f"Error storing fitness data: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FitnessApp(root)
    root.mainloop()