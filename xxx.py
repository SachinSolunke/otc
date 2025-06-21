#!/usr/bin/env python3
# OTC MATH FORMULAS ANALYZER v1.2.1 - Syntax Fix
# Powered by Anuj & AI God (Enhanced by Sachin & AI)

import os
import sys
import shutil
import re
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import json

from colorama import Fore, Style, init

init(autoreset=True)

# --- Configuration & Constants ---
APP_NAME = "OTC MATH ANALYZER"
APP_VERSION = "v1.2.1" # Version up for Syntax Fix
POWERED_BY = "Anuj & AI God (Enhanced by Sachin & AI)"
BOX_WIDTH = 90 
DATA_DIR = "data"
LOG_DIR = "logs"

BACKTEST_WINDOW_DAYS = 30 
MIN_HIT_RATE_SUGGESTION = 0.39 
MIN_TRIES_SUGGESTION = 10    
NUM_ANK_SUGGESTIONS_COMBINED = 3 
NUM_INDIVIDUAL_FORMULA_SUGGESTIONS_TO_DISPLAY = 7 

# Color Palette
C_PRIMARY_BRIGHT = Fore.CYAN + Style.BRIGHT; C_SECONDARY_BRIGHT = Fore.MAGENTA + Style.BRIGHT
C_SUCCESS_BRIGHT = Fore.GREEN + Style.BRIGHT; C_ERROR_BRIGHT = Fore.RED + Style.BRIGHT
C_WARNING_BRIGHT = Fore.YELLOW + Style.BRIGHT; C_INFO_BRIGHT = Fore.BLUE + Style.BRIGHT
C_ACCENT_BRIGHT = Fore.WHITE + Style.BRIGHT; C_PRIMARY = Fore.CYAN; C_SECONDARY = Fore.MAGENTA
C_SUCCESS = Fore.GREEN; C_ERROR = Fore.RED; C_WARNING = Fore.YELLOW; C_INFO = Fore.BLUE
C_RESET = Style.RESET_ALL; C_BANNER_BORDER = C_SECONDARY_BRIGHT; C_BANNER_TITLE = C_SUCCESS_BRIGHT
C_BANNER_SUBTITLE = C_WARNING_BRIGHT; C_BANNER_TEXT = C_PRIMARY

MARKETS = [
    "KALYAN-NIGHT", "MAIN-BAZAR", "RAJDHANI-NIGHT", "SUPREME-NIGHT", "KALYAN",
    "MILAN-DAY", "SRIDEVI-NIGHT", "TIME-BAZAR", "MADHUR-DAY", "MILAN-NIGHT",
    "SRIDEVI", "MADHUR-NIGHT", "RAJDHANI-DAY", "SUPREME-DAY"
]

# --- Styling Utilities ---
def print_box_top(w=BOX_WIDTH, c=C_SECONDARY_BRIGHT): print(c + f"╔{'═'*(w-2)}╗" + C_RESET)
def print_box_bottom(w=BOX_WIDTH, c=C_SECONDARY_BRIGHT): print(c + f"╚{'═'*(w-2)}╝" + C_RESET)
def print_box_sep(w=BOX_WIDTH, c=C_SECONDARY_BRIGHT): print(c + f"╠{'═'*(w-2)}╣" + C_RESET)
def strip_ansi(t): return re.sub(r'\x1b\[[0-9;]*[mK]', '', t)
def print_box_line(t, w=BOX_WIDTH, bc=C_SECONDARY_BRIGHT, tc="", align="left", p=2):
    st, cw = strip_ansi(t), w-2-(p*2); dsp_t = t; cl_diff = len(t)-len(st)
    if len(st) > cw:
        cut_at=0; cur_st_len=0; max_st_len=cw-3 if cw>3 else cw
        for char_idx, char_val in enumerate(t):
            is_ansi_char=False
            if char_idx+1 < len(t) and t[char_idx]=='\x1b' and t[char_idx+1]=='[': is_ansi_char=True
            if not is_ansi_char and char_val not in ['\x1b']: cur_st_len+=1
            if cur_st_len >= max_st_len: cut_at=char_idx+1; break
        dsp_t = t[:cut_at] + ("..." if cw > 3 else "") if cut_at > 0 else t[:max_st_len] + ("..." if cw > 3 else "")
        cl_diff = len(dsp_t) - len(strip_ansi(dsp_t))
    eff_w = cw + cl_diff
    at = dsp_t.center(eff_w) if align=="center" else (dsp_t.rjust(eff_w) if align=="right" else dsp_t.ljust(eff_w))
    print(f"{bc}║{' '*p}{tc}{at}{' '*p}{bc}║{C_RESET}")

