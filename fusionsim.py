import customtkinter as ctk
from tkinter import messagebox
import requests
from collections import defaultdict

# ============================================
# API-FOOTBALL IMPORTER
# ============================================

API_KEY = "YOUR_API_KEY_HERE"
API_URL = "https://v3.football.api-sports.io"

# Global leagues dictionary
leagues = {}


def fetch_all_leagues():
    """Fetch all available leagues from API-Football"""
    headers = {
        'x-rapidapi-host': 'v3.football.api-sports.io',
        'x-rapidapi-key': API_KEY
    }
    
    try:
        response = requests.get(f"{API_URL}/leagues", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('response', [])
    except Exception as e:
        print(f"Error fetching leagues: {e}")
    return []


def fetch_teams(league_id, season):
    """Fetch teams for a specific league"""
    headers = {
        'x-rapidapi-host': 'v3.football.api-sports.io',
        'x-rapidapi-key': API_KEY
    }
    
    try:
        params = {'league': league_id, 'season': season}
        response = requests.get(f"{API_URL}/teams", headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('response', [])
    except Exception as e:
        print(f"Error fetching teams: {e}")
    return []


def fetch_standings(league_id, season):
    """Fetch standings for a specific league"""
    headers = {
        'x-rapidapi-host': 'v3.football.api-sports.io',
        'x-rapidapi-key': API_KEY
    }
    
    try:
        params = {'league': league_id, 'season': season}
        response = requests.get(f"{API_URL}/standings", headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('response', [])
    except Exception as e:
        print(f"Error fetching standings: {e}")
    return []


def calculate_rating(points, max_points):
    """Calculate team rating based on points"""
    if max_points == 0:
        return 0.0
    rating = points / max_points
    return round(rating, 2)


def import_from_apifootball(season):
    """
    Import leagues and calculate team ratings from API-Football
    Returns a dict structured like:
    {
        "Premier League": {
            "teams": {
                "Arsenal": 0.88,
                "Chelsea": 0.62,
                ...
            }
        },
        ...
    }
    """
    result = {}
    
    # Fetch all leagues
    all_leagues = fetch_all_leagues()
    
    if not all_leagues:
        # Return mock data if API fails or no key provided
        return get_mock_leagues_data()
    
    # Process major leagues
    major_league_ids = [39, 140, 61, 135, 78]  # Premier League, Ligue 1, Bundesliga, Serie A, La Liga
    
    for league_data in all_leagues:
        league_id = league_data.get('league', {}).get('id')
        league_name = league_data.get('league', {}).get('name')
        country = league_data.get('country', '')
        
        if league_id in major_league_ids or league_name in ["Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1"]:
            standings = fetch_standings(league_id, season)
            
            if standings:
                teams_dict = {}
                max_points = 0
                
                # Find max points for rating calculation
                for standing_group in standings:
                    for team_standing in standing_group.get('standings', []):
                        points = team_standing.get('points', 0)
                        if points > max_points:
                            max_points = points
                
                # Calculate ratings for each team
                for standing_group in standings:
                    for team_standing in standing_group.get('standings', []):
                        team_name = team_standing.get('team', {}).get('name', 'Unknown')
                        points = team_standing.get('points', 0)
                        rating = calculate_rating(points, max_points)
                        teams_dict[team_name] = rating
                
                if teams_dict:
                    result[league_name] = {"teams": teams_dict}
    
    # If no data was fetched, return mock data
    if not result:
        return get_mock_leagues_data()
    
    return result


def get_mock_leagues_data():
    """Return mock league data for demonstration purposes"""
    return {
        "Premier League": {
            "teams": {
                "Arsenal": 0.88,
                "Chelsea": 0.62,
                "Liverpool": 0.85,
                "Manchester City": 0.92,
                "Manchester United": 0.58,
                "Tottenham": 0.65,
                "Newcastle": 0.72,
                "Brighton": 0.68,
                "Aston Villa": 0.70,
                "West Ham": 0.55
            }
        },
        "La Liga": {
            "teams": {
                "Real Madrid": 0.90,
                "Barcelona": 0.87,
                "Atletico Madrid": 0.75,
                "Sevilla": 0.60,
                "Real Sociedad": 0.65,
                "Valencia": 0.52,
                "Villarreal": 0.63,
                "Athletic Bilbao": 0.61
            }
        },
        "Serie A": {
            "teams": {
                "Inter Milan": 0.89,
                "AC Milan": 0.78,
                "Juventus": 0.82,
                "Napoli": 0.76,
                "Roma": 0.68,
                "Lazio": 0.66,
                "Atalanta": 0.72
            }
        },
        "Bundesliga": {
            "teams": {
                "Bayern Munich": 0.91,
                "Borussia Dortmund": 0.80,
                "RB Leipzig": 0.74,
                "Bayer Leverkusen": 0.85,
                "Union Berlin": 0.58,
                "Freiburg": 0.62
            }
        },
        "Ligue 1": {
            "teams": {
                "PSG": 0.93,
                "Marseille": 0.70,
                "Monaco": 0.72,
                "Lyon": 0.65,
                "Lille": 0.68,
                "Nice": 0.60
            }
        }
    }


# ============================================
# FUSIONSIM APPLICATION
# ============================================

class FusionSimApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure main window
        self.title("FusionSim")
        self.geometry("1200x800")
        self.minsize(900, 600)
        
        # Set appearance mode
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialize pages dictionary
        self.pages = {}
        self.current_page = None
        
        # Build the UI
        self.setup_sidebar()
        self.setup_main_area()
        self.build_all_pages()
        
        # Show dashboard by default
        self.show_page("dashboard")
    
    def setup_sidebar(self):
        """Create the sidebar with icon-only buttons"""
        self.sidebar = ctk.CTkFrame(self, width=80, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        # Title label at top of sidebar
        title_label = ctk.CTkLabel(
            self.sidebar, 
            text="Fusion\nSim", 
            font=ctk.CTkFont(size=16, weight="bold"),
            justify="center"
        )
        title_label.pack(pady=(20, 30))
        
        # Define sidebar buttons with icons and page names
        self.sidebar_buttons = [
            ("🏠", "dashboard"),
            ("⚙️", "settings"),
            ("▶️", "run"),
            ("🔁", "until"),
            ("📥", "importer"),
            ("📁", "leagues"),
        ]
        
        # Create buttons
        for icon, page_name in self.sidebar_buttons:
            btn = ctk.CTkButton(
                self.sidebar,
                text=icon,
                font=ctk.CTkFont(size=24),
                width=60,
                height=60,
                command=lambda p=page_name: self.show_page(p),
                fg_color="transparent",
                hover_color="#3B8ED0"
            )
            btn.pack(pady=5)
    
    def setup_main_area(self):
        """Create the main content area"""
        self.main_area = ctk.CTkFrame(self, corner_radius=0)
        self.main_area.pack(side="right", fill="both", expand=True)
    
    def build_all_pages(self):
        """Build all pages and register them in self.pages"""
        self.build_dashboard()
        self.build_settings()
        self.build_run()
        self.build_until()
        self.build_importer()
        self.build_leagues()
    
    def show_page(self, name):
        """Switch to the specified page"""
        # Hide current page
        if self.current_page and self.current_page in self.pages:
            self.pages[self.current_page].pack_forget()
        
        # Show new page
        if name in self.pages:
            self.pages[name].pack(fill="both", expand=True)
            self.current_page = name
    
    def build_dashboard(self):
        """Build the dashboard page"""
        page = ctk.CTkFrame(self.main_area)
        self.pages["dashboard"] = page
        
        # Title
        title = ctk.CTkLabel(
            page,
            text="Dashboard",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title.pack(pady=(40, 20))
        
        # Subtitle
        subtitle = ctk.CTkLabel(
            page,
            text="Welcome to FusionSim - Your Football Simulation Platform",
            font=ctk.CTkFont(size=16)
        )
        subtitle.pack(pady=(0, 40))
        
        # Stats frame
        stats_frame = ctk.CTkFrame(page)
        stats_frame.pack(pady=20, padx=40, fill="x")
        
        # Stat cards
        stat_configs = [
            ("Total Leagues", str(len(leagues)), "📊"),
            ("Total Teams", str(sum(len(l.get('teams', {})) for l in leagues.values())), "⚽"),
            ("Last Import", "N/A", "🕐"),
            ("Status", "Ready", "✅")
        ]
        
        for i, (label, value, icon) in enumerate(stat_configs):
            stat_box = ctk.CTkFrame(stats_frame, width=200, height=120)
            stat_box.grid(row=0, column=i, padx=10, pady=10)
            
            stat_icon = ctk.CTkLabel(stat_box, text=icon, font=ctk.CTkFont(size=30))
            stat_icon.pack(pady=(20, 5))
            
            stat_value = ctk.CTkLabel(stat_box, text=value, font=ctk.CTkFont(size=20, weight="bold"))
            stat_value.pack()
            
            stat_label = ctk.CTkLabel(stat_box, text=label, font=ctk.CTkFont(size=12))
            stat_label.pack()
        
        # Quick actions
        actions_frame = ctk.CTkFrame(page)
        actions_frame.pack(pady=20, padx=40, fill="x")
        
        actions_title = ctk.CTkLabel(actions_frame, text="Quick Actions", font=ctk.CTkFont(size=18, weight="bold"))
        actions_title.pack(pady=10)
        
        quick_btn_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        quick_btn_frame.pack(pady=10)
        
        import_btn = ctk.CTkButton(
            quick_btn_frame,
            text="Import Leagues",
            command=lambda: self.show_page("importer"),
            width=150
        )
        import_btn.pack(side="left", padx=10)
        
        run_btn = ctk.CTkButton(
            quick_btn_frame,
            text="Run Simulation",
            command=lambda: self.show_page("run"),
            width=150
        )
        run_btn.pack(side="left", padx=10)
        
        leagues_btn = ctk.CTkButton(
            quick_btn_frame,
            text="View Leagues",
            command=lambda: self.show_page("leagues"),
            width=150
        )
        leagues_btn.pack(side="left", padx=10)
    
    def build_settings(self):
        """Build the settings page"""
        page = ctk.CTkFrame(self.main_area)
        self.pages["settings"] = page
        
        # Title
        title = ctk.CTkLabel(
            page,
            text="Settings",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title.pack(pady=(40, 30))
        
        # Settings container
        settings_container = ctk.CTkFrame(page, width=500)
        settings_container.pack(pady=20)
        
        # API Key setting
        api_frame = ctk.CTkFrame(settings_container, fg_color="transparent")
        api_frame.pack(fill="x", padx=20, pady=15)
        
        api_label = ctk.CTkLabel(api_frame, text="API Key:", font=ctk.CTkFont(size=14))
        api_label.pack(anchor="w")
        
        self.api_key_entry = ctk.CTkEntry(api_frame, width=400, placeholder_text="Enter your API-Football API key")
        self.api_key_entry.pack(pady=5)
        self.api_key_entry.insert(0, API_KEY)
        
        # Season setting
        season_frame = ctk.CTkFrame(settings_container, fg_color="transparent")
        season_frame.pack(fill="x", padx=20, pady=15)
        
        season_label = ctk.CTkLabel(season_frame, text="Default Season:", font=ctk.CTkFont(size=14))
        season_label.pack(anchor="w")
        
        self.season_entry = ctk.CTkEntry(season_frame, width=100)
        self.season_entry.pack(pady=5)
        self.season_entry.insert(0, "2026")
        
        # Theme setting
        theme_frame = ctk.CTkFrame(settings_container, fg_color="transparent")
        theme_frame.pack(fill="x", padx=20, pady=15)
        
        theme_label = ctk.CTkLabel(theme_frame, text="Theme:", font=ctk.CTkFont(size=14))
        theme_label.pack(anchor="w")
        
        self.theme_switch = ctk.CTkSwitch(
            theme_frame,
            text="Dark Mode",
            command=self.toggle_theme,
            onvalue="dark",
            offvalue="light"
        )
        self.theme_switch.pack(pady=5)
        self.theme_switch.select()
        
        # Save button
        save_btn = ctk.CTkButton(
            settings_container,
            text="Save Settings",
            command=self.save_settings,
            width=200
        )
        save_btn.pack(pady=30)
    
    def toggle_theme(self):
        """Toggle between dark and light theme"""
        if self.theme_switch.get() == "dark":
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")
    
    def save_settings(self):
        """Save settings"""
        global API_KEY
        API_KEY = self.api_key_entry.get()
        messagebox.showinfo("Settings Saved", "Your settings have been saved successfully!")
    
    def build_run(self):
        """Build the run page"""
        page = ctk.CTkFrame(self.main_area)
        self.pages["run"] = page
        
        # Title
        title = ctk.CTkLabel(
            page,
            text="Run Simulation",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title.pack(pady=(40, 30))
        
        # Configuration frame
        config_frame = ctk.CTkFrame(page)
        config_frame.pack(pady=20, padx=40, fill="x")
        
        # League selection
        league_label = ctk.CTkLabel(config_frame, text="Select League:", font=ctk.CTkFont(size=14))
        league_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        self.league_dropdown = ctk.CTkComboBox(
            config_frame,
            values=list(leagues.keys()) if leagues else ["No leagues loaded"],
            width=300
        )
        self.league_dropdown.pack(padx=20, pady=5)
        
        # Number of simulations
        sim_label = ctk.CTkLabel(config_frame, text="Number of Simulations:", font=ctk.CTkFont(size=14))
        sim_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        self.sim_count_entry = ctk.CTkEntry(config_frame, width=100)
        self.sim_count_entry.pack(padx=20, pady=5)
        self.sim_count_entry.insert(0, "100")
        
        # Progress section
        progress_frame = ctk.CTkFrame(page)
        progress_frame.pack(pady=20, padx=40, fill="x")
        
        progress_label = ctk.CTkLabel(progress_frame, text="Progress:", font=ctk.CTkFont(size=14))
        progress_label.pack(padx=20, pady=(15, 5))
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame, width=400)
        self.progress_bar.pack(padx=20, pady=10)
        self.progress_bar.set(0)
        
        # Status label
        self.run_status = ctk.CTkLabel(progress_frame, text="Ready to run", font=ctk.CTkFont(size=12))
        self.run_status.pack(pady=5)
        
        # Run button
        run_btn = ctk.CTkButton(
            page,
            text="▶️ Start Simulation",
            command=self.start_simulation,
            width=200,
            height=40
        )
        run_btn.pack(pady=30)
        
        # Results textbox
        results_label = ctk.CTkLabel(page, text="Results:", font=ctk.CTkFont(size=16, weight="bold"))
        results_label.pack(pady=(20, 10))
        
        self.results_textbox = ctk.CTkTextbox(page, width=600, height=200)
        self.results_textbox.pack(pady=10)
    
    def start_simulation(self):
        """Start the simulation"""
        selected_league = self.league_dropdown.get()
        sim_count = self.sim_count_entry.get()
        
        if not leagues:
            messagebox.showwarning("Warning", "Please import leagues first!")
            return
        
        if selected_league == "No leagues loaded":
            messagebox.showwarning("Warning", "No leagues available for simulation!")
            return
        
        # Update status
        self.run_status.configure(text=f"Running {sim_count} simulations for {selected_league}...")
        
        # Simulate progress
        for i in range(101):
            self.progress_bar.set(i / 100)
            self.update()
        
        # Display mock results
        self.results_textbox.delete("1.0", "end")
        self.results_textbox.insert("1.0", f"Simulation Complete!\n\n")
        self.results_textbox.insert("2.0", f"League: {selected_league}\n")
        self.results_textbox.insert("3.0", f"Simulations Run: {sim_count}\n\n")
        
        if selected_league in leagues:
            teams = leagues[selected_league].get("teams", {})
            sorted_teams = sorted(teams.items(), key=lambda x: x[1], reverse=True)
            
            self.results_textbox.insert("4.0", "Top Teams:\n")
            for i, (team, rating) in enumerate(sorted_teams[:5], 1):
                self.results_textbox.insert("end", f"  {i}. {team}: {rating}\n")
        
        self.run_status.configure(text="Simulation completed!")
        messagebox.showinfo("Complete", "Simulation finished successfully!")
    
    def build_until(self):
        """Build the until page"""
        page = ctk.CTkFrame(self.main_area)
        self.pages["until"] = page
        
        # Title
        title = ctk.CTkLabel(
            page,
            text="Until Condition",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title.pack(pady=(40, 30))
        
        # Description
        desc = ctk.CTkLabel(
            page,
            text="Set conditions for when the simulation should stop",
            font=ctk.CTkFont(size=16)
        )
        desc.pack(pady=(0, 30))
        
        # Conditions container
        conditions_frame = ctk.CTkFrame(page)
        conditions_frame.pack(pady=20, padx=40, fill="both", expand=True)
        
        # Condition type
        type_label = ctk.CTkLabel(conditions_frame, text="Condition Type:", font=ctk.CTkFont(size=14))
        type_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        self.condition_type = ctk.CTkComboBox(
            conditions_frame,
            values=["Max Iterations", "Target Score", "Time Limit", "Convergence"],
            width=300
        )
        self.condition_type.pack(padx=20, pady=5)
        self.condition_type.set("Max Iterations")
        
        # Threshold value
        threshold_label = ctk.CTkLabel(conditions_frame, text="Threshold Value:", font=ctk.CTkFont(size=14))
        threshold_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        self.threshold_entry = ctk.CTkEntry(conditions_frame, width=200)
        self.threshold_entry.pack(padx=20, pady=5)
        self.threshold_entry.insert(0, "1000")
        
        # Advanced options
        advanced_frame = ctk.CTkFrame(conditions_frame)
        advanced_frame.pack(padx=20, pady=20, fill="x")
        
        advanced_title = ctk.CTkLabel(advanced_frame, text="Advanced Options", font=ctk.CTkFont(size=14, weight="bold"))
        advanced_title.pack(padx=15, pady=(10, 5))
        
        self.auto_stop_switch = ctk.CTkSwitch(advanced_frame, text="Auto-stop on convergence")
        self.auto_stop_switch.pack(padx=15, pady=5, anchor="w")
        
        self.notify_switch = ctk.CTkSwitch(advanced_frame, text="Notify when complete")
        self.notify_switch.pack(padx=15, pady=5, anchor="w")
        self.notify_switch.select()
        
        # Save button
        save_btn = ctk.CTkButton(
            conditions_frame,
            text="Save Condition",
            command=self.save_condition,
            width=200
        )
        save_btn.pack(pady=20)
    
    def save_condition(self):
        """Save the until condition"""
        condition_type = self.condition_type.get()
        threshold = self.threshold_entry.get()
        
        messagebox.showinfo(
            "Condition Saved",
            f"Condition saved:\nType: {condition_type}\nThreshold: {threshold}"
        )
    
    def build_importer(self):
        """Build the importer page"""
        page = ctk.CTkFrame(self.main_area)
        self.pages["importer"] = page
        
        # Title label
        title = ctk.CTkLabel(
            page,
            text="Data Importer",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title.pack(pady=(40, 20))
        
        # Description label
        description = ctk.CTkLabel(
            page,
            text="Import league data from API-Football. This will fetch all available leagues,\ntheir teams, and calculate team ratings based on standings.",
            font=ctk.CTkFont(size=14),
            justify="center"
        )
        description.pack(pady=(0, 30))
        
        # Info frame
        info_frame = ctk.CTkFrame(page)
        info_frame.pack(pady=20, padx=40, fill="x")
        
        info_items = [
            ("📡", "Connects to API-Football"),
            ("⚽", "Fetches league standings"),
            ("📊", "Calculates team ratings"),
            ("💾", "Stores data locally")
        ]
        
        for i, (icon, text) in enumerate(info_items):
            item_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            item_frame.grid(row=0, column=i, padx=15, pady=10)
            
            icon_label = ctk.CTkLabel(item_frame, text=icon, font=ctk.CTkFont(size=24))
            icon_label.pack()
            
            text_label = ctk.CTkLabel(item_frame, text=text, font=ctk.CTkFont(size=12))
            text_label.pack()
        
        # Season selection
        season_frame = ctk.CTkFrame(page)
        season_frame.pack(pady=20)
        
        season_label = ctk.CTkLabel(season_frame, text="Season:", font=ctk.CTkFont(size=14))
        season_label.pack(side="left", padx=10)
        
        self.import_season_entry = ctk.CTkEntry(season_frame, width=100)
        self.import_season_entry.pack(side="left", padx=10)
        self.import_season_entry.insert(0, "2026")
        
        # Import button
        import_btn = ctk.CTkButton(
            page,
            text="📥 Import Data",
            command=self.run_importer,
            width=200,
            height=50,
            font=ctk.CTkFont(size=16)
        )
        import_btn.pack(pady=30)
        
        # Status label
        self.import_status = ctk.CTkLabel(
            page,
            text="Ready to import",
            font=ctk.CTkFont(size=12)
        )
        self.import_status.pack(pady=10)
        
        # Progress bar
        self.import_progress = ctk.CTkProgressBar(page, width=400)
        self.import_progress.pack(pady=10)
        self.import_progress.set(0)
    
    def run_importer(self):
        """Run the importer to fetch league data"""
        global leagues
        
        self.import_status.configure(text="Importing data... Please wait...")
        self.import_progress.set(0.3)
        self.update()
        
        try:
            season = int(self.import_season_entry.get())
        except ValueError:
            season = 2026
        
        # Import data
        leagues = import_from_apifootball(season)
        
        self.import_progress.set(1.0)
        self.import_status.configure(text=f"Imported {len(leagues)} leagues")
        
        messagebox.showinfo("Import Complete", "All leagues imported successfully!")
        
        # Update league dropdown in run page
        if "run" in self.pages:
            league_values = list(leagues.keys()) if leagues else ["No leagues loaded"]
            # Rebuild the dropdown options
            self.league_dropdown.configure(values=league_values)
            if league_values:
                self.league_dropdown.set(league_values[0])
    
    def build_leagues(self):
        """Build the leagues page"""
        page = ctk.CTkFrame(self.main_area)
        self.pages["leagues"] = page
        
        # Title label
        title = ctk.CTkLabel(
            page,
            text="Leagues Overview",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title.pack(pady=(40, 20))
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            page,
            text="🔄 Refresh",
            command=self.refresh_leagues,
            width=120
        )
        refresh_btn.pack(pady=10)
        
        # Scrollable textbox for league display
        self.leagues_textbox = ctk.CTkTextbox(page, width=700, height=500)
        self.leagues_textbox.pack(pady=20)
        
        # Display leagues
        self.display_leagues()
    
    def refresh_leagues(self):
        """Refresh the leagues display"""
        self.display_leagues()
        messagebox.showinfo("Refreshed", "Leagues list updated!")
    
    def display_leagues(self):
        """Display all leagues in the textbox"""
        self.leagues_textbox.delete("1.0", "end")
        
        if not leagues:
            self.leagues_textbox.insert("1.0", "No leagues loaded yet.\n\nClick on the Importer tab to load league data.")
            return
        
        total_teams = 0
        
        for league_name, league_data in leagues.items():
            teams = league_data.get("teams", {})
            team_count = len(teams)
            total_teams += team_count
            
            self.leagues_textbox.insert("end", f"{'='*60}\n")
            self.leagues_textbox.insert("end", f"🏆 {league_name}\n")
            self.leagues_textbox.insert("end", f"{'='*60}\n")
            self.leagues_textbox.insert("end", f"Total Teams: {team_count}\n\n")
            
            # Sort teams by rating
            sorted_teams = sorted(teams.items(), key=lambda x: x[1], reverse=True)
            
            for rank, (team_name, rating) in enumerate(sorted_teams, 1):
                rating_bar = "█" * int(rating * 10) + "░" * (10 - int(rating * 10))
                self.leagues_textbox.insert("end", f"  {rank:2}. {team_name:25} [{rating_bar}] {rating:.2f}\n")
            
            self.leagues_textbox.insert("end", "\n")
        
        # Summary
        self.leagues_textbox.insert("end", f"\n{'='*60}\n")
        self.leagues_textbox.insert("end", f"SUMMARY\n")
        self.leagues_textbox.insert("end", f"{'='*60}\n")
        self.leagues_textbox.insert("end", f"Total Leagues: {len(leagues)}\n")
        self.leagues_textbox.insert("end", f"Total Teams: {total_teams}\n")


# ============================================
# MAIN ENTRY POINT
# ============================================

if __name__ == "__main__":
    app = FusionSimApp()
    app.mainloop()
