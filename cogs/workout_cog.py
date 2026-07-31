import nextcord
from nextcord.ext import commands
import motor.motor_asyncio
import os
from datetime import datetime

ROUTINES = {
    "Novice Initiate": {
        "Gym": {
            "Monday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (8 kgs)", "10x3"), ("Hammer curls (8 kgs)", "10x3")],
            "Tuesday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (8 kgs)", "10x3"), ("Hammer curls (8 kgs)", "10x3")],
            "Wednesday": "Rest Day",
            "Thursday": [("Arm + neck rotation", "10x1"), ("Crunches / Ab crunch machine", "7x1"), ("Seated Cable row", "7x1")],
            "Friday": [("Arm + neck rotation", "10x1"), ("Crunches / Ab crunch machine", "7x1"), ("Seated Cable row", "7x1")],
            "Saturday": [("Arm + neck rotation", "10x1"), ("Bodyweight squats", "7x1"), ("Weighted squats (3kg/6.5lbs)", "7x1"), ("Treadmill", "5 minutes")],
            "Sunday": "Rest Day"
        },
        "Calisthenics": {
            "Monday": [("Arm + neck rotation", "10x1"), ("Push Ups", "7x1"), ("Elevated push ups", "7x1")],
            "Tuesday": [("Arm + neck rotation", "10x1"), ("Push Ups", "7x1"), ("Elevated push ups", "7x1")],
            "Wednesday": "Rest Day",
            "Thursday": [("Arm + neck rotation", "10x1"), ("Crunches", "7x1"), ("Plank", "1 set")],
            "Friday": [("Arm + neck rotation", "10x1"), ("Crunches", "7x1"), ("Plank", "1 set")],
            "Saturday": [("Arm + neck rotation", "10x1"), ("Bodyweight squats", "7x1"), ("Bodyweight lunges", "7x1"), ("Running", "5 minutes")],
            "Sunday": "Rest Day"
        }
    },
    "Bronze Legionnaire": {
        "Gym": {
            "Monday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (8 kgs)", "10x2"), ("Hammer curls (8 kgs)", "10x2"), ("Overhead Triceps extension", "10x2"), ("Preacher curls", "10x2")],
            "Tuesday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (8 kgs)", "10x2"), ("Hammer curls (8 kgs)", "10x2"), ("Overhead Triceps extension", "10x2"), ("Preacher curls", "10x2")],
            "Wednesday": "Rest Day",
            "Thursday": [("Arm + neck rotation", "10x1"), ("Crunches / Ab crunch machine", "10x2"), ("Seated Cable row", "10x2"), ("Cable lats pulldown", "10x2")],
            "Friday": [("Arm + neck rotation", "10x1"), ("Crunches / Ab crunch machine", "10x2"), ("Seated Cable row", "10x2"), ("Cable lats pulldown", "10x2")],
            "Saturday": [("Arm + neck rotation", "10x1"), ("Weighted squats", "10x2"), ("Leg press", "10x2"), ("Leg extension", "10x2")],
            "Sunday": "Rest Day"
        },
        "Calisthenics": {
            "Monday": [("Arm + neck rotation", "10x1"), ("Push Ups", "10x2"), ("Elevated push ups", "10x2"), ("Chair assisted dips", "10x2"), ("Pull ups", "10x2")],
            "Tuesday": [("Arm + neck rotation", "10x1"), ("Push Ups", "10x2"), ("Elevated push ups", "10x2"), ("Chair assisted dips", "10x2"), ("Pull ups", "10x2")],
            "Wednesday": "Rest Day",
            "Thursday": [("Arm + neck rotation", "10x1"), ("Crunches", "10x2"), ("Twist crunches", "10x2"), ("Push ups", "10x2"), ("Plank", "2 sets")],
            "Friday": [("Arm + neck rotation", "10x1"), ("Crunches", "10x2"), ("Twist crunches", "10x2"), ("Push ups", "10x2"), ("Plank", "2 sets")],
            "Saturday": [("Arm + neck rotation", "10x1"), ("Bodyweight squats", "10x2"), ("Bodyweight lunges", "10x2"), ("Jumping", "10x2"), ("Running", "10 minutes")],
            "Sunday": "Rest Day"
        }
    },
    "Iron Vanguard": {
        "Gym": {
            "Monday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (8 kgs)", "10x3"), ("Hammer curls (8 kgs)", "10x3"), ("Overhead Triceps extension", "10x3"), ("Preacher curls", "10x3")],
            "Tuesday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (8 kgs)", "10x3"), ("Hammer curls (8 kgs)", "10x3"), ("Overhead Triceps extension", "10x3"), ("Preacher curls", "10x3")],
            "Wednesday": "Rest Day",
            "Thursday": [("Arm + neck rotation", "10x1"), ("Crunches / Ab crunch machine", "10x3"), ("Seated Cable row", "10x3"), ("Cable lats pulldown", "10x3"), ("Pec dec", "10x3"), ("Bench press (10-15 kg)", "2x5")],
            "Friday": [("Arm + neck rotation", "10x1"), ("Crunches / Ab crunch machine", "10x3"), ("Seated Cable row", "10x3"), ("Cable lats pulldown", "10x3"), ("Pec dec", "10x3"), ("Bench press (10-15 kg)", "2x5")],
            "Saturday": [("Arm + neck rotation", "10x1"), ("Weighted squats", "10x2"), ("Leg press", "10x2"), ("Leg extension", "10x2"), ("Incline leg press", "10x2"), ("Seated leg curl", "10x2")],
            "Sunday": "Rest Day"
        },
        "Calisthenics": {
            "Monday": [("Arm + neck rotation", "10x1"), ("Push Ups", "10x2"), ("Frog stand with parallettes", "2 sets"), ("Pull ups", "10x3"), ("Chin ups", "10x3")],
            "Tuesday": [("Arm + neck rotation", "10x1"), ("Push Ups", "10x2"), ("Frog stand with parallettes", "2 sets"), ("Pull ups", "10x3"), ("Chin ups", "10x3")],
            "Wednesday": "Rest Day",
            "Thursday": [("Arm + neck rotation", "10x1"), ("Crunches", "10x2"), ("Twist crunches", "10x2"), ("Push ups", "10x2"), ("Inclined push ups", "10x2"), ("Hindu push ups", "10x1"), ("Chair assisted dips", "10x2")],
            "Friday": [("Arm + neck rotation", "10x1"), ("Crunches", "10x2"), ("Twist crunches", "10x2"), ("Push ups", "10x2"), ("Inclined push ups", "10x2"), ("Hindu push ups", "10x1"), ("Chair assisted dips", "10x2")],
            "Saturday": [("Arm + neck rotation", "10x1"), ("Bodyweight squats", "10x3"), ("Weighted squats", "1 set"), ("Jumping", "10x3"), ("Running", "20 minutes")],
            "Sunday": "Rest Day"
        }
    },
    "Steel Centurion": {
        "Gym": {
            "Monday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (8 kgs)", "10x3"), ("Hammer curls (8 kgs)", "10x3"), ("Overhead Triceps extension", "10x3"), ("Preacher curls", "10x3"), ("Overhead press", "10x3")],
            "Tuesday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (8 kgs)", "10x3"), ("Hammer curls (8 kgs)", "10x3"), ("Overhead Triceps extension", "10x3"), ("Preacher curls", "10x3"), ("Overhead press", "10x3")],
            "Wednesday": "Rest Day",
            "Thursday": [("Arm + neck rotation", "10x1"), ("Crunches / Ab crunch machine", "10x3"), ("Seated Cable row", "10x3"), ("Cable lats pulldown", "10x3"), ("Pec dec", "10x3"), ("Bench press (20-40 kg)", "2x5")],
            "Friday": [("Arm + neck rotation", "10x1"), ("Crunches / Ab crunch machine", "10x3"), ("Seated Cable row", "10x3"), ("Cable lats pulldown", "10x3"), ("Pec dec", "10x3"), ("Bench press (20-40 kg)", "2x5")],
            "Saturday": [("Arm + neck rotation", "10x1"), ("Weighted squats", "10x3"), ("Leg press", "10x3"), ("Leg extension", "10x3"), ("Incline leg press", "10x3"), ("Seated leg curl", "10x3")],
            "Sunday": "Rest Day"
        },
        "Calisthenics": {
            "Monday": [("Arm + neck rotation", "10x1"), ("Push Ups", "10x3"), ("Pull ups", "10x3"), ("Chin ups", "10x3"), ("Frog stand with parallettes", "3 sets")],
            "Tuesday": [("Arm + neck rotation", "10x1"), ("Push Ups", "10x3"), ("Pull ups", "10x3"), ("Chin ups", "10x3"), ("Frog stand with parallettes", "3 sets")],
            "Wednesday": "Rest Day",
            "Thursday": [("Arm + neck rotation", "10x1"), ("Crunches", "10x3"), ("Twist crunches", "10x3"), ("Push ups", "10x3"), ("Inclined push ups", "10x3"), ("Hindu push ups", "10x3"), ("Chair assisted dips", "10x3"), ("L-sit", "2 sets")],
            "Friday": [("Arm + neck rotation", "10x1"), ("Crunches", "10x3"), ("Twist crunches", "10x3"), ("Push ups", "10x3"), ("Inclined push ups", "10x3"), ("Hindu push ups", "10x3"), ("Chair assisted dips", "10x3"), ("L-sit", "2 sets")],
            "Saturday": [("Arm + neck rotation", "10x1"), ("Bodyweight squats", "10x3"), ("Weighted squats", "10x3"), ("Jumping", "10x3"), ("Running", "30 minutes")],
            "Sunday": "Rest Day"
        }
    },
    "Gilded Champion": {
        "Gym": {
            "Monday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (8 kgs)", "10x4"), ("Hammer curls (8 kgs)", "10x4"), ("Overhead Triceps extension", "10x4"), ("Preacher curls", "10x4"), ("Overhead press", "10x4")],
            "Tuesday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (8 kgs)", "10x4"), ("Hammer curls (8 kgs)", "10x4"), ("Overhead Triceps extension", "10x4"), ("Preacher curls", "10x4"), ("Overhead press", "10x4")],
            "Wednesday": "Rest Day",
            "Thursday": [("Arm + neck rotation", "10x1"), ("Crunches / Ab crunch machine", "10x4"), ("Seated Cable row", "10x4"), ("Cable lats pulldown", "10x4"), ("Pec dec", "10x4"), ("Bench press (20-40 kg)", "2x5")],
            "Friday": [("Arm + neck rotation", "10x1"), ("Crunches / Ab crunch machine", "10x4"), ("Seated Cable row", "10x4"), ("Cable lats pulldown", "10x4"), ("Pec dec", "10x4"), ("Bench press (20-40 kg)", "2x5")],
            "Saturday": [("Arm + neck rotation", "10x1"), ("Weighted squats", "10x3"), ("Leg press", "10x3"), ("Leg extension", "10x3"), ("Incline leg press", "10x3"), ("Seated leg curl", "10x3")],
            "Sunday": "Rest Day"
        },
        "Calisthenics": {
            "Monday": [("Arm + neck rotation", "10x1"), ("Push Ups", "10x4"), ("Pull ups", "10x4"), ("Chin ups", "10x4"), ("Frog stand with parallettes", "2 sets"), ("Tuck front lever hold", "2 sets")],
            "Tuesday": [("Arm + neck rotation", "10x1"), ("Push Ups", "10x4"), ("Pull ups", "10x4"), ("Chin ups", "10x4"), ("Frog stand with parallettes", "2 sets"), ("Tuck front lever hold", "2 sets")],
            "Wednesday": "Rest Day",
            "Thursday": [("Arm + neck rotation", "10x1"), ("Crunches", "10x4"), ("Twist crunches", "10x4"), ("Push ups", "10x4"), ("Inclined push ups", "10x4"), ("Hindu push ups", "10x4"), ("Chair assisted dips", "10x4"), ("L-sit", "2 sets")],
            "Friday": [("Arm + neck rotation", "10x1"), ("Crunches", "10x4"), ("Twist crunches", "10x4"), ("Push ups", "10x4"), ("Inclined push ups", "10x4"), ("Hindu push ups", "10x4"), ("Chair assisted dips", "10x4"), ("L-sit", "2 sets")],
            "Saturday": [("Arm + neck rotation", "10x1"), ("Bodyweight squats", "10x3"), ("Weighted squats", "10x3"), ("Jumping", "10x3"), ("Running", "40 minutes")],
            "Sunday": "Rest Day"
        }
    },
    "Arena Master": {
        "Gym": {
            "Monday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (8 kgs)", "15x3"), ("Hammer curls (8 kgs)", "15x3"), ("Overhead Triceps extension", "15x3"), ("Preacher curls", "15x3"), ("Overhead press", "15x3")],
            "Tuesday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (8 kgs)", "15x3"), ("Hammer curls (8 kgs)", "15x3"), ("Overhead Triceps extension", "15x3"), ("Preacher curls", "15x3"), ("Overhead press", "15x3")],
            "Wednesday": "Rest Day",
            "Thursday": [("Arm + neck rotation", "10x1"), ("Pull ups", "10x2"), ("Crunches / Ab crunch machine", "15x3"), ("Seated Cable row", "15x3"), ("Cable lats pulldown", "15x3"), ("Pec dec", "15x3"), ("Bench press (20-40 kg)", "2x5")],
            "Friday": [("Arm + neck rotation", "10x1"), ("Pull ups", "10x2"), ("Crunches / Ab crunch machine", "15x3"), ("Seated Cable row", "15x3"), ("Cable lats pulldown", "15x3"), ("Pec dec", "15x3"), ("Bench press (20-40 kg)", "2x5")],
            "Saturday": [("Weighted squats", "10x3"), ("Leg press", "10x3"), ("Leg extension", "10x3"), ("Incline leg press", "10x3"), ("Seated leg curl", "10x3")],
            "Sunday": "Rest Day"
        },
        "Calisthenics": {
            "Monday": [("Arm + neck rotation", "10x1"), ("Push Ups", "15x3"), ("Pull ups", "15x3"), ("Chin ups", "15x3"), ("Frog stand with parallettes", "2 sets"), ("Tuck front lever hold", "2 sets"), ("Negative front lever raises", "1x1")],
            "Tuesday": [("Arm + neck rotation", "10x1"), ("Push Ups", "15x3"), ("Pull ups", "15x3"), ("Chin ups", "15x3"), ("Frog stand with parallettes", "2 sets"), ("Tuck front lever hold", "2 sets"), ("Negative front lever raises", "1x1")],
            "Wednesday": "Rest Day",
            "Thursday": [("Arm + neck rotation", "10x1"), ("Crunches", "15x3"), ("Twist crunches", "15x3"), ("Push ups", "15x3"), ("Inclined push ups", "15x3"), ("Hindu push ups", "15x3"), ("Chair assisted dips", "15x3"), ("L-sit", "2 sets")],
            "Friday": [("Arm + neck rotation", "10x1"), ("Crunches", "15x3"), ("Twist crunches", "15x3"), ("Push ups", "15x3"), ("Inclined push ups", "15x3"), ("Hindu push ups", "15x3"), ("Chair assisted dips", "15x3"), ("L-sit", "2 sets")],
            "Saturday": [("Arm + neck rotation", "10x1"), ("Bodyweight squats", "10x3"), ("Weighted squats", "10x3"), ("Jumping", "10x3"), ("Running", "30 minutes")],
            "Sunday": "Rest Day"
        }
    },
    "Gold Gladiator": {
        "Gym": {
            "Monday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (10 kgs)", "10x2"), ("Hammer curls (10 kgs)", "10x2"), ("Overhead Triceps extension", "10x2"), ("Preacher curls", "10x2"), ("Overhead press", "10x2")],
            "Tuesday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (10 kgs)", "10x2"), ("Hammer curls (10 kgs)", "10x2"), ("Overhead Triceps extension", "10x2"), ("Preacher curls", "10x2"), ("Overhead press", "10x2")],
            "Wednesday": "Rest Day",
            "Thursday": [("Arm + neck rotation", "10x1"), ("Pull ups", "10x3"), ("Crunches / Ab crunch machine", "10x2"), ("Seated Cable row", "10x2"), ("Cable lats pulldown", "10x2"), ("Pec dec", "10x2"), ("Bench press (20-40 kg)", "2x5")],
            "Friday": [("Arm + neck rotation", "10x1"), ("Pull ups", "10x3"), ("Crunches / Ab crunch machine", "10x2"), ("Seated Cable row", "10x2"), ("Cable lats pulldown", "10x2"), ("Pec dec", "10x2"), ("Bench press (20-40 kg)", "2x5")],
            "Saturday": [("Weighted squats", "10x3"), ("Leg press", "10x3"), ("Leg extension", "10x3"), ("Incline leg press", "10x3"), ("Seated leg curl", "10x3")],
            "Sunday": "Rest Day"
        },
        "Calisthenics": {
            "Monday": [("Arm + neck rotation", "10x1"), ("Push Ups", "20x2"), ("Pull ups", "20x2"), ("Chin ups", "20x2"), ("Frog stand with parallettes", "2 sets"), ("advance tuck front lever hold", "2 sets"), ("Negative front lever raises", "3x1")],
            "Tuesday": [("Arm + neck rotation", "10x1"), ("Push Ups", "20x2"), ("Pull ups", "20x2"), ("Chin ups", "20x2"), ("Frog stand with parallettes", "2 sets"), ("advance tuck front lever hold", "2 sets"), ("Negative front lever raises", "3x1")],
            "Wednesday": "Rest Day",
            "Thursday": [("Arm + neck rotation", "10x1"), ("Crunches", "15x2"), ("Twist crunches", "10x2"), ("Push ups", "20x2"), ("Inclined push ups", "20x2"), ("Hindu push ups", "20x2"), ("Chair assisted dips", "20x2"), ("L-sit", "2 sets")],
            "Friday": [("Arm + neck rotation", "10x1"), ("Crunches", "15x2"), ("Twist crunches", "10x2"), ("Push ups", "20x2"), ("Inclined push ups", "20x2"), ("Hindu push ups", "20x2"), ("Chair assisted dips", "20x2"), ("L-sit", "2 sets")],
            "Saturday": [("Arm + neck rotation", "10x1"), ("Bodyweight squats", "10x3"), ("Weighted squats", "10x3"), ("Jumping", "10x3"), ("Running", "30 minutes")],
            "Sunday": "Rest Day"
        }
    },
    "Apex Centurion": {
        "Gym": {
            "Monday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (10 kgs)", "10x2"), ("Hammer curls (10 kgs)", "10x2"), ("Overhead Triceps extension", "10x2"), ("Preacher curls", "10x2"), ("Overhead press", "10x2")],
            "Tuesday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (10 kgs)", "10x2"), ("Hammer curls (10 kgs)", "10x2"), ("Overhead Triceps extension", "10x2"), ("Preacher curls", "10x2"), ("Overhead press", "10x2")],
            "Wednesday": "Rest Day",
            "Thursday": [("Arm + neck rotation", "10x1"), ("Pull ups", "10x3"), ("Crunches / Ab crunch machine", "10x2"), ("Seated Cable row", "10x2"), ("Cable lats pulldown", "10x2"), ("Pec dec", "10x2"), ("Bench press (20-40 kg)", "2x5")],
            "Friday": [("Arm + neck rotation", "10x1"), ("Pull ups", "10x3"), ("Crunches / Ab crunch machine", "10x2"), ("Seated Cable row", "10x2"), ("Cable lats pulldown", "10x2"), ("Pec dec", "10x2"), ("Bench press (20-40 kg)", "2x5")],
            "Saturday": [("Weighted squats", "10x3"), ("Leg press", "10x3"), ("Leg extension", "10x3"), ("Incline leg press", "10x3"), ("Seated leg curl", "10x3")],
            "Sunday": "Rest Day"
        },
        "Calisthenics": {
            "Monday": [("Arm + neck rotation", "10x1"), ("Push Ups", "20x2"), ("Pull ups", "20x2"), ("Chin ups", "20x2"), ("Frog stand with parallettes", "2 sets"), ("advance tuck front lever hold", "2 sets"), ("Negative front lever raises", "3x1")],
            "Tuesday": [("Arm + neck rotation", "10x1"), ("Push Ups", "20x2"), ("Pull ups", "20x2"), ("Chin ups", "20x2"), ("Frog stand with parallettes", "2 sets"), ("advance tuck front lever hold", "2 sets"), ("Negative front lever raises", "3x1")],
            "Wednesday": "Rest Day",
            "Thursday": [("Arm + neck rotation", "10x1"), ("Crunches", "15x2"), ("Twist crunches", "10x2"), ("Push ups", "20x2"), ("Inclined push ups", "20x2"), ("Hindu push ups", "20x2"), ("Chair assisted dips", "20x2"), ("L-sit", "2 sets")],
            "Friday": [("Arm + neck rotation", "10x1"), ("Crunches", "15x2"), ("Twist crunches", "10x2"), ("Push ups", "20x2"), ("Inclined push ups", "20x2"), ("Hindu push ups", "20x2"), ("Chair assisted dips", "20x2"), ("L-sit", "2 sets")],
            "Saturday": [("Arm + neck rotation", "10x1"), ("Bodyweight squats", "10x3"), ("Weighted squats", "10x3"), ("Jumping", "10x3"), ("Running", "30 minutes")],
            "Sunday": "Rest Day"
        }
    },
    "Titan Ascendant": {
        "Gym": {
            "Monday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (10 kgs)", "10x2"), ("Hammer curls (10 kgs)", "10x2"), ("Overhead Triceps extension", "10x2"), ("Preacher curls", "10x2"), ("Overhead press", "10x2")],
            "Tuesday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (10 kgs)", "10x2"), ("Hammer curls (10 kgs)", "10x2"), ("Overhead Triceps extension", "10x2"), ("Preacher curls", "10x2"), ("Overhead press", "10x2")],
            "Wednesday": "Rest Day",
            "Thursday": [("Arm + neck rotation", "10x1"), ("Pull ups", "10x3"), ("Crunches / Ab crunch machine", "10x2"), ("Seated Cable row", "10x2"), ("Cable lats pulldown", "10x2"), ("Pec dec", "10x2"), ("Bench press (20-40 kg)", "2x5")],
            "Friday": [("Arm + neck rotation", "10x1"), ("Pull ups", "10x3"), ("Crunches / Ab crunch machine", "10x2"), ("Seated Cable row", "10x2"), ("Cable lats pulldown", "10x2"), ("Pec dec", "10x2"), ("Bench press (20-40 kg)", "2x5")],
            "Saturday": [("Weighted squats", "10x3"), ("Leg press", "10x3"), ("Leg extension", "10x3"), ("Incline leg press", "10x3"), ("Seated leg curl", "10x3")],
            "Sunday": "Rest Day"
        },
        "Calisthenics": {
            "Monday": [("Arm + neck rotation", "10x1"), ("Push Ups", "20x2"), ("Pull ups", "20x2"), ("Chin ups", "20x2"), ("Frog stand with parallettes", "2 sets"), ("advance tuck front lever hold", "2 sets"), ("Negative front lever raises", "3x1")],
            "Tuesday": [("Arm + neck rotation", "10x1"), ("Push Ups", "20x2"), ("Pull ups", "20x2"), ("Chin ups", "20x2"), ("Frog stand with parallettes", "2 sets"), ("advance tuck front lever hold", "2 sets"), ("Negative front lever raises", "3x1")],
            "Wednesday": "Rest Day",
            "Thursday": [("Arm + neck rotation", "10x1"), ("Crunches", "15x2"), ("Twist crunches", "10x2"), ("Push ups", "20x2"), ("Inclined push ups", "20x2"), ("Hindu push ups", "20x2"), ("Chair assisted dips", "20x2"), ("L-sit", "2 sets")],
            "Friday": [("Arm + neck rotation", "10x1"), ("Crunches", "15x2"), ("Twist crunches", "10x2"), ("Push ups", "20x2"), ("Inclined push ups", "20x2"), ("Hindu push ups", "20x2"), ("Chair assisted dips", "20x2"), ("L-sit", "2 sets")],
            "Saturday": [("Arm + neck rotation", "10x1"), ("Bodyweight squats", "10x3"), ("Weighted squats", "10x3"), ("Jumping", "10x3"), ("Running", "30 minutes")],
            "Sunday": "Rest Day"
        }
    },
    "Gladiator Maximus": {
        "Gym": {
            "Monday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (10 kgs)", "10x2"), ("Hammer curls (10 kgs)", "10x2"), ("Overhead Triceps extension", "10x2"), ("Preacher curls", "10x2"), ("Overhead press", "10x2")],
            "Tuesday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (10 kgs)", "10x2"), ("Hammer curls (10 kgs)", "10x2"), ("Overhead Triceps extension", "10x2"), ("Preacher curls", "10x2"), ("Overhead press", "10x2")],
            "Wednesday": "Rest Day",
            "Thursday": [("Arm + neck rotation", "10x1"), ("Pull ups", "10x3"), ("Crunches / Ab crunch machine", "10x2"), ("Seated Cable row", "10x2"), ("Cable lats pulldown", "10x2"), ("Pec dec", "10x2"), ("Bench press (20-40 kg)", "2x5")],
            "Friday": [("Arm + neck rotation", "10x1"), ("Pull ups", "10x3"), ("Crunches / Ab crunch machine", "10x2"), ("Seated Cable row", "10x2"), ("Cable lats pulldown", "10x2"), ("Pec dec", "10x2"), ("Bench press (20-40 kg)", "2x5")],
            "Saturday": [("Weighted squats", "10x3"), ("Leg press", "10x3"), ("Leg extension", "10x3"), ("Incline leg press", "10x3"), ("Seated leg curl", "10x3")],
            "Sunday": "Rest Day"
        },
        "Calisthenics": {
            "Monday": [("Arm + neck rotation", "10x1"), ("Push Ups", "20x2"), ("Pull ups", "20x2"), ("Chin ups", "20x2"), ("Frog stand with parallettes", "2 sets"), ("advance tuck front lever hold", "2 sets"), ("Negative front lever raises", "3x1")],
            "Tuesday": [("Arm + neck rotation", "10x1"), ("Push Ups", "20x2"), ("Pull ups", "20x2"), ("Chin ups", "20x2"), ("Frog stand with parallettes", "2 sets"), ("advance tuck front lever hold", "2 sets"), ("Negative front lever raises", "3x1")],
            "Wednesday": "Rest Day",
            "Thursday": [("Arm + neck rotation", "10x1"), ("Crunches", "15x2"), ("Twist crunches", "10x2"), ("Push ups", "20x2"), ("Inclined push ups", "20x2"), ("Hindu push ups", "20x2"), ("Chair assisted dips", "20x2"), ("L-sit", "2 sets")],
            "Friday": [("Arm + neck rotation", "10x1"), ("Crunches", "15x2"), ("Twist crunches", "10x2"), ("Push ups", "20x2"), ("Inclined push ups", "20x2"), ("Hindu push ups", "20x2"), ("Chair assisted dips", "20x2"), ("L-sit", "2 sets")],
            "Saturday": [("Arm + neck rotation", "10x1"), ("Bodyweight squats", "10x3"), ("Weighted squats", "10x3"), ("Jumping", "10x3"), ("Running", "30 minutes")],
            "Sunday": "Rest Day"
        }
    }
}