# --- Core Logic Functions ---
def show_banner():
    os.system("clear" if os.name == 'posix' else 'cls'); print_box_top();
    print_box_line(f"{C_BANNER_TITLE}{APP_NAME}", align="center"); print_box_line(f"{C_BANNER_SUBTITLE}{APP_VERSION}", align="center")
    print_box_sep(); print_box_line(f"{C_BANNER_TEXT}Math-Based OTC Ank Suggester (Sliding Window)", align="center"); print_box_bottom(); print("\n")

def parse_data_line(line_str):
    try:
        date_part_str, result_part_str = map(str.strip, line_str.split('/', 1))
        p1_str, jodi_str, p2_str = map(str.strip, result_part_str.split('-', 2))
        if not (re.fullmatch(r"\d{3}",p1_str) and re.fullmatch(r"\d{2}",jodi_str) and re.fullmatch(r"\d{3}",p2_str)): return None
        dt = datetime.strptime(date_part_str, "%d-%m-%Y")
        all_digits = [int(d) for d in p1_str] + [int(d) for d in jodi_str] + [int(d) for d in p2_str]
        return {
            "date_obj": dt, "p1": p1_str, "jodi": jodi_str, "p2": p2_str,
            "open_ank": p1_str[-1], "close_ank": jodi_str[-1], 
            "jodi_d1": jodi_str[0], "jodi_d2": jodi_str[1],
            "p1_digits_str": [d for d in p1_str], "p2_digits_str": [d for d in p2_str],
            "p1_digits_int": [int(d) for d in p1_str], "p2_digits_int": [int(d) for d in p2_str],
            "all_8_digits_int": all_digits }
    except: return None

def read_data_file(market_name):
    filepath = os.path.join(DATA_DIR, f"{market_name}.txt")
    try:
        with open(filepath, 'r', encoding='utf-8') as f: lines = [line.strip() for line in f if line.strip()]
        parsed = [parse_data_line(line) for line in lines]
        return sorted([d for d in parsed if d is not None], key=lambda x: x['date_obj'])
    except FileNotFoundError: print(C_ERROR_BRIGHT + f"[!] File missing: {filepath}"); return []
    except Exception as e: print(C_ERROR_BRIGHT + f"[!] Read error {filepath}: {e}"); return []

# --- MATHEMATICAL FORMULA DEFINITIONS ---
def f_prev_oc_anks(prev_data, params=None):
    if not prev_data: return set()
    return {prev_data['open_ank'], prev_data['close_ank']}
def f_prev_jodi_digits(prev_data, params=None):
    if not prev_data: return set()
    return {prev_data['jodi_d1'], prev_data['jodi_d2']}
def f_sum_jodi_digits_plus_x(prev_data, params):
    if not prev_data or "X" not in params: return set()
    try: jd1,jd2=int(prev_data['jodi_d1']),int(prev_data['jodi_d2']);x=int(params["X"]); return {str((jd1+jd2+x)%10)}
    except ValueError: return set()
def f_diff_jodi_digits_plus_x(prev_data, params):
    if not prev_data or "X" not in params: return set()
    try: jd1,jd2=int(prev_data['jodi_d1']),int(prev_data['jodi_d2']);x=int(params["X"]); return {str((abs(jd1-jd2)+x)%10)}
    except ValueError: return set()
