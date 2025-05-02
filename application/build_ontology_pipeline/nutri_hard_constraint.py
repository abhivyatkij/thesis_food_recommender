from owlready2 import *
from rdflib import Graph
import json
from merged_food_recipe_design_ontology import designed_merged_ontology

# Load your ontology
owl_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'out_build_ontology_pipeline', 'nutri_mk_vri_recipe_nutrition_calculated.owl')
onto = get_ontology("file://" + owl_file_path ).load()
onto2 = designed_merged_ontology()

#FoodRecipesIRI = onto.search_one(iri="file:/indian_food_ontology.owl#FoodRecipes")
FoodRecipesIRI = onto.FoodRecipes  
IngredientIRI = onto.search_one(iri="file:/indian_food_ontology.owl#FoodIngredients")


VEGETARIAN_EXCLUDE_CLASSES = {
    onto.MeatFromChicken,
    onto.MeatFromPig,
    onto.MeatFromGoat,
    onto.MeatFromLamb,
    onto.MeatFromDeer,
    onto.MiscellaneousMeatFromMammalianProduct,
    onto.MarineProductOrSeafood,
    onto.InsectProduct,
    onto.CannedMeatAndSeafood,
    onto.ReadyToEatFoodWithMeatAndSeafood
}

VEGAN_EXCLUDE_CLASSES = VEGETARIAN_EXCLUDE_CLASSES.union({
    onto.MilkBasedOrDairy,
    onto.AnimalFat
})

#!TODO let the allergies be custom inputted too 
ALLERGY_KEYWORDS = {
    "dairy": ["milk", "cheese", "shredded_cheese", "yogurt", "plain_yogurt", "ghee", "butter", "paneer", "cream"],
    "gluten": ["wheat", "maida", "bread", "semolina", "sooji", "pasta"],
    "nuts": ["peanut", "almond", "cashew", "hazelnut", "walnut"],
    "soy": ["soy", "soybean", "tofu"],
    "shellfish": ["shrimp", "crab", "lobster"],
    # Add more if needed
}

NONVEGETARIAN_KEYWORDS = ["chicken", "fish", "beef", "egg", "mutton", "pork", "shrimp", "meat", "crab", "lobster", "seafood", "prawns", "sardines", "tuna", "salmon", "mackerel", "squid", "octopus"]
VEGAN_KEYWORDS = NONVEGETARIAN_KEYWORDS + ["milk", "cheese", "butter", "yogurt", "paneer", "ghee", "cream"]

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

