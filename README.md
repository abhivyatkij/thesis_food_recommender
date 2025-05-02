# recipe-ontology
Recipe Ontology

- Use the 'make' command to setup the virtual environment and install the required libraries described in requirements.txt file.

- 'in/' folder will contain csv and other files that would work as an input to the application. 

- 'out_build_ontology_pipeline/' folder is the output folder. All the *.csv, *.html and *.png files get created inside 'out/' folder. Use 'make clean_output' to directly get rid of the out/ folder through command line interface. Use make clean_logs to delete all the logs and use make clean_all to delete output, logs and virtualenv folders. Feel free to add more commands in the Makefile as needed.

- After running the Makefile, the virtual environment will have to be manually activated in order to run main.py or other individual scripts.