def f_sum_oc_anks_plus_x(prev_data, params):
    if not prev_data or "X" not in params: return set()
    try: oa,ca=int(prev_data['open_ank']),int(prev_data['close_ank']);x=int(params["X"]); return {str((oa+ca+x)%10)}
    except ValueError: return set()
def f_ank_plus_x_and_cut(prev_data, params):
    if not prev_data or "ank_type" not in params or "X" not in params: return set()
    try:
        ank_val=int(prev_data[params["ank_type"]]);x=int(params["X"]); base_ank=(ank_val+x)%10; cut_ank=(base_ank+5)%10
        return {str(base_ank),str(cut_ank)}
    except ValueError: return set()
def f_panel_digit_op_plus_x(prev_data, params):
    if not prev_data or "panel" not in params or "idx1" not in params or "idx2" not in params or "op" not in params or "X" not in params: return set()
    try:
        panel_digits=prev_data[params["panel"]+"_digits_int"]; d1,d2=panel_digits[params["idx1"]],panel_digits[params["idx2"]]; x=int(params["X"]); res=0
        if params["op"]=="add":res=d1+d2
        elif params["op"]=="sub":res=abs(d1-d2)
        elif params["op"]=="mul":res=d1*d2
        return {str((res+x)%10)}
    except(IndexError, ValueError, KeyError): return set()
def f_ank_jodi_digit_mult_plus_x(prev_data, params):
    if not prev_data or "X" not in params: return set()
    try: jd1,jd2=int(prev_data['jodi_d1']),int(prev_data['jodi_d2']);x=int(params["X"]); prod=jd1*jd2; return {str((prod%10+x)%10)}
    except ValueError: return set()
def f_ank_panel_extremes_op_plus_x(prev_data, params):
    if not prev_data or "panel" not in params or "op" not in params or "X" not in params: return set()
    try:
        panel_digits=prev_data[params["panel"]+"_digits_int"];d1,d_last=panel_digits[0],panel_digits[-1];x=int(params["X"]);res=0
        if params["op"]=="add":res=d1+d_last
        elif params["op"]=="sub":res=abs(d1-d_last)
        return {str((res%10+x)%10)}
    except(IndexError,ValueError,KeyError): return set()
def f_ank_running_digit_and_cut(prev_data, params):
    if not prev_data or "digit_source" not in params: return set()
    try: source_ank_val=int(prev_data[params["digit_source"]]);cut_ank=(source_ank_val+5)%10; return {str(source_ank_val),str(cut_ank)}
    except(ValueError,KeyError): return set()
def f_ank_total_sum_all_plus_x(prev_data, params):
    if not prev_data or "X" not in params: return set()
    try: total_sum=sum(prev_data["all_8_digits_int"]);x=int(params["X"]); return {str((total_sum%10+x)%10)}
    except(ValueError,KeyError): return set()

ALL_FORMULA_SPECS = {} 
ALL_FORMULA_SPECS["PrevOCAnks"] = {"func": f_prev_oc_anks, "params": {}, "display": "Prev O/C Anks", "type": "ank"}
ALL_FORMULA_SPECS["PrevJodiDigits"] = {"func": f_prev_jodi_digits, "params": {}, "display": "Prev Jodi Digits", "type": "ank"}
for x_val in range(10):
    ALL_FORMULA_SPECS[f"SumJodiDigits_X{x_val}"] = {"func": f_sum_jodi_digits_plus_x, "params": {"X": x_val}, "display": f"SumJodi+({x_val})", "type": "ank"}
    ALL_FORMULA_SPECS[f"DiffJodiDigits_X{x_val}"] = {"func": f_diff_jodi_digits_plus_x, "params": {"X": x_val}, "display": f"DiffJodi+({x_val})", "type": "ank"}
    ALL_FORMULA_SPECS[f"SumOCAnks_X{x_val}"] = {"func": f_sum_oc_anks_plus_x, "params": {"X": x_val}, "display": f"SumO+C+({x_val})", "type": "ank"}
    ALL_FORMULA_SPECS[f"JodiDigitMult_X{x_val}"] = {"func": f_ank_jodi_digit_mult_plus_x, "params": {"X": x_val}, "display": f"JodiD1*D2+({x_val})", "type": "ank"}
    ALL_FORMULA_SPECS[f"TotalSumAll_X{x_val}"] = {"func": f_ank_total_sum_all_plus_x, "params": {"X": x_val}, "display": f"TotalAllDigits+({x_val})", "type": "ank"}
