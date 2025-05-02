
from ortools.sat.python import cp_model
import json
import os
import random
from collections import defaultdict
from collections import Counter
# ─── Load recipe and constraint data ───────────────────────────────────────
recipe_path = os.path.join(
    os.path.dirname(__file__),
    'out_build_ontology_pipeline',
    'recommended_recipes',
    'hard_constraint_recommended_recipes.json'
)
with open(recipe_path) as f:
    recipes = json.load(f)

constraint_path = os.path.join(
    os.path.dirname(__file__),
    'out_build_ontology_pipeline',
    'recommended_recipes',
    'user_constraints.json'
)
with open(constraint_path) as f:
    user_constraints = json.load(f)

ncd_nutrient_map = {
            "hypertension": {
                "Sodium (mg)": "mg",
                "Potassium (mg)": "mg",
                "Fibre (g)": "g",
                "Saturated Fat (g)": "g",
                "Fat (g)": "g",
            },
            "diabetes": {
                "Free Sugar (g)": "g",
                "Fibre (g)": "g",
                "Saturated Fat (g)": "g",
                "Sodium (mg)": "mg",
            },
            "pcos": {
                "Fat (g)": "g",
                "Saturated Fat (g)": "g",
                "Free Sugar (g)": "g",
                "EnergyKcal": "kcal",
                "Sodium (mg)": "mg",
            }
        }

def get_numeric_value(recipe, key):
        try:
            return int(round(float(recipe.get(key, 0) or 0)))
        except (ValueError, TypeError):
            return 0

print("\n\nUser profile:", user_constraints)


course_map = {
    "breakfast": "breakfast", "maincourse": "lunch", "main course": "lunch",
    "main -": "lunch", "lunch": "lunch", "breads": "lunch", "rice": "lunch",
    "dinner": "dinner", "snack": "snacks", "beverage": "snacks", "drink": "snacks",
    "appetizer": "snacks", "appetiser": "snacks", "side dish": "snacks", "side": "snacks",
    "soup": "snacks", "dip": "misc", "chutney": "misc", "dessert": "snacks",
    "sweet": "snacks", "cookie": "snacks", "cookies": "snacks", "biscuit": "misc",
    "jam": "misc", "kulfi": "snacks", "ice-cream": "snacks", "pickles": "misc",
    "accompaniment": "snacks", "basic cooking tips": "misc", "basics": "misc",
    "grilling / barbeque": "dinner", "smoothie": "snacks", "starters": "snacks",
}

nutrient_keys = [
    "EnergyKcal", "Carbohydrates (g)", "Protein (g)", "Fat (g)", "Free Sugar (g)", "Fibre (g)",
    "Saturated Fat (g)", "Monounsaturated Fat (g)", "Polyunsaturated Fat (g)",
    "Cholesterol (mg)", "Calcium (mg)", "Phosphorus (mg)", "Magnesium (mg)", "Sodium (mg)",
    "Potassium (mg)", "Iron (mg)", "Copper (mg)", "Selenium (ug)", "Chromium (mg)",
    "Manganese (mg)", "Molybdenum (mg)", "Zinc (mg)", "Vitamin E (mg)", "Vitamin D2 (ug)",
    "Vitamin K1 (ug)", "Folate (ug)", "Vitamin B1 (mg)", "Vitamin B2 (mg)", "Vitamin B3 (mg)",
    "Vitamin B5 (mg)", "Vitamin B6 (mg)", "Vitamin B7 (ug)", "Vitamin B9 (ug)",
    "Vitamin C (mg)", "Carotenoids (ug)"
]


def normalize(text):
    return text.lower().replace(" ", "").replace("-", "")

# Step 3: Assign meal_time to each recipe
for r in recipes:
    course = r.get("course", "").strip().lower()
    slot = "unspecified"
    if course:
        norm_course = normalize(course)
        for key, val in course_map.items():
            if normalize(key) in norm_course:
                slot = val
                break
    r["meal_time"] = slot

valid_meal_times = {"breakfast", "lunch", "snacks", "dinner"}
valid_recipes = [
    r for r in recipes
    if r["meal_time"] in {"breakfast", "lunch", "snacks", "dinner"}
    and r.get("ingredients")  # filters out recipes with no ingredients or an empty list
]

for r in recipes:
    if r.get("meal_time") not in valid_meal_times:
        continue
    if not r.get("ingredients"):
        continue
    if all((r.get(k, 0) == 0 or r.get(k, 0) == "0.0") for k in nutrient_keys):
        continue
    valid_recipes.append(r)
recipes = valid_recipes

# Step 5: Print distribution
meal_time_counts = Counter(r["meal_time"] for r in recipes)
print("\nMeal time counts:", meal_time_counts)

"""
valid_recipes = []
for r in recipes:
    course = r.get("course", "").strip().lower()
    if not course or course == "na":
        continue  # skip recipes with no course info

    if "breakfast" in course:
        r["meal_time"] = "breakfast"
    elif "snack" in course:
        r["meal_time"] = "snacks"
    elif "lunch" in course:
        r["meal_time"] = "lunch"
    elif "dinner" in course:
        r["meal_time"] = "dinner"
    elif "main course" in course:
        if "lunch" in course:
            r["meal_time"] = "lunch"
        elif "dinner" in course:
            r["meal_time"] = "dinner"
        else:
            r["meal_time"] = "lunch"
    else:
        continue

    valid_recipes.append(r)
recipes = valid_recipes
meal_time_counts = Counter(r["meal_time"] for r in recipes)
print ("\n\nMeal time counts:", meal_time_counts)
"""

# ─── Model and variables ──────────────────────────────────────────────────
model = cp_model.CpModel()
N = len(recipes)
x = [model.NewBoolVar(f"select_{i}") for i in range(N)]
penalties = []
meal_times = ["breakfast", "lunch", "snacks", "dinner"]

# ─── Precompute energy kcal integers ──────────────────────────────────────
energy_kcal_int = []
for r in recipes:
    try:
        kcal_val = float(r.get("EnergyKcal", 0))
        energy_kcal_int.append(int(round(kcal_val)))
    except:
        energy_kcal_int.append(0)

def total_of(key: str):
    return sum(x[i] * int(recipes[i].get(key, 0) or 0) for i in range(N))

def cal_for(slot: str):
    return sum(
        x[i] * energy_kcal_int[i]
        for i in range(N)
        if recipes[i].get("meal_time", "").lower() == slot
    )

def fat_total(): return total_of("Fat (g)")
def sat_fat_total(): return total_of("Saturated Fat (g)")