def get_user_profile():
    # ── basic questions ──────────────────────────────────────────
    age = int(input("Enter your age in years: "))
    sex = input("Enter your sex (M/F): ").strip().upper()
    activity = input("Activity level (sedentary, moderately_active, active): ").strip().lower()
    diet_pref = input("Dietary preference (veg, nonveg, vegan): ").strip().lower()

    medical_condition = {
    "diabetes": input("Do you have diabetes? (y/n): ").strip().lower() == 'y',
    "hypertension": input("Do you have hypertension? (y/n): ").strip().lower() == 'y',
}

    if sex == 'F':
        medical_condition["pcos"] = input("Do you have PCOS? (y/n): ").strip().lower() == 'y'
    else:
        medical_condition["pcos"] = False #

    # ── anthropometrics for BMI & calorie estimate ───────────────
    weight = float(input("Weight (kg): "))
    height_cm = float(input("Height (cm): "))
    height_m = height_cm / 100
    bmi = round(weight / (height_m ** 2), 1)

    # Calculate BMR using Mifflin-St Jeor Equation
    bmr = (10 * weight) + (6.25 * height_cm) - (5 * age) + (5 if sex == "M" else -161)
    activity_factor_map = {
        "sedentary": 1.2,
        "moderately_active": 1.55,
        "active": 1.725
    }
    activity_factor = activity_factor_map.get(activity, 1.2)
    tdee = bmr * activity_factor

    print(f"\n🧮 Your Basal Metabolic Rate (BMR) is approximately {int(bmr)} kcal/day.")
    print(f"🚶 Based on your activity level ('{activity}'), your Total Daily Energy Expenditure (TDEE) is approximately {int(tdee)} kcal/day.")

    # ── allergies -------------------------------------------------
    allergies_input = input("Any allergies? (comma-separated, or leave blank): ").strip()
    allergies = [a.strip().lower() for a in allergies_input.split(",")] if allergies_input else []

    # ── per‑meal avoid list --------------------------------------
    avoid_food_preference = {}
    if input("Do you want to avoid any food types at specific meals? (y/N): ").strip().lower() == "y":
        print("Enter comma‑separated foods to avoid for each meal; press Enter to skip a meal.")
        for slot in ["breakfast", "lunch", "snacks", "dinner"]:
            items = input(f"  {slot.capitalize()}: ").strip().lower()
            if items:
                avoid_food_preference[slot] = [x.strip() for x in items.split(",") if x.strip()]

    # ── optional calorie goal if overweight ----------------------
    calorie_goal = None
    if bmi >= 25:
        print(f"\n⚠️ Your BMI is {bmi} (≥ 25). Caloric restriction may be beneficial.")
        suggested = int(max(1200 if sex == "F" else 1500, tdee - 500))
        print(f"⚖️ Based on your stats, a weight-loss target of ≈ {suggested} kcal/day is suggested.")
        if input("Would you like to adopt this calorie limit? (y/N): ").strip().lower() == "y":
            calorie_goal = suggested
    else:
        print("✅ BMI is in the normal range; no calorie restriction is suggested.")
        if input("Would you like to use your TDEE as your calorie goal? (y/N): ").strip().lower() == "y":
            calorie_goal = int(tdee)

    # ── normalise diet ───────────────────────────────────────────
    diet_map = {"veg": "vegetarian", "nonveg": "non vegetarian", "vegan": "vegan"}
    diet = diet_map.get(diet_pref, diet_pref)

    # ── assemble user_constraints dictionary ─────────────────────
    user_constraints = {
        "age": age,
        "sex": sex,
        "activity_level": activity,
        "diet": diet,
        "allergies": allergies,
        "medical_conditions": medical_condition,
        "avoid_food_preference": avoid_food_preference,
    }
    if calorie_goal:
        user_constraints["calorie_goal"] = calorie_goal

    if user_constraints["medical_conditions"].get("pcos", False):
        options = ["after breakfast", "after lunch", "after snacks", "after dinner"]
        mapping = {
            "after breakfast": "breakfast",
            "after lunch": "lunch",
            "after snacks": "snacks",
            "after dinner": "dinner"
        }
        choice = input(f"When are you most active? ({'/'.join(options)}): ").strip().lower()
        while choice not in mapping:
            choice = input(f"Please choose one of {options}: ").strip().lower()

        user_constraints["most_active_before"] = mapping[choice]

    return user_constraints

def resolve_ingredient(ing):
    if isinstance(ing, str):
        iri_part = ing.split("#")[-1].lower()

        # Try resolving from both ontologies
        for onto_source in [onto2, onto]:
            resolved = onto_source.search_one(iri=f"*#{iri_part}")
            if resolved:
                print(f"✔️ RESOLVED {iri_part} by IRI → {resolved}")
                return resolved

            for ind in onto_source.individuals():
                if hasattr(ind, "name") and ind.name.lower() == iri_part:
                    print(f"✔️ RESOLVED {iri_part} by name → {ind}")
                    return ind
                if str(ind).lower().endswith(f"#{iri_part}"):
                    print(f"✔️ RESOLVED {iri_part} by IRI tail → {ind}")
                    return ind

        # Fallback: if not resolvable, treat it as a special string-based case
        #print(f"[SKIP] Could not resolve: {ing} — using keyword fallback for '{iri_part}'")
        return iri_part  # 👈 Return the name string directly for manual keyword check

    return ing  # already resolved OWL Thing



def expand_allergy_terms(user_allergies):
    expanded = set()
    detail_map = {}   # to record the source → expanded terms

    for allergy in user_allergies:
        key = allergy.lower()
        if key in ALLERGY_KEYWORDS:
            terms = ALLERGY_KEYWORDS[key]
            detail_map[key] = terms
            expanded.update(terms)
        else:
            detail_map[key] = [key]
            expanded.add(key)

    return expanded