for ank_t_key in ["open_ank", "close_ank", "jodi_d1", "jodi_d2"]:
    display_ank_t = ank_t_key.replace("_ank","").replace("_d","D").upper()
    ALL_FORMULA_SPECS[f"RunningDigitCut_{display_ank_t}"] = {"func": f_ank_running_digit_and_cut, "params": {"digit_source": ank_t_key},"display": f"{display_ank_t} & Cut", "type": "ank"}
    if ank_t_key in ["open_ank", "close_ank"]:
        for x_val in range(3):
            ALL_FORMULA_SPECS[f"AnkPlusXCut_{display_ank_t}_X{x_val}"] = {"func": f_ank_plus_x_and_cut, "params": {"ank_type": ank_t_key, "X": x_val},"display": f"{display_ank_t}+{x_val} & Cut", "type": "ank"}
panel_indices = [(0,1), (0,2), (1,2)]
panel_ops_sym = {"add":"+", "sub":"-", "mul":"*"}
for p_type_key in ["p1", "p2"]:
    for op_key_str, op_sym_char in panel_ops_sym.items():
        ALL_FORMULA_SPECS[f"PanelExtremesOp_{p_type_key.upper()}_{op_key_str}_X0"] = {"func": f_ank_panel_extremes_op_plus_x, "params": {"panel": p_type_key, "op": op_key_str, "X": 0},"display": f"{p_type_key.upper()}[0]{op_sym_char}[-1]+0", "type": "ank"} 
        if op_key_str != "mul":
            for id1, id2 in panel_indices:
                 for x_val in [0, 1]:
                    ALL_FORMULA_SPECS[f"PanelDigitOp_{p_type_key.upper()}{id1}{op_sym_char}{id2}_X{x_val}"] = {"func": f_panel_digit_op_plus_x,"params": {"panel":p_type_key, "idx1":id1, "idx2":id2, "op":op_key_str, "X":x_val},"display": f"{p_type_key.upper()}[{id1}]{op_sym_char}[{id2}]+{x_val}", "type": "ank"}
# --- END FORMULA REGISTRATION ---

def backtest_all_formulas(full_historical_data):
    if len(full_historical_data) > BACKTEST_WINDOW_DAYS :
        data_for_backtest = full_historical_data[-(BACKTEST_WINDOW_DAYS + 1):]
        print(C_INFO_BRIGHT + f"Backtesting {len(ALL_FORMULA_SPECS)} OTC Ank formulas on last {len(data_for_backtest)-1} days (Sliding Window)...")
    else:
        data_for_backtest = full_historical_data
        print(C_INFO_BRIGHT + f"Backtesting {len(ALL_FORMULA_SPECS)} OTC Ank formulas on all {len(data_for_backtest)-1 if len(data_for_backtest)>1 else 0} available days...")
    stats = {f_id: {"hits":0,"tries":0,"type":spec["type"],"display_name":spec["display"],"params_str":str(spec["params"])} 
             for f_id, spec in ALL_FORMULA_SPECS.items()}
    if len(data_for_backtest) < 2: print(C_WARNING+"Not enough data in window for backtest."); return stats
    for i in range(1, len(data_for_backtest)):
        prev_d, curr_d = data_for_backtest[i-1], data_for_backtest[i]
        actual_otc_relevant_anks = {curr_d['open_ank'], curr_d['close_ank']}
        for f_id, spec in ALL_FORMULA_SPECS.items():
            if prev_d is None : continue
            stats[f_id]["tries"] += 1 
            generated_values = spec["func"](prev_d, spec["params"]) 
            if not generated_values: continue
            if not actual_otc_relevant_anks.isdisjoint(generated_values): stats[f_id]["hits"] += 1
    return stats