# ─── Constraints ──────────────────────────────────────────────────────────
def apply_meal_distribution_constraints():
    present = {
        k.lower() for k, v in user_constraints.get("medical_conditions", {}).items() if v
    }

    
    if {"hypertension", "diabetes", "pcos"} & present:
        model.Add(sum(x) == 4)
        model.Add(sum(x) <= 6)
    else:
        model.Add(sum(x) == 4)


    if "pcos" in present:
        model.Add(cal_for("dinner") <= int(0.10 * user_constraints.get("calorie_goal", 2000)))
        active = user_constraints.get("most_active_before", "").lower()
        if active in meal_times:
            active_cal = cal_for(active)
            for slot in meal_times:
                if slot != active:
                    model.Add(active_cal >= cal_for(slot))

"""
def avoid_these_ingredients():
    avoid_map = user_constraints.get("avoid_food_preference", {})
    for i, r in enumerate(recipes):
        slot = r.get("meal_time", "unspecified")
        for term in avoid_map.get(slot, []):
            name = r.get("name", "").lower()
            ings = [ing.lower() for ing in r.get("ingredients", [])]
            if term in name or any(term in ing for ing in ings):
                penalty = model.NewIntVar(0, 1, f"avoid_{term}_{slot}_{i}")
                model.Add(penalty == x[i])
                penalties.append(penalty)
                print(f"🚫 Avoid '{term}' in {slot}: {r['name']}")
                break

"""
def apply_ncd_constraints():
    present = {
        k.lower() for k, v in user_constraints.get("medical_conditions", {}).items() if v
    }
    def hypertension():
       
        kcal              = user_constraints.get("calorie_goal", 2_000)
        sex               = user_constraints.get("sex", "F").upper()
        MAX_PENALTY_VALUE = 10_000          # adjust if you use a different bound

        penalties_local = []                # local list; extend global `penalties` at end

        # ── Sodium (soft) ─────────────────────────────────────────────
        min_s   = int((1500 / 2000) * kcal)
        max_s   = int((2300 / 2000) * kcal)
        s_under = model.NewIntVar(0, MAX_PENALTY_VALUE, "ht_sodium_under")
        s_over  = model.NewIntVar(0, MAX_PENALTY_VALUE, "ht_sodium_over")
        model.Add(min_s - total_of("Sodium (mg)") <= s_under)
        model.Add(total_of("Sodium (mg)") - max_s <= s_over)
        penalties_local.extend([s_under, s_over])

        # ── Potassium (soft) ──────────────────────────────────────────
        min_k   = int((3500 / 2000) * kcal)
        max_k   = int((5000 / 2000) * kcal)
        k_under = model.NewIntVar(0, MAX_PENALTY_VALUE, "ht_potassium_under")
        k_over  = model.NewIntVar(0, MAX_PENALTY_VALUE, "ht_potassium_over")
        model.Add(min_k - total_of("Potassium (mg)") <= k_under)
        model.Add(total_of("Potassium (mg)") - max_k <= k_over)
        penalties_local.extend([k_under, k_over])

        # ── Fibre minimum (soft) ─────────────────────────────────────
        fibre_min = int(((28 if sex == "F" else 38) / 2000) * kcal)
        fibre_under = model.NewIntVar(0, MAX_PENALTY_VALUE, "ht_fibre_under")
        model.Add(fibre_min - total_of("Fibre (g)") <= fibre_under)
        penalties_local.append(fibre_under)

        # ── Saturated-fat cap (soft) ─────────────────────────────────
        sat_cap = int((0.06 * kcal) / 9)
        sat_over = model.NewIntVar(0, MAX_PENALTY_VALUE, "ht_satfat_over")
        model.Add(total_of("Saturated Fat (g)") - sat_cap <= sat_over)
        penalties_local.append(sat_over)

        # ── Total-fat cap (soft) ─────────────────────────────────────
        fat_cap = int((0.27 * kcal) / 9)
        fat_over = model.NewIntVar(0, MAX_PENALTY_VALUE, "ht_totalfat_over")
        model.Add(total_of("Fat (g)") - fat_cap <= fat_over)
        penalties_local.append(fat_over)

        # ── Register penalties with the global list ─────────────────
        penalties.extend(penalties_local)


    def diabetes():

        kcal = user_constraints.get("calorie_goal", 2000)
        caps = {
            "sugar":     int((0.05 * kcal) / 4),          # ≤ 5 % kcal from free sugar
            "fibre":     int(14 * kcal / 1000),           # ≥ 14 g per 1000 kcal
            "satfat":    int((0.10 * kcal) / 9),          # ≤ 10 % kcal from sat-fat
            "sodium":    int((2300 / 2000) * kcal),       # ≤ 2300 mg scaled to kcal
        }

        model.Add(total_of("Free Sugar (g)")      - caps["sugar"]   <= model.NewIntVar(0, 10000, "dia_sugar_ov"))
        model.Add(caps["fibre"]                   - total_of("Fibre (g)")        <= model.NewIntVar(0, 10000, "dia_fibre_def"))
        model.Add(total_of("Saturated Fat (g)")   - caps["satfat"]  <= model.NewIntVar(0, 10000, "dia_satfat_ov"))
        model.Add(total_of("Sodium (mg)")         - caps["sodium"] <= model.NewIntVar(0, 10000, "dia_sodium_ov"))
        

    def pcos():

        kcal = user_constraints.get("calorie_goal", 2000)

        dinner_over = model.NewIntVar(0, 10_000, "pcos_dinner_over")     
        model.Add(cal_for("dinner") - int(0.10 * kcal) <= dinner_over)   
        penalties.append(dinner_over)   

        active = user_constraints.get("most_active_before", "").lower()
        if active in meal_times:
            a_cal = cal_for(active)
            for slot in meal_times:
                if slot != active:
                    model.Add(a_cal >= cal_for(slot))                  

        model.Add(fat_total()      <= int(0.30 * kcal / 9))            

        for slot in meal_times:
            model.Add(cal_for(slot) <= int(0.30 * kcal))              

        model.Add(
            total_of("Free Sugar (g)") - int(0.05 * kcal / 4)
            <= model.NewIntVar(0, 10_000, "pcos_sugar_ov")
        )

        min_s = int((1500 / 2000) * kcal)
        max_s = int((2300 / 2000) * kcal)

        model.Add(
            min_s - total_of("Sodium (mg)")
            <= model.NewIntVar(0, 10_000, "pcos_sodium_under")
        )
        model.Add(
            total_of("Sodium (mg)") - max_s
            <= model.NewIntVar(0, 10_000, "pcos_sodium_over")
        )


    if "pcos" in present:     pcos()
    if "diabetes" in present: diabetes()
    if "hypertension" in present: hypertension()

