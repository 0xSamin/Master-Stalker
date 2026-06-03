import os
import requests
from bs4 import BeautifulSoup

# File to store notified positions and prevent duplicate alerts
HISTORY_FILE = "stalked_links.txt"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_to_history(link):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(link + "\n")

def send_telegram(message):
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        print(f"[Simulation Mode] Telegram Message:\n{message}\n")
        return
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error sending telegram message: {e}")

def stalk_nus(history):
    print("🔍 Master Stalker is infiltrating NUS Careers...")
    url = "https://careers.nus.edu.sg/NUS/go/Research-&-Other-Teaching-Positions-All/733244/?sortBy=date&pageNumber=0"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"❌ Cannot access NUS (Status: {response.status_code})")
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        job_rows = soup.select("table.table.searchResultsTileView tr.data-row")
        
        for row in job_rows:
            title_element = row.select_one("a.jobTitle-link")
            if title_element:
                title = title_element.text.strip()
                relative_link = title_element['href']
                full_link = f"https://careers.nus.edu.sg{relative_link}"
                
                full_text_lower = title.lower()
                is_target = any(k in full_text_lower for k in ["research assistant", "ra ", "project associate", "master"])
                
                if is_target and full_link not in history:
                    msg = (
                        f"🦁 **Master Stalker Alert: NUS**\n\n"
                        f"🎯 **New Position Detected:**\n"
                        f"`{title}`\n\n"
                        f"🔗 **Apply Here:**\n{full_link}"
                    )
                    send_telegram(msg)
                    save_to_history(full_link)
                    history.add(full_link)
    except Exception as e:
        print(f"❌ Error stalking NUS: {e}")

def stalk_sunway(history):
    print("🔍 Master Stalker is scanning Sunway University...")
    url = "https://sunwayuniversity.edu.my/about/job-opportunities"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"❌ Cannot access Sunway (Status: {response.status_code})")
            return
            
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a')
        
        for link in links:
            href = link.get('href', '')
            text = link.text.strip()
            
            if href and not href.startswith('http'):
                href = f"https://sunwayuniversity.edu.my{href}"
                
            if "research assistant" in text.lower() and href not in history:
                msg = (
                    f"🌞 **Master Stalker Alert: Sunway**\n\n"
                    f"🎯 **New GRA Position Detected:**\n"
                    f"`{text}`\n\n"
                    f"🔗 **Details & Contact:**\n{href}"
                )
                send_telegram(msg)
                save_to_history(href)
                history.add(href)
    except Exception as e:
        print(f"❌ Error stalking Sunway: {e}")

def stalk_usm(history):
    print("🔍 Master Stalker is monitoring USM Product Design...")
    url = "https://productdesign.eng.usm.my/index.php/ms/enterprise/job-vacancies"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"❌ Cannot access USM (Status: {response.status_code})")
            return
            
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a')
        for link in links:
            href = link.get('href', '')
            text = link.text.strip()
            
            if href and not href.startswith('http'):
                href = f"https://productdesign.eng.usm.my{href}"
                
            full_text_lower = text.lower()
            is_target = any(k in full_text_lower for k in ["research assistant", "ra", "vacancy", "jawatan kosong", "master"])
            
            if is_target and href not in history:
                msg = (
                    f"🧪 **Master Stalker Alert: USM**\n\n"
                    f"🎯 **New Vacancy/RA Position Detected:**\n"
                    f"`{text}`\n\n"
                    f"🔗 **Check Details:**\n{href}"
                )
                send_telegram(msg)
                save_to_history(href)
                history.add(href)
    except Exception as e:
        print(f"❌ Error stalking USM: {e}")

def stalk_utm(history):
    print("🔍 Master Stalker is parsing UTM Postgraduate Vacancy Table...")
    url = "https://research.utm.my/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"❌ Cannot access UTM (Status: {response.status_code})")
            return
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Target only tables to bypass podcasts, ads, and widgets
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                # Ensure it's a valid data row from the vacancy table
                if len(cells) >= 5:
                    appointment_type = cells[1].text.strip()
                    degree_type = cells[2].text.strip().lower()
                    project_title = cells[4].text.strip()
                    
                    # Look for application link inside the last cells
                    link_element = row.find('a')
                    apply_link = link_element.get('href', '') if link_element else url
                    
                    # Filter for Master/MSc positions or general GRAs
                    is_master_target = "master" in degree_type or "gra" in appointment_type.lower()
                    
                    if is_master_target and project_title and apply_link not in history:
                        msg = (
                            f"🔮 **Master Stalker Alert: UTM**\n\n"
                            f"🎯 **New Postgraduate Vacancy Found:**\n"
                            f"📂 **Project:** `{project_title}`\n"
                            f"📋 **Type:** {appointment_type} ({cells[2].text.strip()})\n\n"
                            f"🔗 **Apply / View:**\n{apply_link}"
                        )
                        send_telegram(msg)
                        save_to_history(apply_link)
                        history.add(apply_link)
                        
    except Exception as e:
        print(f"❌ Error stalking UTM: {e}")

if __name__ == "__main__":
    history_set = load_history()
    stalk_nus(history_set)
    stalk_sunway(history_set)
    stalk_usm(history_set)
    stalk_utm(history_set)