class SchedulePaginationView(nextcord.ui.View):
    def __init__(self, stage, path, routine_data):
        super().__init__(timeout=120)
        self.stage = stage
        self.path = path
        self.routine_data = routine_data
        self.page = 0
        
    def get_routine_for_day(self, day):
        if isinstance(self.routine_data, dict):
            return self.routine_data.get(day)
        return self.routine_data

    def create_embed(self):
        embed = nextcord.Embed(color=0x3498db)
        embed.set_footer(text=f"Rank: {self.stage} | Type: {self.path} | Page {self.page + 1}/6")

        if self.page == 0:
            embed.title = "📅 Weekly Training Split"
            embed.description = (
                "**Monday:** Arms + Chest\n"
                "**Tuesday:** Arms + Chest\n"
                "**Wednesday:** *Rest & Recovery*\n"
                "**Thursday:** Abs\n"
                "**Friday:** Abs\n"
                "**Saturday:** Leg Day\n"
                "**Sunday:** *Rest & Recovery*"
            )
        elif self.page == 1:
            embed.title = "🏋️‍♀️ Monday & Tuesday: Arms + Chest"
            exercises = self.get_routine_for_day("Monday")
            if isinstance(exercises, list):
                for ex, sets in exercises:
                    embed.add_field(name=f"🧩 {ex}", value=f"└ {sets}", inline=False)
            else:
                embed.description = "🛋️ Rest Day"
        elif self.page == 2: 
            embed.title = "🛋️ Wednesday: Rest"
            embed.description = "Recovery is where the muscle grows. Take it easy today!"
        elif self.page == 3:
            embed.title = "💪 Thursday & Friday: Abs"
            exercises = self.get_routine_for_day("Thursday")
            if isinstance(exercises, list):
                for ex, sets in exercises:
                    embed.add_field(name=f"🧩 {ex}", value=f"└ {sets}", inline=False)
            else:
                embed.description = "🛋️ Rest Day"
        elif self.page == 4:
            embed.title = "🍗 Saturday: Leg Day"
            exercises = self.get_routine_for_day("Saturday")
            if isinstance(exercises, list):
                for ex, sets in exercises:
                    embed.add_field(name=f"🧩 {ex}", value=f"└ {sets}", inline=False)
            else:
                embed.description = "🛋️ Rest Day"
        elif self.page == 5:
            embed.title = "🛋️ Sunday: Rest"
            embed.description = "Prepare your mind and body for the week ahead."

        return embed

    @nextcord.ui.button(label="⬅️", style=nextcord.ButtonStyle.blurple, custom_id="sched_back_btn")
    async def back(self, button, interaction: nextcord.Interaction):
        self.page = max(0, self.page - 1)
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @nextcord.ui.button(label="➡️", style=nextcord.ButtonStyle.blurple, custom_id="sched_forward_btn")
    async def forward(self, button, interaction: nextcord.Interaction):
        self.page = min(5, self.page + 1)
        await interaction.response.edit_message(embed=self.create_embed(), view=self)


