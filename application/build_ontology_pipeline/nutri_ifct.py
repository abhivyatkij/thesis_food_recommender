from merged_food_recipe_design_ontology import designed_merged_ontology
from owlready2 import *
import csv
import json
import pandas as pd
import re


build_ontology_out_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'out_build_ontology_pipeline')
csv_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "in", "ifct_final.csv")
indb_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "in", "indb.csv")


onto = designed_merged_ontology()


extracted_data = []

def to_pascal_case(s):
    s = re.sub(r'[^a-zA-Z0-9]', ' ', s)
    words = s.split()
    pascal_case = ''.join(word.capitalize() for word in words)
    return pascal_case

def get_class_from_fkg_class(class_name):
    return getattr(onto, class_name, None)        


def make_uri_safe(name):
    name = str(name).strip().lower()
    name = name.replace("&", "and")                # Replace ampersand with "and"
    name = re.sub(r"[^\w\d_]", "_", name)          # Replace non-alphanum (excluding underscores)
    name = re.sub(r"__+", "_", name)               # Collapse multiple underscores
    return name.strip("_")                         # Remove leading/trailing _


#fetches all food names from indb.csv file
def indb_data():

    indb_food_names = set()  # For fast existence check
    nutrition_row = {}    # For quick nutritional data retrieval

    with open(indb_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            food_name = row['food_name'].lower()  # Normalize to lowercase
            food_name = make_uri_safe(food_name)  # Make URI safe
            indb_food_names.add(food_name)       # Store for quick lookup
            nutrition_row [food_name] = row

    return indb_food_names, nutrition_row


indb_food_names, nutritional_value = indb_data()
#print(nutritional_value)

def create_ifct_owl():

    counter = 0
    counter2 = 0
    counter3=0
    
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            
            languages = [
            'Assamese', 'Bengali', 'English', 'Gujarati', 'Hindi',
            'Kannada', 'Kashmiri', 'Khasi', 'Konkani', 'Malayalam',
            'Manipuri', 'Marathi', 'Nepali', 'Oriya', 'Punjabi',
            'Sanskrit', 'Tamil', 'Telugu', 'Urdu', 'Common_Name']
            language_tag = {
                "Assamese": "as", "Bengali": "bn", "English": "en", "Gujarati": "gu", "Hindi": "hi",
                "Kannada": "kn", "Kashmiri": "ks", "Khasi": "kha", "Konkani": "kok", "Malayalam": "ml",
                "Manipuri": "mni", "Marathi": "mr", "Nepali": "ne", "Oriya": "or", "Punjabi": "pa",
                "Sanskrit": "sa", "Tamil": "ta", "Telugu": "te", "Urdu": "ur", "Common_Name": "cmn"
            }

            food_code = row['Food_Code']
            food_name = row['Food_Name']
            scientific_name = row['Scientific_Name']
            local_names_with_tags = [
                (row[f'Local_Name_{lang}'], language_tag[lang]) for lang in languages if row[f'Local_Name_{lang}'] != "NA"
            ]
            food_group = row['Food_Group']
            tags = row['Tags']
            fkg_class = row['OWL_Category']


            entry = {
                
                "food_name": food_name, 
                "local_names": local_names_with_tags,
                "food_code": food_code, 
                "scientific_name": scientific_name,
                "food_group": food_group,
                "tags": tags,
                "fkg_class": fkg_class
            }

            food_name = make_uri_safe(food_name)
            counter+=1

            #print(f" {food_name}" )
            scientific_name = scientific_name.lower()

            
            #gets all classes from designed_food_ontology.py
            cls = get_class_from_fkg_class(fkg_class)  
        

            if cls is None:
                
                #classifying unclassed food items to FoodIngredient 
                instance = onto.FoodIngredients(food_name)
                vars()[food_name]= instance
                instance.hasPrefLabel.append(food_name)
                #print(f"Parent class: {cls} not found in ontology. Ingredient: {food_name} added to class FoodIngredients.")
                continue
            
            else:

                instance = cls(food_name)
                instance.hasPrefLabel.append(food_name)
                instance.hasScientificName.append(scientific_name)
                
                for name, tag in local_names_with_tags:
                    name = name.lower()
                    instance.hasAltLabels.append(locstr(name,tag))  # Using the language tag associated with each local name
                            
                instance.hasTags.append(tags)  
                instance.hasFoodCode.append(food_code)
                instance.hasFoodGroup.append(food_group)
                
                #finding nutrition data for the food item (if available)

                if food_name in indb_food_names:

                    counter2+=1
                    nutrition_json = json.dumps(nutritional_value[food_name])   # converts nutritional data to json format for hasnutionalInfo's string datatype
                    instance.hasnutritionalInfo.append(nutrition_json)
                    instance.hasEnergyKJ.append(nutritional_value[food_name]['energy_kj'])
                    instance.hasEnergyKcal.append(nutritional_value[food_name]['energy_kcal'])
                    instance.hasCarbGram.append(nutritional_value[food_name]['carb_g'])
                    instance.hasProteinGram.append(nutritional_value[food_name]['protein_g'])
                    instance.hasFatGram.append(nutritional_value[food_name]['fat_g'])
                    instance.hasFreeSugarGram.append(nutritional_value[food_name]['freesugar_g'])
                    instance.hasFibreGram.append(nutritional_value[food_name]['fibre_g'])
                    instance.hasSFAMGram.append(nutritional_value[food_name]['sfa_mg'])
                    instance.hasMUFAMGram.append(nutritional_value[food_name]['mufa_mg'])
                    instance.hasPUFAMGram.append(nutritional_value[food_name]['pufa_mg'])
                    instance.hasCholesterolMGram.append(nutritional_value[food_name]['cholesterol_mg'])
                    instance.hasCalciumMGram.append(nutritional_value[food_name]['calcium_mg'])
                    instance.hasPhosphorusMGram.append(nutritional_value[food_name]['phosphorus_mg'])
                    instance.hasMagnesiumMGram.append(nutritional_value[food_name]['magnesium_mg'])
                    instance.hasSodiumMGram.append(nutritional_value[food_name]['sodium_mg'])
                    instance.hasPotassiumMGram.append(nutritional_value[food_name]['potassium_mg'])
                    instance.hasIronMGram.append(nutritional_value[food_name]['iron_mg'])
                    instance.hasCopperMGram.append(nutritional_value[food_name]['copper_mg'])
                    instance.hasSeleniumUG.append(nutritional_value[food_name]['selenium_ug'])
                    instance.hasChromiumMGram.append(nutritional_value[food_name]['chromium_mg'])
                    instance.hasManganeseMGram.append(nutritional_value[food_name]['manganese_mg'])
                    instance.hasMolybdenumMGram.append(nutritional_value[food_name]['molybdenum_mg'])
                    instance.hasZincMGram.append(nutritional_value[food_name]['zinc_mg'])
                    instance.hasVitaUG.append(nutritional_value[food_name]['vita_ug'])
                    instance.hasViteMGram.append(nutritional_value[food_name]['vite_mg'])
                    instance.hasVitD2UG.append(nutritional_value[food_name]['vitd2_ug'])
                    instance.hasVitD3UG.append(nutritional_value[food_name]['vitd3_ug'])
                    instance.hasVitK1UG.append(nutritional_value[food_name]['vitk1_ug'])
                    instance.hasVitK2UG.append(nutritional_value[food_name]['vitk2_ug'])
                    instance.hasFolateUG.append(nutritional_value[food_name]['folate_ug'])
                    instance.hasVitB1MGram.append(nutritional_value[food_name]['vitb1_mg'])
                    instance.hasVitB2MGram.append(nutritional_value[food_name]['vitb2_mg'])
                    instance.hasVitB3MGram.append(nutritional_value[food_name]['vitb3_mg'])
                    instance.hasVitB5MGram.append(nutritional_value[food_name]['vitb5_mg'])
                    instance.hasVitB6MGram.append(nutritional_value[food_name]['vitb6_mg'])
                    instance.hasVitB7UG.append(nutritional_value[food_name]['vitb7_ug'])
                    instance.hasVitB9UG.append(nutritional_value[food_name]['vitb9_ug'])
                    instance.hasVitCMGram.append(nutritional_value[food_name]['vitc_mg'])
                    instance.hasCarotenoidsUG.append(nutritional_value[food_name]['carotenoids_ug'])
                
                else :
                    counter3+=1
            
           
        

            #print(f"Created instance of {fkg_class}: {instance}")
        
    #onto.save(os.path.join(build_ontology_out_dir, 'ifct_owl.owl'), format="rdfxml")
    onto.save(os.path.join(build_ontology_out_dir, 'nutri_ifct.owl'), format="rdfxml")

    #print("\nIFCT has been processed. OWL file saved to ifct_owl.owl")
    print("\nIFCT has been processed. OWL file saved to nutri_ifct.owl")
    print(f"Total {counter} food items processed")
    print(f"Total {counter2} food items with nutritional data")
    print(f"Total {counter3} food items without nutritional data")

if __name__ == "__main__":
    create_ifct_owl()

    

