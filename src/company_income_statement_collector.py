import csv
import datetime
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import time
import yaml

from company import Company

driver = webdriver.Chrome()

config_folder = 'config'
general_config_file_path = f'{config_folder}/config.yaml'

# Read config files to populate the configurations
with open(general_config_file_path, 'r') as config_file:
    general_config = yaml.safe_load(config_file)

config_file_name = general_config['config_file_name']['company_income_statement']
config_file_path = f'{config_folder}/{config_file_name}'
default_page_wait_time = general_config['default_page_wait_time']

with open(config_file_path, 'r') as config_file:
    config = yaml.safe_load(config_file)

company_income_statement_url_prefix = config['network']['company_income_statement_url_prefix']
company_income_statement_url_suffix = config['network']['company_income_statement_url_suffix']
num_of_stocks_to_collect_data_from = config['network']['num_of_stocks_to_collect_data_from']

base_stocks_desctiptive_csv_file_path = config['file']['base_stocks_desctiptive_csv_file_path']

income_statement_table_id = config['page_locator']['income_statement_table_id']
attribute_row_css_selector = config['page_locator']['attribute_row_css_selector']
grid_cell_css_selector = config['page_locator']['grid_cell_css_selector']

income_statement_attributes = config['data_table']['attributes']
num_of_companies_to_collect_data_from = config['data_table']['num_of_companies_to_collect_data_from']
latest_year_to_collect = config['data_table']['latest_year_to_collect']
years_of_records_to_collect = config['data_table']['years_of_records_to_collect']

current_date = datetime.date.today()
generated_csv_files_folder = general_config['generated_csv_files_folder']
generated_csv_files_sub_folder = config['file']['generated_csv_files_sub_folder']
company_income_statements_filename = f'{generated_csv_files_folder}/{generated_csv_files_sub_folder}/income_statements_{current_date}.csv'

try:

    # Read the base csv file to grab company names and tickers
    stocks_info = []
    with open(base_stocks_desctiptive_csv_file_path, mode='r', newline='') as file:
      stocks_data = csv.reader(file)
    
      for stock_data in stocks_data:
          stocks_info.append([stock_data[0], stock_data[1]])
      
      stocks_info = stocks_info[1:]

    # Verify expected number of stocks' info are retrived
    assert len(stocks_info) == num_of_stocks_to_collect_data_from

    companies = []
    
    for stock_info in stocks_info[0 : num_of_companies_to_collect_data_from + 1]:
        stock_ticker = stock_info[1]
        company_name_with_dash = stock_info[0].lower().replace(' ', '-')
        company_income_statement_url = f'{company_income_statement_url_prefix}/{stock_ticker}/{company_name_with_dash}/{company_income_statement_url_suffix}'

        # For each stock, open the URL for income statement of the corresponding company
        driver.get(company_income_statement_url)
        driver.maximize_window()

        income_statement_table = WebDriverWait(driver, 30).until(
            expected_conditions.visibility_of_element_located((By.ID, income_statement_table_id))
        )

        time.sleep(2)

        attribute_rows = income_statement_table.find_elements(By.CSS_SELECTOR, attribute_row_css_selector)

        # Verify the number of rows match the number of expected attributes
        assert len(attribute_rows) == len(income_statement_attributes)

        company = Company(stock_info[0], stock_info[1])

        print(f'Collecting income statements for {company}...')

        income_statements = {}
        attribute_index = 0
        # Collect data
        for attribute_row in attribute_rows:
            print(f'Collecting {income_statement_attributes[attribute_index]} data ...')
            income_statements[income_statement_attributes[attribute_index]] = []
            grid_cells = attribute_row.find_elements(By.CSS_SELECTOR, grid_cell_css_selector)

            years_of_records_collected = 0
            for grid_cell in grid_cells[2 : ]:
                income_statements[income_statement_attributes[attribute_index]].append(grid_cell.text)
                print(grid_cell.text)
                years_of_records_collected += 1
                if years_of_records_collected == years_of_records_to_collect:
                    break
            
            # Verify the required number of years of records are collected
            assert years_of_records_collected == years_of_records_to_collect

            attribute_index += 1

        company.income_statements = income_statements
        companies.append(company)
        print(f'Income statements collected for {company}')

    # Initilize data with column headers
    column_headers_text = ['Stock Name', 'Ticker'] + income_statement_attributes + ['Year']
    data = [
        column_headers_text
    ]

    # Convert collected data to row-based data
    rows_data = []
    for company in companies:
        for year_index in range(0, years_of_records_to_collect):
            row_data = [company.name, company.ticker]
            for income_statement_attribute in income_statement_attributes:
                row_data.append(company.income_statements[income_statement_attribute][year_index])
            row_data.append(latest_year_to_collect - year_index)
            rows_data.append(row_data)
        
    data += rows_data

    # Create the directory for csv files to generate if it does not exist
    os.makedirs(generated_csv_files_folder, exist_ok=True)
    os.makedirs(f'{generated_csv_files_folder}/{generated_csv_files_sub_folder}', exist_ok=True)
    
    # Create a new csv file with specified column headers and collected data
    with open(company_income_statements_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

    print(f"CSV file '{company_income_statements_filename}' generated successfully.")

finally:
    # Close the browser
    driver.quit()