import psutil # allows the system to read the CPU and disk usage
import logging # allows the system to log messages
import os # allows the system to interact with the operating system
import time # allows system to use time fuctions
import shutil # also allows the system to interact with the operating system, this will be used to delete files

CPU_Threshold = 10 # The CPU usage threshold for logging
Disk_Threshold = 20 # The disk usage threshold for logging
Check_Delay = 5 # The delay between each check in seconds

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Use os.path.join to stick the filename onto that folder path
Log_File = os.path.join(SCRIPT_DIR, "system.log")
Temp_Folder = os.path.join(SCRIPT_DIR, "dummy_cache")

def check_CPU():
    '''
    Checks the CPU usage and logs the top 3 processes using the most CPU
    '''
    # 1. Take the pulse
    # this function checks the CPU usage over the course of 1 second
    usage = psutil.cpu_percent(interval=1)
    
    # 2. Check against the rule (Threshold)
    # if the usage is over the set threshold then warning message is printed and logged
    if usage > CPU_Threshold:
        print(f"WARNING HIGH CPU DETECTED: {usage}%")
        logging.warning(f"HIGH CPU DETECTED: {usage}%")
        
        # 3. Start the Investigation (Find culprits)
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        # this is a loop that uses psutil to get all the processes running on the system
        # it then gets the process ID, name, and CPU usage
            try:
                p_info = proc.info
                
                # Skip the System Idle Process (PID 0)
                if p_info['pid'] == 0:
                    continue
        # then appends the ID, name, and usage to a list
                processes.append(proc.info)
        # if the process isn't running or can't be accessed then the program skips it to prevent a crash
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # 4. Sort and pick the Top 3
        # sorts the lists of processes using lambda and tells it to sort by the CPU precent and also sort it 
        # in reverse order (highest to lowest) so the program can then take the top 3
        top_processes = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:3]
        
        # 5. Log the results
        # logs the top 3 in a readable format
        # also returns true to indicate that a warning was issued
        logging.info(f"Top CPU Consumers: {top_processes}")
        return True
    else:
        print(f"CPU is Healthy: {usage}%")
        logging.info(f"CPU is Healthy: {usage}%")
        return False
        
    return False


def check_disk():
    pass

def auto_fix_disk():
    pass

# --- SETUP LOGGING ---
def setup_logging():
    """
    Configures the logging system to save events to a file.
    """
    logging.basicConfig(
        filename=Log_File, # creates a log file with the name "system.log"
        level=logging.INFO, # records all the info and warning messages
        format='%(asctime)s - %(levelname)s - %(message)s', # formate for the log, shows time, level of log, and message
        datefmt='%Y-%m-%d %H:%M:%S' # format for the date
    )

def start_monitoring():
    print("--- IT Automation Suite Starting ---")
    print("Press Ctrl+C to stop.")
    
    # 1. Initialize Logging (Run this once at the start)
    setup_logging()

    create_dummy_cache()  # <--- ADD THIS LINE HERE
    print(f"DEBUG: Dummy junk files created in {Temp_Folder}")

    # 2. The Infinite Loop (The "Heartbeat")
    try:
        while True:
            # --- JOB 1: RUN THE CHECKS ---
            # This line jumps up to your check_CPU function, runs that code, 
            # and comes back here when it's done.
            check_CPU()
            
            # This runs the disk check. We store the result (True/False) 
            # in a variable because we might need to fix it.

            is_disk_low = check_disk()

            # --- JOB 2: REACT TO PROBLEMS ---
            # We only react to Disk issues (Safety First!)
            if is_disk_low == True:
                logging.warning("Disk Critical! Starting Auto-Fix...")
                auto_fix_disk()

            # --- JOB 3: THE PAUSE ---
            # Wait 5 seconds (or whatever CHECK_DELAY is) before checking again.
            # Without this, your script would eat 100% of your CPU!
            time.sleep(Check_Delay)
            
    except KeyboardInterrupt:
        # This handles the user pressing Ctrl+C cleanly
        print("\nStopping Monitor.")
        logging.info("Monitor stopped by user.")

def create_dummy_cache():
    # creates a folder to store dummy files
    if not os.path.exists(Temp_Folder):
        os.makedirs(Temp_Folder)

    # Create 5 dummy text files
    for i in range(5):
        filename = os.path.join(Temp_Folder, f"temp_log_{i}.txt")
        with open(filename, 'w') as f:
            f.write("This is a junk file taking up space.")


if __name__ == "__main__":
    start_monitoring()

