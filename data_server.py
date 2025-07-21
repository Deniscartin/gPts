import requests
from flask import Flask, jsonify, render_template, request
import investpy
import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
import threading
import re
from functools import wraps

# --- Configuration ---
EXCHANGE_RATE_URL = 'https://api.frankfurter.app/latest?from=USD&to=EUR'
FIRESTORE_COLLECTION = 'platts'
FIRESTORE_DOCUMENT = 'auto10'

# --- Flask App Setup ---
app = Flask(__name__, template_folder='platts')

# Initialize Firebase Admin
try:
    if not firebase_admin._apps:
        # Try different credential sources
        credential_paths = [
            "serviceAccount.json",
            "firebase-credentials.json",
            os.path.join(os.getcwd(), "firebase-credentials.json")
        ]
        
        cred = None
        for path in credential_paths:
            if os.path.exists(path):
                print(f"Using Firebase credentials from: {path}")
                cred = credentials.Certificate(path)
                break
        
        if cred:
            firebase_admin.initialize_app(cred)
        else:
            print("No Firebase credentials found, using application default credentials")
            firebase_admin.initialize_app()
    
    db = firestore.client()
    print("Firebase initialized successfully")
except Exception as e:
    print(f"Firebase initialization failed: {e}")
    print("Using mock data for development. See firebase_setup.md for configuration instructions.")
    db = None