# ─── Solve model ──────────────────────────────────────────────────────────
apply_meal_distribution_constraints()
#avoid_these_ingredients()
apply_ncd_constraints()


MEAL_SELECTION_PENALTY_WEIGHT = 50 # Example weight

breakfast_idxs = [i for i, r in enumerate(recipes) if r.get("meal_time") == "breakfast"] # Get indices again
if breakfast_idxs:
    print(f"Breakfast recipes available: {len(breakfast_idxs)}")
    has_breakfast = model.NewBoolVar("has_breakfast")
    model.Add(sum(x[i] for i in breakfast_idxs) >= 1).OnlyEnforceIf(has_breakfast)
    no_breakfast_penalty = model.NewIntVar(0, MEAL_SELECTION_PENALTY_WEIGHT, "no_breakfast_penalty")
    model.Add(no_breakfast_penalty == MEAL_SELECTION_PENALTY_WEIGHT * (1 - has_breakfast))
    penalties.append(no_breakfast_penalty)
else:
    print("No breakfast recipes available. Cannot add soft constraint for breakfast selection.")


# Lunch
lunch_idxs = [i for i, r in enumerate(recipes) if r.get("meal_time") == "lunch"]
if lunch_idxs:
    print(f"Lunch recipes available: {len(lunch_idxs)}")
    has_lunch = model.NewBoolVar("has_lunch")
    model.Add(sum(x[i] for i in lunch_idxs) >= 1).OnlyEnforceIf(has_lunch)
    no_lunch_penalty = model.NewIntVar(0, MEAL_SELECTION_PENALTY_WEIGHT, "no_lunch_penalty")
    model.Add(no_lunch_penalty == MEAL_SELECTION_PENALTY_WEIGHT * (1 - has_lunch))
    penalties.append(no_lunch_penalty)
else:
     print("No lunch recipes available. Cannot add soft constraint for lunch selection.")


# Snacks
snacks_idxs = [i for i, r in enumerate(recipes) if r.get("meal_time") == "snacks"]
if snacks_idxs:
    print(f"Snacks recipes available: {len(snacks_idxs)}")
    has_snacks = model.NewBoolVar("has_snacks")
    model.Add(sum(x[i] for i in snacks_idxs) >= 1).OnlyEnforceIf(has_snacks)

    no_snacks_penalty = model.NewIntVar(0, MEAL_SELECTION_PENALTY_WEIGHT, "no_snacks_penalty")
    model.Add(no_snacks_penalty == MEAL_SELECTION_PENALTY_WEIGHT * (1 - has_snacks))
    penalties.append(no_snacks_penalty)
else:
     print("No snacks recipes available. Cannot add soft constraint for snacks selection.")

# Dinner
dinner_idxs = [i for i, r in enumerate(recipes) if r.get("meal_time") == "dinner"]
if dinner_idxs:
    print(f"Dinner recipes available: {len(dinner_idxs)}")
    has_dinner = model.NewBoolVar("has_dinner")
    model.Add(sum(x[i] for i in dinner_idxs) >= 1).OnlyEnforceIf(has_dinner)
    no_dinner_penalty = model.NewIntVar(0, MEAL_SELECTION_PENALTY_WEIGHT, "no_dinner_penalty")
    model.Add(no_dinner_penalty == MEAL_SELECTION_PENALTY_WEIGHT * (1 - has_dinner))
    penalties.append(no_dinner_penalty)
else:
    print("No dinner recipes available. Cannot add soft constraint for dinner selection.")

# --- End of soft constraints for meal selection ---

model.Minimize(sum(penalties))

solver = cp_model.CpSolver()
solver.parameters.random_seed = random.randint(1, 10000)
status = solver.Solve(model)
print("\n\nSOLVER OBJECTIVE VALUE:", solver.ObjectiveValue())

print("Status:", solver.StatusName(status))
selected = [r["name"] for i, r in enumerate(recipes) if solver.Value(x[i])]
#print("Selected:", selected)


# --- Print NCD Wise Results ---
print("\n--- NCD Wise Nutritional Summary ---")
present_conditions = {k.lower() for k, v in user_constraints.get("medical_conditions", {}).items() if v}
total_calorie_goal = user_constraints.get("calorie_goal", 2000) # Get goal again

# Recalculate targets here for printing
# This assumes your target calculations in apply_ncd_constraints are based on total_calorie_goal
# You might need to adjust calculations based on your specific logic
target_sodium_max = int((2300 / 2000) * total_calorie_goal) if total_calorie_goal else 0
target_sodium_min = int((1500 / 2000) * total_calorie_goal) if total_calorie_goal else 0 # Example min target
target_sugar_cap = int(0.05 * total_calorie_goal / 4) if total_calorie_goal else 0
target_fibre_min = int(14 * total_calorie_goal / 1000) if total_calorie_goal else 0
target_satfat_cap = int(0.10 * total_calorie_goal / 9) if total_calorie_goal else 0
target_fat_cap = int(0.30 * total_calorie_goal / 9) if total_calorie_goal else 0
# target_allowed_calories = ... # Your logic to calculate meal slot targets if printing calorie distribution

# Final edited version of your script:

from ortools.sat.python import cp_model
import json
import os
import random
from collections import defaultdict
from collections import Counter

# ─── Load recipe and constraint data ───────────────────────────────────────
recipe_path = os.path.join(
    os.path.dirname(__file__),
    'out_build_ontology_pipeline',
    'recommended_recipes',
    'hard_constraint_recommended_recipes.json'
)
try:
    with open(recipe_path) as f:
        all_recipes = json.load(f) # Load all recipes initially
except FileNotFoundError:
    print(f"Error: Recipe file not found at {recipe_path}")
    exit()

constraint_path = os.path.join(
    os.path.dirname(__file__),
    'out_build_ontology_pipeline',
    'recommended_recipes',
    'user_constraints.json'
)
try:
    with open(constraint_path) as f:
        user_constraints = json.load(f)
except FileNotFoundError:
    print(f"Error: User constraints file not found at {constraint_path}")
    exit()


ncd_nutrient_map = {
            "hypertension": {
                "Sodium (mg)": "mg",
                "Potassium (mg)": "mg",
                "Fibre (g)": "g",
                "Saturated Fat (g)": "g",
                "Fat (g)": "g",
            },
            "diabetes": {
                "Free Sugar (g)": "g",
                "Fibre (g)": "g",
                "Saturated Fat (g)": "g",
                "Sodium (mg)": "mg",
            },
            "pcos": {
                "Fat (g)": "g",
                "Saturated Fat (g)": "g",
                "Free Sugar (g)": "g",
                "EnergyKcal": "kcal",
                "Sodium (mg)": "mg",
            }
        }

