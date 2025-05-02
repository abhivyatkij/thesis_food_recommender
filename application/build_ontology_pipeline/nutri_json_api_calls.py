import os
import json
import csv
import re
import requests
from owlready2 import *
from fuzzywuzzy import fuzz
import urllib.parse
import requests
from merged_food_recipe_design_ontology import designed_merged_ontology
from nutri_ifct import indb_data


#NOTE: refer this block is you wish to automate hindi and roman hindi locstr
#from googletrans import Translator
#from indic_transliteration import sanscript
#from indic_transliteration.sanscript import transliterate

build_ontology_pipeline_out_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'out_build_ontology_pipeline') 
generated_owl_file = get_ontology(os.path.join(build_ontology_pipeline_out_dir, 'nutri_ifct.owl')).load() 
csv_file_path = os.path.join(build_ontology_pipeline_out_dir, 'ingredients_recipes.csv')


onto = designed_merged_ontology()
global error_messages
stats_nodes_added = 0
stats_labels_added= 0 
error_messages = []
exception_counter = 0
id = []
data_collected = []
#count_ing_nutri = 0 
indb_food_names, indb_nutritional_value = indb_data() #fetches all the nutritional values from indb 
ingredient_nutrition_data = {}
api_counter = 0

#translator = Translator()

def to_lower_case(word):
    return word.lower()

def normalize(word):
    return word.strip().lower()

def get_class_from_fkg_class(class_name):
    return getattr(onto, class_name, None)

def fuzzy_match(food_item, threshold=80):
    
    food_item_normalized = normalize(food_item)
    
    for cls in generated_owl_file.classes():
        
        for instance in cls.instances():
            instance_name = instance.name
            instance_normalized = normalize(instance_name)
            
            if fuzz.ratio(food_item_normalized, instance_normalized) >= threshold:
                return instance_name, True
      
    return None, False


def make_uri_safe(name):
    name = str(name).strip().lower()
    name = name.replace("&", "and")                # Replace ampersand with "and"
    name = re.sub(r"[^\w\d_]", "_", name)          # Replace non-alphanum (excluding underscores)
    name = re.sub(r"__+", "_", name)               # Collapse multiple underscores
    return name.strip("_")                         # Remove leading/trailing _



def fetch_api_nutrition(ingredient, api_ingredient):
    global api_counter 
    api_url   = "https://api.api-ninjas.com/v1/nutrition?query="
    headers   = {"X-Api-Key": "nwM0kJaXgsQ3F2lACMvNuw==32DMcAtIm99BQt1D"}
    query_str = urllib.parse.quote(api_ingredient)

    resp = requests.get(api_url + query_str, headers=headers)
    if resp.status_code != requests.codes.ok:
        print(f"Error fetching {api_ingredient}:", resp.status_code, resp.text)
        return

    data = resp.json()        # API‑Ninjas returns a top‑level list
    if not data:
        print(f"No nutrition data for '{api_ingredient}'")
        return

    item = data[0]
    print("Parsed item:", item)

    # Look up the existing individual in the ontology
    inst = onto.search_one(iri=f"*{ingredient}")
    if not inst:
        print(f"⚠️ Ingredient '{ingredient}' not found in ontology")
        return

    # Append each nutrient to the ontology individual
    inst.hasEnergyKcal.append(str(item["calories"]))
    inst.hasCarbGram.append(str(item["carbohydrates_total_g"]))
    inst.hasProteinGram.append(str(item["protein_g"]))
    inst.hasFatGram.append(str(item["fat_total_g"]))
    inst.hasFreeSugarGram.append(str(item["sugar_g"]))
    inst.hasFibreGram.append(str(item["fiber_g"]))
    inst.hasSFAMGram.append(str(item["fat_saturated_g"]))
    inst.hasSodiumMGram.append(str(item["sodium_mg"]))
    inst.hasPotassiumMGram.append(str(item["potassium_mg"]))
    inst.hasCholesterolMGram.append(str(item["cholesterol_mg"]))
    api_counter += 1
    onto.save(os.path.join(build_ontology_pipeline_out_dir, 'test_.owl'), format="rdfxml")

