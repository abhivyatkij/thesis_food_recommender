from owlready2 import *


#onto = get_ontology("http://example.org/food_ontology.owl")
onto = get_ontology("file:/indian_food_ontology.owl")
       
def designed_merged_ontology():
    
    with onto:
        
        #Food Ontology

        class Food(Thing):
            pass
        
        class FoodIngredients(Food):
            pass
        
        class PlantOrigin(FoodIngredients):
            pass
        
        class PrimaryFoodCommodityFromPlantOrigin(PlantOrigin):
            pass
        
        class Fruit(PrimaryFoodCommodityFromPlantOrigin):
            pass
        
        class Vegetables(PrimaryFoodCommodityFromPlantOrigin):
            pass
        
        class CucumbersGourdsAndSquashes(Vegetables):
            pass
        
        class LeafySaladAndSeaVegetables(Vegetables):
            pass

        class EdibleFlowers(Vegetables):
            pass
        
        class BulbAndStemVegetables(Vegetables):
            pass
        
        class RootAndTuberousVegetables(Vegetables):
            pass
        
        class ChilliesAndCapsicums(Vegetables):
            pass

        class MiscellaneousVegetables(Vegetables):
            pass
        
        class HerbsAndSpices(PrimaryFoodCommodityFromPlantOrigin):
            pass
        
        class NutsAndSeeds(PrimaryFoodCommodityFromPlantOrigin):
            pass
        
        class Cereals(PrimaryFoodCommodityFromPlantOrigin):
            pass
        
        class PulsesAndLegumes(PrimaryFoodCommodityFromPlantOrigin):
            pass
        
        class MiscellaneousPrimaryFoodCommodityFromPlantOrigin(PrimaryFoodCommodityFromPlantOrigin):
            pass
        
        class SecondaryFoodCommodityOrProcessedFoodFromPlantOrigin(PlantOrigin):
            pass
        
        class MilledCerealProducts(SecondaryFoodCommodityOrProcessedFoodFromPlantOrigin):
            pass
        
        class SoybeanProducts(SecondaryFoodCommodityOrProcessedFoodFromPlantOrigin):
            pass
        
        class Sweeteners(SecondaryFoodCommodityOrProcessedFoodFromPlantOrigin):
            pass
        
        class OilsAndFats(SecondaryFoodCommodityOrProcessedFoodFromPlantOrigin):
            pass
        
        class DoughBasedProducts(SecondaryFoodCommodityOrProcessedFoodFromPlantOrigin):
            pass
        
        class Noodles(DoughBasedProducts):
            pass

        class Pasta(DoughBasedProducts):
            pass
        
        class FrozenFood(SecondaryFoodCommodityOrProcessedFoodFromPlantOrigin):
            pass
        
        class PackagedFriedFood(SecondaryFoodCommodityOrProcessedFoodFromPlantOrigin):
            pass
        
        class SaucesAndCondiments(SecondaryFoodCommodityOrProcessedFoodFromPlantOrigin):
            pass
        
        class Chutneys(SaucesAndCondiments):
            pass
        
        class DriedPowders(SaucesAndCondiments):
            pass

        class Sauce(SaucesAndCondiments):
            pass

        class Acids(SaucesAndCondiments):
            pass
        
        class Flavourings(SaucesAndCondiments):
            pass

        class Pickle(SaucesAndCondiments):
            pass

        class Dips(SaucesAndCondiments):
            pass

        class PastesAndSpreads(SaucesAndCondiments):
            pass
        
        class MiscellaneousSaucesAndCondiments(SaucesAndCondiments):
            pass
        
        class AnimalOrigin(FoodIngredients):
            pass
        
        class PrimaryFoodCommodityFromAnimalOrigin(AnimalOrigin):
            pass
        
        class PoultryProduct(PrimaryFoodCommodityFromAnimalOrigin):
            pass
        
        class Egg(PoultryProduct):
            pass
        
        class MeatFromPoultryProduct(PoultryProduct):
            pass
        
        class MeatFromChicken(MeatFromPoultryProduct):
            pass
        
        class MiscellaneousMeatFromPoultryProduct(MeatFromPoultryProduct):
            pass 
        
        class MammalianProduct(PrimaryFoodCommodityFromAnimalOrigin):
            pass
        
        class MeatFromMammalianProduct(MammalianProduct):
            pass
        
        class MeatFromCattle(MeatFromMammalianProduct):
            pass 
        
        class MeatFromPig(MeatFromMammalianProduct):
            pass 
        
        class MeatFromGoat(MeatFromMammalianProduct):
            pass 
        
        class MeatFromLamb(MeatFromMammalianProduct):
            pass 
        
        class MeatFromDeer(MeatFromMammalianProduct):
            pass 
        
        class MiscellaneousMeatFromMammalianProduct(MeatFromMammalianProduct):
            pass 
        
        class MilkBasedOrDairy(MammalianProduct):
            pass

        class AnimalFat(MammalianProduct):
            pass
        
        class MarineProductOrSeafood(PrimaryFoodCommodityFromAnimalOrigin):
            pass
        
        class InsectProduct(PrimaryFoodCommodityFromAnimalOrigin):
            pass
        
        class MiscellaneousPrimaryFoodCommodityFromAnimalOrigin(PrimaryFoodCommodityFromAnimalOrigin):
            pass

        class SecondaryFoodCommodityOrProcessedFoodFromAnimalOrigin(AnimalOrigin):
            pass
        
        class CannedMeatAndSeafood(SecondaryFoodCommodityOrProcessedFoodFromAnimalOrigin):
            pass
        
        class SmokedMeatAndSeafood(SecondaryFoodCommodityOrProcessedFoodFromAnimalOrigin):
            pass
        
        class SausageMeatAndSeafood(SecondaryFoodCommodityOrProcessedFoodFromAnimalOrigin):
            pass
        
        class DriedOrCuredOrSlicedMeatAndSeafood(SecondaryFoodCommodityOrProcessedFoodFromAnimalOrigin):
            pass
        
        class PackagedPate(SecondaryFoodCommodityOrProcessedFoodFromAnimalOrigin):
            pass
        
        class FrozenMeatAndSeafood(SecondaryFoodCommodityOrProcessedFoodFromAnimalOrigin):
            pass

        class ReadyToEatFoodWithMeatAndSeafood(SecondaryFoodCommodityOrProcessedFoodFromAnimalOrigin):
            pass
        
        class FungusOrigin(FoodIngredients):
            pass
        
        class PrimaryFoodCommodityFromFungusOrigin(FungusOrigin):
            pass
        
        class Mushroom(PrimaryFoodCommodityFromFungusOrigin):
            pass

        class Yeast(PrimaryFoodCommodityFromFungusOrigin):
            pass

        class SecondaryFoodCommodityOrProcessedFoodFromFungusOrigin(FungusOrigin):
            pass
        
        class Mushroom(SecondaryFoodCommodityOrProcessedFoodFromFungusOrigin):
            pass

        class Yeast(SecondaryFoodCommodityOrProcessedFoodFromFungusOrigin):
            pass
        
        class ChemicalFoodProduct(FoodIngredients):
            pass
        
        class EmulsifiersAndStabilizers(ChemicalFoodProduct):
            pass
        
        class MiscellaneousChemicalFoodProduct(ChemicalFoodProduct):
            pass

        # Food-level attributes
        
        """""
        TODO: Remove 
        class has_id(FunctionalProperty):
            domain = [Food]
            range = [str]
        """

        class hasPrefLabel(DataProperty):
            domain = [Food]
            range = [str]

        class hasAltLabels(DataProperty):
            domain = [Food]
            range = [str]

        class hasDescription(DataProperty):
            domain = [Food]
            range = [str]

        class hasCategories(DataProperty):
            domain = [Food]
            range = [str]

        class isIllegalIn(DataProperty):
            domain = [Food]
            range = [str]

        class hasDietLabels(DataProperty):
            domain = [Food]
            range = [str]

        class flavor(DataProperty):
            domain = [Food]
            range = [str]

        class texture(DataProperty):
            domain = [Food]
            range = [str]

        class taste(DataProperty):
            domain = [Food]
            range = [str]

        class nutritionalInfo(DataProperty):
            domain = [Food]
            range = [str]

        class storageInfo(DataProperty):
            domain = [Food]
            range = [str]


        # FoodIngredient-level attributes

        class hasScientificName(DataProperty):
            domain = [FoodIngredients]
            range = [str]

        class hasIFCTProperties(DataProperty):
            domain = [FoodIngredients]
            range = [str]

        class hasTags(DataProperty):
            domain = [FoodIngredients]
            range = [str]
            
        class hasFoodCode(DataProperty):
            domain = [FoodIngredients]
            range = [str]
        
        class hasFoodGroup(DataProperty):
            domain = [FoodIngredients]
            range = [str]
        
        class hasPhValue(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasGlycemicIndex(DataProperty):
            domain = [FoodIngredients]
            range = [int]

        class hasAvailableForms(DataProperty):
            domain = [FoodIngredients]
            range = [str]

        class isAcidic(DataProperty):
            domain = [FoodIngredients]
            range = [bool]

        class isAromatic(DataProperty):
            domain = [FoodIngredients]
            range = [bool]

        class isAlkaline(DataProperty):
            domain = [FoodIngredients]
            range = [bool]

        class hasCriticalTempThresholds(DataProperty):
            domain = [FoodIngredients]
            range = [str]

        class ingrIsSubstituteFor(FoodIngredients >> FoodIngredients):
            pass
            
        """""
        class hasIngredientDescription(DataProperty):
            domain = [Thing]
            range = [str]
        """

        #Nutrional Food Data Properties (from INDB)
        
        class hasnutritionalInfo(DataProperty):
            domain = [FoodIngredients]
            range = [str]

        class hasEnergyKJ(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasEnergyKcal(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasCarbGram(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasProteinGram(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasFatGram(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasFreeSugarGram(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasFibreGram(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasSFAMGram(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasMUFAMGram(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasPUFAMGram(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasCholesterolMGram(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasCalciumMGram(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasPhosphorusMGram(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasMagnesiumMGram(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasSodiumMGram(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasPotassiumMGram(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasIronMGram(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasCopperMGram(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasSeleniumUG(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasChromiumMGram(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasManganeseMGram(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasMolybdenumMGram(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasZincMGram(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasVitaUG(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasViteMGram(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasVitD2UG(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasVitD3UG(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasVitK1UG(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasVitK2UG(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasFolateUG(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasVitB1MGram(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasVitB2MGram(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasVitB3MGram(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasVitB5MGram(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasVitB6MGram(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasVitB7UG(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasVitB9UG(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasVitCMGram(DataProperty):
            domain = [FoodIngredients]
            range = [float]

        class hasCarotenoidsUG(DataProperty):
            domain = [FoodIngredients]
            range = [float]
            
        #Recipe Ontology 

        class FoodRecipes(Food):
            pass

        class DrinksAndBeverages(FoodRecipes):
            pass

        class Alcoholic(DrinksAndBeverages):
            pass
        
        class LowAlcoholic(DrinksAndBeverages):
            pass
        
        class Cocktails(DrinksAndBeverages):
            pass
        
        class Mocktails(DrinksAndBeverages):
            pass
        
        class CarbonatedBeverages(DrinksAndBeverages):
            pass
        
        class HotBeverages(DrinksAndBeverages):
            pass
        
        class ColdBeverages(DrinksAndBeverages):
            pass
        
        class InstantMixDrink(DrinksAndBeverages):
            pass
        
        class FunctionalBeverages(DrinksAndBeverages):
            pass
        
        class SpecialtyBeverages(DrinksAndBeverages):
            pass
        
        class Juices(DrinksAndBeverages):
            pass

        class Smoothies(DrinksAndBeverages):
            pass
        
        class DairyBasedBeverages(DrinksAndBeverages):
            pass
        
        class FastFood(FoodRecipes):
            pass
        
        class Munchies(FoodRecipes):
            pass

        class Chips(Munchies):
            pass

        class NutsAndSeeds(Munchies):
            pass

        class Crackers(Munchies):
            pass
        
        class Popcorn(Munchies):
            pass
        
        class SnackBars(Munchies):
            pass
        
        class Cookies(Munchies):
            pass
        
        class CandyAndSweets(Munchies):
            pass
        
        class BiscuitsAndRusks(Munchies):
            pass
        
        class SnackFood(FoodRecipes):
            pass
        
        class StreetFood(FoodRecipes):
            pass
        
        class FingerFood(FoodRecipes):
            pass
        
        class Flatbreads(FoodRecipes):
            pass

        class Sandwiches(FoodRecipes):
            pass
        
        class SoupsAndStews(FoodRecipes):
            pass
        
        class Salads(FoodRecipes):
            pass
        
        class CurriesAndGravyDishes(FoodRecipes):
            pass
        
        class LentilDishes(FoodRecipes):
            pass

        class RiceDishes(FoodRecipes):
            pass
        
        class NonRiceCerealBasedDishes(FoodRecipes):
            pass
        
        class Desserts(FoodRecipes):
            pass

        # FoodRecipe-level Attributes
        
        class hasRecipeID(FoodRecipes >> str):
            pass
        
        class hasRecipeItem(FoodRecipes >> str):
            pass
        
        class hasRecipeURL(FoodRecipes >> str):
            pass

        class hasPrepTime(FoodRecipes >> str):
            pass

        class hasFermentTime(FoodRecipes >> str):
            pass

        class hasSoakTime(FoodRecipes >> str):
            pass

        class hasCookTime(FoodRecipes >> str):
            pass

        class hasTotalTime(FoodRecipes >> str):
            pass

        class hasCuisine(FoodRecipes >> str):
            pass

        class hasCourse(FoodRecipes >> str):
            pass
        
        class hasActualIngredients(FoodRecipes >> str):
            pass

        class hasDifficulty(FoodRecipes >> str):
            pass

        class hasDiet(FoodRecipes >> str):
            pass

        class hasServings(FoodRecipes >> int):
            pass

        class hasInstructions(FoodRecipes >> str):
            pass

        class hasNotes(FoodRecipes >> str):
            pass
        
        class hasIngredientDescription(FoodRecipes >> str):
            pass

        class hasSourceDomain(FoodRecipes >> str):
            pass

        class hasPlaceOfOrigin(FoodRecipes >> str):
            pass

        class hasServingPattern(FoodRecipes >> str):
            pass

        class hasMealTime(FoodRecipes >> str):
            pass

        class hasCourse(FoodRecipes >> str):
            pass

        class hasServingTemp(FoodRecipes >> str):
            pass

        class hasEtymology(FoodRecipes >> str):
            pass

        #Recipe Nutrition 

        class hasRecipeNutritionalInfo(FoodRecipes >> str):
            pass

        class hasRecipeEnergyKJ(FoodRecipes >> float):
            pass

        class hasRecipeEnergyKcal(FoodRecipes >> float):
            pass

        class hasRecipeCarbGram(FoodRecipes >> float):
            pass

        class hasRecipeProteinGram(FoodRecipes >> float):
            pass

        class hasRecipeFatGram(FoodRecipes >> float):
            pass

        class hasRecipeFreeSugarGram(FoodRecipes >> float):
            pass

        class hasRecipeFibreGram(FoodRecipes >> float):
            pass

        class hasRecipeSFAMGram(FoodRecipes >> float):
            pass

        class hasRecipeMUFAMGram(FoodRecipes >> float):
            pass

        class hasRecipePUFAMGram(FoodRecipes >> float):
            pass

        class hasRecipeCholesterolMGram(FoodRecipes >> float):
            pass

        class hasRecipeCalciumMGram(FoodRecipes >> float):
            pass

        class hasRecipePhosphorusMGram(FoodRecipes >> float):
            pass

        class hasRecipeMagnesiumMGram(FoodRecipes >> float):
            pass

        class hasRecipeSodiumMGram(FoodRecipes >> float):
            pass

        class hasRecipePotassiumMGram(FoodRecipes >> float):
            pass

        class hasRecipeIronMGram(FoodRecipes >> float):
            pass

        class hasRecipeCopperMGram(FoodRecipes >> float):
            pass

        class hasRecipeSeleniumUG(FoodRecipes >> float):
            pass

        class hasRecipeChromiumMGram(FoodRecipes >> float):
            pass

        class hasRecipeManganeseMGram(FoodRecipes >> float):
            pass

        class hasRecipeMolybdenumMGram(FoodRecipes >> float):
            pass

        class hasRecipeZincMGram(FoodRecipes >> float):
            pass

        class hasRecipeVitaUG(FoodRecipes >> float):
            pass

        class hasRecipeViteMGram(FoodRecipes >> float):
            pass

        class hasRecipeVitD2UG(FoodRecipes >> float):
            pass

        class hasRecipeVitD3UG(FoodRecipes >> float):
            pass

        class hasRecipeVitK1UG(FoodRecipes >> float):
            pass

        class hasRecipeVitK2UG(FoodRecipes >> float):
            pass

        class hasRecipeFolateUG(FoodRecipes >> float):
            pass

        class hasRecipeVitB1MGram(FoodRecipes >> float):
            pass

        class hasRecipeVitB2MGram(FoodRecipes >> float):
            pass

        class hasRecipeVitB3MGram(FoodRecipes >> float):
            pass

        class hasRecipeVitB5MGram(FoodRecipes >> float):
            pass

        class hasRecipeVitB6MGram(FoodRecipes >> float):
            pass

        class hasRecipeVitB7UG(FoodRecipes >> float):
            pass

        class hasRecipeVitB9UG(FoodRecipes >> float):
            pass

        class hasRecipeVitCMGram(FoodRecipes >> float):
            pass

        class hasRecipeCarotenoidsUG(FoodRecipes >> float):
            pass


        """
        class hasPairingInfo(ObjectProperty): # Pairing between ingredients and recipes both, to be implemented later.
            domain = [Food]
            range = [str]
        """
        class recpIsRelatedTo(FoodRecipes >> FoodRecipes):
            pass

        class recpPairsWellWith(FoodRecipes >> FoodRecipes):
            pass

        class hasAdditionalTrivia(FoodRecipes >> str):
            pass

        class hasAdditionalTips(FoodRecipes >> str):
            pass

        class hasIngredient(FoodRecipes >> FoodIngredients):
            pass
        
        """""
        class isIngredientOf(FoodIngredients >> FoodRecipes):
            inverse_property = hasIngredient
        """
        
        class hasStorageInfo(FoodRecipes >> str):
            pass
           

        #Cooking Characteristics Ontology

        class CookingChar(Thing):
            pass
        
        class KitchenTool(CookingChar):
            pass

        class CookingMeasure(CookingChar):
            pass

        class Cookware(CookingChar):
            pass

        class CookingTechnique(CookingChar):
            pass

        class KnifeCut(CookingChar):
            pass

        class CookingTemp(CookingChar):
            pass

        class HeatSource(CookingChar):
            pass

        class ChemicalReaction(CookingChar):
            pass

        class CookingProperty(CookingChar):
            pass

        class hasCookingChar(FoodRecipes >> CookingChar):
            pass


        # Meal, Dish, Platter Ontology

        class FoodDish(FoodRecipes):
            pass

        class hasRecipe(FoodDish >> FoodRecipes):
            pass

        class isRecipeOf(FoodRecipes >> FoodDish):
            pass

        class FoodPlatter(FoodRecipes):
            pass

        class hasDish(FoodPlatter >> FoodDish):
            pass

        class isDishOf(FoodDish >> FoodPlatter):
            inverse_property = hasDish

        class FoodMeal(FoodPlatter):
            pass

    return onto
"""""
if __name__ == "__main__" :
    designed_merged_ontology()
    print("Succesfully updated ontology!")
"""