import firebase_admin
from firebase_admin import credentials, firestore
import matplotlib.pyplot as plt
import datetime
import tkinter as tk
from tkinter import Canvas, Scrollbar, Frame, Label

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")  # Ensure this path is correct
firebase_admin.initialize_app(cred)
db = firestore.client()

# Function to convert Firestore document timestamps to readable datetime
def convert_timestamp_to_datetime(timestamp):
    try:
        return datetime.datetime.fromtimestamp(float(timestamp))
    except ValueError:
        print(f"Skipping '{timestamp}' as it cannot be converted to a timestamp.")
        return None

# Function to fetch data from all collections and plot all graphs in a scrollable window
def fetch_and_plot_data():
    fitness_collection = db.collection('fitness_data').stream()

    timestamps = []
    data_dict = {
        'body_fat_percentage': [],
        'calories_burned': [],
        'distance_traveled': [],
        'energy_expended': [],
        'heart_points': [],
        'heart_rate': [],
        'sleep_duration': [],
        'steps': [],
        'vigorous_activity_minutes': []
    }

    # Iterate through each document in the collection
    for doc in fitness_collection:
        doc_data = doc.to_dict()
        timestamp = convert_timestamp_to_datetime(doc_data.get('timestamp'))
        if timestamp is None:
            continue

        timestamps.append(timestamp)

        for key in data_dict:
            data_dict[key].append(doc_data.get(key, 0))

    # Create a Tkinter window with scrollable canvas
    window = tk.Tk()
    window.title("Fitness Data Plots")

    canvas = Canvas(window, bg='white')
    scrollbar = Scrollbar(window, orient="vertical", command=canvas.yview)
    scrollable_frame = Frame(canvas, bg='white')

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    # Plot each fitness metric and display as images in the scrollable frame
    for metric, values in data_dict.items():
        if values:
            plt.figure(figsize=(10, 6))
            plt.plot(timestamps, values, label=metric, marker='o')
            plt.xlabel('Time')
            plt.ylabel(metric.capitalize().replace('_', ' '))
            plt.title(f'{metric.capitalize().replace("_", " ")} Over Time')
            plt.grid(True)
            plt.legend()

            # Save the plot as an image
            output_file = f'{metric}_plot.png'
            plt.savefig(output_file)
            plt.close()

            # Load and display the image in the scrollable frame
            img = tk.PhotoImage(file=output_file)
            label = Label(scrollable_frame, image=img, bg='white')
            label.image = img  # Keep a reference to avoid garbage collection
            label.pack(pady=10)

    # Configure the canvas and scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Mouse wheel scrolling
    window.bind("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))

    window.mainloop()

# Run the plotting function
fetch_and_plot_data()