class WorkoutFinishView(nextcord.ui.View):
    def __init__(self, stage, count):
        super().__init__(timeout=120)
        self.stage = stage
        self.count = count

    @nextcord.ui.button(label="Complete Workout", style=nextcord.ButtonStyle.green, emoji="✅", custom_id="complete_workout_btn")
    async def finish_callback(self, button, interaction: nextcord.Interaction):
        cog = interaction.client.get_cog("WorkoutCog")
        if cog:
            await cog.users.update_one(
                {"_id": str(interaction.user.id)}, 
                {"$inc": {"workout_count": 1}}, 
                upsert=True
            )
            new_stage, new_count = await cog.get_user_stage(interaction.user.id)
            
            if new_stage != self.stage:
                msg = f"🎊 **LEVEL UP!** You've completed {new_count} workouts and reached the **{new_stage}** stage!"
            else:
                msg = f"💪 Workout logged! ({new_count} total)"
        else:
            msg = "💪 Workout logged!"

        await interaction.response.edit_message(content=msg, embed=None, view=None)


class WorkoutSelectView(nextcord.ui.View):
    def __init__(self, stage, day_name, count):
        super().__init__(timeout=120)
        self.stage = stage
        self.day_name = day_name
        self.count = count

        self.select = nextcord.ui.Select(
            placeholder=f"Rank: {stage} | Day: {day_name}",
            options=[
                nextcord.SelectOption(label="Gym", emoji="🏋️", description="Weights & Machines"),
                nextcord.SelectOption(label="Calisthenics", emoji="🤸", description="Bodyweight mastery")
            ],
            custom_id="startworkout_select_type"
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)

    async def select_callback(self, itx: nextcord.Interaction):
        path = self.select.values[0]
        stage_data = ROUTINES[self.stage][path]
        
        if isinstance(stage_data, dict):
            routine = stage_data.get(self.day_name)
        else:
            routine = stage_data

        embed = nextcord.Embed(title=f"🔥 {self.stage} {path} Routine", color=0x9B59B6)
        embed.set_footer(text=f"Progress: {self.count} workouts completed | Stay disciplined.")

        disclaimer_text = "⚠️ Warning: Leave the ego at the door. Strength comes from consistency and understanding your limits, do not ego lift or overexert yourself. Safety first warriors! 💪"

        if routine == "Rest Day":
            embed.description = "🛋️ **Rest Day!** Recovery is where the muscle grows. See you tomorrow!"
            await itx.response.edit_message(content=f"{disclaimer_text}\n\n{embed.description}" if not embed.description else disclaimer_text, embed=embed, view=None)
            return
        
        if self.stage not in ["Novice Initiate", "Bronze Legionnaire"]:
            embed.add_field(name="🧩 Warm-up", value="└ Stretches (5-10 mins)", inline=False)
        
        for exercise, sets in routine:
            embed.add_field(name=f"🧩 **{exercise}**", value=f"└ {sets}", inline=False)
                    
        finish_view = WorkoutFinishView(self.stage, self.count)
        
        await itx.response.edit_message(content=disclaimer_text, embed=embed, view=finish_view)