def verify_token(f):
    """
    Decorator to verify Firebase Auth token from Authorization header
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "Token di autenticazione mancante"}), 401
        
        try:
            # Extract token from "Bearer <token>"
            token = auth_header.split('Bearer ')[1]
        except IndexError:
            return jsonify({"error": "Formato token non valido"}), 401
        
        try:
            # Verify the token with Firebase Admin
            decoded_token = auth.verify_id_token(token)
            # Add user info to request context
            request.current_user = decoded_token
            return f(*args, **kwargs)
        except auth.InvalidIdTokenError:
            return jsonify({"error": "Token non valido"}), 401
        except auth.ExpiredIdTokenError:
            return jsonify({"error": "Token scaduto"}), 401
        except Exception as e:
            print(f"Token verification error: {e}")
            return jsonify({"error": "Errore verifica autenticazione"}), 401
    
    return decorated_function

def get_base_value_from_firestore():
    """
    Retrieves the base value (mq) and base Platts price from Firestore collection platts/auto10
    """
    try:
        if db is None:
            print("Firestore not initialized, using mock data")
            return 729.25, 1.1646  # Mock values for testing
        
        doc_ref = db.collection(FIRESTORE_COLLECTION).document(FIRESTORE_DOCUMENT)
        doc = doc_ref.get()
        
        if doc.exists:
            data = doc.to_dict()
            base_value = data.get('mq', 729.25)  # Default to 729.25 if not found
            base_platts_price = data.get('platts_price', 1.1646)  # Default to 1.1646 if not found
            print(f"Retrieved from Firestore: base value={base_value}, base Platts price={base_platts_price}")
            return base_value, base_platts_price
        else:
            print("Document not found in Firestore, using default values")
            return 729.25, 1.1646
    except Exception as e:
        print(f"Error retrieving from Firestore: {e}")
        return 729.25, 1.1646  # Default values

def get_price_change_from_investing():
    """
    Gets price change from investing.com using investpy API
    """
    print("--- Starting price change retrieval using investpy ---")
    
    try:
        # Get recent data for London Gas Oil
        print("Fetching London Gas Oil data...")
        recent_data = investpy.get_commodity_recent_data(commodity='London Gas Oil')
        
        if len(recent_data) < 2:
            print("Insufficient data to calculate price change")
            return None
        
        # Get the latest and previous close prices
        latest = recent_data.iloc[-1]
        previous = recent_data.iloc[-2]
        
        price_change = latest['Close'] - previous['Close']
        
        print(f"Latest close price: {latest['Close']:.2f} USD/MT")
        print(f"Previous close price: {previous['Close']:.2f} USD/MT")
        print(f"Price change: {price_change:+.2f} USD/MT")
        
        return price_change
        
    except Exception as e:
        print(f"!!! investpy data retrieval failed: {e}")
        print("Trying alternative search method...")
        
        try:
            # Fallback to search method
            search_result = investpy.search_quotes(text='London Gas Oil', products=['commodities'], n_results=1)
            if search_result:
                recent_data = search_result.retrieve_recent_data()
                
                if len(recent_data) >= 2:
                    latest = recent_data.iloc[-1]
                    previous = recent_data.iloc[-2]
                    price_change = latest['Close'] - previous['Close']
                    
                    print(f"Search method - Latest close: {latest['Close']:.2f}, Previous: {previous['Close']:.2f}")
                    print(f"Search method - Price change: {price_change:+.2f} USD/MT")
                    
                    return price_change
        except Exception as search_error:
            print(f"!!! Search method also failed: {search_error}")
        
        return None

# COMMENTED OUT - Using only investing.com scraping now
# def get_bloomberg_change():
#     """
#     Scrapes Gasoil (Nymex) change from Bloomberg Energy page
#     """
#     print("--- Starting Bloomberg scraping ---")
#     
#     options = webdriver.ChromeOptions()
#     options.add_argument('--headless')
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')
#     options.add_argument('--disable-blink-features=AutomationControlled')
#     options.add_argument('--disable-gpu')
#     options.add_argument('--disable-software-rasterizer')
#     options.add_argument('--disable-background-timer-throttling')
#     options.add_argument('--disable-backgrounding-occluded-windows')
#     options.add_argument('--disable-renderer-backgrounding')
#     options.add_argument('--disable-features=TranslateUI')
#     options.add_argument('--disable-ipc-flooding-protection')
#     options.add_argument('--remote-debugging-port=9222')
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option('useAutomationExtension', False)
#     options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
#     
#     try:
#         # Try to use Chrome, fallback to Chromium if needed
#         try:
#             driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
#         except Exception as chrome_error:
#             print(f"Chrome failed, trying Chromium: {chrome_error}")
#             # Fallback to Chromium
#             options.binary_location = "/usr/bin/chromium"
#             driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
#         
#         with driver:
#             # Execute script to remove webdriver property
#             driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
#             
#             print(f"Fetching {BLOOMBERG_URL}...")
#             driver.get(BLOOMBERG_URL)
#             
#             # Wait for page to load and add delay for JavaScript content
#             import time
#             time.sleep(5)
#             
#             wait = WebDriverWait(driver, 30)
# 
#             # Handle cookie consent if present
#             try:
#                 cookie_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Accept')] | //button[contains(text(), 'Accept')] | //*[contains(text(), 'Accetta')] | //*[contains(text(), 'agree')]")))
#                 cookie_button.click()
#                 print("Cookie consent accepted.")
#                 time.sleep(2)
#             except Exception:
#                 print("No cookie consent found, continuing...")
# 
#             print("Looking for QS1:COM Gasoil (Nymex) data...")
#             
#             # Wait for table content to load with specific selectors
#             try:
#                 # Wait for the data table to be present
#                 wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tr.data-table-row")))
#                 time.sleep(5)  # Extended wait for dynamic content
#                 
#                 print("Searching for QS1:COM row using CSS selectors...")
#                 
#                 # Method 1: Look for QS1:COM using the exact table structure
#                 qs1_rows = driver.find_elements(By.CSS_SELECTOR, "tr.data-table-row")
#                 print(f"Found {len(qs1_rows)} data table rows")
#                 
#                 # DETAILED DEBUG: Show all table content
#                 print("\n=== COMPLETE TABLE CONTENT DEBUG ===")
#                 
#                 for i, row in enumerate(qs1_rows):
#                     try:
#                         print(f"\n--- ROW {i+1} ---")
#                         row_text = row.text.strip()
#                         print(f"Row text: '{row_text}'")
#                         
#                         # Get all cells in this row
#                         all_cells = row.find_elements(By.CSS_SELECTOR, "td, th")
#                         print(f"Found {len(all_cells)} cells in row {i+1}")
#                         
#                         for j, cell in enumerate(all_cells):
#                             cell_text = cell.text.strip()
#                             cell_data_type = cell.get_attribute("data-type")
#                             cell_aria_label = cell.get_attribute("aria-label")
#                             print(f"  Cell {j+1}: '{cell_text}' (data-type: {cell_data_type}, aria-label: {cell_aria_label})")
#                             
#                             # Look for spans inside the cell
#                             spans = cell.find_elements(By.CSS_SELECTOR, "span.data-table-row-cell__value")
#                             for k, span in enumerate(spans):
#                                 span_text = span.text.strip()
#                                 print(f"    Span {k+1}: '{span_text}'")
#                         
#                         # Check if this row contains QS1:COM
#                         qs1_link = row.find_elements(By.CSS_SELECTOR, "a[href*='QS1:COM']")
#                         if qs1_link:
#                             print(f"*** QS1:COM ROW FOUND! Row {i+1} ***")
#                             
#                             # Get the HTML content of the row
#                             row_html = row.get_attribute("innerHTML")
#                             print(f"Row HTML: {row_html[:500]}...")  # First 500 chars
#                             
#                             # Get ALL cells in order and check the 4th one specifically
#                             all_row_cells = row.find_elements(By.CSS_SELECTOR, "td, th")
#                             print(f"*** QS1:COM ROW HAS {len(all_row_cells)} TOTAL CELLS ***")
#                             
#                             for cell_idx, cell in enumerate(all_row_cells):
#                                 cell_text = cell.text.strip()
#                                 cell_html = cell.get_attribute("innerHTML")
#                                 cell_data_type = cell.get_attribute("data-type")
#                                 print(f"*** QS1:COM Cell {cell_idx+1}: '{cell_text}' (data-type: {cell_data_type}) ***")
#                                 print(f"    Cell HTML: {cell_html[:200]}...")
#                                 
#                                 # Look for spans in each cell
#                                 cell_spans = cell.find_elements(By.CSS_SELECTOR, "span.data-table-row-cell__value")
#                                 for span_idx, span in enumerate(cell_spans):
#                                     span_text = span.text.strip()
#                                     print(f"    Span {span_idx+1}: '{span_text}'")
#                                 
#                                 # Check if this is the 4th cell (index 3) - the change value cell
#                                 if cell_idx == 3:  # 4th cell (0-indexed)
#                                     print(f"*** CHECKING 4TH CELL FOR CHANGE VALUE ***")
#                                     
#                                     # Try to extract value directly from HTML using regex
#                                     html_match = re.search(r'<span class="data-table-row-cell__value">([+-]?\d+\.?\d*)</span>', cell_html)
#                                     if html_match:
#                                         html_value = html_match.group(1)
#                                         print(f"*** FOUND VALUE IN HTML: '{html_value}' ***")
#                                         
#                                         if html_value and html_value.startswith(('+', '-')):
#                                             try:
#                                                 change_value = float(html_value.replace('+', '').replace(',', '.'))
#                                                 print(f"*** FOUND QS1:COM CHANGE VALUE FROM HTML: {html_value} -> {change_value} ***")
#                                                 return change_value
#                                             except ValueError:
#                                                 print(f"Could not parse '{html_value}' as float")
#                                     
#                                     # Try using JavaScript to get the value
#                                     try:
#                                         js_value = driver.execute_script("return arguments[0].innerText || arguments[0].textContent;", cell)
#                                         print(f"*** JavaScript cell value: '{js_value}' ***")
#                                         
#                                         if js_value and js_value.strip().startswith(('+', '-')) and not js_value.endswith('%'):
#                                             try:
#                                                 change_value = float(js_value.strip().replace('+', '').replace(',', '.'))
#                                                 print(f"*** FOUND QS1:COM CHANGE VALUE FROM JS: {js_value} -> {change_value} ***")
#                                                 return change_value
#                                             except ValueError:
#                                                 print(f"Could not parse '{js_value}' as float")
#                                     except Exception as e:
#                                         print(f"JavaScript extraction failed: {e}")
#                                     
#                                     # Try to get the span value
#                                     if cell_spans:
#                                         for span in cell_spans:
#                                             span_text = span.text.strip()
#                                             print(f"*** 4th cell span text: '{span_text}' ***")
#                                             
#                                             # Try JavaScript on the span directly
#                                             try:
#                                                 js_span_value = driver.execute_script("return arguments[0].innerText || arguments[0].textContent;", span)
#                                                 print(f"*** JavaScript span value: '{js_span_value}' ***")
#                                                 
#                                                 if js_span_value and js_span_value.strip().startswith(('+', '-')) and not js_span_value.endswith('%'):
#                                                     try:
#                                                         change_value = float(js_span_value.strip().replace('+', '').replace(',', '.'))
#                                                         print(f"*** FOUND QS1:COM CHANGE VALUE FROM JS SPAN: {js_span_value} -> {change_value} ***")
#                                                         return change_value
#                                                     except ValueError:
#                                                         print(f"Could not parse '{js_span_value}' as float")
#                                             except Exception as e:
#                                                 print(f"JavaScript span extraction failed: {e}")
#                                             
#                                             if span_text and span_text.startswith(('+', '-')) and not span_text.endswith('%'):
#                                                 try:
#                                                     change_value = float(span_text.replace('+', '').replace(',', '.'))
#                                                     print(f"*** FOUND QS1:COM CHANGE VALUE FROM 4TH CELL: {span_text} -> {change_value} ***")
#                                                     return change_value
#                                                 except ValueError:
#                                                     print(f"Could not parse '{span_text}' as float")
#                                     
#                                     # If span is empty, try cell text directly
#                                     if cell_text and cell_text.startswith(('+', '-')) and not cell_text.endswith('%'):
#                                         try:
#                                             change_value = float(cell_text.replace('+', '').replace(',', '.'))
#                                             print(f"*** FOUND QS1:COM CHANGE VALUE FROM 4TH CELL DIRECT: {cell_text} -> {change_value} ***")
#                                             return change_value
#                                         except ValueError:
#                                             print(f"Could not parse '{cell_text}' as float")
#                             
#                             # Wait a bit more and try again if cells are empty
#                             if not any(cell.text.strip() for cell in all_row_cells[1:]):  # Skip first cell (header)
#                                 print("*** CELLS ARE EMPTY, WAITING MORE FOR JAVASCRIPT TO LOAD ***")
#                                 time.sleep(3)
#                                 
#                                 # Try again
#                                 all_row_cells = row.find_elements(By.CSS_SELECTOR, "td, th")
#                                 print(f"*** RETRY: QS1:COM ROW HAS {len(all_row_cells)} TOTAL CELLS ***")
#                                 
#                                 for cell_idx, cell in enumerate(all_row_cells):
#                                     cell_text = cell.text.strip()
#                                     print(f"*** RETRY Cell {cell_idx+1}: '{cell_text}' ***")
#                                     
#                                     if cell_idx == 3:  # 4th cell
#                                         print(f"*** RETRY CHECKING 4TH CELL ***")
#                                         cell_spans = cell.find_elements(By.CSS_SELECTOR, "span.data-table-row-cell__value")
#                                         
#                                         for span in cell_spans:
#                                             span_text = span.text.strip()
#                                             print(f"*** RETRY 4th cell span: '{span_text}' ***")
#                                             
#                                             if span_text and span_text.startswith(('+', '-')) and not span_text.endswith('%'):
#                                                 try:
#                                                     change_value = float(span_text.replace('+', '').replace(',', '.'))
#                                                     print(f"*** FOUND QS1:COM CHANGE VALUE FROM 4TH CELL RETRY: {span_text} -> {change_value} ***")
#                                                     return change_value
#                                                 except ValueError:
#                                                     print(f"Could not parse '{span_text}' as float")
#                                         
#                                         if cell_text and cell_text.startswith(('+', '-')) and not cell_text.endswith('%'):
#                                             try:
#                                                 change_value = float(cell_text.replace('+', '').replace(',', '.'))
#                                                 print(f"*** FOUND QS1:COM CHANGE VALUE FROM 4TH CELL DIRECT RETRY: {cell_text} -> {change_value} ***")
#                                                 return change_value
#                                             except ValueError:
#                                                 print(f"Could not parse '{cell_text}' as float")
#                         
#                         # Alternative: Look for Gasoil (Nymex) text in the row
#                         gasoil_text = row.find_elements(By.XPATH, ".//*[contains(text(), 'Gasoil') and contains(text(), 'Nymex')]")
#                         if gasoil_text:
#                             print(f"*** GASOIL (NYMEX) ROW FOUND! Row {i+1} ***")
#                             
#                             # Extract the change value
#                             change_cells = row.find_elements(By.CSS_SELECTOR, "td[data-type='better'] span.data-table-row-cell__value")
#                             if change_cells:
#                                 for j, cell in enumerate(change_cells):
#                                     change_text = cell.text.strip()
#                                     print(f"*** Gasoil change cell {j+1}: '{change_text}' ***")
#                                     
#                                     if change_text and change_text.startswith(('+', '-')) and not change_text.endswith('%'):
#                                         try:
#                                             change_value = float(change_text.replace('+', '').replace(',', '.'))
#                                             print(f"*** FOUND GASOIL CHANGE VALUE: {change_text} -> {change_value} ***")
#                                             return change_value
#                                         except ValueError:
#                                             continue
#                     
#                     except Exception as e:
#                         print(f"Error processing row {i+1}: {e}")
#                         continue
#                 
#                 print("\n=== END TABLE CONTENT DEBUG ===\n")
#                 
#                 # Method 2: Broader search through all table cells
#                 print("Searching through all table cells...")
#                 all_cells = driver.find_elements(By.CSS_SELECTOR, "span.data-table-row-cell__value")
#                 print(f"Found {len(all_cells)} table cells")
#                 
#                 for i, cell in enumerate(all_cells):
#                     try:
#                         cell_text = cell.text.strip()
#                         if cell_text == "QS1:COM":
#                             print(f"Found QS1:COM cell at position {i+1}")
#                             
#                             # Look for the parent row
#                             row = cell.find_element(By.XPATH, "./ancestor::tr")
#                             
#                             # Find change values in this row
#                             change_cells = row.find_elements(By.CSS_SELECTOR, "td[data-type='better'] span.data-table-row-cell__value")
#                             for j, change_cell in enumerate(change_cells):
#                                 change_text = change_cell.text.strip()
#                                 print(f"QS1:COM row change cell {j+1}: '{change_text}'")
#                                 
#                                 if change_text and change_text.startswith(('+', '-')) and not change_text.endswith('%'):
#                                     try:
#                                         change_value = float(change_text.replace('+', '').replace(',', '.'))
#                                         print(f"Found QS1:COM change value: {change_text} -> {change_value}")
#                                         return change_value
#                                     except ValueError:
#                                         continue
#                     except Exception as e:
#                         continue
#                 
#                 # Method 3: Try to find any change value in USD/MT context
#                 print("Searching for USD/MT context...")
#                 usd_mt_cells = driver.find_elements(By.XPATH, "//*[contains(text(), 'USD/MT')]")
#                 
#                 for cell in usd_mt_cells:
#                     try:
#                         # Get the parent row
#                         row = cell.find_element(By.XPATH, "./ancestor::tr")
#                         
#                         # Check if this row contains Gasoil or QS1
#                         row_text = row.text.lower()
#                         if 'gasoil' in row_text or 'qs1' in row_text:
#                             print(f"Found USD/MT row with Gasoil/QS1: {row.text}")
#                             
#                             # Find change values in this row
#                             change_cells = row.find_elements(By.CSS_SELECTOR, "td[data-type='better'] span.data-table-row-cell__value")
#                             for change_cell in change_cells:
#                                 change_text = change_cell.text.strip()
#                                 print(f"USD/MT row change: '{change_text}'")
#                                 
#                                 if change_text and change_text.startswith(('+', '-')) and not change_text.endswith('%'):
#                                     try:
#                                         change_value = float(change_text.replace('+', '').replace(',', '.'))
#                                         print(f"Found USD/MT change value: {change_text} -> {change_value}")
#                                         return change_value
#                                     except ValueError:
#                                         continue
#                     except Exception as e:
#                         continue
#                 
#                 print("Could not find QS1:COM/Gasoil change value in any method")
#                 return None
#                 
#             except Exception as e:
#                 print(f"Error waiting for table content: {e}")
#                 return None
# 
#     except Exception as e:
#         print(f"!!! Bloomberg scraping failed: {e}")
#         return None

