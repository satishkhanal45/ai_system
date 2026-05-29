from colorama import Fore, Style, init

init(autoreset=True)

def print_menu(menu_text: str):
    print(Fore.CYAN + menu_text)

def print_user(text: str):
    print(Fore.GREEN + "\n  You: " + Style.RESET_ALL + text)

def print_assistant(text: str):
    print(Fore.YELLOW + "\n  Assistant: " + Style.RESET_ALL + text + "\n")

def print_success(text: str):
    print(Fore.GREEN + f"\n  ✔ {text}" + Style.RESET_ALL)

def print_error(text: str):
    print(Fore.RED + f"\n  ✘ {text}" + Style.RESET_ALL)

def print_info(text: str):
    print(Fore.CYAN + f"\n  ℹ {text}" + Style.RESET_ALL)

def print_section(title: str):
    print(Fore.MAGENTA + f"\n  {'─' * 44}")
    print(Fore.MAGENTA + f"  {title}")
    print(Fore.MAGENTA + f"  {'─' * 44}" + Style.RESET_ALL)

def print_response(label: str, value: str):
    print(Fore.CYAN + f"  {label}: " + Style.RESET_ALL + value)

def input_prompt(text: str) -> str:
    return input(Fore.GREEN + f"  {text}" + Style.RESET_ALL)