class ScheduleSelectView(nextcord.ui.View):
    def __init__(self, stage):
        super().__init__(timeout=120)
        self.stage = stage

        self.select = nextcord.ui.Select(
            placeholder=f"Your Rank: {stage} | Select Type",
            options=[
                nextcord.SelectOption(label="Gym", emoji="🏋️", description="Machines & Weights"),
                nextcord.SelectOption(label="Calisthenics", emoji="🤸", description="Bodyweight Mastery")
            ],
            custom_id="schedule_select_type"
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)

    async def select_callback(self, itx: nextcord.Interaction):
        path = self.select.values[0]
        routine_data = ROUTINES[self.stage][path]
                
        pag_view = SchedulePaginationView(self.stage, path, routine_data)
        await itx.response.edit_message(content=None, embed=pag_view.create_embed(), view=pag_view)


class WorkoutCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if hasattr(bot, "mongo_client") and bot.mongo_client is not None:
            self.cluster = bot.mongo_client
        else:
            self.cluster = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGO_URI"), serverSelectionTimeoutMS=5000)
        self.db = self.cluster["GymBotDB"]
        self.users = self.db["user_stats"]

    async def get_user_stage(self, user_id):
        user = await self.users.find_one({"_id": str(user_id)})
        if not user: return "Novice Initiate", 0
        count = user.get("workout_count", 0)
        
        if count >= 1000: return "Gladiator Maximus", count
        if count >= 810: return "Titan Ascendant", count
        if count >= 600: return "Apex Centurion", count
        if count >= 390: return "Gold Gladiator", count
        if count >= 330: return "Arena Master", count
        if count >= 240: return "Gilded Champion", count
        if count >= 150: return "Steel Centurion", count
        if count >= 120: return "Iron Vanguard", count
        if count >= 60: return "Bronze Legionnaire", count
        return "Novice Initiate", count
    
    @nextcord.slash_command(name="schedule", description="View the weekly training split details")
    async def schedule(self, interaction: nextcord.Interaction):
        if not interaction.response.is_done():
            try:
                await interaction.response.defer(ephemeral=True)
            except Exception:
                pass
        stage, _ = await self.get_user_stage(interaction.user.id)
        
        view = ScheduleSelectView(stage)
        await interaction.followup.send("Select a training path to see your specific routine:", view=view, ephemeral=True)

    @nextcord.slash_command(name="startworkout", description="Access your level-based training routine")
    async def startworkout(self, interaction: nextcord.Interaction):
        if not interaction.response.is_done():
            try:
                await interaction.response.defer(ephemeral=True)
            except Exception:
                pass
        stage, count = await self.get_user_stage(interaction.user.id)
        day_name = datetime.now().strftime("%A")
        
        view = WorkoutSelectView(stage, day_name, count)
        await interaction.followup.send("Choose your focus for today:", view=view, ephemeral=True)

    @nextcord.slash_command(name="levels", description="View the grueling path of discipline, ranks, and workout milestones")
    async def levels(self, interaction: nextcord.Interaction):
        if not interaction.response.is_done():
            try:
                await interaction.response.defer(ephemeral=True)
            except Exception:
                pass

        embed = nextcord.Embed(
            title="⚔️ The Path of Ascendance: Ranks & Milestones",
            description=(
                "*Discipline is forged in repetition. Every session breaks a limit; every milestone claims a new rank.*\n"
                "Here is the strict hierarchy of the arena. Rise through the ranks or remain in the dust.\n\n"
                "• **Level 1:** Novice / Beginner:\n Month 1 = 30 workouts\n\n"
                "• **Level 2:** Bronze Legionnaire:\n Month 2 = 60 workouts\n\n"
                "• **Level 3:** Iron Vanguard:\n Month 4 = 120 workouts\n\n"
                "• **Level 4:** Steel Centurion:\n Month 5 = 150 workouts\n\n"
                "• **Level 5:** Gilded Champion:\n Month 8 = 240 workouts\n\n"
                "• **Level 6:** Arena Master:\n Month 11 = 330 workouts\n\n"
                "• **Level 7:** Gold Gladiator:\n Month 13 = 390 workouts\n\n"
                "• **Level 8:** Apex Centurion:\n Month 20 = 600 workouts\n\n"
                "• **Level 9:** Titan Ascendant:\n Month 27 = 810 workouts\n\n"
                "• **Level 10:** Gladiator Maximus:\n Month 34 = 1000+ workouts"
            ),
            color=0xE67E22
        )
        embed.set_footer(text="Log your daily progress using /startworkout. Glory favors the relentless.")
        
        await interaction.followup.send(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(WorkoutCog(bot))