# fitness_evaluation.py

# Define references for each fitness metric used in the evaluation
references = {
    'heart_points': "1. World Health Organization (WHO). \"Physical Activity and Heart Health.\" [WHO Link](https://www.who.int).",
    'steps': "2. American Heart Association. \"How Many Steps Should You Take a Day?\" [AHA Link](https://www.heart.org).",
    'calories_burned': "3. Mayo Clinic. \"Calories Burned in Exercise.\" [Mayo Clinic Link](https://www.mayoclinic.org).",
    'distance_traveled': "4. American College of Sports Medicine (ACSM). \"Distance Running and Health.\" [ACSM Link](https://www.acsm.org).",
    'move_minutes': "5. Centers for Disease Control and Prevention. \"Move Minutes and Physical Activity Recommendations.\" [CDC Link](https://www.cdc.gov).",
    'weight': "8. World Health Organization (WHO). \"Body Weight and Health Recommendations.\" [WHO Link](https://www.who.int).",
    'energy_expended': "9. National Institutes of Health (NIH). \"Energy Expenditure and Metabolism.\" [NIH Link](https://www.nih.gov).",
    'average_heart_rate': "10. American Heart Association. \"Target Heart Rates.\" [AHA Link](https://www.heart.org).",
    'body_fat_percentage': "11. National Institutes of Health (NIH). \"Body Fat Percentage Guidelines.\" [NIH Link](https://www.nih.gov)."
}

def evaluate_fitness(fitness_data):
    """
    Evaluates the fitness data of a student and categorizes them based on sports suitability.
    
    Parameters:
    - fitness_data (dict): A dictionary containing fitness metrics.

    Returns:
    - str: Category of sports suitability along with recommendations, positive aspects, and references.
    """

    # Extract fitness metrics from the provided data
    metrics = {
        'heart_points': fitness_data.get('heart_points', 0),
        'steps': fitness_data.get('steps', 0),
        'calories_burned': fitness_data.get('calories_burned', 0),
        'distance_traveled': fitness_data.get('distance_traveled', 0),
        'weight': fitness_data.get('weight', 0),
        'energy_expended': fitness_data.get('energy_expended', 0),
        'vigorous_activity_minutes': fitness_data.get('vigorous_activity_minutes', 0),
        'average_heart_rate': fitness_data.get('average_heart_rate', 0),
        'body_fat_percentage': fitness_data.get('body_fat_percentage', 0)  
    }

    # Initialize lists to store verdicts and positive traits
    verdicts = []
    positive_traits = []

    # Define thresholds and corresponding messages
    thresholds = {
        'heart_points': {
            'threshold': 21.42,
            'low_message': "Heart Points below the recommended target; aim for 150 points per week.",
            'high_message': "Good achievement of Heart Points, supports cardiovascular health."
        },
        'steps': {
            'threshold': 7000,
            'low_message': "Low activity level; consider increasing daily steps.",
            'high_message': "Achieving a good level of daily steps."
        },
        'calories_burned': {
            'threshold': 2000,
            'low_message': "Low calorie expenditure; may not be suitable for competitive sports.",
            'high_message': "Good calorie expenditure; likely supports an active lifestyle."
        },
        'distance_traveled': {
            'threshold': 5,
            'low_message': "Low running distance; may not be suitable for endurance sports.",
            'high_message': "Good running distance; supports endurance capabilities."
        },
        'weight': {
            'threshold': 90,  
            'high_message': "Weight is within a healthy range for athletic performance.",
            'low_message': "Weight is above the optimal range; consider weight management for better performance."
        },
        'energy_expended': {
            'threshold': 1500,
            'low_message': "Low energy expenditure; consider increasing activity levels.",
            'high_message': "Good energy expenditure; supports an active lifestyle."
        },
        'vigorous_activity_minutes': {
            'threshold': 75,  
            'low_message': "Insufficient vigorous activity; aim for at least 75 minutes per week.",
            'high_message': "Good amount of vigorous activity, supports overall fitness."
        },
        'average_heart_rate': {
            'threshold': 100, 
            'low_message': "Average heart rate is above the healthy range; consider monitoring your intensity.",
            'high_message': "Average heart rate is within a healthy range; supports cardiovascular fitness."
        },
        'body_fat_percentage': {
            'threshold': 25,  # Example threshold for body fat percentage (for males, varies by gender)
            'low_message': "Body fat percentage is above the recommended level; consider a fitness plan.",
            'high_message': "Body fat percentage is within a healthy range."
        }
    }

    # Evaluate each metric against its thresholds
    for metric, values in thresholds.items():
        if metric == 'weight':
            # Invert logic for weight
            if metrics[metric] > values['threshold']:
                verdicts.append(values['low_message'])
            else:
                positive_traits.append(values['high_message'])
        elif metric =='average_heart_rate':
            # Invert logic for weight
            if metrics[metric] > values['threshold']:
                verdicts.append(values['low_message'])
            else:
                positive_traits.append(values['high_message'])
        elif metric == 'body_fat_percentage':
            # Invert logic for weight
            if metrics[metric] > values['threshold']:
                verdicts.append(values['low_message'])
            else:
                positive_traits.append(values['high_message'])
        else:
            if metrics[metric] < values['threshold']:
                verdicts.append(values['low_message'])
            else:
                positive_traits.append(values['high_message'])

    # Final verdict based on accumulated verdicts and positive traits
    final_verdict = []

    if positive_traits:
        final_verdict.append("\n\nPOSITIVE ASPECTS:\n\n" + "\n".join(positive_traits))
    else:
        final_verdict.append("\n\nPOSITIVE ASPECTS:\n\nKeep trying and stay active; every step counts toward improving your fitness!")
    if not verdicts:
        final_verdict.append("\n\nSuitable for a variety of sports based on current fitness level.")
    else:
        final_verdict.append("\n\nRECOMMENDATIONS:\n\n" + "\n".join(verdicts))

    # Add positive feedback if any
    

    # Add references at the end of the report
    reference_section = "\n\nREFERENCES:\n\n" + "\n".join([f"{key.capitalize()}: {reference}" for key, reference in references.items()])
    final_verdict.append(reference_section)

    return "\n".join(final_verdict)
