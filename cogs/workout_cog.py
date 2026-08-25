import nextcord
from nextcord.ext import commands
import motor.motor_asyncio
import os
import re
from datetime import datetime

# ==========================================
# WORKOUT ROUTINES DATABASE
# ==========================================
ROUTINES = {
    "Novice Initiate": {
        "Gym": {
            "Monday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (8 kgs/17 lbs)", "10x3"), ("Hammer curls (8 kgs/17 lbs)", "10x3")],
            "Tuesday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (8 kgs/17 lbs)", "10x3"), ("Hammer curls (8 kgs/17 lbs)", "10x3")],
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
            "Monday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (8 kgs/17 lbs)", "10x2"), ("Hammer curls (8 kgs/17 lbs)", "10x2"), ("Overhead Triceps extension", "10x2"), ("Preacher curls", "10x2")],
            "Tuesday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (8 kgs/17 lbs)", "10x2"), ("Hammer curls (8 kgs/17 lbs)", "10x2"), ("Overhead Triceps extension", "10x2"), ("Preacher curls", "10x2")],
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
            "Monday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (8 kgs/17 lbs)", "10x3"), ("Hammer curls (8 kgs/17 lbs)", "10x3"), ("Overhead Triceps extension", "10x3"), ("Preacher curls", "10x3")],
            "Tuesday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (8 kgs/17 lbs)", "10x3"), ("Hammer curls (8 kgs/17 lbs)", "10x3"), ("Overhead Triceps extension", "10x3"), ("Preacher curls", "10x3")],
            "Wednesday": "Rest Day",
            "Thursday": [("Arm + neck rotation", "10x1"), ("Crunches / Ab crunch machine", "10x3"), ("Seated Cable row", "10x3"), ("Cable lats pulldown", "10x3"), ("Pec dec", "10x3"), ("Bench press (10-15 kgs/22-33 lbs)", "2x5")],
            "Friday": [("Arm + neck rotation", "10x1"), ("Crunches / Ab crunch machine", "10x3"), ("Seated Cable row", "10x3"), ("Cable lats pulldown", "10x3"), ("Pec dec", "10x3"), ("Bench press (10-15 kgs/22-33 lbs)", "2x5")],
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
            "Monday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (8 kgs/17 lbs)", "10x3"), ("Hammer curls (8 kgs/17 lbs)", "10x3"), ("Overhead Triceps extension", "10x3"), ("Preacher curls", "10x3"), ("Overhead press", "10x3")],
            "Tuesday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (8 kgs/17 lbs)", "10x3"), ("Hammer curls (8 kgs/17 lbs)", "10x3"), ("Overhead Triceps extension", "10x3"), ("Preacher curls", "10x3"), ("Overhead press", "10x3")],
            "Wednesday": "Rest Day",
            "Thursday": [("Arm + neck rotation", "10x1"), ("Crunches / Ab crunch machine", "10x3"), ("Seated Cable row", "10x3"), ("Cable lats pulldown", "10x3"), ("Pec dec", "10x3"), ("Bench press (20-40 kgs/44-88 lbs)", "2x5")],
            "Friday": [("Arm + neck rotation", "10x1"), ("Crunches / Ab crunch machine", "10x3"), ("Seated Cable row", "10x3"), ("Cable lats pulldown", "10x3"), ("Pec dec", "10x3"), ("Bench press (20-40 kgs/44-88 lbs)", "2x5")],
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
            "Monday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (8 kgs/17 lbs)", "10x4"), ("Hammer curls (8 kgs/17 lbs)", "10x4"), ("Overhead Triceps extension", "10x4"), ("Preacher curls", "10x4"), ("Overhead press", "10x4")],
            "Tuesday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (8 kgs/17 lbs)", "10x4"), ("Hammer curls (8 kgs/17 lbs)", "10x4"), ("Overhead Triceps extension", "10x4"), ("Preacher curls", "10x4"), ("Overhead press", "10x4")],
            "Wednesday": "Rest Day",
            "Thursday": [("Arm + neck rotation", "10x1"), ("Crunches / Ab crunch machine", "10x4"), ("Seated Cable row", "10x4"), ("Cable lats pulldown", "10x4"), ("Pec dec", "10x4"), ("Bench press (20-40 kgs/44-88 lbs)", "2x5")],
            "Friday": [("Arm + neck rotation", "10x1"), ("Crunches / Ab crunch machine", "10x4"), ("Seated Cable row", "10x4"), ("Cable lats pulldown", "10x4"), ("Pec dec", "10x4"), ("Bench press (20-40 kgs/44-88 lbs)", "2x5")],
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
            "Monday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (8 kgs/17 lbs)", "15x3"), ("Hammer curls (8 kgs/17 lbs)", "15x3"), ("Overhead Triceps extension", "15x3"), ("Preacher curls", "15x3"), ("Overhead press", "15x3")],
            "Tuesday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (8 kgs/17 lbs)", "15x3"), ("Hammer curls (8 kgs/17 lbs)", "15x3"), ("Overhead Triceps extension", "15x3"), ("Preacher curls", "15x3"), ("Overhead press", "15x3")],
            "Wednesday": "Rest Day",
            "Thursday": [("Arm + neck rotation", "10x1"), ("Pull ups", "10x2"), ("Crunches / Ab crunch machine", "15x3"), ("Seated Cable row", "15x3"), ("Cable lats pulldown", "15x3"), ("Pec dec", "15x3"), ("Bench press (20-40 kgs/44-88 lbs)", "2x5")],
            "Friday": [("Arm + neck rotation", "10x1"), ("Pull ups", "10x2"), ("Crunches / Ab crunch machine", "15x3"), ("Seated Cable row", "15x3"), ("Cable lats pulldown", "15x3"), ("Pec dec", "15x3"), ("Bench press (20-40 kgs/44-88 lbs)", "2x5")],
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
            "Monday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (10 kgs/22 lbs)", "10x2"), ("Hammer curls (10 kgs/22 lbs)", "10x2"), ("Overhead Triceps extension", "10x2"), ("Preacher curls", "10x2"), ("Overhead press", "10x2")],
            "Tuesday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (10 kgs/22 lbs)", "10x2"), ("Hammer curls (10 kgs/22 lbs)", "10x2"), ("Overhead Triceps extension", "10x2"), ("Preacher curls", "10x2"), ("Overhead press", "10x2")],
            "Wednesday": "Rest Day",
            "Thursday": [("Arm + neck rotation", "10x1"), ("Pull ups", "10x3"), ("Crunches / Ab crunch machine", "10x2"), ("Seated Cable row", "10x2"), ("Cable lats pulldown", "10x2"), ("Pec dec", "10x2"), ("Bench press (20-40 kgs/44-88 lbs)", "2x5")],
            "Friday": [("Arm + neck rotation", "10x1"), ("Pull ups", "10x3"), ("Crunches / Ab crunch machine", "10x2"), ("Seated Cable row", "10x2"), ("Cable lats pulldown", "10x2"), ("Pec dec", "10x2"), ("Bench press (20-40 kgs/44-88 lbs)", "2x5")],
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
            "Monday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (10 kgs/22 lbs)", "10x2"), ("Hammer curls (10 kgs/22 lbs)", "10x2"), ("Overhead Triceps extension", "10x2"), ("Preacher curls", "10x2"), ("Overhead press", "10x2")],
            "Tuesday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (10 kgs/22 lbs)", "10x2"), ("Hammer curls (10 kgs/22 lbs)", "10x2"), ("Overhead Triceps extension", "10x2"), ("Preacher curls", "10x2"), ("Overhead press", "10x2")],
            "Wednesday": "Rest Day",
            "Thursday": [("Arm + neck rotation", "10x1"), ("Pull ups", "10x3"), ("Crunches / Ab crunch machine", "10x2"), ("Seated Cable row", "10x2"), ("Cable lats pulldown", "10x2"), ("Pec dec", "10x2"), ("Bench press (20-40 kgs/44-88 lbs)", "2x5")],
            "Friday": [("Arm + neck rotation", "10x1"), ("Pull ups", "10x3"), ("Crunches / Ab crunch machine", "10x2"), ("Seated Cable row", "10x2"), ("Cable lats pulldown", "10x2"), ("Pec dec", "10x2"), ("Bench press (20-40 kgs/44-88 lbs)", "2x5")],
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
            "Monday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (10 kgs/22 lbs)", "10x2"), ("Hammer curls (10 kgs/22 lbs)", "10x2"), ("Overhead Triceps extension", "10x2"), ("Preacher curls", "10x2"), ("Overhead press", "10x2")],
            "Tuesday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (10 kgs/22 lbs)", "10x2"), ("Hammer curls (10 kgs/22 lbs)", "10x2"), ("Overhead Triceps extension", "10x2"), ("Preacher curls", "10x2"), ("Overhead press", "10x2")],
            "Wednesday": "Rest Day",
            "Thursday": [("Arm + neck rotation", "10x1"), ("Pull ups", "10x3"), ("Crunches / Ab crunch machine", "10x2"), ("Seated Cable row", "10x2"), ("Cable lats pulldown", "10x2"), ("Pec dec", "10x2"), ("Bench press (20-40 kgs/44-88 lbs)", "2x5")],
            "Friday": [("Arm + neck rotation", "10x1"), ("Pull ups", "10x3"), ("Crunches / Ab crunch machine", "10x2"), ("Seated Cable row", "10x2"), ("Cable lats pulldown", "10x2"), ("Pec dec", "10x2"), ("Bench press (20-40 kgs/44-88 lbs)", "2x5")],
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
            "Monday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (10 kgs/22 lbs)", "10x2"), ("Hammer curls (10 kgs/22 lbs)", "10x2"), ("Overhead Triceps extension", "10x2"), ("Preacher curls", "10x2"), ("Overhead press", "10x2")],
            "Tuesday": [("Arm + neck rotation", "10x1"), ("Dumbbell bicep curls (10 kgs/22 lbs)", "10x2"), ("Hammer curls (10 kgs/22 lbs)", "10x2"), ("Overhead Triceps extension", "10x2"), ("Preacher curls", "10x2"), ("Overhead press", "10x2")],
            "Wednesday": "Rest Day",
            "Thursday": [("Arm + neck rotation", "10x1"), ("Pull ups", "10x3"), ("Crunches / Ab crunch machine", "10x2"), ("Seated Cable row", "10x2"), ("Cable lats pulldown", "10x2"), ("Pec dec", "10x2"), ("Bench press (20-40 kgs/44-88 lbs)", "2x5")],
            "Friday": [("Arm + neck rotation", "10x1"), ("Pull ups", "10x3"), ("Crunches / Ab crunch machine", "10x2"), ("Seated Cable row", "10x2"), ("Cable lats pulldown", "10x2"), ("Pec dec", "10x2"), ("Bench press (20-40 kgs/44-88 lbs)", "2x5")],
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