def get_exchange_rate():
    """
    Gets USD/EUR exchange rate
    """
    try:
        print(f"Fetching exchange rate from {EXCHANGE_RATE_URL}...")
        response = requests.get(EXCHANGE_RATE_URL)
        response.raise_for_status()
        rate_data = response.json()
        exchange_rate = rate_data['rates']['EUR']
        print(f"Successfully fetched USD/EUR rate: {exchange_rate}")
        return exchange_rate
    except Exception as e:
        print(f"!!! Exchange rate fetch failed: {e}")
        return None

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('platts_viewer.html')

@app.route('/api/data')
@verify_token
def get_data():
    """API endpoint to get fresh data every time. Requires authentication."""
    user_email = request.current_user.get('email', 'Unknown')
    print(f"--- Fetching fresh data for user: {user_email} ---")
    
    # Get all data fresh - Using only investing.com scraping now
    base_value, base_platts_price = get_base_value_from_firestore()
    investing_change = get_price_change_from_investing()
    exchange_rate = get_exchange_rate()
    
    if base_value is None or investing_change is None or exchange_rate is None or base_platts_price is None:
        missing = []
        if base_value is None:
            missing.append("base_value")
        if base_platts_price is None:
            missing.append("base_platts_price")
        if investing_change is None:
            missing.append("investing_change")
        if exchange_rate is None:
            missing.append("exchange_rate")
        
        return jsonify({"error": f"Missing data: {', '.join(missing)}. Check server logs."}), 500
    
    # Calculations - Using investing.com change as primary source
    valore_aggiornato = base_value + investing_change
    quotazione = exchange_rate * 0.845
    final_price = (valore_aggiornato / 1000) * quotazione + 0.6324
    
    # Calculate variation in €cents/liter from base Platts price
    price_variation_euro_cents = (final_price - base_platts_price) * 100
    
    print(f"Calculations completed for {user_email}:")
    print(f"  Base value (mq): {base_value}")
    print(f"  Base Platts price (€/liter): {base_platts_price:.4f}")
    print(f"  Investing.com change: {investing_change}")
    print(f"  Valore aggiornato: {valore_aggiornato}")
    print(f"  Price variation (€cents/liter): {price_variation_euro_cents:+.2f}")
    print(f"  USD/EUR rate: {exchange_rate}")
    print(f"  Quotazione: {quotazione}")
    print(f"  Final price: {final_price}")

    response_data = {
        "baseValue": f"{base_value:.2f}",
        "basePlattsPrice": f"{base_platts_price:.4f}",
        "priceChange": f"{investing_change:+.2f}",
        "valoreAggiornato": f"{valore_aggiornato:.2f}",
        "priceVariationCents": f"{price_variation_euro_cents:+.2f}",
        "exchangeRate": f"{exchange_rate:.4f}",
        "quotazione": f"{quotazione:.2f}",
        "finalPrice": f"{final_price:.4f}",
        "investingChange": f"{investing_change:+.2f}",
        "investingValoreAggiornato": f"{valore_aggiornato:.2f}",
        "investingFinalPrice": f"{final_price:.4f}",
        "lastUpdated": "Fresh data"
    }

    return jsonify(response_data)
        


if __name__ == '__main__':
    # Start Flask server
    print("\n--- Flask Server Starting ---")
    print("Server will be available on port 5001")
    print("Each data refresh will fetch fresh data from all sources.")
    app.run(host='0.0.0.0', debug=False, port=5001) 