def get_otc_suggestions_for_tomorrow_modified(latest_day_data, all_formula_stats, current_min_tries_for_filter):
    suggestions = [] 
    if not latest_day_data: return suggestions
    eligible_formulas = []
    for f_id, perf_data in all_formula_stats.items():
        if perf_data['tries'] >= current_min_tries_for_filter:
            hit_rate = (perf_data['hits'] / perf_data['tries']) if perf_data['tries'] > 0 else 0
            if hit_rate >= MIN_HIT_RATE_SUGGESTION:
                eligible_formulas.append((f_id, perf_data, hit_rate))
    eligible_formulas.sort(key=lambda x: (x[2], x[1]['tries']), reverse=True)
    for f_id, perf_data, hit_rate in eligible_formulas:
        spec = ALL_FORMULA_SPECS.get(f_id)
        if not spec: continue
        generated_values = spec["func"](latest_day_data, spec["params"])
        if generated_values:
            suggestions.append({
                "display_name": perf_data["display_name"], "params_str": perf_data["params_str"],
                "generated_anks": sorted(list(generated_values)), "hit_rate": hit_rate * 100,
                "hits_tries_str": f"{perf_data['hits']}/{perf_data['tries']}" })
    return suggestions

def log_top_suggestion(market_name, suggestion):
    os.makedirs(LOG_DIR, exist_ok=True)
    log_file = os.path.join(LOG_DIR, "otc_math_daily_suggestions.txt")
    today = datetime.now().strftime("%d-%m-%Y"); tomorrow = (datetime.now()+timedelta(days=1)).strftime("%d-%m-%Y")
    entry = (f"{today} (For {tomorrow}) | Mkt: {market_name} | "
             f"Formula: {suggestion['display_name']} {suggestion['params_str']} | "
             f"Rate: {suggestion['hit_rate']:.0f}% ({suggestion['hits_tries_str']}) | "
             f"Sugg. Anks: {' '.join(suggestion['generated_anks'])}\n")
    try: # ***** CORRECTED SYNTAX HERE *****
        with open(log_file, 'a') as f:
            f.write(entry)
    except IOError:
        print(C_ERROR + f"Log write error: {log_file}")

def display_performance_summary(all_stats):
    print_box_top(c=C_INFO_BRIGHT); print_box_line(f"{C_ACCENT_BRIGHT}Math Formula Performance (OTC Anks - Last {BACKTEST_WINDOW_DAYS} Days)", bc=C_INFO_BRIGHT, align="center")
    print_box_sep(c=C_INFO_BRIGHT)
    header = f"{'Formula Display Name'.ljust(35)} | {'Parameters'.ljust(20)} | {'Rate'.rjust(7)} | {'Hits/Tries'.rjust(10)}"
    print_box_line(C_WARNING_BRIGHT + header, bc=C_INFO_BRIGHT, p=1); print_box_sep(c=C_INFO_BRIGHT)
    sorted_stats = sorted(all_stats.items(), key=lambda x: (x[1]['hits']/x[1]['tries'] if x[1]['tries']>0 else 0, x[1]['tries']), reverse=True)
    for f_id, data in sorted_stats[:20]: 
        rate = (data['hits']/data['tries']*100) if data['tries']>0 else 0
        name = data.get('display_name', f_id)[:33]; param = data.get('params_str', "{}")[:18]
        clr = C_SUCCESS if rate >= MIN_HIT_RATE_SUGGESTION*100 and data['tries'] >= MIN_TRIES_SUGGESTION else C_PRIMARY
        line = f"{name.ljust(35)} | {param.ljust(20)} | {f'{rate:.0f}%'.rjust(7)} | {f'''{data['hits']}/{data['tries']}'''.rjust(10)}"
        print_box_line(clr + line, bc=C_INFO_BRIGHT, p=1)
    if len(sorted_stats) > 20: print_box_line("... and more ...", bc=C_INFO_BRIGHT, align="center", p=1)
    print_box_bottom(c=C_INFO_BRIGHT)