def fetch_indb_nutrition (ingredient):
    global count_ing_nutri
    #count_ing_nutri +=1 
    ingredient_instance = onto.FoodIngredients(ingredient)
    nutri_json = json.dumps(indb_nutritional_value[ingredient])   # converts nutritional data to json format for hasnutionalInfo's string datatype
    ingredient_instance.hasnutritionalInfo.append(nutri_json)
    ingredient_instance.hasEnergyKJ.append(indb_nutritional_value[ingredient]['energy_kj'])
    ingredient_instance.hasEnergyKcal.append(indb_nutritional_value[ingredient]['energy_kcal'])
    ingredient_instance.hasCarbGram.append(indb_nutritional_value[ingredient]['carb_g'])
    ingredient_instance.hasProteinGram.append(indb_nutritional_value[ingredient]['protein_g'])
    ingredient_instance.hasFatGram.append(indb_nutritional_value[ingredient]['fat_g'])
    ingredient_instance.hasFreeSugarGram.append(indb_nutritional_value[ingredient]['freesugar_g'])
    ingredient_instance.hasFibreGram.append(indb_nutritional_value[ingredient]['fibre_g'])
    ingredient_instance.hasSFAMGram.append(indb_nutritional_value[ingredient]['sfa_mg'])
    ingredient_instance.hasMUFAMGram.append(indb_nutritional_value[ingredient]['mufa_mg'])
    ingredient_instance.hasPUFAMGram.append(indb_nutritional_value[ingredient]['pufa_mg'])
    ingredient_instance.hasCholesterolMGram.append(indb_nutritional_value[ingredient]['cholesterol_mg'])
    ingredient_instance.hasCalciumMGram.append(indb_nutritional_value[ingredient]['calcium_mg'])
    ingredient_instance.hasPhosphorusMGram.append(indb_nutritional_value[ingredient]['phosphorus_mg'])
    ingredient_instance.hasMagnesiumMGram.append(indb_nutritional_value[ingredient]['magnesium_mg'])
    ingredient_instance.hasSodiumMGram.append(indb_nutritional_value[ingredient]['sodium_mg'])
    ingredient_instance.hasPotassiumMGram.append(indb_nutritional_value[ingredient]['potassium_mg'])
    ingredient_instance.hasIronMGram.append(indb_nutritional_value[ingredient]['iron_mg'])
    ingredient_instance.hasCopperMGram.append(indb_nutritional_value[ingredient]['copper_mg'])
    ingredient_instance.hasSeleniumUG.append(indb_nutritional_value[ingredient]['selenium_ug'])
    ingredient_instance.hasChromiumMGram.append(indb_nutritional_value[ingredient]['chromium_mg'])
    ingredient_instance.hasManganeseMGram.append(indb_nutritional_value[ingredient]['manganese_mg'])
    ingredient_instance.hasMolybdenumMGram.append(indb_nutritional_value[ingredient]['molybdenum_mg'])
    ingredient_instance.hasZincMGram.append(indb_nutritional_value[ingredient]['zinc_mg'])
    ingredient_instance.hasVitaUG.append(indb_nutritional_value[ingredient]['vita_ug'])
    ingredient_instance.hasViteMGram.append(indb_nutritional_value[ingredient]['vite_mg'])
    ingredient_instance.hasVitD2UG.append(indb_nutritional_value[ingredient]['vitd2_ug'])
    ingredient_instance.hasVitD3UG.append(indb_nutritional_value[ingredient]['vitd3_ug'])
    ingredient_instance.hasVitK1UG.append(indb_nutritional_value[ingredient]['vitk1_ug'])
    ingredient_instance.hasVitK2UG.append(indb_nutritional_value[ingredient]['vitk2_ug'])
    ingredient_instance.hasFolateUG.append(indb_nutritional_value[ingredient]['folate_ug'])
    ingredient_instance.hasVitB1MGram.append(indb_nutritional_value[ingredient]['vitb1_mg'])
    ingredient_instance.hasVitB2MGram.append(indb_nutritional_value[ingredient]['vitb2_mg'])
    ingredient_instance.hasVitB3MGram.append(indb_nutritional_value[ingredient]['vitb3_mg'])
    ingredient_instance.hasVitB5MGram.append(indb_nutritional_value[ingredient]['vitb5_mg'])
    ingredient_instance.hasVitB6MGram.append(indb_nutritional_value[ingredient]['vitb6_mg'])
    ingredient_instance.hasVitB7UG.append(indb_nutritional_value[ingredient]['vitb7_ug'])
    ingredient_instance.hasVitB9UG.append(indb_nutritional_value[ingredient]['vitb9_ug'])
    ingredient_instance.hasVitCMGram.append(indb_nutritional_value[ingredient]['vitc_mg'])
    ingredient_instance.hasCarotenoidsUG.append(indb_nutritional_value[ingredient]['carotenoids_ug'])

    onto.save(os.path.join(build_ontology_pipeline_out_dir, 'test_.owl'), format="rdfxml")
                                        

