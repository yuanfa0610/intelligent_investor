import csv
import datetime
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import yaml

driver = webdriver.Chrome()

config_folder = 'config'
general_config_file_path = f'{config_folder}/config.yaml'

# Read config files to populate the configurations
with open(general_config_file_path, 'r') as config_file:
    general_config = yaml.safe_load(config_file)

config_file_name = general_config['config_file_name']['stocks_descriptive']
config_file_path = f'{config_folder}/{config_file_name}'
default_page_wait_time = general_config['default_page_wait_time']

with open(config_file_path, 'r') as config_file:
    config = yaml.safe_load(config_file)

macrotrends_stock_screener_url = config['network']['macrotrends_stock_screener_url']

stocks_table_id = config['page_locator']['stocks_table_id']
descriptive_tab_id = config['page_locator']['descriptive_tab_id']
country_column_header_xpath = config['page_locator']['country_column_header_xpath']
column_headers_css_selector = config['page_locator']['column_headers_css_selector']
row_id_prefix = config['page_locator']['row_id_prefix']
row_id_suffix = config['page_locator']['row_id_suffix']
grid_cell_css_selector = config['page_locator']['grid_cell_css_selector']
next_button_css_selector = config['page_locator']['next_button_css_selector']

column_headers_text = config['data_table']['column_headers_text']

current_date = datetime.date.today()
generated_csv_files_folder = general_config['generated_csv_files_folder']
generated_csv_files_sub_folder = config['file']['generated_csv_files_sub_folder']
stocks_descriptive_filename = f'{generated_csv_files_folder}/{generated_csv_files_sub_folder}/stocks_descriptive_{current_date}.csv'

num_of_records_collected = 0
num_of_records_to_collect = config['data_table']['num_of_records_to_collect']
rows_per_page = config['data_table']['rows_per_page']

try:
    # Open the URL
    driver.get(macrotrends_stock_screener_url)
    driver.maximize_window()

     # Wait until 'Stocks' table is visible
    WebDriverWait(driver, default_page_wait_time).until(
        expected_conditions.visibility_of_element_located((By.ID, stocks_table_id))
    )

    # Click the 'Descriptive' tab
    descriptive_tab = driver.find_element(By.ID, descriptive_tab_id)
    descriptive_tab.click()

     # Wait until 'Country' column is visible
    WebDriverWait(driver, default_page_wait_time).until(
        expected_conditions.visibility_of_element_located((By.XPATH, country_column_header_xpath))
    )

    # Get all column headers
    column_headers = driver.find_elements(By.CSS_SELECTOR, column_headers_css_selector)

    # Verify all expected column headers show up
    assert len(column_headers) == len(column_headers_text)
    for i in range(0, len(column_headers) - 1):
        assert column_headers[i].text.startswith(column_headers_text[i])

    # Initilize data with column headers
    data = [
        column_headers_text
    ]

    # Collect data from the table
    while num_of_records_collected < num_of_records_to_collect:
        for row_index in range(0, rows_per_page):
            record_element = driver.find_element(By.ID, f'{row_id_prefix}{row_index}{row_id_suffix}')
            record_data_elements = record_element.find_elements(By.CSS_SELECTOR, grid_cell_css_selector)
            record_data = []
            for i in range(0, len(record_data_elements)):
                record_data.append(record_data_elements[i].text)
            data.append(record_data)
            num_of_records_collected += 1
        next_button = driver.find_element(By.CSS_SELECTOR, next_button_css_selector)
        next_button.click()

    # Create the directory for csv files to generate if it does not exist
    os.makedirs(generated_csv_files_folder, exist_ok=True)
    os.makedirs(f'{generated_csv_files_folder}/{generated_csv_files_sub_folder}', exist_ok=True)
    
    # Create a new csv file with specified column headers and collected data
    with open(stocks_descriptive_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

    print(f"CSV file '{stocks_descriptive_filename}' generated successfully.")

finally:
    # Close the browser
    driver.quit()