def get_numeric_value(recipe, key):
        try:
            return int(round(float(recipe.get(key, 0) or 0)))
        except (ValueError, TypeError):
            return 0

print("\n\nUser profile:", user_constraints)


course_map = {
    "breakfast": "breakfast", "maincourse": "lunch", "main course": "lunch",
    "main -": "lunch", "lunch": "lunch", "breads": "lunch", "rice": "lunch",
    "dinner": "dinner", "snack": "snacks", "beverage": "snacks", "drink": "snacks",
    "appetizer": "snacks", "appetiser": "snacks", "side dish": "snacks", "side": "snacks",
    "soup": "snacks", "dip": "misc", "chutney": "misc", "dessert": "snacks",
    "sweet": "snacks", "cookie": "snacks", "cookies": "snacks", "biscuit": "misc",
    "jam": "misc", "kulfi": "snacks", "ice-cream": "snacks", "pickles": "misc",
    "accompaniment": "snacks", "basic cooking tips": "misc", "basics": "misc",
    "grilling / barbeque": "dinner", "smoothie": "snacks", "starters": "snacks",
}

nutrient_keys = [
    "EnergyKcal", "Carbohydrates (g)", "Protein (g)", "Fat (g)", "Free Sugar (g)", "Fibre (g)",
    "Saturated Fat (g)", "Monounsaturated Fat (g)", "Polyunsaturated Fat (g)",
    "Cholesterol (mg)", "Calcium (mg)", "Phosphorus (mg)", "Magnesium (mg)", "Sodium (mg)",
    "Potassium (mg)", "Iron (mg)", "Copper (mg)", "Selenium (ug)", "Chromium (mg)",
    "Manganese (mg)", "Molybdenum (mg)", "Zinc (mg)", "Vitamin E (mg)", "Vitamin D2 (ug)",
    "Vitamin K1 (ug)", "Folate (ug)", "Vitamin B1 (mg)", "Vitamin B2 (mg)", "Vitamin B3 (mg)",
    "Vitamin B5 (mg)", "Vitamin B6 (mg)", "Vitamin B7 (ug)", "Vitamin B9 (ug)",
    "Vitamin C (mg)", "Carotenoids (ug)"
]


def normalize(text):
    return text.lower().replace(" ", "").replace("-", "")

# Step 3: Assign meal_time to each recipe for all recipes initially
for r in all_recipes:
    course = r.get("course", "").strip().lower()
    slot = "unspecified"
    if course:
        norm_course = normalize(course)
        for key, val in course_map.items():
            if normalize(key) in norm_course:
                slot = val
                break
    r["meal_time"] = slot

valid_meal_times = {"breakfast", "lunch", "snacks", "dinner"}
# Filter initial set of all recipes to get valid ones
initial_valid_recipes = [
    r for r in all_recipes
    if r["meal_time"] in valid_meal_times
    and r.get("ingredients")
    and not all((r.get(k, 0) == 0 or r.get(k, 0) == "0.0") for k in nutrient_keys)
]

# Start the main loop for generating and refining the meal plan
recipes = list(initial_valid_recipes) # Start with the initial valid recipes
disliked_recipes_cumulative = [] # Keep track of all disliked recipes across iterations

