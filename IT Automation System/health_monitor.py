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
        print(f"[!] HIGH CPU DETECTED: {usage}%")
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
    """
    Checks disk usage. Returns True if space is CRITICALLY LOW.
    """
    # 1. Get the stats for the drive where the script is running
    disk = psutil.disk_usage(SCRIPT_DIR)
    
    # 2. Math: Calculate the percentage of free space
    free_percent = (disk.free / disk.total) * 100
    
    # 3. Decision Time
    if free_percent < Disk_Threshold:
        # BAD NEWS: Space is lower than our limit 
        print(f"[!] LOW DISK SPACE: Only {free_percent:.1f}% Free")
        logging.warning(f"LOW DISK SPACE: Only {free_percent:.1f}% Free")
        return True  # This tells the Main Loop: "ACTIVATE AUTO-FIX!"
        
    else:
        # GOOD NEWS: We have plenty of space
        print(f"Disk is Healthy: {free_percent:.1f}% Free")
        logging.info(f"Disk is Healthy: {free_percent:.1f}% Free")
        return False # This tells the Main Loop: "Relax, do nothing."

def auto_fix_disk():
    """
    Simulates clearing disk space by deleting the dummy cache.
    """
    print("--> AUTO-FIX INITIATED: Clearing Temp Files...")
    logging.info("Auto-Fix Started: Cleaning temp folder.")
    
    deleted_count = 0
    
    # 1. Check if our dummy folder actually exists
    if os.path.exists(Temp_Folder):
        
        # 2. Loop through every file inside that folder
        for filename in os.listdir(Temp_Folder):
            file_path = os.path.join(Temp_Folder, filename)
            
            try:
                # 3. Verify it's a file (not a folder) and DELETE it
                if os.path.isfile(file_path):
                    os.remove(file_path) 
                    deleted_count += 1
            except Exception as e:
                # If a file is locked or in use, log the error but keep going
                logging.error(f"Failed to delete {filename}: {e}")

    # 4. Report the results
    if deleted_count > 0:
        print(f"--> Cleanup Complete. Removed {deleted_count} files.")
        logging.info(f"Auto-Fix Successful. Removed {deleted_count} files.")
    else:
        print("--> No temp files found to clean.")
        logging.info("Auto-Fix ran, but no files were found.")



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

    create_dummy_cache()
    print(f"DEBUG: Dummy junk files created in {Temp_Folder}")

    # 2. The Infinite Loop (The "Heartbeat")
    try:
        while True:
            # This line jumps up to your check_CPU function, runs that code, 
            # and comes back here when it's done.
            check_CPU()
            
            # This runs the disk check. We store the result (True/False) 
            # in a variable because we might need to fix it.

            is_disk_low = check_disk()


            # We only react to Disk issues (Safety First!)
            if is_disk_low == True:
                logging.warning("Disk Critical! Starting Auto-Fix...")
                auto_fix_disk()


            logging.info("---Next Check in 5 seconds...---")
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

