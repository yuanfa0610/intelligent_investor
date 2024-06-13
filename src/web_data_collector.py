import csv
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

driver = webdriver.Chrome()

macrotrends_stock_screener_url = 'https://www.macrotrends.net/stocks/stock-screener'

stocks_table_id = 'jqxGrid'
descriptive_tab_id = 'columns_descriptive'
country_column_header_xpath = "//span[text()='Country']"
column_headers_css_selector = "div[role='columnheader']"
row_id_prefix = 'row'
row_id_suffix = 'jqxGrid'
grid_cell_css_selector = 'div[role="gridcell"]'
next_button_css_selector = 'div[title="next"]'

column_headers_text = ["Stock Name", "Ticker", "Market Cap", "Exchange", "Country", "Sector", "Industry"]

current_date = datetime.date.today()
generated_csv_files_folder = 'generated_csv_files'
stocks_descriptive_filename = f'{generated_csv_files_folder}/stocks_descriptive_{current_date}.csv'

num_of_records_to_collect = 1000
num_of_records_collected = 0
rows_per_page = 20

try:
    # Open the URL
    driver.get(macrotrends_stock_screener_url)
    driver.maximize_window()

     # Wait until 'Stocks' table is visible
    WebDriverWait(driver, 10).until(
        expected_conditions.visibility_of_element_located((By.ID, stocks_table_id))
    )

    # Click the 'Descriptive' tab
    descriptive_tab = driver.find_element(By.ID, descriptive_tab_id)
    descriptive_tab.click()

     # Wait until 'Country' column is visible
    WebDriverWait(driver, 10).until(
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

        
    
    # Create a new csv file with specified column headers and collected data
    with open(stocks_descriptive_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

    print(f"CSV file '{stocks_descriptive_filename}' generated successfully.")

    


finally:
    # Close the browser
    driver.quit()