def diet_constraints():


    def extract_recipe_data(recipe):


        def get_val(attr):
            return float(getattr(recipe, attr)[0]) if hasattr(recipe, attr) and getattr(recipe, attr) else 0.0

        return {
            "name": recipe.name,
            "id": recipe.hasRecipeID[0] if hasattr(recipe, "hasRecipeID") and recipe.hasRecipeID else "NA",
            "URL": recipe.hasRecipeURL[0] if hasattr(recipe, "hasRecipeURL") and recipe.hasRecipeURL else "NA",
            "diet": recipe.hasDiet[0] if hasattr(recipe, "hasDiet") and recipe.hasDiet else "NA",
            "course": recipe.hasCourse[0] if hasattr(recipe, "hasCourse") and recipe.hasCourse else "NA",
            "cuisine": recipe.hasCuisine[0] if hasattr(recipe, "hasCuisine") and recipe.hasCuisine else "NA",
            "difficulty level": recipe.hasDifficulty[0] if hasattr(recipe, "hasDifficulty") and recipe.hasDifficulty else "NA",
            "preparation time": recipe.hasPrepTime[0] if hasattr(recipe, "hasPrepTime") and recipe.hasPrepTime else "NA",
            "fermentation time": recipe.hasFermentTime[0] if hasattr(recipe, "hasFermentTime") and recipe.hasFermentTime else "NA",
            "cooking time": recipe.hasCookTime[0] if hasattr(recipe, "hasCookTime") and recipe.hasCookTime else "NA",
            "total time": recipe.hasTotalTime[0] if hasattr(recipe, "hasTotalTime") and recipe.hasTotalTime else "NA",
            "servings": recipe.hasServings[0] if hasattr(recipe, "hasServings") and recipe.hasServings else "NA",
            "ingredients": [
                ing.name if hasattr(ing, "name") else str(ing)
                for ing in getattr(recipe, "hasIngredient", [])
            ],
            "instructions": recipe.hasInstructions[0] if hasattr(recipe, "hasInstructions") and recipe.hasInstructions else "NA",

            # Changing µg to ug for consistency 
            "EnergyKcal": get_val("hasRecipeEnergyKcal"),
            "Carbohydrates (g)": get_val("hasRecipeCarbGram"),
            "Protein (g)": get_val("hasRecipeProteinGram"),
            "Fat (g)": get_val("hasRecipeFatGram"),
            "Free Sugar (g)": get_val("hasRecipeFreeSugarGram"),
            "Fibre (g)": get_val("hasRecipeFibreGram"),
            "Saturated Fat (g)": get_val("hasRecipeSFAMGram"),
            "Monounsaturated Fat (g)": get_val("hasRecipeMUFAMGram"),
            "Polyunsaturated Fat (g)": get_val("hasRecipePUFAMGram"),
            "Cholesterol (mg)": get_val("hasRecipeCholesterolMGram"),
            "Calcium (mg)": get_val("hasRecipeCalciumMGram"),
            "Phosphorus (mg)": get_val("hasRecipePhosphorusMGram"),
            "Magnesium (mg)": get_val("hasRecipeMagnesiumMGram"),
            "Sodium (mg)": get_val("hasRecipeSodiumMGram"),
            "Potassium (mg)": get_val("hasRecipePotassiumMGram"),
            "Iron (mg)": get_val("hasRecipeIronMGram"),
            "Copper (mg)": get_val("hasRecipeCopperMGram"),
            "Selenium (ug)": get_val("hasRecipeSeleniumUG"),  
            "Chromium (mg)": get_val("hasRecipeChromiumMGram"),
            "Manganese (mg)": get_val("hasRecipeManganeseMGram"),
            "Molybdenum (mg)": get_val("hasRecipeMolybdenumMGram"),
            "Zinc (mg)": get_val("hasRecipeZincMGram"),
            "Vitamin E (mg)": get_val("hasRecipeViteMGram"),
            "Vitamin D2 (ug)": get_val("hasRecipeVitD2UG"),
            "Vitamin K1 (ug)": get_val("hasRecipeVitK1UG"),
            "Folate (ug)": get_val("hasRecipeFolateUG"),
            "Vitamin B1 (mg)": get_val("hasRecipeVitB1MGram"),
            "Vitamin B2 (mg)": get_val("hasRecipeVitB2MGram"),
            "Vitamin B3 (mg)": get_val("hasRecipeVitB3MGram"),
            "Vitamin B5 (mg)": get_val("hasRecipeVitB5MGram"),
            "Vitamin B6 (mg)": get_val("hasRecipeVitB6MGram"),
            "Vitamin B7 (ug)": get_val("hasRecipeVitB7UG"),
            "Vitamin B9 (ug)": get_val("hasRecipeVitB9UG"),
            "Vitamin C (mg)": get_val("hasRecipeVitCMGram"),
            "Carotenoids (ug)": get_val("hasRecipeCarotenoidsUG"),
        }
    

    def is_vegetarian_ingredient(ingredient):
        ingredient_classes = set(ingredient.is_a)
        name = ingredient.name.lower()
        if ingredient_classes & VEGETARIAN_EXCLUDE_CLASSES:
            return False
        if any(kw in name for kw in NONVEGETARIAN_KEYWORDS):
            return False
        #print(f"{name} is vegetarian")
        return True

    def is_non_veg_ingredient(ingredient):
        return True  # No restriction for non-veg

    def is_vegan_ingredient(ingredient):
        ingredient_classes = set(ingredient.is_a)
        name = ingredient.name.lower()
        if ingredient_classes & VEGAN_EXCLUDE_CLASSES:
            return False
        if any(kw in name for kw in VEGAN_KEYWORDS):
            return False
        #print(f"{ingredient} is vegan")
        return True

    def is_ingredient_allowed(ingredient, user_constraints):
        resolved = resolve_ingredient(ingredient)
        user_diet = user_constraints["diet"].lower()

        if isinstance(resolved, str):  # e.g., 'mustard_seeds'
            name = resolved

            if user_diet == "non vegetarian":
                return True
            elif user_diet == "vegetarian":
                return name not in NONVEGETARIAN_KEYWORDS
            elif user_diet == "vegan":
                return name not in NONVEGETARIAN_KEYWORDS and name not in VEGAN_KEYWORDS
            return False

        if not resolved or not isinstance(resolved, Thing):
            unresolved_ingredients.append(ingredient)
            return False

        if user_diet == "vegetarian":
            return is_vegetarian_ingredient(resolved)
        elif user_diet == "vegan":
            return is_vegan_ingredient(resolved)
        elif user_diet == "non vegetarian":
            return is_non_veg_ingredient(resolved)
        return False

    def is_recipe_allowed(recipe, user_constraints):
       
        global rej1, rej2, rej3 # Track rejections
        user_diet = user_constraints["diet"].lower()
        recipe_name = recipe.name if hasattr(recipe, "name") else str(recipe)

        #Rejects recipes because it has no diet info (hasDiet) AND no ingredients (hasIngredient).
        if (
            (not hasattr(recipe, 'hasDiet') or not recipe.hasDiet or recipe.hasDiet[0].lower() == "na") and
            (not hasattr(recipe, 'hasIngredient') or not recipe.hasIngredient)
        ):
            #print(f"⛔ Rejected '{recipe_name}': no diet and no ingredients provided.")
            rej1 += 1
            return False


        #If hasDiet is missing or "na" (not available), but ingredients do exist. 
        #Rejects recipes whose ingredient mismatches with the diet. Ex- it will reject ing(fish) in diet(vegan) by checking with is_ingredient_allowed()
        #Here ingredients are checked with the vegan,veg keywords
        if not hasattr(recipe, 'hasDiet') or not recipe.hasDiet or recipe.hasDiet[0].lower() == "na":
            for ing in getattr(recipe, 'hasIngredient', []):
                if not is_ingredient_allowed(ing, user_constraints):
                    #print(f"❗️ Rejected '{recipe_name}': ingredient '{ing}' not allowed for user diet '{user_diet}'.")
                    rej2 += 1
                    return False
            return True


        # If both diet and ingredients are present 
        declared_diet = recipe.hasDiet[0].lower()
        declared_diet_tags = [tag.strip() for tag in declared_diet.split(",")]

        if user_diet == "non vegetarian":
            return True  # Accept everything for non-vegetarians

        if user_diet == "vegetarian" and "vegan" in declared_diet_tags:
            return True  # Veg can eat vegan

        if user_diet in declared_diet_tags:
            return True  # Exact match

        #print(f"⚠️ Rejected '{recipe_name}': declared diet '{declared_diet}' does not match user's diet preference '{user_diet}'.")
        rej3 += 1
        return False


    for recipe in FoodRecipesIRI.instances():

        if "FoodRecipes" not in [cls.name for cls in recipe.is_a]:
            continue  

        if is_recipe_allowed(recipe, user_constraints):
            #print(f"✔️ {recipe.name}")
            recommended_recipes.append(extract_recipe_data(recipe))
        else :
            #print(f"❌ {recipe.name}")
            rejected_recipes.append(extract_recipe_data(recipe))  

    return recommended_recipes, rejected_recipes