def display_final_otc_suggestions(market_name, suggestions_from_formulas):
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%d-%m-%Y (%A)')
    print_box_top(c=C_SUCCESS_BRIGHT)
    print_box_line(f"{C_ACCENT_BRIGHT}OTC Ank Suggestions for {market_name} - {tomorrow}", bc=C_SUCCESS_BRIGHT, align="center")
    print_box_sep(c=C_SUCCESS_BRIGHT)
    if not suggestions_from_formulas:
        print_box_line(C_WARNING+"No formulas met suggestion criteria today.", bc=C_SUCCESS_BRIGHT, align="center")
    else:
        header = f"{'Rank'.ljust(4)}| {'Formula'.ljust(35)}| {'Params'.ljust(20)}| {'Anks'.ljust(10)}| {'Rate'.rjust(7)}"
        print_box_line(C_WARNING_BRIGHT+header, bc=C_SUCCESS_BRIGHT,p=1); print_box_sep(c=C_SUCCESS_BRIGHT)
        final_combined_anks = set(); contributing_details = []
        for i, sug in enumerate(suggestions_from_formulas[:NUM_INDIVIDUAL_FORMULA_SUGGESTIONS_TO_DISPLAY]):
            name=sug['display_name'][:33];param=sug['params_str'][:18];anks=' '.join(sug['generated_anks'])[:8];rate=f"{sug['hit_rate']:.0f}%"
            clr = C_SUCCESS_BRIGHT 
            line = f"{str(i+1).ljust(4)}| {name.ljust(35)}| {param.ljust(20)}| {anks.ljust(10)}| {rate.rjust(7)}"
            print_box_line(clr+line, bc=C_SUCCESS_BRIGHT, p=1)
            if i == 0: log_top_suggestion(market_name, sug)
            for ank_val in sug['generated_anks']:
                if len(final_combined_anks) < NUM_ANK_SUGGESTIONS_COMBINED:
                    final_combined_anks.add(ank_val)
                    is_new_reason_for_ank = True
                    for existing_reason in contributing_details:
                        if existing_reason.startswith(f"{ank_val} ("): is_new_reason_for_ank=False; break
                    if is_new_reason_for_ank and len(contributing_details) < NUM_ANK_SUGGESTIONS_COMBINED:
                        contributing_details.append(f"{ank_val} (from {sug['display_name']} @{sug['hit_rate']:.0f}%)")
        print_box_sep(c=C_SUCCESS_BRIGHT)
        if final_combined_anks:
            display_list = sorted(list(final_combined_anks))[:NUM_ANK_SUGGESTIONS_COMBINED]
            while len(display_list) < NUM_ANK_SUGGESTIONS_COMBINED and NUM_ANK_SUGGESTIONS_COMBINED > 0: display_list.append('?')
            print_box_line(f"{C_ACCENT_BRIGHT}Tomorrow's Top {NUM_ANK_SUGGESTIONS_COMBINED} Combined OTC Anks: {C_SUCCESS_BRIGHT}{'  '.join(display_list)}", bc=C_SUCCESS_BRIGHT, align="center", p=1)
            for detail in sorted(list(set(contributing_details)))[:NUM_ANK_SUGGESTIONS_COMBINED]:
                 print_box_line(f"{C_INFO_BRIGHT} {detail[:BOX_WIDTH-6]}", bc=C_SUCCESS_BRIGHT,p=1)
        else: print_box_line(C_WARNING+f"Could not determine {NUM_ANK_SUGGESTIONS_COMBINED} OTC anks.", bc=C_SUCCESS_BRIGHT, align="center", p=1)
    print_box_bottom(c=C_SUCCESS_BRIGHT)

