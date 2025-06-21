#!/usr/bin/env python3
#  MATKA DATA ADDER v1.0 - Powered by Anuj & AI God (Enhanced by Sachin & AI)

import os
import sys
import re # For input validation
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

# --- Configuration & Constants ---
APP_NAME = "MATKA DATA ADDER"
APP_VERSION = "v1.0"
POWERED_BY = "Anuj & AI God (Enhanced by Sachin & AI)"
BOX_WIDTH = 60 # Adjusted for potentially longer market names and data lines
DATA_DIR = "data"

# Color Palette (consistent with the main tool)
C_PRIMARY_BRIGHT = Fore.CYAN + Style.BRIGHT
C_SECONDARY_BRIGHT = Fore.MAGENTA + Style.BRIGHT
C_SUCCESS_BRIGHT = Fore.GREEN + Style.BRIGHT
C_ERROR_BRIGHT = Fore.RED + Style.BRIGHT
C_WARNING_BRIGHT = Fore.YELLOW + Style.BRIGHT
C_INFO_BRIGHT = Fore.BLUE + Style.BRIGHT
C_ACCENT_BRIGHT = Fore.WHITE + Style.BRIGHT

C_PRIMARY = Fore.CYAN
C_SECONDARY = Fore.MAGENTA
C_SUCCESS = Fore.GREEN
C_ERROR = Fore.RED
C_WARNING = Fore.YELLOW
C_INFO = Fore.BLUE

C_RESET = Style.RESET_ALL

C_BANNER_BORDER = C_SECONDARY_BRIGHT
C_BANNER_TITLE = C_SUCCESS_BRIGHT
C_BANNER_SUBTITLE = C_WARNING_BRIGHT
C_BANNER_TEXT = C_PRIMARY

# --- Utility Functions for Styling (copied from main tool) ---
def print_box_top(width=BOX_WIDTH, color=C_SECONDARY_BRIGHT):
    print(color + f"╔{'═' * (width - 2)}╗" + C_RESET)

def print_box_bottom(width=BOX_WIDTH, color=C_SECONDARY_BRIGHT):
    print(color + f"╚{'═' * (width - 2)}╝" + C_RESET)

def print_box_separator(width=BOX_WIDTH, color=C_SECONDARY_BRIGHT):
    print(color + f"╠{'═' * (width - 2)}╣" + C_RESET)

def strip_ansi_codes(text):
    return re.sub(r'\x1b\[[0-9;]*[mK]', '', text)

def print_box_line(text, width=BOX_WIDTH, border_color=C_SECONDARY_BRIGHT, text_color="", align="left", padding=2):
    stripped_text = strip_ansi_codes(text)
    content_width = width - 2 - (padding * 2)
    
    # Calculate padding based on stripped text length
    if align == "center":
        text_to_display = text.center(content_width + (len(text) - len(stripped_text)))
    elif align == "right":
        text_to_display = text.rjust(content_width + (len(text) - len(stripped_text)))
    else: # left
        text_to_display = text.ljust(content_width + (len(text) - len(stripped_text)))
    
    # Truncate if the display text (with ANSI) is too long for the visual content_width
    # This is a simplified truncation, might cut ANSI codes improperly in rare complex cases
    visual_len = len(stripped_text)
    if visual_len > content_width:
        diff = visual_len - content_width
        # Attempt to truncate original text proportionally
        # This is very hard to do perfectly with embedded ANSI codes
        # For now, a simpler approach: show truncated stripped text if overflow
        text_to_display = stripped_text[:content_width-3] + "..."
        if align == "center": text_to_display = text_to_display.center(content_width)
        elif align == "right": text_to_display = text_to_display.rjust(content_width)
        else: text_to_display = text_to_display.ljust(content_width)

    print(f"{border_color}║{' ' * padding}{text_color}{text_to_display}{' ' * padding}{border_color}║{C_RESET}")