def create_json_owl(json_file_path, recipe_name):
    global exception_counter
    stats_skipped_labels = 0
    global stats_nodes_added
    global stats_labels_added


    try:
        
        with open(json_file_path, 'r') as file:
            data = file.read()    
            recipe_data = json.loads(data)

        iteration_count = 0
        count = 0
        instruct = []
        

        for recipe_var in recipe_data['recipes']:
            
            """""
            #control the number of recipes iterated
            iteration_count += 1
            if iteration_count > 20:
                break   
            """ 
            
            
            try:
                safe_recipe_name = make_uri_safe(str(recipe_var['recipeItem']))
                recipe_instance = onto.FoodRecipes(safe_recipe_name) 
                recipe_instance.hasRecipeID.append(recipe_var['recipeID'])
                id.append(recipe_var['recipeID'])
                recipe_instance.hasRecipeURL.append(recipe_var['recipeURL'])
                recipe_instance.hasPrepTime.append(recipe_var['prepTime'])
                recipe_instance.hasFermentTime.append(recipe_var['fermentTime'])
                recipe_instance.hasCookTime.append(recipe_var['cookTime'])
                recipe_instance.hasTotalTime.append(recipe_var['totalTime'])
                recipe_instance.hasCuisine.append(recipe_var['cuisine'])
                recipe_instance.hasCourse.append(recipe_var['course'])
                recipe_instance.hasDifficulty.append(recipe_var['difficulty'])
                recipe_instance.hasDiet.append(recipe_var['diet'])
                recipe_instance.hasServings.append(recipe_var['servings'])
                    
                if 'instructions' in recipe_var:
                    for instruction in recipe_var['instructions']:
                        heading = instruction['heading']
                        items = instruction['items']
                        instructions_combined = " ".join(items)  
                        instruct.append({
                            "heading": heading,
                            "instructions": instructions_combined
                        })
                        recipe_instance.hasInstructions.append(str(instruct))
                        instruct = []
                        
                if 'notes' in recipe_var:
                    for recipe_note in recipe_var['notes']:
                        note = recipe_note['items']
                        recipe_instance.hasNotes.append(str(note))
              
                vars()[str(recipe_var['recipeItem'])] = recipe_instance

            
            except Exception as e:
                exception_counter += 1
                error_message = (f"\n#{exception_counter} Exception in handling recipe properties for {recipe_var['recipeItem']}, ID: {recipe_var['recipeID']}: {e}")
                error_messages.append(error_message) 
            
            try: 
                
                for section in recipe_var['ingredients']:
                    
                    recipe_instance.hasIngredientDescription.append(str(recipe_var['ingredients']))
                    
                    try: 
                        
                        if isinstance(section['items'], dict):  
                            for ingredient, details in section['items'].items():
                                
                                api_ingredient = ingredient #normal ingredient name without _ 
                                ingredient = make_uri_safe(ingredient)
                                
                                
                                if 'ingredients' in recipe_var:

                                    ingredient_instance = onto.FoodIngredients(ingredient)

                                    recipe_instance.hasIngredient.append(ingredient_instance)
                                 
                                    if ingredient in indb_food_names:
                                        fetch_indb_nutrition(ingredient) 
                                    """""
                                    elif not hasattr(ingredient, "hasnutritionalInfo") or not ingredient.hasnutritionalInfo:
                                        fetch_api_nutrition(ingredient, api_ingredient)
                                    onto.save(os.path.join(build_ontology_pipeline_out_dir, 'test_.owl'), format="rdfxml")
                                   """
                                #NOTE: allow adding an alt label in the devnagri script. it is not executed in the code due to lack of knowledge
                                #of the ingredients' local names' place of origin 
                                #devanagri = (translator.translate(ingredient, src='en', dest='hi')).text
                                
                                cls = get_class_from_fkg_class(details['category'])
                                    
                                if cls is None: 
                                    
                                    #classifying unclassed food items to FoodIngredient 
                                    instance = onto.FoodIngredients((ingredient))
                                    vars()[ingredient]= instance
                                    instance.hasPrefLabel.append(ingredient)
                                    #print(f"Parent class: {details['category']} not found in ontology. Ingredient: {ingredient} added to class FoodIngredients.")
                                    continue
                                
                                else:
                                    
                                    cls_string = cls.name
                                    matched_to, match_boolean = fuzzy_match(ingredient)
                                    
                                    if match_boolean:
                                        
                                        count = count + 1
                                        all_labels = [] #includes alternate and preferred labels 
                                        
                                        
                                        for owl_class in generated_owl_file.classes(): 
                                            owl_class_string = owl_class.name
                                            if owl_class_string ==  cls_string:
                                            
                                                inst = owl_class(str(matched_to))
                                              
                                                #gathers all the alt labels from main.owl
                                                all_labels = inst.hasAltLabels + inst.hasPrefLabel
                                                data_collected.append((ingredient, all_labels, recipe_instance))

                                                for label in all_labels:
                                                    
                                                    if ingredient == label: 
                                                        stats_skipped_labels += 1 
                                                        #print(f"#{stats_skipped_labels} skipped label {ingredient} due to match with {label}")   
                                                        continue    
                                                                                    
                                                    else:
                                                        
                                                        stats_labels_added += 1
                                                        inst.hasAltLabels.append(ingredient) #TODO: add a locstr with the region language tag when the dataset is available
                                                        
                                                        onto.save(os.path.join(build_ontology_pipeline_out_dir, 'test_mk_vri_json_api.owl'), format="rdfxml")
                                                        #generated_owl_file.save(os.path.join(build_ontology_pipeline_out_dir, 'test_mk_vri_json_api.owl'), format="rdfxml")

                                                        #print(f"#{stats_labels_added} label created: {ingredient}")
                                                        break
                                        continue
                                    
                                    else:
                                        
                                        stats_nodes_added += 1
                                        instance = cls(ingredient)
                                        vars()[ingredient]= instance                                           
                                        instance.hasPrefLabel.append(make_uri_safe(ingredient)) #TODO: add a locstr with the region language tag when the dataset is available
                                    
                                        onto.save(os.path.join(build_ontology_pipeline_out_dir, 'mk_vri_json_api.owl'), format="rdfxml")

                                        #generated_owl_file.save(os.path.join(build_ontology_pipeline_out_dir, 'mk_vri_json_api.owl'), format="rdfxml")

                                        #print(f"#{stats_nodes_added} node created: {instance} from recipe {recipe_name}, with labels: {instance.hasAltLabels}")
                                            
                    except Exception as e:
                        exception_counter +=1
                        error_message = (f"\n#{exception_counter} Exception in handling class instances for {recipe_var['recipeItem']}, ID: {recipe_var['recipeID']}: {e}")
                        error_messages.append(error_message) 
            
            except Exception as e:
                exception_counter += 1
                error_message = (f"\n#{exception_counter} No ingredients found for {recipe_var['recipeItem']}, ID: {recipe_var['recipeID']}: {e}")
                error_messages.append(error_message)      
                      
        onto.save(os.path.join(build_ontology_pipeline_out_dir, 'mk_vri_json_api.owl'), format="rdfxml")
        #generated_owl_file.save(os.path.join(build_ontology_pipeline_out_dir, 'mk_vri_json_api.owl'), format="rdfxml")
        
    
    except Exception as e:
        exception_counter +=1
        error_message =(f"\n#{exception_counter} Error to process the recipe {recipe_var['recipeItem']}, ID: {recipe_var['recipeID']} has been encountered , error: {e}")
        error_messages.append(error_message) 



