import time
import random
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains

def scrape_rmp_sjsu():
    # 기존 CSV 파일이 있는지 확인하고 있으면 읽어오기
    existing_professors = []
    csv_filename = 'sjsu_professors_data.csv'
    
    if os.path.exists(csv_filename):
        try:
            existing_df = pd.read_csv(csv_filename)
            existing_professors = existing_df.to_dict('records')
            print(f"Loaded {len(existing_professors)} existing professors from {csv_filename}")
        except Exception as e:
            print(f"Error loading existing data: {e}")
            existing_professors = []
    
    # Set up Chrome options
    chrome_options = Options()
    
    # SSL Error handling options
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--allow-running-insecure-content')
    
    # Regular options
    # chrome_options.add_argument("--headless")  # Comment this out to see the browser
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    # Initialize the driver with ChromeDriverManager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Go to Rate My Professor SJSU page
    url = "https://www.ratemyprofessors.com/search/professors/881?q=*"
    driver.get(url)
    
    # Wait for any cookie consent popups and dismiss them if necessary
    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[aria-label='Accept cookies']"))
        ).click()
        print("Accepted cookies popup")
    except:
        print("No cookies popup found or could not click it")
    
    # 기존 데이터를 professors_data에 복사
    professors_data = existing_professors.copy()
    existing_names = {p['Name'] for p in existing_professors}
    
    new_professors_added = 0
    
    try:
        # Wait for the page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[class*='TeacherCard__StyledTeacherCard']"))
        )
        
        # How many times to click "Show More"
        max_pages = 20  # Adjust this value as needed
        
        for page in range(max_pages):
            print(f"Processing page {page + 1}...")
            
            # Wait a moment for any dynamic content to load
            time.sleep(3)
            
            # Find all professor cards
            professor_cards = driver.find_elements(By.CSS_SELECTOR, "a[class*='TeacherCard__StyledTeacherCard']")
            
            new_professors_on_page = 0
            
            for card in professor_cards:
                try:
                    # Extract name
                    name_element = card.find_element(By.CSS_SELECTOR, "div[class*='CardName__StyledCardName']")
                    name = name_element.text.strip()
                    
                    # Check if this professor is already in our existing data
                    if name in existing_names:
                        continue
                    
                    # Extract department
                    department_element = card.find_element(By.CSS_SELECTOR, "div[class*='CardSchool__Department']")
                    department = department_element.text.strip()
                    
                    # Extract rating
                    rating_element = card.find_element(By.CSS_SELECTOR, "div[class*='CardNumRating__CardNumRatingNumber']")
                    rating = rating_element.text.strip()
                    
                    # Extract "would take again" and "level of difficulty"
                    feedback_items = card.find_elements(By.CSS_SELECTOR, "div[class*='CardFeedback__CardFeedbackItem']")
                    would_take_again = "N/A"
                    difficulty = "N/A"
                    
                    for item in feedback_items:
                        item_text = item.text.strip()
                        if "would take again" in item_text:
                            would_take_again = item_text.split("would take again")[0].strip()
                        elif "level of difficulty" in item_text:
                            difficulty = item_text.split("level of difficulty")[0].strip()
                    
                    # Add to our data list
                    professors_data.append({
                        'Name': name,
                        'Department': department,
                        'Rating': rating,
                        'Would Take Again': would_take_again,
                        'Level of Difficulty': difficulty
                    })
                    
                    # Add to our set of existing names
                    existing_names.add(name)
                    
                    new_professors_added += 1
                    new_professors_on_page += 1
                    
                    print(f"Added: {name} from {department}")
                    
                except Exception as e:
                    print(f"Error extracting professor data: {e}")
            
            print(f"Added {new_professors_on_page} new professors on this page")
            
            # 이 페이지에서 새로운 교수가 없으면 다음 페이지로 넘어가는 것이 의미 없을 수 있음
            if new_professors_on_page == 0:
                print("No new professors found on this page. We might have all data already.")
                # 일단은 계속 진행 (다음 페이지에 새로운 교수가 있을 수도 있음)
            
            # Try to click "Show More" button with precise selector
            try:
                # Use the exact class names from the HTML
                show_more_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.Buttons__Button-sc-19xdot-1.PaginationButton__StyledPaginationButton-txi1dr-1"))
                )
                
                # If that specific selector doesn't work, try a more general one
                if not show_more_button:
                    show_more_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[text()='Show More']"))
                    )
                
                # Scroll to make button visible, but stop a bit before it
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", show_more_button)
                time.sleep(2)  # Wait for scroll to complete
                
                # Try JavaScript click which is more reliable for intercepted elements
                driver.execute_script("arguments[0].click();", show_more_button)
                print("Clicked 'Show More' button with JavaScript")
                
                # Wait for more content to load
                time.sleep(4)
                
            except Exception as e:
                print(f"Error with primary click method: {e}")
                
                # Try removing overlays that might be intercepting clicks
                try:
                    # Remove any overlays or popups that might be intercepting clicks
                    driver.execute_script("""
                        var elements = document.querySelectorAll('div.bx-slab');
                        for(var i=0; i<elements.length; i++){
                            elements[i].parentNode.removeChild(elements[i]);
                        }
                    """)
                    
                    # Try clicking by selector
                    driver.execute_script("document.querySelector('button[type=\"button\"][class*=\"PaginationButton\"]').click();")
                    print("Removed overlays and clicked button")
                    
                    time.sleep(3)
                except Exception as overlay_error:
                    print(f"Couldn't remove overlays: {overlay_error}")
                    
                    # One last attempt - try clicking any button at the bottom of the page
                    try:
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(2)
                        driver.execute_script("""
                            var buttons = document.querySelectorAll('button');
                            for(var i=0; i<buttons.length; i++) {
                                if(buttons[i].textContent.includes('Show More')) {
                                    buttons[i].click();
                                    break;
                                }
                            }
                        """)
                        print("Tried clicking with JavaScript by text content")
                        time.sleep(3)
                    except Exception as final_error:
                        print(f"All click attempts failed: {final_error}")
                        break
            
            # Verify if we loaded new content by checking element count
            new_cards = driver.find_elements(By.CSS_SELECTOR, "a[class*='TeacherCard__StyledTeacherCard']")
            if len(new_cards) <= len(professor_cards):
                print("No new cards loaded after clicking 'Show More'. May have reached the end.")
                break
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        
    finally:
        # Close the driver
        driver.quit()
        
    # Create DataFrame and save to CSV
    df = pd.DataFrame(professors_data)
    df.to_csv(csv_filename, index=False)
    print(f"Updated data with {new_professors_added} new professors. Total: {len(professors_data)} professors saved to {csv_filename}")
    
    return df

# Run the scraper
if __name__ == "__main__":
    professors_df = scrape_rmp_sjsu()