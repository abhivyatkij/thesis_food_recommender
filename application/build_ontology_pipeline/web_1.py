# app.py
import streamlit as st
import json, os
import nutri_hard_constraint as hard

st.set_page_config(page_title="Hard Constraints Demo", layout="centered")
st.title("🔒 Hard Constraints via Streamlit")

# 1) Collect user profile
st.header("Step 1: Your Profile")

age = st.number_input("Age (years)", min_value=0, max_value=120, value=25)
sex = st.selectbox("Sex", ["M", "F"])
activity = st.selectbox(
    "Activity level", 
    ["sedentary", "moderately_active", "active"]
)
diet_pref = st.selectbox(
    "Dietary preference", 
    ["veg", "nonveg", "vegan"]
)

weight = st.number_input("Weight (kg)", min_value=1.0, value=60.0)
height_cm = st.number_input("Height (cm)", min_value=30.0, value=160.0)

allergies_input = st.text_input("Allergies (comma-separated)", "")
avoid_meals = st.checkbox("Avoid foods at specific meals?")
avoid_food_preference = {}
if avoid_meals:
    for slot in ["breakfast", "lunch", "snacks", "dinner"]:
        items = st.text_input(f"• Avoid at {slot}:", "")
        if items:
            avoid_food_preference[slot] = [i.strip().lower() for i in items.split(",")]

diabetes    = st.checkbox("Diabetes")
hypertension= st.checkbox("Hypertension")
pcos        = st.checkbox("PCOS")
most_active = None
if pcos:
    most_active = st.selectbox(
        "When are you most active?",
        ["after breakfast","after lunch","after snacks","after dinner"]
    )

# 2) Build exactly your user_constraints dict
if st.button("Run Hard Constraints"):
    height_m = height_cm / 100
    bmi = round(weight / (height_m**2), 1)
    bmr = (10*weight) + (6.25*height_cm) - (5*age) + (5 if sex=="M" else -161)
    tdee = bmr * {"sedentary":1.2,"moderately_active":1.55,"active":1.725}[activity]

    user_constraints = {
        "age": age,
        "sex": sex,
        "activity_level": activity,
        "diet": {"veg":"vegetarian","nonveg":"non vegetarian","vegan":"vegan"}[diet_pref],
        "allergies": [a.strip().lower() for a in allergies_input.split(",")] if allergies_input else [],
        "avoid_food_preference": avoid_food_preference,
        "medical_conditions": {
            "diabetes": diabetes,
            "hypertension": hypertension,
            "pcos": pcos
        },
        "calorie_goal": None  # you can add logic here if you want
    }
    if pcos:
        mapping = {
            "after breakfast":"breakfast",
            "after lunch":"lunch",
            "after snacks":"snacks",
            "after dinner":"dinner"
        }
        user_constraints["most_active_before"] = mapping[most_active]

    # 3) Inject into your module and run
    hard.user_constraints = user_constraints
    try:
        recommended, rejected = hard.diet_constraints()
    except Exception as e:
        st.error(f"Failed: {e}")
        st.stop()

    # 4) Show results
    st.success(f"Found {len(recommended)} recipes after hard constraints")
    for r in recommended[:5]:
        st.write(f"- {r['name'].replace('_',' ').title()} ({r['EnergyKcal']} kcal)")
