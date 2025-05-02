# Import libraries
import os
from application import config

from build_food_entity_db_pipeline.build_food_entity_database import populate_food_entity_database
from build_food_entity_db_pipeline.populate_entity_and_what_words import separate_entity_and_what_words
from manage_what_words_pipeline.what_words_app import run_what_words_application
from run_build_ontology_pipeline.build_foundational_ontology import build_foundational_ontology_from_vocabulary  # type: ignore
from run_build_ontology_pipeline.build_recipe_ontology import build_indian_food_ontology  # type: ignore

dir_path = config.DIR_PATH
logger = config.LOGGER


def run_build_food_entity_db_pipeline():
    """
    End-to-end pipeline for building the food entity database from reliable knowledge bases and generating the final list of 'what words'

    Input: ner_output_llm/validated_food_entities_list.csv, Reliable food entity sources (such as IFCT_Data.csv), what_words.csv
    Output: food_entity_vocabulary.csv, what_words.csv
    """

    logger.info(
        "Starting the build food entity DB and generating what words pipeline")

    populate_food_entity_database()
    separate_entity_and_what_words()

    logger.info(
        "Ending the the build food entity DB and generating what words pipeline.")


def run_manage_what_words_pipeline():
    """
    End-to-end pipeline for classifying what words into food words, food-related words and non-food related (or noise) words

    Input: food_words_vocabulary.csv, what_words.csv
    Output: classified_what_words/food.csv, classified_what_words/food_related.csv, classified_what_words/non_food.csv
    """

    logger.info(
        "Starting the Flask (Python) based what words application")

    # The flask application runs in a non-blocking manner
    run_what_words_application()

    logger.info(
        "Ending the Flask (Python) based what words application")


def run_build_ontology_pipeline():
    """
    End-to-end pipeline for organizing vocabularies pertaining to food, cooking and nutrients and building indian food ontology

    Input: food_words_vocabulary.csv, food_vocabulary_custom.json, classified_what_words/food_related.csv and classified_what_words/food_related.csv
    Output: food_entities_ready_for_ontology_population.csv, indian_food_ontology.owl
    """

    build_foundational_ontology_from_vocabulary()
    build_indian_food_ontology()


if __name__ == "__main__":
    # Create an out/ folder if it does not already exist
    os.makedirs(os.path.join(dir_path, 'out'), exist_ok=True)

    run_build_food_entity_db_pipeline()
    run_manage_what_words_pipeline()
    run_build_ontology_pipeline()
    # run_build_evaluate_maintain_fkg_db_pipeline()