while True:
    print("\n" + "="*30)
    print("Generating Meal Plan...")
    print("="*30)

    if not recipes:
        print("No recipes available to generate a meal plan after removals.")
        break

    # ─── Model and variables ──────────────────────────────────────────────────
    model = cp_model.CpModel()
    N = len(recipes)
    x = [model.NewBoolVar(f"select_{i}") for i in range(N)]
    penalties = []
    meal_times = ["breakfast", "lunch", "snacks", "dinner"]

    # ─── Precompute energy kcal integers (based on current recipes) ──────────
    energy_kcal_int = []
    for r in recipes:
        try:
            kcal_val = float(r.get("EnergyKcal", 0))
            energy_kcal_int.append(int(round(kcal_val)))
        except:
            energy_kcal_int.append(0)

    # ─── Helper functions (use current recipes and x) ─────────────────────────
    def total_of(key: str):
        # Ensure key exists before accessing
        if key not in recipes[0]: # Check if key exists in at least one recipe (assuming consistent keys)
             # Handle missing key - maybe return 0 or raise an error
             print(f"Warning: Nutrient key '{key}' not found in recipes.")
             return 0

        # Ensure the attribute is numeric before summing
        return sum(
            x[i] * get_numeric_value(recipes[i], key) # Use the helper function to get numeric value safely
            for i in range(N)
        )


    def cal_for(slot: str):
        return sum(
            x[i] * energy_kcal_int[i]
            for i in range(N)
            if recipes[i].get("meal_time", "").lower() == slot
        )

    def fat_total(): return total_of("Fat (g)")
    def sat_fat_total(): return total_of("Saturated Fat (g)")

    # ─── Constraints ──────────────────────────────────────────────────────────
    def apply_meal_distribution_constraints():
        present = {
            k.lower() for k, v in user_constraints.get("medical_conditions", {}).items() if v
        }


        if {"hypertension", "diabetes", "pcos"} & present:
            model.Add(sum(x) >= 4) # Use >= 4 to allow for more flexibility
            model.Add(sum(x) <= 6)
        else:
            model.Add(sum(x) == 4)


        if "pcos" in present:
            # Check if calorie_goal is available and is a number
            calorie_goal = user_constraints.get("calorie_goal")
            if isinstance(calorie_goal, (int, float)):
                model.Add(cal_for("dinner") <= int(0.10 * calorie_goal))
            else:
                 # Handle case where calorie_goal is missing or not a number
                 print("Warning: 'calorie_goal' is missing or not a number. Cannot apply PCOS dinner calorie constraint.")
                 pass # For now, do nothing if calorie_goal is not set

            active = user_constraints.get("most_active_before", "").lower()
            if active in meal_times:
                active_cal = cal_for(active)
                for slot in meal_times:
                    if slot != active:
                        # Ensure active_cal and cal_for(slot) are not None or invalid here if using non-numeric calorie_goal
                        model.Add(active_cal >= cal_for(slot)) # Assuming cal_for returns a CP-SAT variable

    def apply_ncd_constraints():
        present = {
            k.lower() for k, v in user_constraints.get("medical_conditions", {}).items() if v
        }
        present_conditions = present # Keep track of present conditions for printing

        kcal = user_constraints.get("calorie_goal", 2000) # Use default if missing
        # Ensure kcal is numeric
        if not isinstance(kcal, (int, float)):
            print("Warning: Calorie goal is not a number, using default 2000 for NCD constraints.")
            kcal = 2000

        MAX_PENALTY_VALUE = 10_000 # adjust if you use a different bound

        # Helper to add penalties
        def add_soft_constraint(condition_name, constraint_desc, penalty_var):
            penalties.append(penalty_var)
            # print(f"Soft constraint for {condition_name} - {constraint_desc}") # Optional: for debugging


        def hypertension():
            sex = user_constraints.get("sex", "F").upper()

            # ── Sodium (soft) ─────────────────────────────────────────────
            min_s   = int((1500 / 2000) * kcal)
            max_s   = int((2300 / 2000) * kcal)
            s_under = model.NewIntVar(0, MAX_PENALTY_VALUE, "ht_sodium_under")
            s_over  = model.NewIntVar(0, MAX_PENALTY_VALUE, "ht_sodium_over")
            model.Add(min_s - total_of("Sodium (mg)") <= s_under)
            model.Add(total_of("Sodium (mg)") - max_s <= s_over)
            add_soft_constraint("Hypertension", "Sodium (under)", s_under)
            add_soft_constraint("Hypertension", "Sodium (over)", s_over)


            # ── Potassium (soft) ──────────────────────────────────────────
            min_k   = int((3500 / 2000) * kcal)
            max_k   = int((5000 / 2000) * kcal) # Added max_k as per original snippet
            k_under = model.NewIntVar(0, MAX_PENALTY_VALUE, "ht_potassium_under")
            k_over  = model.NewIntVar(0, MAX_PENALTY_VALUE, "ht_potassium_over")
            model.Add(min_k - total_of("Potassium (mg)") <= k_under)
            model.Add(total_of("Potassium (mg)") - max_k <= k_over)
            add_soft_constraint("Hypertension", "Potassium (under)", k_under)
            add_soft_constraint("Hypertension", "Potassium (over)", k_over)

            # ── Fibre minimum (soft) ─────────────────────────────────────
            fibre_min = int(((28 if sex == "F" else 38) / 2000) * kcal)
            fibre_under = model.NewIntVar(0, MAX_PENALTY_VALUE, "ht_fibre_under")
            model.Add(fibre_min - total_of("Fibre (g)") <= fibre_under)
            add_soft_constraint("Hypertension", "Fibre (under)", fibre_under)

            # ── Saturated-fat cap (soft) ─────────────────────────────────
            sat_cap = int((0.06 * kcal) / 9)
            sat_over = model.NewIntVar(0, MAX_PENALTY_VALUE, "ht_satfat_over")
            model.Add(total_of("Saturated Fat (g)") - sat_cap <= sat_over)
            add_soft_constraint("Hypertension", "Saturated Fat (over)", sat_over)

            # ── Total-fat cap (soft) ─────────────────────────────────────
            fat_cap = int((0.27 * kcal) / 9)
            fat_over = model.NewIntVar(0, MAX_PENALTY_VALUE, "ht_totalfat_over")
            model.Add(total_of("Fat (g)") - fat_cap <= fat_over)
            add_soft_constraint("Hypertension", "Total Fat (over)", fat_over)


        def diabetes():
            # Ensure kcal is numeric
            kcal = user_constraints.get("calorie_goal", 2000)
            if not isinstance(kcal, (int, float)):
                 kcal = 2000 # Use default if not numeric

            caps = {
                "sugar":     int((0.05 * kcal) / 4),          # ≤ 5 % kcal from free sugar
                "fibre":     int(14 * kcal / 1000),           # ≥ 14 g per 1000 kcal
                "satfat":    int((0.10 * kcal) / 9),          # ≤ 10 % kcal from sat-fat
                "sodium":    int((2300 / 2000) * kcal),       # ≤ 2300 mg scaled to kcal
            }

            sugar_over = model.NewIntVar(0, MAX_PENALTY_VALUE, "dia_sugar_ov")
            model.Add(total_of("Free Sugar (g)")      - caps["sugar"]   <= sugar_over)
            add_soft_constraint("Diabetes", "Sugar (over)", sugar_over)

            fibre_def = model.NewIntVar(0, MAX_PENALTY_VALUE, "dia_fibre_def")
            model.Add(caps["fibre"]                   - total_of("Fibre (g)")        <= fibre_def)
            add_soft_constraint("Diabetes", "Fibre (deficit)", fibre_def)

            satfat_ov = model.NewIntVar(0, MAX_PENALTY_VALUE, "dia_satfat_ov")
            model.Add(total_of("Saturated Fat (g)")   - caps["satfat"]  <= satfat_ov)
            add_soft_constraint("Diabetes", "Sat Fat (over)", satfat_ov)

            sodium_ov = model.NewIntVar(0, MAX_PENALTY_VALUE, "dia_sodium_ov")
            model.Add(total_of("Sodium (mg)")         - caps["sodium"] <= sodium_ov)
            add_soft_constraint("Diabetes", "Sodium (over)", sodium_ov)


        def pcos():
            # Ensure kcal is numeric
            kcal = user_constraints.get("calorie_goal", 2000)
            if not isinstance(kcal, (int, float)):
                 kcal = 2000 # Use default if not numeric

            dinner_over = model.NewIntVar(0, MAX_PENALTY_VALUE, "pcos_dinner_over")
            model.Add(cal_for("dinner") - int(0.10 * kcal) <= dinner_over)
            add_soft_constraint("PCOS", "Dinner Calories (over)", dinner_over)

            active = user_constraints.get("most_active_before", "").lower()
            if active in meal_times:
                a_cal = cal_for(active)
                for slot in meal_times:
                    if slot != active:
                         # Ensure a_cal and cal_for(slot) are valid
                         model.Add(a_cal >= cal_for(slot)) # Assuming cal_for returns a CP-SAT variable


            fat_over = model.NewIntVar(0, MAX_PENALTY_VALUE, "pcos_fat_ov")
            model.Add(fat_total() - int(0.30 * kcal / 9) <= fat_over)
            add_soft_constraint("PCOS", "Total Fat (over)", fat_over)

            for slot in meal_times:
                slot_cal_over = model.NewIntVar(0, MAX_PENALTY_VALUE, f"pcos_{slot}_cal_ov")
                model.Add(cal_for(slot) - int(0.30 * kcal) <= slot_cal_over)
                add_soft_constraint("PCOS", f"{slot.capitalize()} Calories (over)", slot_cal_over)


            sugar_over = model.NewIntVar(0, MAX_PENALTY_VALUE, "pcos_sugar_ov")
            model.Add(
                total_of("Free Sugar (g)") - int(0.05 * kcal / 4)
                <= sugar_over
            )
            add_soft_constraint("PCOS", "Free Sugar (over)", sugar_over)

            min_s = int((1500 / 2000) * kcal)
            max_s = int((2300 / 2000) * kcal)

            sodium_under = model.NewIntVar(0, MAX_PENALTY_VALUE, "pcos_sodium_under")
            model.Add( min_s - total_of("Sodium (mg)") <= sodium_under )
            add_soft_constraint("PCOS", "Sodium (under)", sodium_under)

            sodium_over = model.NewIntVar(0, MAX_PENALTY_VALUE, "pcos_sodium_over")
            model.Add( total_of("Sodium (mg)") - max_s <= sodium_over )
            add_soft_constraint("PCOS", "Sodium (over)", sodium_over)


        present_conditions_for_display = {k.lower() for k, v in user_constraints.get("medical_conditions", {}).items() if v} # Use a different name to avoid conflict


        if "pcos" in present_conditions_for_display: pcos()
        if "diabetes" in present_conditions_for_display: diabetes()
        if "hypertension" in present_conditions_for_display: hypertension()


    # ─── Solve model ──────────────────────────────────────────────────────────
    apply_meal_distribution_constraints()
    apply_ncd_constraints()


    MEAL_SELECTION_PENALTY_WEIGHT = 50 # Example weight

    # Soft constraints to encourage selection of at least one recipe per meal type
    meal_types_to_check = ["breakfast", "lunch", "snacks", "dinner"]
    for meal_type in meal_types_to_check:
        meal_type_idxs = [i for i, r in enumerate(recipes) if r.get("meal_time") == meal_type]
        if meal_type_idxs:
            print(f"Recipes available for {meal_type}: {len(meal_type_idxs)}")
            has_meal_type = model.NewBoolVar(f"has_{meal_type}")
            model.Add(sum(x[i] for i in meal_type_idxs) >= 1).OnlyEnforceIf(has_meal_type)
            no_meal_type_penalty = model.NewIntVar(0, MEAL_SELECTION_PENALTY_WEIGHT, f"no_{meal_type}_penalty")
            model.Add(no_meal_type_penalty == MEAL_SELECTION_PENALTY_WEIGHT * (1 - has_meal_type))
            penalties.append(no_meal_type_penalty)
        else:
            print(f"No recipes available for {meal_type}. Cannot add soft constraint.")


    model.Minimize(sum(penalties))

    solver = cp_model.CpSolver()
    solver.parameters.random_seed = random.randint(1, 10000)
    status = solver.Solve(model)

    print("\n\nSOLVER OBJECTIVE VALUE:", solver.ObjectiveValue())
    print("Status:", solver.StatusName(status))

    print("\n--- NCD Wise Nutritional Summary ---")
    present_conditions = {k.lower() for k, v in user_constraints.get("medical_conditions", {}).items() if v}
    total_calorie_goal = user_constraints.get("calorie_goal", 2000) # Get goal again

    # Recalculate targets here for printing
    # This assumes your target calculations in apply_ncd_constraints are based on total_calorie_goal
    # You might need to adjust calculations based on your specific logic
    target_sodium_max = int((2300 / 2000) * total_calorie_goal) if total_calorie_goal else 0
    target_sodium_min = int((1500 / 2000) * total_calorie_goal) if total_calorie_goal else 0 # Example min target
    target_sugar_cap = int(0.05 * total_calorie_goal / 4) if total_calorie_goal else 0
    target_fibre_min = int(14 * total_calorie_goal / 1000) if total_calorie_goal else 0
    target_satfat_cap = int(0.10 * total_calorie_goal / 9) if total_calorie_goal else 0
    target_fat_cap = int(0.30 * total_calorie_goal / 9) if total_calorie_goal else 0
    # target_allowed_calories = ... # Your logic to calculate meal slot targets if printing calorie distribution

    # --- Print NCD sections based on active conditions ---
    if "hypertension" in present_conditions:
        kcal = user_constraints.get("calorie_goal", 2000)
        sex  = user_constraints.get("sex", "F").upper()
        pot_min = int((3500 / 2000) * kcal)
        pot_max = int((5000 / 2000) * kcal)

        print("\nHypertension in Focus:")
        # Ensure total_of("Sodium (mg)") is defined and accessible to solver.Value()
        try:
            achieved_sodium = solver.Value(total_of("Sodium (mg)"))
            print(f"    Sodium (mg): Achieved = {achieved_sodium} mg")
            if target_sodium_min > 0 or target_sodium_max > 0:
                target_range_str = f"{target_sodium_min} - {target_sodium_max} mg" if target_sodium_min > 0 else f"<= {target_sodium_max} mg"
                print(f"    Recommended Target: {target_range_str}")
        except Exception as e:
            print(f"  Could not retrieve Sodium (mg) value: {e}")
        
        achieved_pot = solver.Value(total_of("Potassium (mg)"))
        print(f"    Potassium (mg):  Achieved = {achieved_pot} mg, "
            f"Recommended = {pot_min} – {pot_max} mg")

        # ❷ Fibre minimum (28 g female  / 38 g male  per 2 000 kcal)
        fibre_min = int(((28 if sex == "F" else 38) / 2000) * kcal)
        achieved_fibre = solver.Value(total_of("Fibre (g)"))
        print(f"    Fibre (g):      Achieved = {achieved_fibre} g, "
            f"Recommended ≥ {fibre_min} g")

        # ❸ Saturated-fat cap (≤ 6 % kcal)
        satfat_cap = int((0.06 * kcal) / 9)
        achieved_satfat = solver.Value(total_of("Saturated Fat (g)"))
        print(f"    Saturated Fat (g): Achieved = {achieved_satfat} g, "
            f"Recommended ≤ {satfat_cap} g")

        # ❹ Total-fat cap (≤ 27 % kcal)
        fat_cap = int((0.27 * kcal) / 9)
        achieved_fat = solver.Value(total_of("Fat (g)"))
        print(f"    Total Fat (g):  Achieved = {achieved_fat} g, "
            f"Recommended ≤ {fat_cap} g")


    if "diabetes" in present_conditions:
        print("\nDiabetes in Focus:")
        try:
            achieved_sugar = solver.Value(total_of("Free Sugar (g)"))
            achieved_fibre = solver.Value(total_of("Fibre (g)"))
            achieved_satfat = solver.Value(total_of("Saturated Fat (g)"))
            achieved_sodium = solver.Value(total_of("Sodium (mg)"))

            print(f"  Free Sugar (g): Achieved = {achieved_sugar} g, Recommended Target = <= {target_sugar_cap} g")
            print(f"  Fibre (g): Achieved = {achieved_fibre} g, Recommended Target = >= {target_fibre_min} g")
            print(f"  Saturated Fat (g): Achieved = {achieved_satfat} g, Recommended Target = <= {target_satfat_cap} g")
            print(f"  Sodium (mg): Achieved = {achieved_sodium} g, Recommended Target = <= {target_sodium_max} g")

        except Exception as e:
            print(f"  Could not retrieve Diabetes-related nutrient values: {e}")


    if "pcos" in present_conditions:
        print("\nPCOS in Focus:")
        try:
            achieved_total_cal = solver.Value(sum(x[i] * energy_kcal_int[i] for i in range(N)))
            achieved_fat = solver.Value(total_of("Fat (g)"))
            # SatFat and Sugar might be printed under Diabetes if active, or here if only PCOS
            achieved_satfat_pcos = solver.Value(total_of("Saturated Fat (g)"))
            achieved_sugar_pcos = solver.Value(total_of("Free Sugar (g)"))
            achieved_sodium    = solver.Value(total_of("Sodium (mg)"))


            print(f"  Total Calories (kcal): Achieved = {achieved_total_cal}, Recommended Target = ~{total_calorie_goal}")
            print(f"  Total Fat (g): Achieved = {achieved_fat} g, Recommended Target = <= {target_fat_cap} g")
            # Only print if not already covered by Diabetes or if targets are different
            if "diabetes" not in present_conditions:
                print(f"  Saturated Fat (g): Achieved = {achieved_satfat_pcos} g, Recommended Target = <= {target_satfat_cap} g")
                print(f"  Free Sugar (g): Achieved = {achieved_sugar_pcos} g, Recommended Target = <= {target_sugar_cap} g")
            print(
                f"  Sodium (mg): Achieved = {achieved_sodium} mg, "
                f"  Recommended Window = {target_sodium_min}–{target_sodium_max} mg"
            )

            # If you have meal slot calorie targets for PCOS:
            # print("\n  Calories per Slot (PCOS):")
            # for slot in ["Breakfast", "Lunch", "Snacks", "Dinner"]:
            #      achieved_slot_cal = solver.Value(cal_for(slot.lower()))
            #      target_slot_cal = target_allowed_calories.get(slot.lower(), 0) # Get target if available
            #      print(f"    {slot}: Achieved = {achieved_slot_cal} kcal, Recommended Target = ~{target_slot_cal} kcal")

        except Exception as e:
            print(f" Could not retrieve PCOS-related nutrient/calorie values: {e}")

    if not present_conditions:
        # No NCDs present
        print("No health conditions detected. Showing general nutrition info.")
        print("\nGeneral Nutrition Summary:")
        
        achieved_total_cal = solver.Value(sum(x[i] * energy_kcal_int[i] for i in range(N)))
        achieved_fat       = solver.Value(total_of("Fat (g)"))
        achieved_satfat    = solver.Value(total_of("Saturated Fat (g)"))
        achieved_sugar     = solver.Value(total_of("Free Sugar (g)"))
        achieved_sodium    = solver.Value(total_of("Sodium (mg)"))
        achieved_potassium = solver.Value(total_of("Potassium (mg)"))
        achieved_fibre     = solver.Value(total_of("Fibre (g)"))

        # General Recommended Targets (for healthy adult ~2000 kcal diet)
        total_calorie_goal = user_constraints.get("calorie_goal", 2000)
        fat_cap        = int((0.3 * total_calorie_goal) / 9)    # ≤ 30% of kcal, 9 kcal/g
        satfat_cap     = int((0.10 * total_calorie_goal) / 9)   # ≤ 10% of kcal
        sugar_cap      = int((0.05 * total_calorie_goal) / 4)   # ≤ 5% of kcal, 4 kcal/g
        sodium_max     = 2300  # mg/day
        potassium_min  = 3500  # mg/day
        fibre_min      = int(14 * total_calorie_goal / 1000) 
        
        print(f"  Total Calories (kcal): Achieved = {achieved_total_cal}, Recommended Target = ~{total_calorie_goal} kcal")
        print(f"  Total Fat (g): Achieved = {achieved_fat} g, Recommended = ≤ {fat_cap} g")
        print(f"  Saturated Fat (g): Achieved = {achieved_satfat} g, Recommended = ≤ {satfat_cap} g")
        print(f"  Free Sugar (g): Achieved = {achieved_sugar} g, Recommended = ≤ {sugar_cap} g")
        print(f"  Sodium (mg): Achieved = {achieved_sodium} mg, Recommended = ≤ {sodium_max} mg")
        print(f"  Potassium (mg): Achieved = {achieved_potassium} mg, Recommended = ≥ {potassium_min} mg")
        print(f"  Fibre (g): Achieved = {achieved_fibre} g, Recommended = ≥ {fibre_min} g")


    # ─── Process and display results ──────────────────────────────────────────
    selected_recipes_current_run = [] # Store selected recipes for this iteration

    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        print("\nHere’s your personalized meal plan:")
        meal_plan_display = defaultdict(list)
        for i, r in enumerate(recipes):
            if solver.Value(x[i]):
                selected_recipes_current_run.append(r)
                slot = r.get("meal_time", "Unspecified").capitalize()
                meal_plan_display[slot].append(r)

        # Use the present_conditions_for_display determined in apply_ncd_constraints
        present_conditions_for_display = {k.lower() for k, v in user_constraints.get("medical_conditions", {}).items() if v}


        for slot in ["Breakfast", "Lunch", "Snacks", "Dinner"]:
            items = meal_plan_display.get(slot)
            if items:
                print(f"\n{slot}:")
                for r in items:
                    recipe_name = r.get("name", "Unknown Recipe").replace("_", " ").title()
                    print(f"  {recipe_name}") # Print recipe name without bullet

                    nutrient_details = []
                    for condition in present_conditions_for_display:
                        for nutrient, unit in ncd_nutrient_map.get(condition, {}).items():
                            if nutrient in r:
                                val = get_numeric_value(r, nutrient)
                                nutrient_details.append(f"    {nutrient}: {val}{unit}") # Indent nutrient details

                    if nutrient_details:
                        for detail in nutrient_details:
                            print(detail) # Print each nutrient detail on a new line

    else:
        print("\nSorry, no feasible plan could be generated with the current recipe list.")
        # If no feasible plan, ask if they want to remove any anyway or exit
        user_action = input("\nNo feasible plan found. Do you want to try removing some recipes to see if a plan can be generated? (yes/no): ").lower()
        if user_action != 'yes':
             break # Exit the loop if they don't want to try removing

    # ─── Ask user to remove recipes ─────────────────────────────────────────
    # Only ask to remove from selected if a plan was generated and has recipes
    if selected_recipes_current_run and status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        while True: # Inner loop for getting valid recipe removal input
            print("\nSelected recipes from this plan to potentially remove:")
            for i, recipe in enumerate(selected_recipes_current_run):
                 print(f"{i + 1}. {recipe.get('name', 'Unknown Recipe').replace('_', ' ').title()}")
                 # Optionally print nutrient details here too if helpful for removal decision
                 # You could add the nutrient printing logic from above here if desired

            user_input = input("\nEnter the numbers of recipes you dislike and want to remove from future plans, separated by commas (e.g., 1, 3, 5), or type 'n' if you are satisfied: ")

            if user_input.lower() == 'n':
                break # Exit the inner loop, user is satisfied and will break main loop later

            try:
                indices_to_remove = [int(x.strip()) - 1 for x in user_input.split(',')]
                valid_indices = sorted([idx for idx in indices_to_remove if 0 <= idx < len(selected_recipes_current_run)], reverse=True)

                if not valid_indices:
                    print("No valid recipe numbers entered. Please try again or type 'n'.")
                    continue

                removed_count = 0
                for index in valid_indices:
                    # Add the full recipe dictionary to the cumulative disliked list
                    recipe_to_add = selected_recipes_current_run[index]
                    if recipe_to_add not in disliked_recipes_cumulative: # Avoid adding duplicates
                         disliked_recipes_cumulative.append(recipe_to_add)
                         removed_count += 1

                if removed_count > 0:
                     print(f"Marked {removed_count} recipe(s) for removal in the next iteration.")
                     break # Exit the inner loop after processing valid removals
                else:
                     print("The numbers entered correspond to recipes already marked for removal or are invalid. Please try again or type 'n'.")


            except ValueError:
                print("Invalid input format. Please enter numbers separated by commas or 'n'.")

    # If no recipes were selected in this run OR no feasible plan was found, allow removing from the full list
    elif status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        user_input = input("\nNo recipes were selected in this attempt. Do you want to remove recipes from the *entire available* list to try again? (yes/no): ").lower()
        if user_input != 'yes':
            break # Exit the main loop if they don't want to remove from the full list

        # If they want to remove from the full list, display the full list of *available* recipes
        available_to_remove_from = [r for r in initial_valid_recipes if r not in disliked_recipes_cumulative]
        if not available_to_remove_from:
            print("\nNo additional recipes available to remove.")
            break # Exit the main loop if no more recipes to remove from

        print("\nAvailable recipes to remove from:")
        # Create a temporary mapping for display indices
        # available_map = {i + 1: recipe for i, recipe in enumerate(available_to_remove_from)} # Not directly used, but good for understanding
        for i, recipe in enumerate(available_to_remove_from):
             print(f"{i + 1}. {recipe.get('name', 'Unknown Recipe').replace('_', ' ').title()}")


        user_remove_input = input("\nEnter the numbers of recipes you dislike and want to remove, separated by commas, or type 'n' to exit: ")

        if user_remove_input.lower() == 'n':
            break # Exit the main loop

        try:
             indices_to_remove = [int(x.strip()) - 1 for x in user_remove_input.split(',')]
             # Map the input index back to the recipe in available_to_remove_from
             valid_recipes_to_add_to_disliked = []
             for index in indices_to_remove:
                 if 0 <= index < len(available_to_remove_from):
                     recipe_to_add = available_to_remove_from[index]
                     if recipe_to_add not in disliked_recipes_cumulative: # Avoid adding duplicates
                         valid_recipes_to_add_to_disliked.append(recipe_to_add)
                 else:
                     print(f"Invalid recipe number: {index + 1}")

             if valid_recipes_to_add_to_disliked:
                 disliked_recipes_cumulative.extend(valid_recipes_to_add_to_disliked)
                 print(f"Marked {len(valid_recipes_to_add_to_disliked)} recipe(s) for removal in the next iteration.")
             else:
                 print("No valid recipes selected for removal or recipes already marked. Please try again or type 'n'.")


        except ValueError:
             print("Invalid input format. Please enter numbers separated by commas or 'n'.")


    # ─── Filter recipes for the next iteration ──────────────────────────────
    # This filtering happens whether recipes were selected in the last run or not,
    # as long as the user didn't choose to exit.
    if disliked_recipes_cumulative:
        # Filter the initial set of valid recipes based on the cumulative disliked list
        recipes = [r for r in initial_valid_recipes if r not in disliked_recipes_cumulative]
        print(f"\nTotal {len(disliked_recipes_cumulative)} recipe(s) marked for exclusion in the next meal plan generation.")
        if not recipes:
            print("After removing disliked recipes, no recipes remain. Exiting.")
            break # Exit if no recipes are left
    else:
        # If the inner loop (or the fallback removal section) finished and no *new* recipes
        # were added to disliked_recipes_cumulative, it means the user is satisfied (typed 'n')
        # or there were no recipes to remove. Break the main loop.
        break

