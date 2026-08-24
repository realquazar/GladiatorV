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
            "1. **Neck Circles:** Stand tall with shoulders relaxed. Slowly roll your neck in gentle 360-degree circles. Reverse direction after 5 reps.\n"
            "2. **Arm Circles:** Extend both arms straight out to sides at shoulder height. Make small controlled forward circles, gradually widening them.\n"
            "3. **Reverse:** Reverse the arm rotation backward, opening the chest and activating shoulder stabilizers."
        ),
        "tips": "• Move slowly and never jerk or whip your neck.\n• Keep breathing steadily throughout the mobility warm-up.",
        "image_url": "https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=800&q=80"
    },
    "Dumbbell bicep curls": {
        "title": "Dumbbell Bicep Curls",
        "category": "Gym / Arms",
        "muscles": "Biceps Brachii, Brachialis, Forearms",
        "form": (
            "1. Stand with feet shoulder-width apart, holding dumbbells at your sides with palms facing forward.\n"
            "2. Keep your elbows tucked close to your torso and stationary.\n"
            "3. Exhale and curl the dumbbells up toward shoulder level by contracting your biceps.\n"
            "4. Squeeze your biceps at the peak for 1 second, then slowly lower the weights (2-3 seconds) back to starting position."
        ),
        "tips": "• Do not swing your body or use momentum from your lower back.\n• Keep your wrists straight and firm throughout the movement.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Biceps-curl-1.svg/800px-Biceps-curl-1.svg.png"
    },
    "Hammer curls": {
        "title": "Dumbbell Hammer Curls",
        "category": "Gym / Arms",
        "muscles": "Brachioradialis (Forearms), Brachialis, Biceps",
        "form": (
            "1. Stand upright holding dumbbells with a neutral grip (palms facing inward toward each other).\n"
            "2. Keeping your upper arms fixed to your sides, bend at the elbows to curl the dumbbells upward.\n"
            "3. Lift until the top of the dumbbells are near shoulder height.\n"
            "4. Pause and squeeze the forearms and biceps, then lower with strict control."
        ),
        "tips": "• Keep elbows pinned to your ribs; do not let them drift forward.\n• Maintain a neutral wrist angle without bending wrists inward.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Biceps-curl-2.svg/800px-Biceps-curl-2.svg.png"
    },
    "Overhead Triceps extension": {
        "title": "Overhead Triceps Extension",
        "category": "Gym / Arms",
        "muscles": "Triceps Brachii (Long Head)",
        "form": (
            "1. Stand or sit upright holding a dumbbell or rope attachment with both hands raised straight overhead.\n"
            "2. Keep your upper arms vertical and close to your ears, elbows pointing forward.\n"
            "3. Inhale and slowly bend your elbows to lower the weight behind your head until your forearms reach ~90 degrees.\n"
            "4. Exhale and push the weight back up by extending your triceps until arms are fully locked out."
        ),
        "tips": "• Avoid flaring your elbows out to the sides.\n• Brace your core so you don't over-arch your lower back.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Triceps-dip-1.png/800px-Triceps-dip-1.png"
    },
    "Preacher curls": {
        "title": "Preacher Curls",
        "category": "Gym / Arms",
        "muscles": "Biceps Brachii (Short Head Isolation)",
        "form": (
            "1. Sit at a preacher bench with the back of your upper arms resting firmly against the slanted pad.\n"
            "2. Hold an EZ-curl bar or dumbbells with an underhand grip, arms extended.\n"
            "3. Curl the weight upward toward your chin while keeping your armpits snug against the top of the pad.\n"
            "4. Squeeze biceps at the top, then lower with control until arms are almost fully extended (don't hyperextend)."
        ),
        "tips": "• Do not lift your torso or armpits off the pad to cheat the weight up.\n• Control the eccentric (lowering) phase smoothly to protect elbows.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Biceps-curl-1.svg/800px-Biceps-curl-1.svg.png"
    },
    "Overhead press": {
        "title": "Overhead Press (Shoulder Press)",
        "category": "Gym / Shoulders",
        "muscles": "Anterior & Lateral Deltoids, Triceps, Upper Chest, Core",
        "form": (
            "1. Stand with feet hip-width apart, holding weights at shoulder height with palms facing forward.\n"
            "2. Brace your abs and squeeze your glutes for a rock-solid base.\n"
            "3. Press the weights straight overhead until your arms are fully extended.\n"
            "4. Lower the weight under control back to collarbone/shoulder height."
        ),
        "tips": "• Avoid leaning backward or hyperextending your lumbar spine.\n• Keep your head neutral and push the weight vertically in a straight bar path.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Shoulder-press-1.png/800px-Shoulder-press-1.png"
    },
    "Crunches": {
        "title": "Abdominal Crunches",
        "category": "Core",
        "muscles": "Rectus Abdominis (Upper Abs)",
        "form": (
            "1. Lie on your back with knees bent and feet flat on the floor, hip-width apart.\n"
            "2. Place fingertips lightly behind your ears or cross your hands over your chest.\n"
            "3. Exhale and contract your abdominals, lifting your shoulder blades 2-3 inches off the ground.\n"
            "4. Squeeze your core hard at the top for 1 second, then slowly lower back down."
        ),
        "tips": "• Do NOT pull on your neck or tuck your chin into your chest.\n• Keep your lower back pressed into the mat throughout.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Crunch-1.svg/800px-Crunch-1.svg.png"
    },
    "Crunches / Ab crunch machine": {
        "title": "Crunches / Ab Crunch Machine",
        "category": "Gym / Core",
        "muscles": "Rectus Abdominis",
        "form": (
            "1. **Floor Crunch:** Lie on mat with knees bent; curl shoulders up toward knees using abdominal contraction.\n"
            "2. **Machine Crunch:** Sit securely in the machine, feet hooked under pads and hands holding handles.\n"
            "3. Flex forward at the waist by squeezing your abs to bring elbows towards knees.\n"
            "4. Pause for a peak contraction, then slowly return without letting the weight stack slam."
        ),
        "tips": "• Focus on curling your ribcage toward your pelvis, not pushing with arms.\n• Keep breathing rhythmic—exhale as you crunch.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Crunch-1.svg/800px-Crunch-1.svg.png"
    },
    "Seated Cable row": {
        "title": "Seated Cable Row",
        "category": "Gym / Back",
        "muscles": "Latissimus Dorsi, Rhomboids, Middle Traps, Biceps",
        "form": (
            "1. Sit on the bench with knees slightly bent and feet placed on the footrests.\n"
            "2. Grasp the V-bar handle with a neutral grip and sit upright with chest lifted and back straight.\n"
            "3. Pull the handle toward your lower abdomen while driving elbows back and squeezing shoulder blades.\n"
            "4. Hold for 1 second, then slowly extend your arms back to starting position."
        ),
        "tips": "• Avoid excessive rocking or swinging back and forth.\n• Keep your chest proud and spine neutral at all times.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Lat-pulldown-1.png/800px-Lat-pulldown-1.png"
    },
    "Cable lats pulldown": {
        "title": "Cable Lat Pulldown",
        "category": "Gym / Back",
        "muscles": "Latissimus Dorsi, Teres Major, Biceps, Rear Delts",
        "form": (
            "1. Sit at the pulldown machine and adjust the thigh pad snugly over your legs.\n"
            "2. Grasp the wide bar with an overhand grip slightly wider than shoulder-width.\n"
            "3. Lean back slightly (~10-15 degrees), pull the bar down to your upper chest by driving elbows down.\n"
            "4. Squeeze your lats at the bottom, then slowly return the bar under control."
        ),
        "tips": "• Pull with your back muscles and elbows, not just your forearms.\n• Never pull the bar behind your neck to protect your cervical spine.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Lat-pulldown-1.png/800px-Lat-pulldown-1.png"
    },
    "Pec dec": {
        "title": "Pec Dec (Chest Fly Machine)",
        "category": "Gym / Chest",
        "muscles": "Pectoralis Major (Sternal Head)",
        "form": (
            "1. Adjust seat height so handles or arm pads align directly with the middle of your chest.\n"
            "2. Place forearms/hands on the pads and press your upper back flat against the backrest.\n"
            "3. Inhale, then exhale as you bring the handles together in front of your chest in an arc motion.\n"
            "4. Squeeze your chest firmly at the center for 1 second, then slowly open arms back to starting stretch."
        ),
        "tips": "• Maintain a slight, soft bend in your elbows; don't lock or bend them excessively.\n• Don't let your shoulders roll forward at the peak squeeze.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Bench-press-1.png/800px-Bench-press-1.png"
    },
    "Bench press": {
        "title": "Barbell / Dumbbell Bench Press",
        "category": "Gym / Chest",
        "muscles": "Pectoralis Major, Anterior Deltoids, Triceps",
        "form": (
            "1. Lie flat on the bench with eyes directly under the bar and feet planted firmly on the floor.\n"
            "2. Grip the bar slightly wider than shoulder-width with thumbs wrapped around.\n"
            "3. Unrack the bar, lower it with control to mid-chest while tucking elbows at roughly a 45-degree angle.\n"
            "4. Touch chest lightly, then press forcefully back up to lockout above your chest."
        ),
        "tips": "• Retract shoulder blades and keep your butt glued to the bench.\n• Avoid flaring your elbows straight out at 90 degrees.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Bench-press-1.png/800px-Bench-press-1.png"
    },
    "Bodyweight squats": {
        "title": "Bodyweight Squats",
        "category": "Calisthenics / Legs",
        "muscles": "Quadriceps, Gluteus Maximus, Hamstrings, Calves, Core",
        "form": (
            "1. Stand with feet slightly wider than shoulder-width, toes angled 15-30 degrees outward.\n"
            "2. Keep your chest high, gaze forward, and hands clasped in front of your chest.\n"
            "3. Hinge hips back and bend knees, lowering your body until thighs are parallel to the floor (or deeper).\n"
            "4. Drive through mid-foot and heels to return to standing, squeezing glutes at the top."
        ),
        "tips": "• Keep your knees tracking in line with your toes—don't let them cave inward.\n• Keep heels grounded throughout the entire repetition.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Squats-1.svg/800px-Squats-1.svg.png"
    },
    "Weighted squats": {
        "title": "Weighted Squats (Barbell / Dumbbell)",
        "category": "Gym / Legs",
        "muscles": "Quadriceps, Glutes, Hamstrings, Spinal Erectors, Core",
        "form": (
            "1. Position barbell on upper traps (or hold dumbbells at sides/goblet position).\n"
            "2. Stand with feet shoulder-width apart, brace core tightly.\n"
            "3. Break at hips and knees simultaneously, lowering down until thighs are parallel to the ground.\n"
            "4. Push the floor away through your heels to stand up powerfully."
        ),
        "tips": "• Maintain a neutral spine; do not round your lower back.\n• Take a deep breath into your belly and brace before descending.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Squats-1.svg/800px-Squats-1.svg.png"
    },
    "Leg press": {
        "title": "Leg Press",
        "category": "Gym / Legs",
        "muscles": "Quadriceps, Glutes, Hamstrings",
        "form": (
            "1. Sit in the machine with your back and head resting comfortably against the padded support.\n"
            "2. Place feet shoulder-width apart on the sled platform.\n"
            "3. Disengage safety bars and slowly lower the sled until knees form a 90-degree angle.\n"
            "4. Press back up through your heels and mid-foot to full extension (do NOT lock knees)."
        ),
        "tips": "• Never fully lock out your knees at the top of the press.\n• Ensure your lower back and glutes remain pressed flat against the seat.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Leg-press-1.png/800px-Leg-press-1.png"
    },
    "Incline leg press": {
        "title": "45° Incline Leg Press",
        "category": "Gym / Legs",
        "muscles": "Quadriceps, Glutes, Hamstrings",
        "form": (
            "1. Sit securely into the 45-degree leg press with lower back firmly against the pad.\n"
            "2. Place feet in the center of the plate, shoulder-width apart.\n"
            "3. Inhale and lower the weight under strict control until thighs approach 90 degrees with knees.\n"
            "4. Exhale and drive through heels to press the platform back up."
        ),
        "tips": "• Stop descending if your pelvis or lower back begins to roll off the pad.\n• Keep knees aligned with feet.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Leg-press-1.png/800px-Leg-press-1.png"
    },
    "Leg extension": {
        "title": "Seated Leg Extension",
        "category": "Gym / Legs",
        "muscles": "Quadriceps (Isolation)",
        "form": (
            "1. Sit on the machine with knees aligned with the pivot point and shin pad resting above ankles.\n"
            "2. Grip side handles firmly to keep your hips anchored.\n"
            "3. Extend your legs forward until fully straight, contracting the quads hard at the top.\n"
            "4. Pause for 1 second, then lower the weight slowly (2-3 seconds) back down."
        ),
        "tips": "• Do not use jerky momentum or swing your hips off the seat.\n• Control the weight all the way down for maximum hypertrophy.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c6/Leg-extension-1.png/800px-Leg-extension-1.png"
    },
    "Seated leg curl": {
        "title": "Seated Leg Curl",
        "category": "Gym / Legs",
        "muscles": "Hamstrings (Biceps Femoris, Semitendinosus)",
        "form": (
            "1. Sit with back against pad, thigh brace adjusted snugly on top of thighs, and lever pad behind lower calves.\n"
            "2. Grasp handles and keep torso firmly pressed against back support.\n"
            "3. Flex knees to curl the lever down and backward toward your seat.\n"
            "4. Squeeze hamstrings tight at peak flexion, then return slowly to starting position."
        ),
        "tips": "• Keep toes pointed straight ahead or slightly flexed.\n• Avoid arching your lower back during the contraction.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Leg-curl-1.png/800px-Leg-curl-1.png"
    },
    "Treadmill": {
        "title": "Treadmill Cardio / Jogging",
        "category": "Cardio / Conditioning",
        "muscles": "Cardiovascular System, Calves, Quads, Hamstrings",
        "form": (
            "1. Step onto treadmill belt, attach safety clip, and start at a brisk walking pace.\n"
            "2. Keep shoulders relaxed, chest open, and arms bent at 90 degrees swinging rhythmically.\n"
            "3. Land softly on midfoot (not heavy on heels) with a slight forward lean from the ankles.\n"
            "4. Maintain steady, rhythmic nasal-oral breathing."
        ),
        "tips": "• Avoid gripping the handrails while running.\n• Look straight ahead, not down at your feet.",
        "image_url": "https://images.unsplash.com/photo-1538805060514-97d9cc17730c?auto=format&fit=crop&w=800&q=80"
    },
    "Running": {
        "title": "Outdoor / Track Running",
        "category": "Cardio / Conditioning",
        "muscles": "Cardiovascular System, Glutes, Quads, Hamstrings, Calves",
        "form": (
            "1. Maintain an upright posture with a slight whole-body forward lean.\n"
            "2. Strike the ground beneath your center of gravity with your midfoot.\n"
            "3. Drive knees forward and cycle feet smoothly with a cadence around 160-180 steps/min.\n"
            "4. Keep hands relaxed and shoulders away from your ears."
        ),
        "tips": "• Don't overstride (landing too far ahead of your hips).\n• Pace yourself according to the session duration.",
        "image_url": "https://images.unsplash.com/photo-1486218119243-13883505764c?auto=format&fit=crop&w=800&q=80"
    },
    "Push Ups": {
        "title": "Standard Push-Ups",
        "category": "Calisthenics / Chest & Triceps",
        "muscles": "Pectoralis Major, Anterior Deltoids, Triceps, Core",
        "form": (
            "1. Place hands shoulder-width apart on the floor with fingers spread, body in a rigid high plank.\n"
            "2. Squeeze glutes and brace your core so your body forms a straight line from heels to head.\n"
            "3. Lower your chest until it is about 1-2 inches above the floor, keeping elbows angled at 45 degrees.\n"
            "4. Push through palms to lock out arms at the top."
        ),
        "tips": "• Don't let your lower back or hips sag.\n• Keep your neck neutral by gazing a few inches ahead of your hands.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/Pushups-1.png/800px-Pushups-1.png"
    },
    "Elevated push ups": {
        "title": "Elevated / Incline Push-Ups",
        "category": "Calisthenics / Chest",
        "muscles": "Lower Pectoralis, Anterior Deltoids, Triceps",
        "form": (
            "1. Place hands on an elevated surface (bench, bar, or step) shoulder-width apart.\n"
            "2. Step feet back so body forms a straight incline plank.\n"
            "3. Lower your chest toward the edge of the elevated surface.\n"
            "4. Press through your palms to return to starting position."
        ),
        "tips": "• Great progression for building chest pushing strength.\n• Keep your core tight and elbows tucked at 45 degrees.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/Pushups-1.png/800px-Pushups-1.png"
    },
    "Inclined push ups": {
        "title": "Incline / Decline Push-Ups",
        "category": "Calisthenics / Upper Body",
        "muscles": "Pectoralis Major, Clavicular Head, Triceps, Deltoids",
        "form": (
            "1. Place feet on a bench or elevated platform and hands on the floor (Decline Push-Up for upper chest).\n"
            "2. Or hands elevated on a bench (Incline Push-Up for beginners).\n"
            "3. Lower chest with control until nearly touching floor/surface.\n"
            "4. Press forcefully back to starting lockout."
        ),
        "tips": "• Maintain strict straight-line body tension from heels to head.\n• Avoid letting hips drop or piking in the air.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/Pushups-1.png/800px-Pushups-1.png"
    },
    "Hindu push ups": {
        "title": "Hindu Push-Ups (Dand)",
        "category": "Calisthenics / Full Body Push",
        "muscles": "Shoulders, Chest, Triceps, Hamstrings, Lower Back Flexibility",
        "form": (
            "1. Start in a downward dog pose with hips high in the air and feet spread wide.\n"
            "2. Bend elbows and swoop your chest down toward the floor between your hands.\n"
            "3. Glide forward and arch your torso upward into an upward dog pose (chest up, hips low).\n"
            "4. Push hips back up and return smoothly to starting downward dog."
        ),
        "tips": "• Perform the motion in one fluid, continuous scoop.\n• Great for shoulder mobility and core conditioning.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/Pushups-1.png/800px-Pushups-1.png"
    },
    "Plank": {
        "title": "Forearm Plank",
        "category": "Core / Isometric",
        "muscles": "Transverse Abdominis, Rectus Abdominis, Glutes, Deltoids",
        "form": (
            "1. Rest on forearms with elbows stacked directly beneath your shoulders.\n"
            "2. Extend legs behind you with toes planted, forming a straight line from crown of head to heels.\n"
            "3. Engage your abs as if expecting a punch; squeeze glutes and quads firmly.\n"
            "4. Hold position statically while maintaining steady, deep breathing."
        ),
        "tips": "• Do not let hips sag toward the floor or pike upward.\n• Keep neck neutral by looking at the floor between your forearms.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Plank-exercise.svg/800px-Plank-exercise.svg.png"
    },
    "Bodyweight lunges": {
        "title": "Bodyweight Walking / Forward Lunges",
        "category": "Calisthenics / Legs",
        "muscles": "Quadriceps, Gluteus Maximus, Hamstrings, Core Balance",
        "form": (
            "1. Stand tall with feet hip-width apart and hands on hips.\n"
            "2. Take a controlled step forward with one leg and lower hips until both knees are bent at ~90 degrees.\n"
            "3. The back knee should hover 1 inch above the floor without banging down.\n"
            "4. Drive through front heel to step back to starting position (or step forward for walking lunges)."
        ),
        "tips": "• Ensure your front knee stays stacked above ankle, not past toes.\n• Keep torso upright—avoid leaning forward.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Squats-1.svg/800px-Squats-1.svg.png"
    },
    "Chair assisted dips": {
        "title": "Bench / Chair Dips",
        "category": "Calisthenics / Triceps",
        "muscles": "Triceps Brachii, Anterior Deltoids, Lower Chest",
        "form": (
            "1. Sit on edge of a sturdy chair or bench, hands gripping the edge right next to your hips.\n"
            "2. Slide hips forward off the chair, legs extended forward with knees slightly bent or straight.\n"
            "3. Inhale and lower hips by bending elbows until they reach a 90-degree angle.\n"
            "4. Exhale and press through palms to straighten arms back to top position."
        ),
        "tips": "• Keep your back close to the chair/bench throughout to prevent shoulder strain.\n• Don't dip below 90 degrees at the elbows.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Triceps-dip-1.png/800px-Triceps-dip-1.png"
    },
    "Pull ups": {
        "title": "Overhand Pull-Ups",
        "category": "Calisthenics / Upper Body Pull",
        "muscles": "Latissimus Dorsi, Biceps, Upper Back, Forearms, Core",
        "form": (
            "1. Hang from a pull-up bar with an overhand grip (palms facing away), slightly wider than shoulder-width.\n"
            "2. Start from a dead hang; depress and retract shoulder blades (active hang).\n"
            "3. Pull your chest toward the bar by driving your elbows down to your ribs until chin clears the bar.\n"
            "4. Pause briefly, then lower yourself with complete control back to a full hang."
        ),
        "tips": "• Do not swing, kick, or use kipping momentum.\n• Focus on driving elbows down and back rather than curling with wrists.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Pull-up-1.png/800px-Pull-up-1.png"
    },
    "Chin ups": {
        "title": "Underhand Chin-Ups",
        "category": "Calisthenics / Arms & Back",
        "muscles": "Biceps Brachii, Latissimus Dorsi, Teres Major, Core",
        "form": (
            "1. Hang from the bar with an underhand grip (palms facing you), shoulder-width apart.\n"
            "2. Engage back and biceps, pulling yourself upward until chin is over the bar.\n"
            "3. Keep elbows close to your body and chest open.\n"
            "4. Lower smoothly all the way down to a full extension dead hang."
        ),
        "tips": "• Squeeze your biceps hard at the top of every rep.\n• Avoid rounding shoulders forward at the top.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Pull-up-1.png/800px-Pull-up-1.png"
    },
    "Twist crunches": {
        "title": "Twist / Bicycle Crunches",
        "category": "Core / Obliques",
        "muscles": "Internal & External Obliques, Rectus Abdominis",
        "form": (
            "1. Lie on your back with hands behind your head and knees bent in tabletop position.\n"
            "2. Lift shoulder blades and twist your right elbow across to touch your left knee while extending right leg straight.\n"
            "3. Switch sides smoothly, bringing left elbow to right knee while extending left leg.\n"
            "4. Keep the motion controlled and continuous like pedaling."
        ),
        "tips": "• Rotate through your ribcage and obliques, not just pulling your elbow.\n• Keep lower back firmly anchored to the floor.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Crunch-1.svg/800px-Crunch-1.svg.png"
    },
    "Jumping": {
        "title": "Jumping Jacks / Vertical Jumps",
        "category": "Cardio / Conditioning",
        "muscles": "Calves, Quads, Deltoids, Cardiovascular System",
        "form": (
            "1. Stand with feet together and arms at your sides.\n"
            "2. Jump lightly, spreading feet beyond shoulder-width while sweeping arms overhead.\n"
            "3. Land softly on balls of feet and immediately jump back to starting stance.\n"
            "4. Keep a brisk, steady rhythm."
        ),
        "tips": "• Keep knees soft on every landing to absorb impact safely.\n• Breathe rhythmically throughout.",
        "image_url": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=800&q=80"
    },
    "Frog stand with parallettes": {
        "title": "Frog Stand / Crow Pose on Parallettes",
        "category": "Calisthenics / Skill & Balance",
        "muscles": "Wrists, Forearms, Shoulders, Core Balance",
        "form": (
            "1. Place parallettes on the floor shoulder-width apart and grip them firmly.\n"
            "2. Squat down and place inner knees resting against the outside of your triceps/elbows.\n"
            "3. Lean forward slowly, shifting your center of gravity until your feet gently lift off the floor.\n"
            "4. Balance your entire bodyweight on your hands, engaging your core and shoulders."
        ),
        "tips": "• Look slightly forward, not straight down, to prevent tipping over.\n• Grip parallettes tightly and push the ground away.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/L-sit.svg/800px-L-sit.svg.png"
    },
    "Tuck front lever hold": {
        "title": "Tuck Front Lever Hold",
        "category": "Calisthenics / Advanced Pull",
        "muscles": "Latissimus Dorsi, Rhomboids, Rear Delts, Abdominals",
        "form": (
            "1. Hang from a pull-up bar with an overhand grip.\n"
            "2. Retract scapulae, lock arms straight, and pull your torso up into a horizontal plane.\n"
            "3. Pull your knees tightly into your chest to shorten the lever arm.\n"
            "4. Hold your torso completely parallel to the ground for target time."
        ),
        "tips": "• Keep arms 100% straight; do not bend at the elbows.\n• Drive your hands down against the bar like a straight-arm pulldown.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Front-lever.svg/800px-Front-lever.svg.png"
    },
    "advance tuck front lever hold": {
        "title": "Advanced Tuck Front Lever Hold",
        "category": "Calisthenics / Advanced Pull",
        "muscles": "Latissimus Dorsi, Core, Rear Delts, Scapular Retractors",
        "form": (
            "1. From a straight-arm hang on the bar, pull your torso into horizontal alignment with the floor.\n"
            "2. Move your knees away from your chest until thighs are at a 90-degree angle with your torso.\n"
            "3. Keep your back flat and arms locked out straight.\n"
            "4. Hold the isometric position with maximum lat tension."
        ),
        "tips": "• Keep your hips in line with your shoulders—don't let hips sag.\n• Squeeze glutes and keep core locked tight.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Front-lever.svg/800px-Front-lever.svg.png"
    },
    "Negative front lever raises": {
        "title": "Negative Front Lever Raises (Eccentrics)",
        "category": "Calisthenics / Advanced Pull",
        "muscles": "Latissimus Dorsi, Rear Deltoids, Core, Grip",
        "form": (
            "1. Invert your body on the pull-up bar so your feet point straight up toward the ceiling.\n"
            "2. Lock your arms straight and engage your back.\n"
            "3. Slowly lower your entire straight body down in a horizontal line toward the floor (3-5 seconds).\n"
            "4. Resist gravity all the way through parallel before lowering to a dead hang."
        ),
        "tips": "• Make the eccentric lowering as slow and controlled as possible.\n• Keep your body in a rigid line without arching or piking.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Front-lever.svg/800px-Front-lever.svg.png"
    },
    "L-sit": {
        "title": "L-Sit Hold (Parallettes / Floor)",
        "category": "Calisthenics / Isometric Core",
        "muscles": "Rectus Abdominis, Hip Flexors, Triceps, Anterior Deltoids",
        "form": (
            "1. Sit on floor or between parallettes with hands pressing firmly beside hips.\n"
            "2. Depress your shoulders (push down into floor/bars to create neck space).\n"
            "3. Lift your hips and extend your legs straight out in front, parallel to the ground.\n"
            "4. Point toes, squeeze quads, and hold the 90-degree 'L' shape."
        ),
        "tips": "• Don't let your shoulders shrug up to your ears.\n• If full L-sit is difficult, start with one leg extended or bent-knee tuck.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/L-sit.svg/800px-L-sit.svg.png"
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
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Squats-1.svg/800px-Squats-1.svg.png"
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
        await interaction.response.edit_message(content=self.disclaimer_text, embed=guide_embed, view=self)

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