def main():
    show_banner()
    print_box_top(w=BOX_WIDTH//2,c=C_PRIMARY_BRIGHT); print_box_line("Select Market",w=BOX_WIDTH//2,bc=C_PRIMARY_BRIGHT,align="center")
    for i,m in enumerate(MARKETS): print_box_line(f"{C_WARNING}{i+1}. {C_SECONDARY}{m}",w=BOX_WIDTH//2,bc=C_PRIMARY_BRIGHT)
    print_box_bottom(w=BOX_WIDTH//2,c=C_PRIMARY_BRIGHT)
    mk_idx = -1
    while not (0 <= mk_idx < len(MARKETS)):
        try: mk_idx = int(input(C_PRIMARY_BRIGHT+"Enter market number: "+C_RESET))-1
        except ValueError: print(C_ERROR+"Invalid input.")
        if not (0 <= mk_idx < len(MARKETS)): print(C_ERROR+"Invalid choice.")
    market_name = MARKETS[mk_idx]
    print(C_INFO_BRIGHT+f"\nAnalyzing Market: {C_ACCENT_BRIGHT}{market_name}{C_RESET} for OTC Anks using Math Formulas\n")
    
    full_historical_data = read_data_file(market_name)
    if not full_historical_data or len(full_historical_data) < 2 :
        print(C_ERROR_BRIGHT+f"Not enough data for {market_name} (found {len(full_historical_data)}). At least 2 days needed."); sys.exit(1)
    
    # Adjust effective_min_tries based on the actual data available within the window
    # The number of possible tries in the window is len(window_data) - 1
    # If full_historical_data is shorter than BACKTEST_WINDOW_DAYS + 1, window is smaller
    
    actual_data_len_for_window_tries = 0
    if len(full_historical_data) > BACKTEST_WINDOW_DAYS :
        actual_data_len_for_window_tries = BACKTEST_WINDOW_DAYS # Tries = Window_days
    else:
        actual_data_len_for_window_tries = max(0, len(full_historical_data) -1) # Tries = all_data - 1
        
    effective_min_tries = min(MIN_TRIES_SUGGESTION, actual_data_len_for_window_tries)
    if effective_min_tries < MIN_TRIES_SUGGESTION and actual_data_len_for_window_tries > 0 :
        print(C_WARNING_BRIGHT + f"Adjusted MIN_TRIES for suggestion to {effective_min_tries} (max possible tries in window: {actual_data_len_for_window_tries}).")
    elif actual_data_len_for_window_tries == 0 and len(full_historical_data) >=2 : # Should not happen if data >=2
        print(C_ERROR_BRIGHT + f"Logic error in calculating tries for window."); sys.exit(1)
    elif len(full_historical_data) <2: # Already handled, but as a safeguard.
        print(C_ERROR_BRIGHT + f"Not enough data for any backtest tries."); sys.exit(1)


    all_formula_stats = backtest_all_formulas(full_historical_data)
    
    if all_formula_stats: display_performance_summary(all_formula_stats)
    else: print(C_WARNING+"No formula performance data from backtest.")

    latest_day_data = full_historical_data[-1] if full_historical_data else None
    otc_ank_suggestions = get_otc_suggestions_for_tomorrow_modified(latest_day_data, all_formula_stats, effective_min_tries)

    if otc_ank_suggestions:
        display_final_otc_suggestions(market_name, otc_ank_suggestions)
    else: 
        print(C_WARNING_BRIGHT + f"\nNo Math Formulas for {market_name} met the required hit rate ({MIN_HIT_RATE_SUGGESTION*100:.0f}%) and min tries ({effective_min_tries}) within the last {BACKTEST_WINDOW_DAYS} days for an OTC Ank suggestion today.")

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: print(C_WARNING_BRIGHT+"\n\n[!] User interrupted."+C_RESET)
    except Exception as e:
        print(C_ERROR_BRIGHT+f"\n[!!!] CRITICAL ERROR: {e}"); import traceback; traceback.print_exc()
        print(C_ERROR_BRIGHT+"Please report this."+C_RESET)
    finally: print(C_PRIMARY_BRIGHT+f"\n✨ Thank you for using {APP_NAME}! ✨"+C_RESET)