def process_json_recipes():
    
    iteration_count = 0
    global id_counter
    id_counter = 0
    path_to_json_directory = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "in", "jsons_recipe_owl")
    json_files = [pos_json for pos_json in os.listdir(path_to_json_directory) if pos_json.endswith('.json')]
   
    for recipe_file in json_files:
        
        """""
        #control the number of recipes iterated
        iteration_count += 1
        if iteration_count > 2:
            break 
        """
                
        json_path  = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "in", "jsons_recipe_owl", recipe_file)
        create_json_owl(json_path, recipe_file)

        with open(csv_file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Ingredient', 'Labels', 'Used in Recipe'])
            for ingredient, labels, recipe in data_collected:
                writer.writerow([ingredient, ', '.join(labels), recipe])

        print(f"\nJSON recipe {recipe_file} has been processed. OWL file saved to mk_vri_json_api.owl\n")
         
    debugging = input ("\nDo you wish to validate errors? Yes/No?")
    
    if debugging=="Yes" or "yes" or "y":
        print(f"\nErrors encountered in the script {recipe_file}:")
        for error in error_messages:
            print(error)       
    
    print_id = input("\n\nDo you wish to check the recipe IDs created? Yes/No?")
    if print_id =="Yes" or "yes" or "y":
        print(f"\nIDs processed in the script {recipe_file}:\n")
        for recipe_id in id:
            id_counter += 1
            print(f"#{id_counter} {recipe_id}")
            
    id_counter=0       
    for recipe_id in id:
        id_counter += 1
        
        
        
        
        
if __name__ == "__main__":
    process_json_recipes()
    print (f"\nTotal new nodes created by JSONS: {stats_nodes_added}, Total number of JSON ingredients added as alt labels of IFCT data: {stats_labels_added}, total recipe instances created: {id_counter}")
    print (f"\nTotal API calls made: {api_counter}")
    #print(f"\nTotal nutritional values added : {count_ing_nutri} \n")