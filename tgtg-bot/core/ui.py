from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import time
import datetime
import threading
import random # Added for placeholder dynamic behavior

# --- Placeholders for dependencies (as specified in THIS subtask description) ---
class AccountManager:
    def __init__(self, accounts_dir): 
        self.accounts_dir = accounts_dir
        self._accounts_data = {
            "acc1": {"credentials": {"user_id": "User1"}}, 
            "acc2": {"credentials": {"user_id": "User2"}}, 
            "acc3": {"credentials": {"user_id": "User3"}}
        }
        # Internal status for placeholder simulation
        self._account_status_internal = {"acc1": "active", "acc2": "cooldown", "acc3": "captcha"}
        print(f"AccountManager (Placeholder UI Task) initialized for directory: {accounts_dir}")


    def get_all_account_names(self): 
        return list(self._accounts_data.keys())

    def get_status(self, account_name): 
        # Simulate status changes for testing UI refresh
        # For example, acc1 might flip between active and cooldown
        if account_name == "acc1":
            if random.random() < 0.05: # Small chance to flip status
                self._account_status_internal["acc1"] = "cooldown" if self._account_status_internal["acc1"] == "active" else "active"
        
        # acc2 might come out of cooldown
        if account_name == "acc2" and self._account_status_internal["acc2"] == "cooldown":
             if random.random() < 0.02:
                 self._account_status_internal["acc2"] = "active"

        return self._account_status_internal.get(account_name, "unknown")

    def get_credentials(self, account_name): 
        return self._accounts_data.get(account_name, {}).get("credentials")

    def check_cooldown(self, account_name): 
        # This method in a real AccountManager would update status if cooldown expired.
        # For placeholder, get_status handles simple random changes.
        if self._account_status_internal.get(account_name) == "cooldown": 
            # Simulate that check_cooldown might lead to status change if called by Scheduler
            # but UI itself should primarily be reading status, not changing it.
            return True 
        return False 

class TGTGClientWrapper: # Placeholder, mainly for item structure
    def __init__(self, creds): 
        self.creds = creds
        self.user_id = creds.get("user_id", "UnknownUser") # Store user_id from creds

    def get_favorites(self): # Simulate some items
        # user_id = self.creds.get("user_id") # Already set in __init__
        print(f"TGTGClientWrapper (Placeholder UI Task) get_favorites for {self.user_id}")
        if self.user_id == "User1":
            return [
                {"item_id": "1", "display_name": "Eataly Bag", "items_available": random.choice([0,0,1,2]), "store": {"store_name": "Eataly"}, "sold_out_at": None if random.random() > 0.3 else datetime.datetime.utcnow().isoformat()+"Z"},
                {"item_id": "1b", "display_name": "Eataly Pasta", "items_available": random.choice([0,1]), "store": {"store_name": "Eataly"}, "sold_out_at": None}
            ]
        elif self.user_id == "User2":
            return [{"item_id": "2", "display_name": "Pizza Place", "items_available": random.choice([0,1]), "store": {"store_name": "Pizza Express"}, "sold_out_at": datetime.datetime.utcnow().isoformat()+"Z" if random.random() > 0.5 else None}]
        return [] # User3 (captcha) or others return empty

class Scheduler: # Placeholder
    def __init__(self): 
        self.next_poll_time = time.time() + random.randint(45,75) # Initial random poll time
        self.successful_reservations = 0
        self.active_cooldowns = 1 # Initial based on placeholder AccountManager
        print("Scheduler (Placeholder UI Task) initialized")

    def get_next_poll_time(self): 
        if time.time() > self.next_poll_time -5: # Simulate time progression, refresh if close
            self.next_poll_time = time.time() + random.randint(45,75)
        return self.next_poll_time

    def get_stats(self): 
        # In a real scenario, active_cooldowns would be updated by the Scheduler
        # based on its interactions with AccountManager. The UI reads this.
        return {"successful_reservations": self.successful_reservations, "active_cooldowns": self.active_cooldowns} 
# --- End Placeholders ---