def show_banner():
    os.system("clear" if os.name == 'posix' else 'cls')
    banner_width = BOX_WIDTH
    print_box_top(banner_width, C_BANNER_BORDER)
    print_box_line(f"{C_BANNER_TITLE}{APP_NAME}", banner_width, C_BANNER_BORDER, "", "center")
    print_box_line(f"{C_BANNER_SUBTITLE}{APP_VERSION}", banner_width, C_BANNER_BORDER, "", "center")
    print_box_separator(banner_width, C_BANNER_BORDER)
    print_box_line(f"{C_BANNER_TEXT}Easily Add Matka Results", banner_width, C_BANNER_BORDER, "", "center")
    print_box_bottom(banner_width, C_BANNER_BORDER)
    print("\n")

def get_market_files():
    """Scans the DATA_DIR for .txt files (markets)."""
    if not os.path.isdir(DATA_DIR):
        print(C_ERROR_BRIGHT + f"[!] Data directory '{DATA_DIR}/' not found.")
        print(C_WARNING_BRIGHT + "    Please create it and add your market .txt files.")
        return []
    try:
        files = [f for f in os.listdir(DATA_DIR) if f.endswith(".txt") and os.path.isfile(os.path.join(DATA_DIR, f))]
        return sorted(files)
    except Exception as e:
        print(C_ERROR_BRIGHT + f"[!] Error reading data directory: {e}")
        return []

def display_market_selection(market_files):
    """Displays market files in a box for selection."""
    print_box_top(BOX_WIDTH, C_PRIMARY_BRIGHT)
    print_box_line(f"{C_ACCENT_BRIGHT}Select Market File to Add Data", BOX_WIDTH, C_PRIMARY_BRIGHT, "", "center")
    print_box_separator(BOX_WIDTH, C_PRIMARY_BRIGHT)
    if not market_files:
        print_box_line(f"{C_WARNING}No market files (.txt) found in '{DATA_DIR}/'", BOX_WIDTH, C_PRIMARY_BRIGHT, "", "center")
    else:
        for i, market_file in enumerate(market_files, 1):
            print_box_line(f"{C_WARNING}{i:>2}. {C_SECONDARY}{market_file}", BOX_WIDTH, C_PRIMARY_BRIGHT)
    print_box_separator(BOX_WIDTH, C_PRIMARY_BRIGHT)
    print_box_line(f"{C_WARNING_BRIGHT}{'0':>2}. {C_ERROR_BRIGHT}Exit Application", BOX_WIDTH, C_PRIMARY_BRIGHT)
    print_box_bottom(BOX_WIDTH, C_PRIMARY_BRIGHT)

def get_validated_input(prompt, validation_regex, error_message, example=""):
    """Generic function to get and validate string input."""
    while True:
        value = input(C_PRIMARY_BRIGHT + prompt + C_RESET + (f" (e.g., {C_INFO}{example}{C_RESET})" if example else "") + ": ").strip()
        if re.fullmatch(validation_regex, value):
            return value
        else:
            print(C_ERROR + error_message + C_RESET)

def get_date_input():
    """Gets and validates date input from the user."""
    while True:
        date_str = input(C_PRIMARY_BRIGHT + "Enter Date (DD-MM-YYYY) or type 'c' to cancel: " + C_RESET).strip()
        if date_str.lower() == 'c':
            return None
        try:
            datetime.strptime(date_str, "%d-%m-%Y")
            return date_str
        except ValueError:
            print(C_ERROR + "Invalid date format. Please use DD-MM-YYYY." + C_RESET)

def append_data_to_file(market_filename, data_line):
    """Appends the formatted data line to the specified market file."""
    filepath = os.path.join(DATA_DIR, market_filename)
    try:
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(data_line + "\n")
        print(C_SUCCESS_BRIGHT + f"\n[+] Data successfully added to {C_SECONDARY}{market_filename}{C_RESET}")
        print(C_INFO + f"    Added: {C_ACCENT_BRIGHT}{data_line}{C_RESET}")
        return True
    except IOError as e:
        print(C_ERROR_BRIGHT + f"[!] Error writing to file {market_filename}: {e}")
        return False
    except Exception as e:
        print(C_ERROR_BRIGHT + f"[!] An unexpected error occurred: {e}")
        return False

