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

config_file_name = general_config['config_file_name']['company_financial_ratios']
config_file_path = f'{config_folder}/{config_file_name}'
default_page_wait_time = general_config['default_page_wait_time']

with open(config_file_path, 'r') as config_file:
    config = yaml.safe_load(config_file)

company_financial_ratios_url_prefix = config['network']['company_financial_ratios_url_prefix']
company_financial_ratios_url_suffix = config['network']['company_financial_ratios_url_suffix']

base_stocks_desctiptive_csv_file_path = config['file']['base_stocks_desctiptive_csv_file_path']

financial_ratios_table_id = config['page_locator']['financial_ratios_table_id']
attribute_row_css_selector = config['page_locator']['attribute_row_css_selector']
grid_cell_css_selector = config['page_locator']['grid_cell_css_selector']

financial_ratios_attributes = config['data_table']['attributes']
starting_company_index = config['data_table']['starting_company_index']
num_of_companies_to_collect_data_from = config['data_table']['num_of_companies_to_collect_data_from']
latest_year_to_collect = config['data_table']['latest_year_to_collect']
years_of_records_to_collect = config['data_table']['years_of_records_to_collect']

current_date = datetime.date.today()
generated_csv_files_folder = general_config['generated_csv_files_folder']
generated_csv_files_sub_folder = config['file']['generated_csv_files_sub_folder']
company_financial_ratios_filename_suffix = config['file']['company_financial_ratios_filename_suffix']
company_financial_ratios_filename = f'{generated_csv_files_folder}/{generated_csv_files_sub_folder}/financial_ratios_{company_financial_ratios_filename_suffix}_{current_date}.csv'

try:

    # Read the base csv file to grab company names and tickers
    stocks_info = []
    with open(base_stocks_desctiptive_csv_file_path, mode='r', newline='') as file:
      stocks_data = csv.reader(file)
    
      for stock_data in stocks_data:
          stocks_info.append([stock_data[0], stock_data[1]])
      
      stocks_info = stocks_info[1:]

    # Verify expected number of stocks' info are retrived
    assert len(stocks_info) >= num_of_companies_to_collect_data_from

    companies = []
    
    for stock_info in stocks_info[starting_company_index : (starting_company_index + num_of_companies_to_collect_data_from)]:
        print(stock_info)
        stock_ticker = stock_info[1]
        company_name_with_dash = stock_info[0].lower().replace(' ', '-')
        company_financial_ratios_url = f'{company_financial_ratios_url_prefix}/{stock_ticker}/{company_name_with_dash}/{company_financial_ratios_url_suffix}'
        company_financial_ratios_url = company_financial_ratios_url.replace('&', '-')
        print(company_financial_ratios_url)

        # For each stock, open the URL for financial_ratios of the corresponding company
        driver.get(company_financial_ratios_url)
        driver.maximize_window()

        financial_ratios_table = WebDriverWait(driver, 30).until(
            expected_conditions.visibility_of_element_located((By.ID, financial_ratios_table_id))
        )

        time.sleep(2)

        attribute_rows = financial_ratios_table.find_elements(By.CSS_SELECTOR, attribute_row_css_selector)

        # Verify the number of rows match the number of expected attributes
        assert len(attribute_rows) == len(financial_ratios_attributes)

        company = Company(stock_info[0], stock_info[1])

        print(f'Collecting financial_ratios for {company}...')

        financial_ratios = {}
        attribute_index = 0
        # Collect data
        for attribute_row in attribute_rows:
            print(f'Collecting {financial_ratios_attributes[attribute_index]} data ...')
            financial_ratios[financial_ratios_attributes[attribute_index]] = []
            grid_cells = attribute_row.find_elements(By.CSS_SELECTOR, grid_cell_css_selector)

            years_of_records_collected = 0
            for grid_cell in grid_cells[2 : ]:
                financial_ratios[financial_ratios_attributes[attribute_index]].append(grid_cell.text)
                print(grid_cell.text)
                years_of_records_collected += 1
                if years_of_records_collected == years_of_records_to_collect:
                    break
            
            # Verify the required number of years of records are collected
            if years_of_records_collected != years_of_records_to_collect:
                print(f'Only {years_of_records_collected} years data have been collected for company {company.ticker}')

            attribute_index += 1

        company.financial_ratios = financial_ratios
        companies.append(company)
        print(f'Financial ratios collected for {company}')

    # Initilize data with column headers
    column_headers_text = ['Stock Name', 'Ticker'] + financial_ratios_attributes + ['Year']
    data = [
        column_headers_text
    ]

    # Convert collected data to row-based data
    rows_data = []
    for company in companies:
        for year_index in range(0, years_of_records_to_collect):
            row_data = [company.name, company.ticker]
            for financial_ratios_attribute in financial_ratios_attributes:
                if year_index < len(company.financial_ratios[financial_ratios_attribute]):
                    row_data.append(company.financial_ratios[financial_ratios_attribute][year_index])
                else:
                    row_data.append('')
            row_data.append(latest_year_to_collect - year_index)
            rows_data.append(row_data)
        
    data += rows_data

    # Create the directory for csv files to generate if it does not exist
    os.makedirs(generated_csv_files_folder, exist_ok=True)
    os.makedirs(f'{generated_csv_files_folder}/{generated_csv_files_sub_folder}', exist_ok=True)
    
    # Create a new csv file with specified column headers and collected data
    with open(company_financial_ratios_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

    print(f"CSV file '{company_financial_ratios_filename}' generated successfully.")

finally:
    # Close the browser
    driver.quit()