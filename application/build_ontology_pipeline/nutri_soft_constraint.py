from ortools.sat.python import cp_model
import json
import os
import random
from collections import defaultdict, Counter
import copy

BASE_DIR = os.path.dirname(__file__)
RECIPE_PATH = os.path.join(BASE_DIR, 'out_build_ontology_pipeline', 'recommended_recipes', 'hard_constraint_recommended_recipes.json')
CONSTRAINT_PATH = os.path.join(BASE_DIR, 'out_build_ontology_pipeline', 'recommended_recipes', 'user_constraints.json')

NCD_NUTRIENT_MAP = {
    "hypertension": {
        "Sodium (mg)": "mg", "Potassium (mg)": "mg", "Fibre (g)": "g",
        "Saturated Fat (g)": "g", "Fat (g)": "g",
    },
    "diabetes": {
        "Free Sugar (g)": "g", "Fibre (g)": "g", "Saturated Fat (g)": "g",
        "Sodium (mg)": "mg", "Fat (g)": "g",
    },
    "pcos": {
        "Fat (g)": "g", "Saturated Fat (g)": "g", "Free Sugar (g)": "g",
        "EnergyKcal": "kcal", "Sodium (mg)": "mg",
    }
}

COURSE_MAP = {
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

NUTRIENT_KEYS = [
    "EnergyKcal", "Carbohydrates (g)", "Protein (g)", "Fat (g)", "Free Sugar (g)", "Fibre (g)",
    "Saturated Fat (g)", "Monounsaturated Fat (g)", "Polyunsaturated Fat (g)",
    "Cholesterol (mg)", "Calcium (mg)", "Phosphorus (mg)", "Magnesium (mg)", "Sodium (mg)",
    "Potassium (mg)", "Iron (mg)", "Copper (mg)", "Selenium (ug)", "Chromium (mg)",
    "Manganese (mg)", "Molybdenum (mg)", "Zinc (mg)", "Vitamin E (mg)", "Vitamin D2 (ug)",
    "Vitamin K1 (ug)", "Folate (ug)", "Vitamin B1 (mg)", "Vitamin B2 (mg)", "Vitamin B3 (mg)",
    "Vitamin B5 (mg)", "Vitamin B6 (mg)", "Vitamin B7 (ug)", "Vitamin B9 (ug)",
    "Vitamin C (mg)", "Carotenoids (ug)"
]

MEAL_TIMES = ["breakfast", "lunch", "snacks", "dinner"]
VALID_MEAL_TIMES_SET = set(MEAL_TIMES)
MAX_PENALTY_VALUE = 10000
MEAL_SELECTION_PENALTY_WEIGHT = 50

def load_json_data(file_path):
    with open(file_path) as f:
        return json.load(f)

def get_numeric_value(recipe, key):
    try:
        return int(round(float(recipe.get(key, 0) or 0)))
    except (ValueError, TypeError):
        return 0

def normalize_text(text):
    return text.lower().replace(" ", "").replace("-", "")

def preprocess_recipes(raw_recipes, course_map_dict, valid_meal_times_set, nutrient_keys_list):
    processed_recipes = []
    for r_orig in raw_recipes:
        r = copy.deepcopy(r_orig)
        course = r.get("course", "").strip().lower()
        slot = "unspecified"
        if course:
            norm_course = normalize_text(course)
            for key, val in course_map_dict.items():
                if normalize_text(key) in norm_course:
                    slot = val
                    break
        r["meal_time"] = slot
        
        r["energy_kcal_int"] = get_numeric_value(r, "EnergyKcal")

        is_valid_meal_time = r["meal_time"] in valid_meal_times_set
        has_ingredients = bool(r.get("ingredients"))
        has_nutrients = not all(get_numeric_value(r, k) == 0 for k in nutrient_keys_list)

        if is_valid_meal_time and has_ingredients and has_nutrients:
            processed_recipes.append(r)
    return processed_recipes

def get_total_nutrient_expr(model, x_vars, current_recipes, nutrient_key):
    terms = []
    for i, recipe in enumerate(current_recipes):
        terms.append(x_vars[i] * get_numeric_value(recipe, nutrient_key))
    if not terms: 
        return model.NewIntVar(0,0, f"empty_total_{nutrient_key.replace(' ','_')}") 
    return sum(terms)


def get_calories_for_slot_expr(model, x_vars, current_recipes, meal_slot):
    terms = []
    for i, recipe in enumerate(current_recipes):
        if recipe.get("meal_time", "").lower() == meal_slot:
            terms.append(x_vars[i] * recipe["energy_kcal_int"])
    if not terms:
         return model.NewIntVar(0,0, f"empty_cal_{meal_slot}") 
    return sum(terms)

def apply_meal_distribution_constraints(model, x_vars, user_constraints_dict, current_recipes):
    present_conditions = {
        k.lower() for k, v in user_constraints_dict.get("medical_conditions", {}).items() if v
    }
    total_selected_recipes = sum(x_vars)

    if {"hypertension", "diabetes", "pcos"} & present_conditions:
        model.Add(total_selected_recipes >= 4)
        model.Add(total_selected_recipes <= 6)
    else:
        model.Add(total_selected_recipes == 4)

    if "pcos" in present_conditions:
        active_time = user_constraints_dict.get("most_active_before", "").lower()
        if active_time in MEAL_TIMES:
            active_calories = get_calories_for_slot_expr(model, x_vars, current_recipes, active_time)
            for slot in MEAL_TIMES:
                if slot != active_time:
                    slot_calories = get_calories_for_slot_expr(model, x_vars, current_recipes, slot)
                    model.Add(active_calories >= slot_calories)

def apply_ncd_constraints(model, x_vars, current_recipes, user_constraints_dict, penalties_list):
    present_conditions = {
        k.lower() for k, v in user_constraints_dict.get("medical_conditions", {}).items() if v
    }
    kcal = user_constraints_dict.get("calorie_goal", 2000)
    if not isinstance(kcal, (int, float)): kcal = 2000

    def add_soft_penalty(description, actual_expr, target_expr, is_less_than_target, penalty_name):
        penalty_var = model.NewIntVar(0, MAX_PENALTY_VALUE, penalty_name)
        if is_less_than_target:
            model.Add(target_expr - actual_expr <= penalty_var)
        else:
            model.Add(actual_expr - target_expr <= penalty_var)
        penalties_list.append(penalty_var)

    if "hypertension" in present_conditions:
        sex = user_constraints_dict.get("sex", "F").upper()
        
        sodium_total = get_total_nutrient_expr(model, x_vars, current_recipes, "Sodium (mg)")
        min_s = int((1500 / 2000) * kcal)
        max_s = int((2300 / 2000) * kcal)
        add_soft_penalty("HT Sodium Low", sodium_total, min_s, True, "ht_sodium_under")
        add_soft_penalty("HT Sodium High", sodium_total, max_s, False, "ht_sodium_over")

        potassium_total = get_total_nutrient_expr(model, x_vars, current_recipes, "Potassium (mg)")
        min_k = int((3500 / 2000) * kcal)
        max_k = int((5000 / 2000) * kcal)
        add_soft_penalty("HT Potassium Low", potassium_total, min_k, True, "ht_potassium_under")
        add_soft_penalty("HT Potassium High", potassium_total, max_k, False, "ht_potassium_over")
        
        sat_fat_total = get_total_nutrient_expr(model, x_vars, current_recipes, "Saturated Fat (g)")
        sat_cap = int((0.06 * kcal) / 9)
        add_soft_penalty("HT SatFat High", sat_fat_total, sat_cap, False, "ht_satfat_over")

        fat_total_expr = get_total_nutrient_expr(model, x_vars, current_recipes, "Fat (g)")
        fat_cap = int((0.27 * kcal) / 9)
        add_soft_penalty("HT TotalFat High", fat_total_expr, fat_cap, False, "ht_totalfat_over")

    if "diabetes" in present_conditions:
        sugar_total = get_total_nutrient_expr(model, x_vars, current_recipes, "Free Sugar (g)")
        sugar_cap = int((0.05 * kcal) / 4)
        add_soft_penalty("Dia Sugar High", sugar_total, sugar_cap, False, "dia_sugar_ov")

        fibre_total = get_total_nutrient_expr(model, x_vars, current_recipes, "Fibre (g)")
        fibre_min_dia = int(14 * kcal / 1000)
        add_soft_penalty("Dia Fibre Low", fibre_total, fibre_min_dia, True, "dia_fibre_def")

        sat_fat_total = get_total_nutrient_expr(model, x_vars, current_recipes, "Saturated Fat (g)")
        sat_fat_cap_dia = int((0.10 * kcal) / 9)
        add_soft_penalty("Dia SatFat High", sat_fat_total, sat_fat_cap_dia, False, "dia_satfat_ov")

        sodium_total = get_total_nutrient_expr(model, x_vars, current_recipes, "Sodium (mg)")
        sodium_cap_dia = int((2300 / 2000) * kcal)
        add_soft_penalty("Dia Sodium High", sodium_total, sodium_cap_dia, False, "dia_sodium_ov")

        fat_total_dia = get_total_nutrient_expr(model, x_vars, current_recipes, "Fat (g)")
        min_fat_dia = int((0.25 * kcal) / 9)
        max_fat_dia = int((0.35 * kcal) / 9)
        add_soft_penalty("Diabetes Total Fat Low", fat_total_dia, min_fat_dia, True, "dia_total_fat_under")
        add_soft_penalty("Diabetes Total Fat High", fat_total_dia, max_fat_dia, False, "dia_total_fat_over")

    if "pcos" in present_conditions:
        dinner_cal = get_calories_for_slot_expr(model, x_vars, current_recipes, "dinner")
        dinner_cal_cap = int(0.10 * kcal)
        add_soft_penalty("PCOS Dinner Cal High", dinner_cal, dinner_cal_cap, False, "pcos_dinner_over")
        
        fat_total_expr_pcos = get_total_nutrient_expr(model, x_vars, current_recipes, "Fat (g)")
        fat_total_cap_pcos = int(0.30 * kcal / 9)
        add_soft_penalty("PCOS Total Fat High", fat_total_expr_pcos, fat_total_cap_pcos, False, "pcos_fat_ov")

        sat_fat_total_pcos = get_total_nutrient_expr(model, x_vars, current_recipes, "Saturated Fat (g)")
        sat_fat_cap_pcos = int((0.10 * kcal) / 9)
        add_soft_penalty("PCOS SatFat High", sat_fat_total_pcos, sat_fat_cap_pcos, False, "pcos_satfat_ov")

        active_time_pcos = user_constraints_dict.get("most_active_before", "").lower()
        for slot in MEAL_TIMES:
            slot_cal = get_calories_for_slot_expr(model, x_vars, current_recipes, slot)
            slot_cal_cap_pcos_meal = 0
            penalty_tag = ""
            if active_time_pcos in MEAL_TIMES and slot == active_time_pcos:
                slot_cal_cap_pcos_meal = int(0.40 * kcal) 
                penalty_tag = f"PCOS {slot} (Active) Cal High"
            else:
                slot_cal_cap_pcos_meal = int(0.30 * kcal)
                penalty_tag = f"PCOS {slot} Cal High"
            add_soft_penalty(penalty_tag, slot_cal, slot_cal_cap_pcos_meal, False, f"pcos_{slot}_cal_ov")

        sugar_total_pcos = get_total_nutrient_expr(model, x_vars, current_recipes, "Free Sugar (g)")
        sugar_cap_pcos = int(0.05 * kcal / 4)
        add_soft_penalty("PCOS Sugar High", sugar_total_pcos, sugar_cap_pcos, False, "pcos_sugar_ov")

        sodium_total_pcos = get_total_nutrient_expr(model, x_vars, current_recipes, "Sodium (mg)")
        min_s_pcos = int((1500 / 2000) * kcal)
        max_s_pcos = int((2300 / 2000) * kcal)
        add_soft_penalty("PCOS Sodium Low", sodium_total_pcos, min_s_pcos, True, "pcos_sodium_under")
        add_soft_penalty("PCOS Sodium High", sodium_total_pcos, max_s_pcos, False, "pcos_sodium_over")


def apply_meal_selection_soft_constraints(model, x_vars, current_recipes, penalties_list):
    for meal_type in MEAL_TIMES:
        meal_type_indices = [i for i, r in enumerate(current_recipes) if r.get("meal_time") == meal_type]
        if meal_type_indices:
            has_meal_type_bool = model.NewBoolVar(f"has_{meal_type}")
            model.Add(sum(x_vars[i] for i in meal_type_indices) >= 1).OnlyEnforceIf(has_meal_type_bool)
            
            no_meal_type_penalty_var = model.NewIntVar(0, MEAL_SELECTION_PENALTY_WEIGHT, f"no_{meal_type}_penalty")
            model.Add(no_meal_type_penalty_var == MEAL_SELECTION_PENALTY_WEIGHT * (1 - has_meal_type_bool))
            penalties_list.append(no_meal_type_penalty_var)
        else:
            print(f"No recipes available for {meal_type}. Cannot add soft constraint.")


def print_nutritional_summary(solver, x_vars, current_recipes, user_constraints_dict, ncd_map, total_recipes_selected_count):
    print("\n--- Nutritional Summary ---")
    present_conditions = {k.lower() for k, v in user_constraints_dict.get("medical_conditions", {}).items() if v}
    total_calorie_goal = user_constraints_dict.get("calorie_goal", 2000)
    if not isinstance(total_calorie_goal, (int, float)): total_calorie_goal = 2000
    
    achieved_nutrients = {}
    for key in NUTRIENT_KEYS:
        val_sum = 0
        for i, r in enumerate(current_recipes):
            if solver.Value(x_vars[i]):
                val_sum += get_numeric_value(r, key)
        achieved_nutrients[key] = val_sum
    
    achieved_calories_per_slot = {}
    for slot in MEAL_TIMES:
        slot_sum = 0
        for i, r in enumerate(current_recipes):
             if solver.Value(x_vars[i]) and r.get("meal_time", "").lower() == slot:
                slot_sum += r["energy_kcal_int"]
        achieved_calories_per_slot[slot] = slot_sum


    print(f"Total Recipes Selected: {total_recipes_selected_count}")
    print(f"Total Calories Achieved: {achieved_nutrients.get('EnergyKcal', 0)} kcal (Goal: ~{total_calorie_goal} kcal)")

    if not present_conditions:
        print("\nGeneral Nutrition Guidelines:")
        print(f"  Fat (g): {achieved_nutrients.get('Fat (g)',0)} (Rec: <= {int((0.3 * total_calorie_goal) / 9)} g)")

    if "hypertension" in present_conditions:
        print("\nHypertension Focus:")
        kcal_ht = total_calorie_goal
        sex_ht = user_constraints_dict.get("sex", "F").upper()
        print(f"  Sodium (mg): {achieved_nutrients.get('Sodium (mg)',0)} (Rec: {int((1500/2000)*kcal_ht)}-{int((2300/2000)*kcal_ht)} mg)")
        print(f"  Potassium (mg): {achieved_nutrients.get('Potassium (mg)',0)} (Rec: {int((3500/2000)*kcal_ht)}-{int((5000/2000)*kcal_ht)} mg)")
        print(f"  Saturated Fat (g): {achieved_nutrients.get('Saturated Fat (g)',0)} (Rec: <= {int((0.06*kcal_ht)/9)} g)")
        print(f"  Total Fat (g): {achieved_nutrients.get('Fat (g)',0)} (Rec: <= {int((0.27*kcal_ht)/9)} g)")

    if "diabetes" in present_conditions:
        print("\nDiabetes Focus:")
        kcal_db = total_calorie_goal
        print(f"  Free Sugar (g): {achieved_nutrients.get('Free Sugar (g)',0)} (Rec: <= {int((0.05*kcal_db)/4)} g)")
        print(f"  Fibre (g): {achieved_nutrients.get('Fibre (g)',0)} (Rec: >= {int(14*kcal_db/1000)} g)")
        print(f"  Saturated Fat (g): {achieved_nutrients.get('Saturated Fat (g)',0)} (Rec: <= {int((0.10*kcal_db)/9)} g)")
        print(f"  Sodium (mg): {achieved_nutrients.get('Sodium (mg)',0)} (Rec: <= {int((2300/2000)*kcal_db)} mg)")
        print(f"  Total Fat (g): {achieved_nutrients.get('Fat (g)',0)} (Rec: {int((0.25*kcal_db)/9)}-{int((0.35*kcal_db)/9)} g)")


    if "pcos" in present_conditions:
        print("\nPCOS Focus:")
        kcal_pcos = total_calorie_goal
        print(f"  Dinner Calories (kcal): {achieved_calories_per_slot.get('dinner', 0)} (Rec: <= {int(0.10*kcal_pcos)} kcal)")
        active_time_pcos = user_constraints_dict.get("most_active_before", "").lower()
        if active_time_pcos in MEAL_TIMES:
            print(f"  Calories for most active time ({active_time_pcos}): {achieved_calories_per_slot.get(active_time_pcos, 0)}")
            for slot in MEAL_TIMES:
                 if slot != active_time_pcos:
                      print(f"    vs {slot}: {achieved_calories_per_slot.get(slot,0)}")

        print(f"  Total Fat (g): {achieved_nutrients.get('Fat (g)',0)} (Rec: <= {int(0.30*kcal_pcos/9)} g)")
        print(f"  Saturated Fat (g): {achieved_nutrients.get('Saturated Fat (g)',0)} (Rec: <= {int((0.10*kcal_pcos)/9)} g)")

        for slot in MEAL_TIMES:
            cap_percentage = 0.30
            if active_time_pcos in MEAL_TIMES and slot == active_time_pcos:
                cap_percentage = 0.40
            print(f"  {slot.capitalize()} Calories (kcal): {achieved_calories_per_slot.get(slot,0)} (Rec per meal: <= {int(cap_percentage*kcal_pcos)} kcal)")

        print(f"  Free Sugar (g): {achieved_nutrients.get('Free Sugar (g)',0)} (Rec: <= {int(0.05*kcal_pcos/4)} g)")
        print(f"  Sodium (mg): {achieved_nutrients.get('Sodium (mg)',0)} (Rec: {int((1500/2000)*kcal_pcos)}-{int((2300/2000)*kcal_pcos)} mg)")


if __name__ == "__main__":
    all_raw_recipes = load_json_data(RECIPE_PATH)
    user_constraints_data = load_json_data(CONSTRAINT_PATH)
    
    print("\nUser profile:", user_constraints_data)

    initial_valid_recipes = preprocess_recipes(all_raw_recipes, COURSE_MAP, VALID_MEAL_TIMES_SET, NUTRIENT_KEYS)

    if not initial_valid_recipes:
        print("No valid recipes found after preprocessing. Exiting.")
        exit()
        
    meal_time_counts = Counter(r["meal_time"] for r in initial_valid_recipes)
    print("\nInitial meal time counts from valid recipes:", meal_time_counts)

    disliked_recipes_identifiers = []
    
    recipe_display_counter = 0

    while True:
        recipe_display_counter = 0
        current_iteration_recipes = [
            r for r in initial_valid_recipes 
            if r.get("name") not in disliked_recipes_identifiers
        ]

        if not current_iteration_recipes:
            print("No recipes available to generate a meal plan after removals. Exiting.")
            break

        print(f"\nGenerating Meal Plan with {len(current_iteration_recipes)} available recipes...")

        model = cp_model.CpModel()
        N_current = len(current_iteration_recipes)
        x_vars_current = [model.NewBoolVar(f"select_{i}") for i in range(N_current)]
        penalties_current = []

        apply_meal_distribution_constraints(model, x_vars_current, user_constraints_data, current_iteration_recipes)
        apply_ncd_constraints(model, x_vars_current, current_iteration_recipes, user_constraints_data, penalties_current)
        apply_meal_selection_soft_constraints(model, x_vars_current, current_iteration_recipes, penalties_current)

        if penalties_current:
            model.Minimize(sum(penalties_current))
        else:
            print("Warning: No penalties defined for minimization. Solving for feasibility.")


        solver = cp_model.CpSolver()
        solver.parameters.random_seed = random.randint(1, 10000)
        status = solver.Solve(model)

        print(f"\nSolver Objective Value: {solver.ObjectiveValue() if penalties_current else 'N/A'}")
        print(f"Status: {solver.StatusName(status)}")

        selected_recipes_in_plan = []
        total_selected_count = 0

        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            meal_plan_display = defaultdict(list)
            for i, r_obj in enumerate(current_iteration_recipes):
                if solver.Value(x_vars_current[i]):
                    selected_recipes_in_plan.append(r_obj)
                    slot = r_obj.get("meal_time", "Unspecified").capitalize()
                    meal_plan_display[slot].append(r_obj)
                    total_selected_count +=1
            
            print_nutritional_summary(solver, x_vars_current, current_iteration_recipes, user_constraints_data, NCD_NUTRIENT_MAP, total_selected_count)

            print("\nYour personalized meal plan:")
            present_conds_for_recipe_print = {k.lower() for k, v in user_constraints_data.get("medical_conditions", {}).items() if v}
            for slot_name in ["Breakfast", "Lunch", "Snacks", "Dinner"]:
                items = meal_plan_display.get(slot_name)
                if items:
                    print(f"\n{slot_name}:")
                    for r_item in items:
                        recipe_display_counter += 1
                        recipe_title = r_item.get("name", "Unknown Recipe").replace("_", " ").title()
                        print(f"  {recipe_display_counter}. {recipe_title}")
                        
                        nutrient_details_to_print = []
                        for cond in present_conds_for_recipe_print:
                            for nutri, unit in NCD_NUTRIENT_MAP.get(cond, {}).items():
                                if nutri in r_item:
                                    val = get_numeric_value(r_item, nutri)
                                    nutrient_details_to_print.append(f"    {nutri}: {val}{unit}")
                        if nutrient_details_to_print:
                            for detail_line in nutrient_details_to_print:
                                print(detail_line)
                        print()
        else:
            print("\nSorry, no feasible plan could be generated with the current recipe list and constraints.")

        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE] and selected_recipes_in_plan:
            print("\nSelected recipes from this plan to potentially remove:")
            for i, recipe_in_plan in enumerate(selected_recipes_in_plan):
                 print(f"{i + 1}. {recipe_in_plan.get('name', 'Unknown Recipe').replace('_', ' ').title()}")
            
            user_input = input("\nEnter numbers of recipes you dislike (e.g., 1, 3), or 'n' if satisfied: ").lower()
            if user_input == 'n':
                break 

            try:
                indices_to_remove_from_selection = [int(x.strip()) - 1 for x in user_input.split(',')]
                newly_disliked_count = 0
                for idx in indices_to_remove_from_selection:
                    if 0 <= idx < len(selected_recipes_in_plan):
                        disliked_recipe_name = selected_recipes_in_plan[idx].get("name")
                        if disliked_recipe_name and disliked_recipe_name not in disliked_recipes_identifiers:
                            disliked_recipes_identifiers.append(disliked_recipe_name)
                            newly_disliked_count += 1
                if newly_disliked_count > 0:
                    print(f"Marked {newly_disliked_count} recipe(s) for removal in the next iteration.")
                else:
                    print("No new recipes marked for removal or invalid input.")
            except ValueError:
                print("Invalid input. Please enter numbers separated by commas or 'n'.")
        
        elif status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
             user_action = input("\nNo feasible plan. Try removing more recipes from general consideration? (yes/no): ").lower()
             if user_action != 'yes':
                 break
             print("In the next iteration, recipes previously marked as disliked will remain excluded.")
             if current_iteration_recipes:
                print("\nAvailable recipes from this attempt to mark as disliked for the *next* attempt:")
                for i, r_avail in enumerate(current_iteration_recipes):
                    print(f"{i + 1}. {r_avail.get('name', 'Unknown Recipe').replace('_', ' ').title()}")
                
                user_dislike_more = input("Enter numbers to dislike (e.g., 1,3) or 'n' to try again / exit: ").lower()
                if user_dislike_more != 'n':
                    try:
                        indices_to_dislike_more = [int(x.strip()) - 1 for x in user_dislike_more.split(',')]
                        newly_disliked_more_count = 0
                        for idx_more in indices_to_dislike_more:
                            if 0 <= idx_more < len(current_iteration_recipes):
                                disliked_recipe_name_more = current_iteration_recipes[idx_more].get("name")
                                if disliked_recipe_name_more and disliked_recipe_name_more not in disliked_recipes_identifiers:
                                    disliked_recipes_identifiers.append(disliked_recipe_name_more)
                                    newly_disliked_more_count +=1
                        if newly_disliked_more_count > 0:
                             print(f"Additionally marked {newly_disliked_more_count} recipe(s) for removal.")
                    except ValueError:
                        print("Invalid input for disliking more recipes.")
             else:
                print("No recipes were even considered in this failed attempt.")
                break
        else:
            break


    print("\nMeal plan generation finished.")
    if disliked_recipes_identifiers:
        print("\nFinal list of recipes excluded due to dislike:")
        for name in disliked_recipes_identifiers:
            print(f"- {name.replace('_', ' ').title()}")