# ==========================================
# EXERCISE FORM & DEMONSTRATION GUIDES
# ==========================================
EXERCISE_GUIDES = {
    "Arm + neck rotation": {
        "title": "Arm & Neck Rotations",
        "category": "Warm-up / Mobility",
        "muscles": "Rotator Cuff, Deltoids, Trapezius, Cervical Spine",
        "form": (
            "1. **Arm Rotations:** Stand upright with arms extended to sides. Rotate arms in smooth, controlled circles forward for 10 reps, then reverse backward for 10 reps.\n"
            "2. **Neck Rotations:** Stand relaxed and slowly roll head in smooth clockwise circles, then reverse counterclockwise."
        ),
        "tips": "• Keep movements smooth and continuous.\n• Keep shoulders relaxed and down away from your ears.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0844-VLYXo8S.gif"
    },
    "Dumbbell bicep curls": {
        "title": "Dumbbell Bicep Curls",
        "category": "Gym / Arms",
        "muscles": "Biceps Brachii, Brachialis, Forearms",
        "form": (
            "1. Stand with feet shoulder-width apart holding dumbbells at sides with palms facing forward.\n"
            "2. Keep elbows tucked close to your torso.\n"
            "3. Exhale and curl the weights up towards shoulders by contracting biceps.\n"
            "4. Squeeze biceps at peak for 1 second, then lower with control (2-3 seconds)."
        ),
        "tips": "• Do not swing your body or use momentum from your lower back.\n• Keep wrists straight and supinating (palms facing up) at the top.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0294-NbVPDMW.gif"
    },
    "Hammer curls": {
        "title": "Dumbbell Hammer Curls",
        "category": "Gym / Arms",
        "muscles": "Brachioradialis (Forearms), Brachialis, Biceps",
        "form": (
            "1. Stand upright holding dumbbells with a neutral grip (palms facing inward toward each other).\n"
            "2. Keeping upper arms fixed to sides, bend at elbows to curl dumbbells upward.\n"
            "3. Lift until top of dumbbells are near shoulder height.\n"
            "4. Pause and squeeze forearms and biceps, then lower with strict control."
        ),
        "tips": "• Keep elbows pinned to your ribs; do not let them drift forward.\n• Maintain a neutral wrist angle (thumbs pointing up) throughout.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0313-slDvUAU.gif"
    },
    "Overhead Triceps extension": {
        "title": "Overhead Triceps Extension",
        "category": "Gym / Arms",
        "muscles": "Triceps Brachii (Long Head)",
        "form": (
            "1. Stand or sit upright holding dumbbell overhead with both hands.\n"
            "2. Keep upper arms vertical and close to ears, elbows pointing forward.\n"
            "3. Inhale and slowly lower weight behind head until forearms reach ~90 degrees.\n"
            "4. Exhale and push weight back up by extending triceps until arms are fully locked out."
        ),
        "tips": "• Avoid flaring elbows out to sides.\n• Brace core so you don't over-arch lower back.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0430-PdmaD0N.gif"
    },
    "Preacher curls": {
        "title": "Preacher Curls",
        "category": "Gym / Arms",
        "muscles": "Biceps Brachii (Short Head Isolation)",
        "form": (
            "1. Sit at preacher bench with upper arms resting firmly against slanted pad.\n"
            "2. Hold EZ-curl bar or barbell with both hands using an underhand grip, arms extended.\n"
            "3. Curl weight upward toward chin with both arms while keeping armpits snug against top of pad.\n"
            "4. Squeeze biceps at peak, then lower with control until arms are almost fully extended."
        ),
        "tips": "• Use both hands on the bar to ensure balanced resistance and prevent elbow strain.\n• Do not lift torso or armpits off pad.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0070-qOgPVf6.gif"
    },
    "Overhead press": {
        "title": "Overhead Press (Shoulder Press)",
        "category": "Gym / Shoulders",
        "muscles": "Anterior & Lateral Deltoids, Triceps, Upper Chest, Core",
        "form": (
            "1. Stand feet hip-width apart holding weights at shoulder height with palms facing forward.\n"
            "2. Brace abs and squeeze glutes for a solid base.\n"
            "3. Press weights straight overhead until arms are fully extended.\n"
            "4. Lower weight under control back to shoulder height."
        ),
        "tips": "• Avoid leaning backward or hyperextending lumbar spine.\n• Keep head neutral and push weight vertically in a straight path.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0426-A6wtbuL.gif"
    },
    "Crunches": {
        "title": "Abdominal Crunches",
        "category": "Core",
        "muscles": "Rectus Abdominis (Upper Abs)",
        "form": (
            "1. Lie on back with knees bent and feet flat on floor, hip-width apart.\n"
            "2. Place fingertips lightly behind ears or cross hands over chest.\n"
            "3. Exhale and contract abdominals, lifting shoulder blades 2-3 inches off ground.\n"
            "4. Squeeze core hard at top for 1 second, then slowly lower back down."
        ),
        "tips": "• Do NOT pull on neck or tuck chin into chest.\n• Keep lower back pressed into floor.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0267-kjJ3VoQ.gif"
    },
    "Crunches / Ab crunch machine": {
        "title": "Crunches / Ab Crunch Machine",
        "category": "Gym / Core",
        "muscles": "Rectus Abdominis",
        "form": (
            "1. **Floor Crunch:** Lie on mat with knees bent; curl shoulders up toward knees using abdominal contraction.\n"
            "2. **Machine Crunch:** Sit securely in machine, feet hooked under pads and hands holding handles.\n"
            "3. Flex forward at waist by squeezing abs to bring elbows towards knees.\n"
            "4. Pause for peak contraction, then slowly return without letting weight stack slam."
        ),
        "tips": "• Focus on curling ribcage toward pelvis, not pushing with arms.\n• Keep breathing rhythmic—exhale as you crunch.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/1452-Wgaz7pm.gif"
    },
    "Seated Cable row": {
        "title": "Seated Cable Row",
        "category": "Gym / Back",
        "muscles": "Latissimus Dorsi, Rhomboids, Middle Traps, Biceps",
        "form": (
            "1. Sit on bench with knees slightly bent and feet placed on footrests.\n"
            "2. Grasp V-bar handle with neutral grip and sit upright with chest lifted and back straight.\n"
            "3. Pull handle toward lower abdomen while driving elbows back and squeezing shoulder blades.\n"
            "4. Hold for 1 second, then slowly extend arms back to starting position."
        ),
        "tips": "• Avoid excessive rocking or swinging back and forth.\n• Keep chest proud and spine neutral at all times.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0861-fUBheHs.gif"
    },
    "Cable lats pulldown": {
        "title": "Cable Lat Pulldown",
        "category": "Gym / Back",
        "muscles": "Latissimus Dorsi, Teres Major, Biceps, Rear Delts",
        "form": (
            "1. Sit at pulldown machine and adjust thigh pad snugly over legs.\n"
            "2. Grasp wide bar with overhand grip slightly wider than shoulder-width.\n"
            "3. Lean back slightly (~10-15 degrees), pull bar down to upper chest by driving elbows down.\n"
            "4. Squeeze lats at bottom, then slowly return bar under control."
        ),
        "tips": "• Pull with back muscles and elbows, not just forearms.\n• Never pull bar behind neck to protect cervical spine.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0150-eYnzaCm.gif"
    },
    "Pec dec": {
        "title": "Pec Dec (Chest Fly Machine)",
        "category": "Gym / Chest",
        "muscles": "Pectoralis Major (Sternal Head)",
        "form": (
            "1. Adjust seat height so handles or arm pads align directly with middle of chest.\n"
            "2. Place forearms/hands on pads and press upper back flat against backrest.\n"
            "3. Inhale, then exhale as you bring handles together in front of chest in an arc motion.\n"
            "4. Squeeze chest firmly at center for 1 second, then slowly open arms back to starting stretch."
        ),
        "tips": "• Maintain a soft bend in elbows; don't lock or bend them excessively.\n• Don't let shoulders roll forward at peak squeeze.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0596-v3xmPAR.gif"
    },
    "Bench press": {
        "title": "Barbell / Dumbbell Bench Press",
        "category": "Gym / Chest",
        "muscles": "Pectoralis Major, Anterior Deltoids, Triceps",
        "form": (
            "1. Lie flat on bench with eyes directly under bar and feet planted firmly on floor.\n"
            "2. Grip bar slightly wider than shoulder-width with thumbs wrapped around.\n"
            "3. Unrack bar, lower with control to mid-chest while tucking elbows at roughly 45-degree angle.\n"
            "4. Touch chest lightly, then press forcefully back up to lockout above chest."
        ),
        "tips": "• Retract shoulder blades and keep butt glued to bench.\n• Avoid flaring elbows straight out at 90 degrees.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0025-EIeI8Vf.gif"
    },
    "Bodyweight squats": {
        "title": "Bodyweight Squats",
        "category": "Calisthenics / Legs",
        "muscles": "Quadriceps, Gluteus Maximus, Hamstrings, Calves, Core",
        "form": (
            "1. Stand with feet slightly wider than shoulder-width, toes angled 15-30 degrees outward.\n"
            "2. Keep chest high, gaze forward, and hands clasped in front of chest.\n"
            "3. Hinge hips back and bend knees, lowering body until thighs are parallel to floor.\n"
            "4. Drive through heels to return to standing, squeezing glutes at top."
        ),
        "tips": "• Keep knees tracking in line with toes—don't let them cave inward.\n• Keep heels grounded throughout entire movement.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0750-Gu2rNJd.gif"
    },
    "Weighted squats": {
        "title": "Weighted Squats (Barbell / Dumbbell)",
        "category": "Gym / Legs",
        "muscles": "Quadriceps, Glutes, Hamstrings, Spinal Erectors, Core",
        "form": (
            "1. Position barbell on upper traps (or hold dumbbells at sides/goblet position).\n"
            "2. Stand feet shoulder-width apart, brace core tightly.\n"
            "3. Break at hips and knees simultaneously, lowering down until thighs are parallel to ground.\n"
            "4. Push floor away through heels to stand up powerfully."
        ),
        "tips": "• Maintain neutral spine; do not round lower back.\n• Take a deep breath into belly and brace before descending.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0043-qXTaZnJ.gif"
    },
    "Leg press": {
        "title": "Leg Press",
        "category": "Gym / Legs",
        "muscles": "Quadriceps, Glutes, Hamstrings",
        "form": (
            "1. Sit in machine with back and head resting comfortably against padded support.\n"
            "2. Place feet shoulder-width apart on platform.\n"
            "3. Disengage safety bars and slowly lower sled until knees form 90-degree angle.\n"
            "4. Press back up through heels to full extension (do NOT lock knees)."
        ),
        "tips": "• Never fully lock out knees at top of press.\n• Ensure lower back and glutes remain pressed flat against seat.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0739-10Z2DXU.gif"
    },
    "Incline leg press": {
        "title": "45° Incline Leg Press",
        "category": "Gym / Legs",
        "muscles": "Quadriceps, Glutes, Hamstrings",
        "form": (
            "1. Sit securely into 45-degree leg press with lower back firmly against pad.\n"
            "2. Place feet in center of plate, shoulder-width apart.\n"
            "3. Inhale and lower weight under strict control until thighs approach 90 degrees with knees.\n"
            "4. Exhale and drive through heels to press platform back up."
        ),
        "tips": "• Stop descending if pelvis or lower back rolls off pad.\n• Keep knees aligned with feet.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0739-10Z2DXU.gif"
    },
    "Leg extension": {
        "title": "Seated Leg Extension",
        "category": "Gym / Legs",
        "muscles": "Quadriceps (Isolation)",
        "form": (
            "1. Sit on machine with knees aligned with pivot point and shin pad resting above ankles.\n"
            "2. Grip side handles firmly to keep hips anchored.\n"
            "3. Extend legs forward until fully straight, contracting quads hard at top.\n"
            "4. Pause for 1 second, then lower weight slowly back down."
        ),
        "tips": "• Do not use jerky momentum or swing hips off seat.\n• Control weight all the way down for maximum hypertrophy.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0585-my33uHU.gif"
    },
    "Seated leg curl": {
        "title": "Seated Leg Curl",
        "category": "Gym / Legs",
        "muscles": "Hamstrings (Biceps Femoris, Semitendinosus)",
        "form": (
            "1. Sit with back against pad, thigh brace adjusted snugly on top of thighs, lever pad behind lower calves.\n"
            "2. Grasp handles and keep torso firmly pressed against back support.\n"
            "3. Flex knees to curl lever down and backward toward seat.\n"
            "4. Squeeze hamstrings tight at peak flexion, then return slowly to starting position."
        ),
        "tips": "• Keep toes pointed straight ahead or slightly flexed.\n• Avoid arching lower back during contraction.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0599-Zg3XY7P.gif"
    },
    "Treadmill": {
        "title": "Treadmill Cardio / Jogging",
        "category": "Cardio / Conditioning",
        "muscles": "Cardiovascular System, Calves, Quads, Hamstrings",
        "form": (
            "1. Step onto treadmill belt, attach safety clip, start at brisk walking pace.\n"
            "2. Keep shoulders relaxed, chest open, arms bent at 90 degrees swinging rhythmically.\n"
            "3. Land softly on midfoot with slight forward lean from ankles.\n"
            "4. Maintain steady, rhythmic breathing."
        ),
        "tips": "• Avoid gripping handrails while running.\n• Look straight ahead, not down at feet.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/3666-rjiM4L3.gif"
    },
    "Running": {
        "title": "Outdoor / Track Running",
        "category": "Cardio / Conditioning",
        "muscles": "Cardiovascular System, Glutes, Quads, Hamstrings, Calves",
        "form": (
            "1. Maintain upright posture with slight whole-body forward lean.\n"
            "2. Strike ground beneath center of gravity with midfoot.\n"
            "3. Drive knees forward and cycle feet smoothly with cadence around 160-180 steps/min.\n"
            "4. Keep hands relaxed and shoulders away from ears."
        ),
        "tips": "• Don't overstride (landing too far ahead of hips).\n• Pace yourself according to session duration.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0685-oLrKqDH.gif"
    },
    "Push Ups": {
        "title": "Standard Push-Ups",
        "category": "Calisthenics / Chest & Triceps",
        "muscles": "Pectoralis Major, Anterior Deltoids, Triceps, Core",
        "form": (
            "1. Place hands shoulder-width apart on floor, body in rigid high plank.\n"
            "2. Squeeze glutes and brace core so body forms straight line from heels to head.\n"
            "3. Lower chest until 1-2 inches above floor, keeping elbows angled at 45 degrees.\n"
            "4. Push through palms to lock out arms at top."
        ),
        "tips": "• Don't let lower back or hips sag.\n• Keep neck neutral by gazing a few inches ahead of hands.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0662-I4hDWkc.gif"
    },
    "Elevated push ups": {
        "title": "Elevated / Incline Push-Ups",
        "category": "Calisthenics / Chest",
        "muscles": "Lower Pectoralis, Anterior Deltoids, Triceps",
        "form": (
            "1. Place hands on elevated surface (bench or step) shoulder-width apart.\n"
            "2. Step feet back so body forms straight incline plank.\n"
            "3. Lower chest toward edge of elevated surface.\n"
            "4. Press through palms to return to starting position."
        ),
        "tips": "• Great progression for building chest pushing strength.\n• Keep core tight and elbows tucked at 45 degrees.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0493-B1EVP9F.gif"
    },
    "Inclined push ups": {
        "title": "Incline / Decline Push-Ups",
        "category": "Calisthenics / Upper Body",
        "muscles": "Pectoralis Major, Clavicular Head, Triceps, Deltoids",
        "form": (
            "1. Place feet on bench or elevated platform and hands on floor.\n"
            "2. Lower chest with control until nearly touching floor.\n"
            "3. Press forcefully back to starting lockout."
        ),
        "tips": "• Maintain strict straight-line body tension from heels to head.\n• Avoid letting hips drop or piking in air.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0493-B1EVP9F.gif"
    },
    "Hindu push ups": {
        "title": "Hindu Push-Ups (Dand)",
        "category": "Calisthenics / Full Body Push",
        "muscles": "Shoulders, Chest, Triceps, Lower Back Flexibility",
        "form": (
            "1. Start in downward dog pose with hips high in air.\n"
            "2. Bend elbows and swoop chest down toward floor between hands.\n"
            "3. Glide forward and arch torso upward into upward dog pose.\n"
            "4. Push hips back up and return smoothly to starting downward dog."
        ),
        "tips": "• Perform motion in one fluid, continuous scoop.\n• Great for shoulder mobility and core conditioning.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/3662-XPUDTt7.gif"
    },
    "Plank": {
        "title": "Forearm Plank",
        "category": "Core / Isometric",
        "muscles": "Transverse Abdominis, Rectus Abdominis, Glutes, Deltoids",
        "form": (
            "1. Rest on forearms with elbows stacked directly beneath shoulders.\n"
            "2. Extend legs behind with toes planted, forming straight line from head to heels.\n"
            "3. Engage abs tightly; squeeze glutes and quads firmly.\n"
            "4. Hold position statically while maintaining steady, deep breathing."
        ),
        "tips": "• Do not let hips sag toward floor or pike upward.\n• Keep neck neutral by looking at floor between forearms.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0464-CosupLu.gif"
    },
    "Bodyweight lunges": {
        "title": "Bodyweight Walking / Forward Lunges",
        "category": "Calisthenics / Legs",
        "muscles": "Quadriceps, Gluteus Maximus, Hamstrings, Core Balance",
        "form": (
            "1. Stand tall with feet hip-width apart and hands on hips.\n"
            "2. Take controlled step forward with one leg and lower hips until both knees bend at ~90 degrees.\n"
            "3. Back knee hovers 1 inch above floor.\n"
            "4. Drive through front heel to step back to starting position."
        ),
        "tips": "• Ensure front knee stays stacked above ankle, not past toes.\n• Keep torso upright—avoid leaning forward.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/1460-IZVHb27.gif"
    },
    "Chair assisted dips": {
        "title": "Bench / Chair Dips",
        "category": "Calisthenics / Triceps",
        "muscles": "Triceps Brachii, Anterior Deltoids, Lower Chest",
        "form": (
            "1. Sit on edge of sturdy chair or bench, hands gripping edge right next to hips.\n"
            "2. Place feet flat on the floor in front with knees bent at 90 degrees.\n"
            "3. Lower hips by bending elbows until upper arms are parallel to the floor.\n"
            "4. Press through palms to straighten arms back to starting position."
        ),
        "tips": "• Keep back close to chair/bench throughout to prevent shoulder strain.\n• Keep feet grounded on the floor (not elevated) for assisted dip variation.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0129-RrLske5.gif"
    },
    "Pull ups": {
        "title": "Overhand Pull-Ups",
        "category": "Calisthenics / Upper Body Pull",
        "muscles": "Latissimus Dorsi, Biceps, Upper Back, Forearms, Core",
        "form": (
            "1. Hang from pull-up bar with overhand grip slightly wider than shoulder-width, legs completely straight.\n"
            "2. Start from a dead hang with fully extended arms and active scapulae.\n"
            "3. Pull chest toward bar in a strict vertical line until chin clears bar.\n"
            "4. Lower with complete control back down to full straight-arm dead hang."
        ),
        "tips": "• Maintain strict body line with straight legs—no swinging, kipping, or bending knees.\n• Focus on driving elbows down and back to engage lats.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/1429-Qqi7bko.gif"
    },
    "Chin ups": {
        "title": "Underhand Chin-Ups",
        "category": "Calisthenics / Arms & Back",
        "muscles": "Biceps Brachii, Latissimus Dorsi, Teres Major, Core",
        "form": (
            "1. Hang from bar with underhand grip (palms facing you), shoulder-width apart.\n"
            "2. Engage back and biceps, pulling upward until chin is over bar.\n"
            "3. Keep elbows close to body and chest open.\n"
            "4. Lower smoothly all the way down to full extension dead hang."
        ),
        "tips": "• Squeeze biceps hard at top of every rep.\n• Avoid rounding shoulders forward at top.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/1326-T2mxWqc.gif"
    },
    "Twist crunches": {
        "title": "Twist / Bicycle Crunches",
        "category": "Core / Obliques",
        "muscles": "Internal & External Obliques, Rectus Abdominis",
        "form": (
            "1. Lie on back with hands behind head and knees bent in tabletop position.\n"
            "2. Lift shoulder blades and twist right elbow across to touch left knee while extending right leg straight.\n"
            "3. Switch sides smoothly, bringing left elbow to right knee while extending left leg.\n"
            "4. Keep motion controlled and continuous like pedaling."
        ),
        "tips": "• Rotate through ribcage and obliques, not just pulling elbow.\n• Keep lower back firmly anchored to floor.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0262-rbu5UUb.gif"
    },
    "Jumping": {
        "title": "Jumping Jacks / Vertical Jumps",
        "category": "Cardio / Conditioning",
        "muscles": "Calves, Quads, Deltoids, Cardiovascular System",
        "form": (
            "1. Stand with feet together and arms at sides.\n"
            "2. Jump lightly, spreading feet beyond shoulder-width while sweeping arms overhead.\n"
            "3. Land softly on balls of feet and immediately jump back to starting stance.\n"
            "4. Keep a brisk, steady rhythm."
        ),
        "tips": "• Keep knees soft on every landing to absorb impact safely.\n• Breathe rhythmically throughout.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/3224-1g5bPpA.gif"
    },
    "Frog stand with parallettes": {
        "title": "Frog Stand / Crow Pose on Parallettes",
        "category": "Calisthenics / Skill & Balance",
        "muscles": "Wrists, Forearms, Shoulders, Core Balance",
        "form": (
            "1. Place parallettes on floor shoulder-width apart and grip firmly.\n"
            "2. Squat down and place inner knees resting against outside of triceps/elbows.\n"
            "3. Lean forward slowly until feet gently lift off floor.\n"
            "4. Balance bodyweight on hands, engaging core and shoulders."
        ),
        "tips": "• Look slightly forward, not straight down, to prevent tipping over.\n• Grip parallettes tightly and push ground away.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/3301-rQhGcin.gif"
    },
    "Tuck front lever hold": {
        "title": "Tuck Front Lever Hold",
        "category": "Calisthenics / Advanced Pull",
        "muscles": "Latissimus Dorsi, Rhomboids, Rear Delts, Abdominals",
        "form": (
            "1. Hang from pull-up bar with overhand grip.\n"
            "2. Retract scapulae, lock arms straight, and pull torso up into horizontal plane.\n"
            "3. Pull knees tightly into chest to shorten lever arm.\n"
            "4. Hold torso completely parallel to ground for target time."
        ),
        "tips": "• Keep arms 100% straight; do not bend at elbows.\n• Drive hands down against bar like a straight-arm pulldown.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/3296-PkCN2lv.gif"
    },
    "advance tuck front lever hold": {
        "title": "Advanced Tuck Front Lever Hold",
        "category": "Calisthenics / Advanced Pull",
        "muscles": "Latissimus Dorsi, Core, Rear Delts, Scapular Retractors",
        "form": (
            "1. From straight-arm hang on bar, pull torso into horizontal alignment with floor.\n"
            "2. Move knees away from chest until thighs are at 90-degree angle with torso.\n"
            "3. Keep back flat and arms locked out straight.\n"
            "4. Hold isometric position with maximum lat tension."
        ),
        "tips": "• Keep hips in line with shoulders—don't let hips sag.\n• Squeeze glutes and keep core locked tight.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/3296-PkCN2lv.gif"
    },
    "Negative front lever raises": {
        "title": "Negative Front Lever Raises (Eccentrics)",
        "category": "Calisthenics / Advanced Pull",
        "muscles": "Latissimus Dorsi, Rear Deltoids, Core, Grip",
        "form": (
            "1. Invert body on pull-up bar so feet point straight up toward ceiling.\n"
            "2. Lock arms straight and engage back.\n"
            "3. Slowly lower entire straight body down in horizontal line toward floor (3-5 seconds).\n"
            "4. Resist gravity all the way through parallel before lowering to dead hang."
        ),
        "tips": "• Make eccentric lowering as slow and controlled as possible.\n• Keep body in rigid line without arching or piking.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/3296-PkCN2lv.gif"
    },
    "L-sit": {
        "title": "L-Sit Hold (Parallettes / Floor)",
        "category": "Calisthenics / Isometric Core",
        "muscles": "Rectus Abdominis, Hip Flexors, Triceps, Anterior Deltoids",
        "form": (
            "1. Sit on floor or between parallettes with hands pressing firmly beside hips.\n"
            "2. Depress shoulders (push down into floor/bars to create neck space).\n"
            "3. Lift hips and extend legs straight out in front, parallel to ground.\n"
            "4. Point toes, squeeze quads, and hold 90-degree 'L' shape."
        ),
        "tips": "• Don't let shoulders shrug up to ears.\n• If full L-sit is difficult, start with one leg extended or bent-knee tuck.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/3419-UpWmA5E.gif"
    }
}