def allergies_constraints(recommended_recipes, rejected, user_constraints):

    global rej4
    allergies = user_constraints.get("allergies", [])
    allergy_terms = expand_allergy_terms(allergies)

    included_recipes = []
    excluded_recipes = rejected

    for recipe in recommended_recipes:
        ingredient_names = [ing.lower() for ing in recipe.get("ingredients", [])]

        # Exclude recipe if any allergen keyword is found in any ingredient
        if any(allergen in ing for ing in ingredient_names for allergen in allergy_terms):
            # print(f"❌ Excluded recipe due to allergy match: {recipe['name']}")
            rej4+=1
            excluded_recipes.append(recipe)
        else:
            included_recipes.append(recipe)

    return included_recipes, excluded_recipes



def violates_meal_specific_avoidance(recommended_recipes, rejected_allergy, user_constraints):

    global rej5 
    included_recipes = []
    excluded_recipes = rejected_allergy

    for recipe in recommended_recipes:
        avoid_map = user_constraints.get("avoid_food_preference", {})
        course_raw = recipe.get("course", "").strip().lower()
        possible_slots = [s.strip() for s in course_raw.split(",")]
        normalized_slots = [course_map.get(s, s) for s in possible_slots]

        name = recipe.get("name", "").lower()
        ingredients = [ing.lower() for ing in recipe.get("ingredients", [])]

        violated = False
        for slot in normalized_slots:
            if slot in avoid_map:
                avoid_keywords = avoid_map[slot]
                for keyword in avoid_keywords:
                    if keyword in name or any(keyword in ing for ing in ingredients):
                        #print(f"🚫 Rejected '{name}' due to '{keyword}' in {slot} avoid list.")
                        violated = True
                        break
            if violated:
                break

        if violated:
            excluded_recipes.append(recipe)
            rej5 += 1
        else:
            included_recipes.append(recipe)

    return included_recipes, excluded_recipes