class CLI_UI:
    def __init__(self, account_manager, scheduler, tgtg_clients_provider=None):
        self.console = Console()
        self.layout = self._make_layout()
        self.account_manager = account_manager
        self.scheduler = scheduler
        # self.tgtg_clients_provider = tgtg_clients_provider # Not used in this version

        self.running = False
        self.thread = None
        # Caching is not part of this specific subtask's direct implementation details for CLI_UI
        # self._favorites_data_cache = {} 
        # self._last_favorites_fetch_time = {}

        print("CLI_UI: Initialized.")

    def _make_layout(self):
        layout = Layout(name="root")
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main_content"),
            Layout(name="footer", size=3)
        )
        layout["main_content"].split_row(
            Layout(name="accounts_status", ratio=1),
            Layout(name="favorites_overview", ratio=2)
        )
        print("CLI_UI: Layout created.")
        return layout

    def _get_header_panel(self):
        header_text = Text("TGTG Reservation Bot - Live Dashboard", style="bold white on blue", justify="center")
        return Panel(header_text)

    def _get_account_status_panel(self):
        table = Table(title="Account Status", expand=True, padding=(0,1))
        table.add_column("Account", style="cyan", no_wrap=True, min_width=8)
        table.add_column("User ID", style="magenta", min_width=10)
        table.add_column("Status", style="green", min_width=10)

        account_names = self.account_manager.get_all_account_names()
        active_cooldown_or_captcha_count = 0
        for name in account_names:
            status_str = self.account_manager.get_status(name) 
            creds = self.account_manager.get_credentials(name)
            user_id = creds.get("user_id", "N/A") if creds else "N/A"

            style = "green"
            if status_str == "cooldown":
                style = "yellow"
                active_cooldown_or_captcha_count += 1
            elif status_str == "captcha":
                style = "red bold"
                active_cooldown_or_captcha_count += 1
            
            table.add_row(name, user_id, Text(status_str.capitalize(), style=style))
        
        # Update scheduler's placeholder stat based on what UI observes.
        # This is a simplification for the placeholder.
        if hasattr(self.scheduler, 'active_cooldowns'):
             self.scheduler.active_cooldowns = active_cooldown_or_captcha_count

        return Panel(table, title="[b]Accounts[/b]", border_style="blue")

    def _get_favorites_panel(self):
        overall_table = Table(title="Favorites Overview", expand=True, padding=(0,1))
        overall_table.add_column("Account", style="cyan", min_width=8)
        overall_table.add_column("Store", style="green", min_width=15)
        overall_table.add_column("Item", style="magenta", min_width=20)
        overall_table.add_column("Available", style="blue", min_width=5, justify="center")
        overall_table.add_column("Sold Out At", style="yellow", min_width=20)

        account_names = self.account_manager.get_all_account_names()

        for acc_idx, acc_name in enumerate(account_names):
            current_acc_status = self.account_manager.get_status(acc_name)
            
            # Only attempt to show favorites for "active" accounts
            if current_acc_status != "active":
                if acc_idx > 0: overall_table.add_row("","", "", "", "") # Add empty line for visual separation if not first
                overall_table.add_row(acc_name, Text(f"({current_acc_status.capitalize()})", style="dim"), "-", "-", "-")
                if acc_idx < len(account_names) -1 : overall_table.add_section()
                continue

            creds = self.account_manager.get_credentials(acc_name)
            if not creds: 
                if acc_idx > 0: overall_table.add_row("","", "", "", "")
                overall_table.add_row(acc_name, Text("(No Credentials)", style="dim"), "-", "-", "-")
                if acc_idx < len(account_names) -1 : overall_table.add_section()
                continue
            
            client_sim = TGTGClientWrapper(creds) # Using the placeholder client as per task
            favorites = client_sim.get_favorites() 

            if not favorites:
                if acc_idx > 0 and acc_idx < len(account_names) : overall_table.add_row(Text(" ",style="dim")," ", " ", " ", " ") # Add empty line for visual separation if not first
                overall_table.add_row(acc_name, Text("No favorites found/listed", style="dim"), "-", "-", "-")
            else:
                for i, item in enumerate(favorites):
                    store_name = item.get("store", {}).get("store_name", "N/A")
                    item_name = item.get("display_name", item.get("item",{}).get("name", "N/A"))
                    
                    items_available_count = item.get("items_available", 0)
                    available_str = str(items_available_count) if items_available_count > 0 else "No"
                    available_style = "bold green" if items_available_count > 0 else "bold red"
                    
                    sold_out_at = item.get("sold_out_at", "N/A")
                    if sold_out_at and isinstance(sold_out_at, str) and sold_out_at.endswith("Z"):
                        try:
                            sold_out_at_dt = datetime.datetime.fromisoformat(sold_out_at.replace("Z", "+00:00"))
                            sold_out_at = sold_out_at_dt.strftime("%Y-%m-%d %H:%M") # Shorter format
                        except ValueError:
                            pass 

                    display_acc_name = acc_name if i == 0 else ""
                    overall_table.add_row(
                        display_acc_name,
                        store_name,
                        item_name,
                        Text(available_str, style=available_style),
                        sold_out_at if sold_out_at else "-"
                    )
            if acc_idx < len(account_names) -1 : overall_table.add_section()

        return Panel(overall_table, title="[b]Favorites Status[/b]", border_style="green")


    def _get_footer_panel(self):
        stats = self.scheduler.get_stats() if hasattr(self.scheduler, 'get_stats') else {}
        reservations = stats.get("successful_reservations", 0)
        cooldowns = stats.get("active_cooldowns", 0) 
        
        next_poll_timestamp = self.scheduler.get_next_poll_time() if hasattr(self.scheduler, 'get_next_poll_time') else time.time()
        time_until_next_poll = max(0, next_poll_timestamp - time.time())
        
        footer_text = f"Successful Reservations: {reservations} | Active Cooldowns/CAPTCHAs: {cooldowns} | Next Global Poll In: {time_until_next_poll:.0f}s"
        quit_instructions = "Press Ctrl+C to quit."
        
        table = Table(expand=True, show_header=False, padding=0)
        table.add_column()
        table.add_column(justify="right")
        table.add_row(footer_text, quit_instructions)

        return Panel(table, border_style="dim")


    def _update_layout(self):
        self.layout["header"].update(self._get_header_panel())
        self.layout["accounts_status"].update(self._get_account_status_panel())
        self.layout["favorites_overview"].update(self._get_favorites_panel()) 
        self.layout["footer"].update(self._get_footer_panel())


    def _run_ui_loop(self):
        print("CLI_UI: Starting UI loop with Rich Live...")
        # screen=True creates an alternate screen, hiding previous terminal output.
        # transient=False might be better if we want to see logs after UI exits.
        # For this subtask, using True as per example.
        with Live(self.layout, console=self.console, refresh_per_second=0.5, screen=True, transient=True) as live:
            while self.running:
                try:
                    self._update_layout()
                    time.sleep(2) # Refresh interval for the UI content update logic
                except KeyboardInterrupt: 
                    print("CLI_UI: KeyboardInterrupt caught in UI loop. Signaling stop...")
                    self.running = False 
                    break 
                except Exception as e: 
                    self.console.print(f"CLI_UI: Error updating UI: {e}\nTraceback:", style="bold red")
                    self.console.print_exception(max_frames=10) # Rich console method
                    time.sleep(5) 

        print("CLI_UI: Rich Live loop finished.")


    def start(self):
        if self.running:
            print("CLI_UI: UI is already running.")
            return
        print("CLI_UI: Starting...")
        self.running = True
        self.thread = threading.Thread(target=self._run_ui_loop, daemon=True)
        self.thread.name = "CLI_UI_Thread"
        self.thread.start()
        print("CLI_UI: Background thread started. Rich Live display should appear.")

    def stop(self):
        print("CLI_UI: Attempting to stop...")
        self.running = False 
        if self.thread and self.thread.is_alive():
            print("CLI_UI: Waiting for UI thread to finish...")
            self.thread.join(timeout=5) 
            if self.thread.is_alive():
                print("CLI_UI: UI thread did not stop gracefully.")
            else:
                print("CLI_UI: UI thread finished.")
        else:
             print("CLI_UI: UI thread already stopped or not started.")
        print("CLI_UI: Stopped.")

# Example Usage (for testing purposes)
if __name__ == '__main__':
    print("CLI_UI Test Script - Starting")
    
    mock_account_manager = AccountManager(accounts_dir="dummy_accounts/")
    mock_scheduler = Scheduler() 
    
    ui = CLI_UI(account_manager=mock_account_manager, scheduler=mock_scheduler)
    ui.start()

    try:
        main_loop_count = 0
        while ui.running: 
            main_loop_count +=1
            time.sleep(1) 
            if main_loop_count > 30: # Auto-stop after 30 seconds for testing
                print("Main: Test run timeout reached (30s). Forcing UI stop.")
                break
    except KeyboardInterrupt:
        print("\nMain: KeyboardInterrupt received by main thread. Stopping UI...")
    finally:
        print("Main: Initiating UI stop sequence...")
        if ui.running:
            ui.stop()
        print("Main: UI Test finished.")
        time.sleep(0.5)
        print("Main: Exiting test script.")