def find_exercise_guide(exercise_raw_name: str):
    """
    Smart matcher to find the proper form guide, instructions, and image
    for any exercise string from routines.
    """
    cleaned = re.sub(r"\(.*?\)", "", exercise_raw_name).strip()
    
    # 1. Exact match with cleaned name
    for key, data in EXERCISE_GUIDES.items():
        if key.lower() == cleaned.lower():
            return data
            
    # 2. Key contained in cleaned name or vice versa
    for key, data in EXERCISE_GUIDES.items():
        if key.lower() in cleaned.lower() or cleaned.lower() in key.lower():
            return data

    # 3. Word overlap match
    cleaned_words = set(cleaned.lower().split())
    best_match = None
    best_score = 0
    for key, data in EXERCISE_GUIDES.items():
        key_words = set(key.lower().split())
        score = len(cleaned_words.intersection(key_words))
        if score > best_score:
            best_score = score
            best_match = data

    if best_match and best_score >= 1:
        return best_match

    # Fallback default
    return {
        "title": cleaned.title(),
        "category": "General Exercise",
        "muscles": "Target Muscle Groups",
        "form": "1. Position yourself with proper upright posture and neutral spine.\n2. Perform the movement with controlled tempo and steady breathing.\n3. Complete the prescribed sets and reps with proper form.",
        "tips": "• Maintain strict control on both the lifting and lowering phases.\n• Never sacrifice form for heavier weights.",
        "image_url": "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0844-VLYXo8S.gif"
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

        await interaction.response.edit_message(content=msg, embed=None, view=None, attachments=[])


def get_workout_file():
    paths = [
        "./assets/workout_img.jpg",
        "assets/workout_img.jpg",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "workout_img.jpg")
    ]
    for p in paths:
        if os.path.exists(p):
            return nextcord.File(fp=p, filename="workout_img.jpg")
    return None