if __name__ == "__main__":


    g = Graph()
    g.parse(owl_file_path, format="xml")  # OWL is RDF/XML by default
    re = []
    recommended_recipes = []
    rejected_recipes = []
    final_recipes = []
    final_rejected = []
    unresolved_ingredients = []
    user_constraints = {}
    rej1 = rej2 = rej3 = rej4 = rej5 = 0

    print(f"Loaded {len(g)} triples")
    
    user_constraints = get_user_profile()
    print("\nCollected Profile:\n")
    print(f"{user_constraints}\n\n")

    output_path = os.path.join(os.path.dirname(owl_file_path), 'recommended_recipes', "user_constraints.json")
    
    with open(output_path, "w") as f:
        json.dump(final_recipes, f, indent=2)
    with open(output_path, "w") as f:
        json.dump(final_rejected, f, indent=2)


    recommended_diet, rejected = diet_constraints()
    recommended_allergy, rejected_allergy = allergies_constraints(recommended_diet, rejected, user_constraints)
    final_recipes, final_rejected = violates_meal_specific_avoidance(recommended_allergy, rejected_allergy, user_constraints)

    base_dir = os.path.join(os.path.dirname(owl_file_path), "recommended_recipes")

    os.makedirs(base_dir, exist_ok=True) # Ensure the directory exists

    files_to_write = [
        ("user_constraints.json", user_constraints),
        ("hard_constraint_recommended_recipes.json", final_recipes),
        ("hard_constraint_rejected_recipes.json", final_rejected),
    ]


    # --- Add this loop to write the files ---
    for filename, data in files_to_write:
        output_path = os.path.join(base_dir, filename)
        try:
            with open(output_path, "w") as f:
                json.dump(data, f, indent=2)
            #print(f"Successfully wrote data to {output_path}")
        except Exception as e:
            print(f"Error writing file {output_path}: {e}")
    # --- End of new loop ---

  
    print(f"\n\nFound {len(final_recipes)} recommended recipes for {user_constraints['diet'].lower()}s.")
    print(f"Skipping {rej1} recipes due to missing diet and ingredients values.")
    print(f"Rejected {rej2+rej3} recipes because they didn't fit the diet.")
    print(f"Rejected {rej4} because of allergy constraints.")

    avoid_map = user_constraints.get("avoid_food_preference", {})
    if avoid_map:
        avoid_phrases = [f"{', '.join(v)} at {k}" for k, v in avoid_map.items() if v]
        summary = "; ".join(avoid_phrases)
        print(f"Rejected {rej5} recipes because user doesn't want {summary} (meal-specific avoid list).")
    else:
        print(f"Rejected {rej5} recipes due to meal-specific avoid list.")

    print(f"\n\nFinal Hard Constraint Result : Found {len(final_recipes)} recommended recipes after complete hard filtering.\n\n")