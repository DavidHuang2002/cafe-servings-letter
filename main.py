from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from threading import Thread
import os
import datetime

def write_list_to_file(file_path, data):
    with open(file_path, 'w') as file:
        # Join the list elements with a comma and write to the file
        file.write(','.join(map(str, data)))

def read_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        return content

def print_all_file_content(folder_path):
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        # Check if it's a file and not a directory
        if os.path.isfile(file_path):
            print(file_name)  # Print the name of the file
            print(read_file(file_path))
            print("")

def today_folder_path(base_path):
    # Get today's date in the format mm-dd-yy
    today = datetime.datetime.now().strftime("%m-%d-%y")

    # Combine the base path with the new folder name
    folder_path = os.path.join(base_path, today)
    return folder_path
#
# def today_folder_exists(base_path):
#     return os.path.exists(today_folder_path(base_path))


# assuming today folder doesnt exist
def create_date_folder(path):
    # Get today's date in the format mm-dd-yy
    today = datetime.datetime.now().strftime("%m-%d-%y")

    # Combine the base path with the new folder name
    folder_path = os.path.join(path, today)

    # Create the folder if it doesn't already exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder created: {folder_path}")
    else:
        print(f"Folder already exists: {folder_path}")
    return folder_path



menu_url = 'https://netnutrition.cbord.com/nn-prod/vucampusdining'
cafe_xpath_dict = {
    "commons": '//*[@id="cbo_nn_unitImages_2"]/div/div/a',
    "roth": '//*[@id="cbo_nn_unitImages_20"]/div/div/a',
    "ebi": '//*[@id="cbo_nn_unitImages_11"]/div/div/a'
}

lunch_xpath = '//*[@id="cbo_nn_menuDataList"]/div/div[1]/section/div/div/div[2]/a'
dinner_path = '//*[@id="cbo_nn_menuDataList"]/div/div[1]/section/div/div/div[3]/a'

serving_xpath_dict = {
    "commons": '//*[@id="itemPanel"]/section/div[4]/table/tbody/tr[40]/td/div',
    "roth": "/html/body/div/main/form/div/div[2]/div/div[5]/section/div[4]/table/tbody/tr[24]/td/div",
    "ebi": '//*[@id="itemPanel"]/section/div[4]/table/tbody/tr[1]/td/div'
}

back_xpath_serving = "/html/body/div/main/form/div/div[2]/div/div[5]/section/div[1]/nav/a[1]"
back_xpath_cafe = "/html/body/div/main/form/div/div[2]/div/div[3]/section/nav/a"

def threaded_cafe_serving(cafe_name, date_folder):
    driver = webdriver.Chrome()
    """Wrapper for get_cafe_serving to run in a thread."""
    get_cafe_serving(driver, cafe_name, date_folder)
    driver.quit()

#  TODO refactor the finding method tehy all are pretty similar
def roth_find_food(driver):
    rows = driver.find_elements(By.XPATH, '//tr[@data-categoryid="2749"]')

    # Iterate through each row
    food = []
    for row in rows:
        # Find all td elements with class "align-middle" within the row
        tds = row.find_elements(By.CLASS_NAME, "align-middle")

        # Extract and print the text content of each td element
        food_td = tds[1]
        food.append(food_td.text)
        # for td in tds:
        #     print(td.text)
    return food



def ebi_find_food(driver):
    rows = driver.find_elements(By.XPATH, '//tr[@data-categoryid="755"]')
    # Iterate through each row
    food = []
    for row in rows:
        # Find all td elements with class "align-middle" within the row
        tds = row.find_elements(By.CLASS_NAME, "align-middle")

        # Extract and print the text content of each td element
        food_td = tds[1]
        food.append(food_td.text)
    return food

find_food_methods = {
    "roth": roth_find_food,
    "ebi": ebi_find_food,
}


def wait_n_click(driver, x_path, timeout=10):
    link = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, x_path))
    )
    link.click()


def get_cafe_serving(driver, cafe_name, data_folder_path):
    # Navigate to the website
    driver.get(menu_url)
    cafe_xpath = cafe_xpath_dict[cafe_name]
    serving_xpath = serving_xpath_dict[cafe_name]
    meal_path = dinner_path

    wait_n_click(driver, cafe_xpath)
    wait_n_click(driver, meal_path)
    wait_n_click(driver, serving_xpath)
    food = find_food_methods[cafe_name](driver)
    file_path = data_folder_path + "/" + cafe_name + ".txt"
    write_list_to_file(file_path, food)
    # time.sleep(3)
    # wait_n_click(driver, back_xpath_serving)
    # wait_n_click(driver, back_xpath_cafe)


def scrape_food(base_path):
    date_folder = create_date_folder(base_path)
    # print(driver.title)
    #
    # # get_cafe_serving(driver, "roth")
    # get_cafe_serving(driver, "ebi")
    # # TODO write to get the Home Grown section of Roth dinner
    # driver.quit()
    # Create threads for each cafe without using a wrapper function
    roth_thread = Thread(target=threaded_cafe_serving, args=["roth", date_folder])
    time.sleep(1)
    ebi_thread = Thread(target=threaded_cafe_serving, args=["ebi", date_folder])

    # Start threads
    roth_thread.start()
    ebi_thread.start()

    # Wait for both threads to complete
    roth_thread.join()
    ebi_thread.join()


def main():
    base_path = "/Users/davidhuang/Desktop/Project/coding-projects/cafe-servings-letter/data"
    today_folder = today_folder_path(base_path)
    if os.path.exists(today_folder):
        # read out existing data
        # read_file(today_folder)
        print_all_file_content(today_folder)
    else:
        scrape_food(base_path)
        print_all_file_content(today_folder)







if __name__ == '__main__':
    main()