class ActiveWorkoutView(nextcord.ui.View):
    """
    Interactive session view for /startworkout that displays the workout overview,
    allows users to inspect exercise form guides with visual demonstration images and tips,
    and log workout completion.
    """
    def __init__(self, stage, path, day_name, routine, count):
        super().__init__(timeout=300)
        self.stage = stage
        self.path = path
        self.day_name = day_name
        self.routine = routine
        self.count = count
        self.current_exercise = None  # None = overview, string = exercise name
        self.disclaimer_text = "⚠️ Warning: Leave the ego at the door. Strength comes from consistency and understanding your limits, do not ego lift or overexert yourself. Safety first warriors! 💪"
        self.build_components()

    def build_components(self):
        self.clear_items()

        # 1. Exercise Form & Image Guide Dropdown
        if isinstance(self.routine, list) and len(self.routine) > 0:
            options = []
            for ex, sets in self.routine:
                guide_info = find_exercise_guide(ex)
                options.append(
                    nextcord.SelectOption(
                        label=guide_info.get("title", ex)[:100],
                        value=ex,
                        description=f"Target: {sets}"[:100],
                        emoji="📖"
                    )
                )
            guide_select = nextcord.ui.Select(
                placeholder="📖 View Exercise Form & Image Guide...",
                options=options,
                custom_id="active_workout_guide_select",
                row=0
            )
            guide_select.callback = self.guide_select_callback
            self.add_item(guide_select)

        # 2. Navigation Button (Back to Routine Overview when inspecting an exercise)
        if self.current_exercise is not None:
            back_btn = nextcord.ui.Button(
                label="Back to Routine Overview",
                style=nextcord.ButtonStyle.blurple,
                emoji="⬅️",
                custom_id="active_workout_back_btn",
                row=1
            )
            back_btn.callback = self.back_overview_callback
            self.add_item(back_btn)

        # 3. Complete Workout Button
        finish_btn = nextcord.ui.Button(
            label="Complete Workout",
            style=nextcord.ButtonStyle.green,
            emoji="✅",
            custom_id="active_workout_finish_btn",
            row=1
        )
        finish_btn.callback = self.finish_callback
        self.add_item(finish_btn)

    def create_routine_embed(self):
        embed = nextcord.Embed(title=f"🔥 {self.stage} {self.path} Routine", color=0x9B59B6)
        embed.set_footer(text=f"Progress: {self.count} workouts completed | Select an exercise below to view its proper form & image.")

        if self.stage not in ["Novice Initiate", "Bronze Legionnaire"]:
            embed.add_field(name="🧩 Warm-up", value="└ Stretches (5-10 mins)", inline=False)

        for exercise, sets in self.routine:
            embed.add_field(name=f"🧩 **{exercise}**", value=f"└ {sets}", inline=False)

        file = get_workout_file()
        if file:
            embed.set_thumbnail(url="attachment://workout_img.jpg")

        return embed

    def create_exercise_guide_embed(self, raw_exercise_name):
        guide = find_exercise_guide(raw_exercise_name)
        
        # Find target sets from current routine
        target_sets = None
        for ex, sets in self.routine:
            if ex == raw_exercise_name:
                target_sets = sets
                break

        embed = nextcord.Embed(
            title=f"📖 Exercise Guide: {guide['title']}",
            color=0x3498DB
        )
        embed.add_field(name="🏷️ Category", value=f"└ {guide.get('category', 'Exercise')}", inline=True)
        embed.add_field(name="🎯 Target Muscles", value=f"└ {guide['muscles']}", inline=True)
        if target_sets:
            embed.add_field(name="🏋️ Today's Target", value=f"└ **{target_sets}**", inline=True)

        embed.add_field(name="📋 How to Perform (Proper Form)", value=guide["form"], inline=False)
        embed.add_field(name="💡 Pro Tips & Common Mistakes", value=guide["tips"], inline=False)

        if guide.get("image_url"):
            embed.set_image(url=guide["image_url"])

        embed.set_footer(text=f"Rank: {self.stage} | Train with strict form. Quality over quantity.")
        return embed

    async def guide_select_callback(self, interaction: nextcord.Interaction):
        selected_ex = interaction.data["values"][0]
        self.current_exercise = selected_ex
        self.build_components()
        guide_embed = self.create_exercise_guide_embed(selected_ex)
        await interaction.response.edit_message(content=self.disclaimer_text, embed=guide_embed, view=self, attachments=[])

    async def back_overview_callback(self, interaction: nextcord.Interaction):
        self.current_exercise = None
        self.build_components()
        routine_embed = self.create_routine_embed()
        
        file = get_workout_file()
        kwargs = {}
        if file:
            kwargs["file"] = file

        await interaction.response.edit_message(content=self.disclaimer_text, embed=routine_embed, view=self, **kwargs)

    async def finish_callback(self, interaction: nextcord.Interaction):
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

        await interaction.response.edit_message(content=msg, embed=None, view=None, attachments=[])


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

        disclaimer_text = "⚠️ Warning: Leave the ego at the door. Strength comes from consistency and understanding your limits, do not ego lift or overexert yourself. Safety first warriors! 💪"

        if routine == "Rest Day":
            embed = nextcord.Embed(title=f"🔥 {self.stage} {path} Routine", color=0x9B59B6)
            embed.set_footer(text=f"Progress: {self.count} workouts completed | Stay disciplined.")
            embed.description = "🛋️ **Rest Day!** Recovery is where the muscle grows. See you tomorrow!"
            file = get_workout_file()
            kwargs = {}
            if file:
                kwargs["file"] = file
                embed.set_thumbnail(url="attachment://workout_img.jpg")
            await itx.response.edit_message(content=disclaimer_text, embed=embed, view=None, **kwargs)
            return

        active_view = ActiveWorkoutView(self.stage, path, self.day_name, routine, self.count)
        routine_embed = active_view.create_routine_embed()

        file = get_workout_file()
        kwargs = {}
        if file:
            kwargs["file"] = file

        await itx.response.edit_message(content=disclaimer_text, embed=routine_embed, view=active_view, **kwargs)


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