def main_data_entry_tool():
    show_banner()
    market_files = get_market_files()

    if not market_files:
        input(C_INFO_BRIGHT + "Press Enter to exit." + C_RESET)
        return

    while True: # Loop for selecting markets
        display_market_selection(market_files)
        
        choice = input(C_PRIMARY_BRIGHT + f"\n👉 Enter market number to add data (or 0 to exit): {C_RESET}").strip()

        if not choice.isdigit():
            print(C_ERROR + "Invalid input. Please enter a number." + C_RESET)
            input(C_INFO_BRIGHT + "Press Enter to continue..." + C_RESET); show_banner()
            continue
        
        choice_num = int(choice)

        if choice_num == 0:
            print(C_INFO_BRIGHT + f"\n👋 Exiting {APP_NAME}. Thank you!" + C_RESET)
            break
        
        if not (1 <= choice_num <= len(market_files)):
            print(C_ERROR + "Invalid market number. Please choose from the list." + C_RESET)
            input(C_INFO_BRIGHT + "Press Enter to continue..." + C_RESET); show_banner()
            continue

        selected_market_file = market_files[choice_num - 1]
        
        while True: # Loop for adding multiple entries to the selected market
            print(C_PRIMARY_BRIGHT + f"\n--- Adding data for: {C_SECONDARY_BRIGHT}{selected_market_file}{C_PRIMARY_BRIGHT} ---" + C_RESET)
            
            date_str = get_date_input()
            if date_str is None: # User cancelled
                break 

            p1 = get_validated_input("Enter Panel 1 (P1)", r"\d{3}", "Panel 1 must be 3 digits.", "123")
            jodi = get_validated_input("Enter Jodi", r"\d{2}", "Jodi must be 2 digits.", "45")
            p2 = get_validated_input("Enter Panel 2 (P2)", r"\d{3}", "Panel 2 must be 3 digits.", "678")

            formatted_data_line = f"{date_str} / {p1} - {jodi} - {p2}"
            
            print(C_INFO + f"\nPreview of data to be added: {C_ACCENT_BRIGHT}{formatted_data_line}{C_RESET}")
            confirm = input(C_WARNING_BRIGHT + "Confirm adding this data? (yes/no/cancel): " + C_RESET).strip().lower()

            if confirm in ['yes', 'y']:
                append_data_to_file(selected_market_file, formatted_data_line)
            elif confirm in ['cancel', 'c']:
                print(C_INFO + "Operation cancelled by user." + C_RESET)
                break # Breaks from adding entries to this market, goes to market selection
            else:
                print(C_INFO + "Data not added." + C_RESET)

            add_another_for_same_market = input(C_PRIMARY_BRIGHT + f"\n❓ Add another entry for {C_SECONDARY}{selected_market_file}{C_PRIMARY_BRIGHT}? (yes/no): " + C_RESET).strip().lower()
            if add_another_for_same_market not in ['yes', 'y']:
                break # Breaks from adding entries to this market, goes to market selection
        
        # After finishing with one market, decide whether to pick another market or exit entirely
        if choice_num == 0: # This check is if '0' was the initial choice.
             break
        
        another_market_prompt = (
            C_PRIMARY_BRIGHT + "\n❓ Select another market file or exit? (" +
            C_SUCCESS_BRIGHT + "select" + C_PRIMARY_BRIGHT + "/" +
            C_ERROR_BRIGHT + "exit" + C_PRIMARY_BRIGHT + "): " + C_RESET
        )
        next_action = input(another_market_prompt).strip().lower()
        if next_action not in ['select', 's']:
            print(C_INFO_BRIGHT + f"\n👋 Exiting {APP_NAME}. Thank you!" + C_RESET)
            break
        show_banner() # Refresh banner and market list

if __name__ == "__main__":
    try:
        main_data_entry_tool()
    except KeyboardInterrupt:
        print(C_WARNING_BRIGHT + "\n\n[!] User interrupted. Exiting..." + C_RESET)
    except Exception as e:
        print(C_ERROR_BRIGHT + f"\n[!!!] An unexpected critical error occurred: {e}")
        # import traceback # For debugging
        # traceback.print_exc() # For debugging
        print(C_ERROR_BRIGHT + "      Please report this issue." + C_RESET)
    finally:
        print(C_PRIMARY_BRIGHT + f"\n✨ Thank you for using {APP_NAME}! ✨" + C_RESET)