# ─── End of main while loop ───────────────────────────────────────────────

print("\nMeal plan generation finished.")
if disliked_recipes_cumulative:
    print("\nRecipes excluded from the final plan:")
    for recipe in disliked_recipes_cumulative:
        print(f"- {recipe.get('name', 'Unknown Recipe').replace('_', ' ').title()}")
def get_numeric_value(recipe, key):
    try:
        return int(round(float(recipe.get(key, 0) or 0)))
    except (ValueError, TypeError):
        return 0

if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
    meal_plan = defaultdict(list)
    for i, r in enumerate(recipes):
        if solver.Value(x[i]):
            slot = r.get("meal_time", "Unspecified").capitalize()
            meal_plan[slot].append(r)

    print("\nHere’s your personalized meal plan:")
    for slot in ["Breakfast", "Lunch", "Snacks", "Dinner"]:
        items = meal_plan.get(slot)
        if items:
            print(f"\n{slot}:")
            for r in items:
                recipe_name = r["name"].replace("_", " ").title()
                nutrient_tags = []

                for condition in present_conditions:
                    for nutrient, unit in ncd_nutrient_map.get(condition, {}).items():
                        if nutrient in r:
                            val = get_numeric_value(r, nutrient)
                            nutrient_tags.append(f"{nutrient}: {val} {unit}")

                nutrient_str = f" ({', '.join(nutrient_tags)})" if nutrient_tags else ""
                print(f"  • {recipe_name}{nutrient_str}")
else:
    print("\nSorry, no feasible plan could be generated.")