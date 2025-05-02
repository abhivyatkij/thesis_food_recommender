import os
import json
from owlready2 import *
from fuzzywuzzy import fuzz
#from googletrans import Translator
#from indic_transliteration import sanscript
#from indic_transliteration.sanscript import transliterate
from merged_food_recipe_design_ontology import designed_merged_ontology

build_ontology_pipeline_out_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'out_build_ontology_pipeline') 
generated_owl_file = get_ontology(os.path.join(build_ontology_pipeline_out_dir, 'ifct_owl.owl')).load() 

onto = designed_merged_ontology()
global error_messages
stats_nodes_added = 0
stats_labels_added= 0 
error_messages = []
exception_counter = 0
id = []

#translator = Translator()

def to_lower_case(word):
    return word.lower()

def normalize(word):
    return word.strip().lower()

def get_class_from_fkg_class(class_name):
    return getattr(onto, class_name, None)

def fuzzy_match(food_item, threshold=90):
    
    food_item_normalized = normalize(food_item)
    
    for cls in generated_owl_file.classes():
        
        for instance in cls.instances():
            instance_name = instance.name
            instance_normalized = normalize(instance_name)
            
            if fuzz.ratio(food_item_normalized, instance_normalized) >= threshold:
                return instance_name, True
      
    return None, False

# Function to filter recipes
def is_filtered_recipe(recipe_item, keywords=["samosa", "cake", "biryani"]):
    
    """""
    #print only exact matches 
    words = recipe_item.lower().split()
    
    for keyword in keywords:
        if keyword in words:
            return True
    return False
    """
    
    return any(keyword.lower() in recipe_item.lower() for keyword in keywords)


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
            recipe_item =  str(recipe_var['recipeItem'])
            filtered_recipe_boolean = is_filtered_recipe(recipe_item)
            
            if filtered_recipe_boolean == True:
                
                try:
                    
                    recipe_instance = onto.FoodRecipes(str(recipe_var['recipeItem'])) 
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
                    """""
                    try: 
                        for section in recipe_var['ingredients']:
                            recipe_instance.hasIngredientDescription.append(str(recipe_var['ingredients']))
                    except Exception as e:
                        exception_counter += 1
                        error_message = (f"\n#{exception_counter} No ingredients found for {recipe_var['recipeItem']}, ID: {recipe_var['recipeID']}: {e}")
                        error_messages.append(error_message)    
                    """
                    vars()[str(recipe_var['recipeItem'])] = recipe_instance

                
                except Exception as e:
                    exception_counter += 1
                    error_message = (f"\n#{exception_counter} Exception in handling recipe properties for {recipe_var['recipeItem']}, ID: {recipe_var['recipeID']}: {e}")
                    error_messages.append(error_message) 
                
                try: 
                    
                    for section in recipe_var['ingredients']:
                        
                        recipe_instance.hasIngredientDescription.append(str(recipe_var['ingredients']))
                        
                    
                        
                        if isinstance(section['items'], dict):  
                            for ingredient, details in section['items'].items():
                                
                                ingredient = to_lower_case(ingredient)
                                
                                
                                if 'ingredients' in recipe_var:
                                    ingredient_instance = onto.FoodIngredients(ingredient)
                                    recipe_instance.hasIngredient.append(ingredient_instance)
                                    #recipe_instance.hasActualIngredients.append(ingredient)

                                #NOTE: allow adding an alt label in the devnagri script. it is not executed in the code due to lack of knowledge
                                #of the ingredients' local names' place of origin 
                                #devanagri = (translator.translate(ingredient, src='en', dest='hi')).text
                
                except Exception as e:
                    exception_counter += 1
                    error_message = (f"\n#{exception_counter} No ingredients found for {recipe_var['recipeItem']}, ID: {recipe_var['recipeID']}: {e}")
                    error_messages.append(error_message)                                             
        
                  
        generated_owl_file.save(os.path.join(build_ontology_pipeline_out_dir, 'samosa_cake_biriyani.owl'), format="rdfxml")
       
    
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
        generated_owl_file.save(os.path.join(build_ontology_pipeline_out_dir, 'samosa_cake_biriyani.owl'), format="rdfxml")
        print(f"\nJSON recipe {recipe_file} has been processed. OWL file saved to samosa_cake_biriyani.owl\n")
         
    debugging = input ("\nDo you wish to validate errors? Yes/No?")
    
    if debugging=="Yes":
        print(f"\nErrors encountered in the script {recipe_file}:")
        for error in error_messages:
            print(error)       
    
    print_id = input("\n\nDo you wish to check the recipe IDs created? Yes/No?")
    if print_id =="Yes":
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
   