class ConfirmResetView(nextcord.ui.View):
    def __init__(self, cog, owner_id):
        super().__init__(timeout=60)
        self.cog = cog
        self.owner_id = owner_id

    @nextcord.ui.button(label="Yes, Reset My Progress", style=nextcord.ButtonStyle.danger, emoji="⚠️", custom_id="confirm_reset_btn")
    async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id != self.owner_id:
            return await interaction.response.send_message("This confirmation isn't for you!", ephemeral=True)

        await self.cog.users.update_one(
            {"_id": str(self.owner_id)},
            {"$set": {"workout_count": 0}},
            upsert=True
        )

        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(
            content="✅ **Your workout count has been reset to 0.** You're back at **Level 1: Novice / Beginner**. Time to start climbing again! 💪",
            view=self
        )

    @nextcord.ui.button(label="Cancel", style=nextcord.ButtonStyle.secondary, custom_id="cancel_reset_btn")
    async def cancel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id != self.owner_id:
            return await interaction.response.send_message("This confirmation isn't for you!", ephemeral=True)

        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(content="❌ Reset cancelled. Your progress is safe.", view=self)


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
        
        if count >= 810: return "Gladiator Maximus", count
        if count >= 600: return "Titan Ascendant", count
        if count >= 390: return "Apex Centurion", count
        if count >= 330: return "Gold Gladiator", count
        if count >= 240: return "Arena Master", count
        if count >= 150: return "Gilded Champion", count
        if count >= 120: return "Steel Centurion", count
        if count >= 60: return "Iron Vanguard", count
        if count >= 30: return "Bronze Legionnaire", count
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

    @nextcord.slash_command(name="exercise", description="View proper form, tips, and demonstration images for any exercise")
    async def exercise(
        self,
        interaction: nextcord.Interaction,
        name: str = nextcord.SlashOption(
            name="name",
            description="Type or select the exercise name",
            required=True
        )
    ):
        if not interaction.response.is_done():
            try:
                await interaction.response.defer(ephemeral=True)
            except Exception:
                pass

        guide = find_exercise_guide(name)
        embed = nextcord.Embed(
            title=f"📖 Exercise Guide: {guide['title']}",
            color=0x3498DB
        )
        embed.add_field(name="🏷️ Category", value=f"└ {guide.get('category', 'Exercise')}", inline=True)
        embed.add_field(name="🎯 Target Muscles", value=f"└ {guide['muscles']}", inline=True)
        embed.add_field(name="📋 How to Perform (Proper Form)", value=guide["form"], inline=False)
        embed.add_field(name="💡 Pro Tips & Common Mistakes", value=guide["tips"], inline=False)
        
        if guide.get("image_url"):
            embed.set_image(url=guide["image_url"])
            
        embed.set_footer(text="Train with strict form. Quality always beats quantity.")
        await interaction.followup.send(embed=embed, ephemeral=True)

    @exercise.on_autocomplete("name")
    async def exercise_autocomplete(self, interaction: nextcord.Interaction, current: str):
        query = current.lower().strip()
        choices = []
        for key, data in EXERCISE_GUIDES.items():
            display_title = data.get("title", key)
            if not query or query in key.lower() or query in display_title.lower():
                if display_title not in choices:
                    choices.append(display_title)
        await interaction.response.send_autocomplete(choices[:25])

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

    @nextcord.slash_command(name="resetworkout", description="Reset your workout count and rank back to zero")
    async def reset_workout(self, interaction: nextcord.Interaction):
        if not interaction.response.is_done():
            try:
                await interaction.response.defer(ephemeral=True)
            except Exception:
                pass

        view = ConfirmResetView(self, interaction.user.id)
        await interaction.followup.send(
            "⚠️ **Are you sure you want to reset your progress?**\n\n"
            "All your workout counts will be lost, and your current rank will be gone. You'll be reset all the way back to **Level 1: Novice / Beginner**.\n\n"
            "**This cannot be undone.**",
            view=view,
            ephemeral=True
        )

def setup(bot):
    bot.add_cog(WorkoutCog(bot))