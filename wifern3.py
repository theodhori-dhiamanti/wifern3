# This Python file uses the following encoding: utf-8
# ## Imports###
import sys, os, subprocess, signal, re, csv, signal, random
from signal import SIGINT
from PyQt6 import QtCore, QtGui, QtSql, QtWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog
from PyQt6.QtCore import Qt, QFileSystemWatcher, QCoreApplication, QProcess, QTimer
from PyQt6.QtSql import QSqlQueryModel, QSqlQuery, QSqlDatabase
from functools import partial
from tempfile import mkdtemp
import form

# ## Initializations
list_processes = []
mon_iface = ''
int_iface = ''
before_intface = ('', '')
after_intface = ('', '')
wordlist_path = ''
wordlist = ''
adapters = []
monitors = []
proglist = []
not_rec_list = []

# ## End of Initializations

class wifern3(QMainWindow, form.Ui_mainwindow):
    def __init__(self, db, parent=None):
        super(wifern3, self).__init__(parent)
        self.db = db
        self.setupUi(self)
        #if os.getuid() != 0:
        #    exit(1)
        wifi_model = QtSql.QSqlQueryModel()
        self.working_dir()
        self.recs()


        # Buttons        
        #self.Get_Wordlist_Button.clicked.connect(dict.select_wordlist)
        #self.Get_Wordlist_Button.clicked.connect(self.opendict)
        self.access_pointScan_Button.clicked.connect(self.start_wifi_scan)
        self.Rec_Install_Button.clicked.connect(self.recInstall)
        self.list_interfaces_Button.clicked.connect(self.wireless_interface)
        self.wlan0_monitor_Button.clicked.connect(self.monitor_mode_enable)
        self.wlan1_monitor_button.clicked.connect(self.UseThis)
        #self.start_wash_Button.clicked.connect(self.wash_call)
        #self.Process_wordlist_Button.clicked.connect(self.process_wordlist)
        #self.startReaver_Button.clicked.connect(self.reaverPrep)
        #self.wordlist_save_button.clicked.connect(self.saveWordlist)
        self.mac_gen_Button.clicked.connect(self.MacGen)

        # ComboBox
        #self.Monitor_select_comboBox.currentIndexChanged.connect(self.washMonitorList)

        # TableView
        #self.wash_tableView.clicked.connect(self.reaverPrep)

        # GUI Initial State Config

        self.wlan0_monitor_Button.setVisible(False)
        self.wlan1_monitor_button.setVisible(False)
        self.start_wash_Button.setEnabled(False)
        self.Monitor_select_comboBox.setEnabled(False)
        self.wordlist_save_button.setEnabled(False)
        self.Process_wordlist_Button.setEnabled(False)
        self.startReaver_Button.setEnabled(False)

        # Call any necessary display functions
        self.showlcd()

######################### Display Functions############################
    def showlcd(self):
        time = QtCore.QTime.currentTime()
        text = time.toString('hh:mm')
        self.lcd_time_Number.display(text)

    def MacGen(self):
        try:
            mac_count = int(self.mac_gen_lineEdit.text())
            file_path = os.path.join(os.path.expanduser(self.working_dir_path), 'wifern.txt')

            with open(file_path, 'w') as mac_file:  # text mode 'w' instead of binary 'wb'
                for _ in range(mac_count):
                    x = self.randomMAC()
                    y = self.get_manufacturer(x)
                    print(x)
                    mac_file.write(f"{x},{y}\n")  # f-string for cleaner formatting

        except ValueError:
            QMessageBox.information(self, 'Wrong Value', 'Please enter a valid number', QMessageBox.StandardButton.Ok )
            self.mac_gen_lineEdit.setText("")


            # Dictionary of vendors and their OUIs (first 3 bytes)
            VENDOR_OUIS = {
                'Apple':      [0x00, 0x1C, 0xB3],
                'Cisco':      [0x00, 0x1A, 0x2B],
                'Intel':      [0x00, 0x13, 0xE8],
                'Samsung':    [0x00, 0x16, 0x6C],
                'Huawei':     [0x00, 0x25, 0x68],
                'TP-Link':    [0xE8, 0x94, 0xF6],
                'Dell':       [0x00, 0x14, 0x22],
                'Xiaomi':     [0x64, 0x09, 0x80],
            }
    def get_manufacturer(self, bssid):
        ##################
        # Method works   #
        ##################
        oui_path0 = '/etc/aircrack-ng/airodump-ng-oui.txt'
        oui_path1 = '/usr/local/etc/aircrack-ng/airodump-ng-oui.txt'
        oui_path2 = '/usr/share/aircrack-ng/airodump-ng-oui.txt'
        partial_mac = ''

        try:
            oui_path = ''
            if os.path.exists(oui_path0):
                oui_path = oui_path0
            elif os.path.exists(oui_path1):
                oui_path = oui_path1
            elif os.path.exists(oui_path2):
                oui_path = oui_path2
            else:
                model = 'Not Available'

            with open(oui_path, 'r') as oui:
                db = oui.readlines()
            for line in db:
                oui_db = line.split()
                lookup_mac = oui_db[0].lower().replace('-', ':')
                partial_mac = bssid[:8]
                if lookup_mac == partial_mac:
                    self.model = ' '.join(oui_db[2:])
                    return model  # need to athached to client before record is displayed
        except IOError as a:
            pass
            #print ("I/O error({0}): {1}".format(a.errno, a.strerror))


    def random_vendor_mac():
        vendor = random.choice(list(VENDOR_OUIS.keys()))
        oui = VENDOR_OUIS[vendor]
        mac = oui + [random.randint(0x00, 0xff) for _ in range(3)]
        mac_str = ':'.join(f'{octet:02x}' for octet in mac)
        #return mac_str, vendor
        for _ in range(5):
            mac, vendor = random_vendor_mac()
            print(f"{mac} ({vendor})")


        #Random MAC. Use the one above
    def randomMAC(self):
        mac = [
            0x00,
            random.randint(0x00, 0x7f),
            random.randint(0x00, 0x7f),

            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff)
        ]
        return ':'.join(f"{octet:02x}" for octet in mac)


    def UseThis(self):  # TODO check for reaver, wash then set buttons active
        if self.monitors_comboBox.currentText() != '':
            self.Monitor_select_comboBox.setEnabled(True)
            self.mon_iface = self.monitors_comboBox.currentText()
            if 'reaver' in proglist and 'wash' in proglist:
                self.start_wash_Button.setEnabled(True)


    # ######################################
    #         Available Programs           #
    ########################################
    def program_find(self, program):
        try:
            subprocess.run(['which', program], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def recs(self):
        try:
            row = 0
            col = 0
            query = QtSql.QSqlQuery(self.db)
            self.my_tableWidget.setColumnCount(3)
            self.my_tableWidget.setColumnWidth(0, 90)
            self.my_tableWidget.setColumnWidth(1, 60)
            self.my_tableWidget.setColumnWidth(2, 60)
            self.my_tableWidget.setRowCount(20)
            programs = {
                'aircrack-ng': ['required', True],
                'aireplay-ng': ['required', True],
                'airodump-ng': ['required', True],
                'airmon-ng': ['required', True],
                'iw': ['required', True],
                'iwconfig': ['required', True],
                'reaver': ['required', True],
                'wash': ['required', True],
                'mdk3': ['required', True],
                'pyrit': ['required', True],
                'ifconfig': ['required', True],
                'sqlite3': ['required', True],
                'bully': ['not_required', True],
                'crunch': ['not_required', True],
                'pw-inspector': ['required', True],
                'oclhashcat': ['not_required', True],
            }
            for prog, (recommendation, available) in programs.items():
                if self.program_find(prog):
                    proglist.append(prog)
                    query.prepare("insert into recs (program_name, available) values (?,?)")
                    query.addBindValue(prog)
                    query.addBindValue(True)
                    query.exec()
                else:
                    not_rec_list.append(prog)
                    query.prepare("insert into recs (program_name, available) values (?,?)")
                    query.addBindValue(prog)
                    query.addBindValue(False)
                    query.exec()
                    available = False
                x = QtWidgets.QTableWidgetItem()
                x.setFlags(Qt.ItemFlag.ItemIsEnabled)
                x.setCheckState(Qt.CheckState.Checked if available else Qt.CheckState.Unchecked)
                y = QtWidgets.QTableWidgetItem()
                y.setFlags(Qt.ItemFlag.ItemIsEnabled)
                y.setCheckState(Qt.CheckState.Checked if recommendation == 'required' else Qt.CheckState.Unchecked)
                row_item = QtWidgets.QTableWidgetItem(prog)
                self.my_tableWidget.setItem(row, col, row_item)
                self.my_tableWidget.setItem(row, 1, x)
                self.my_tableWidget.setItem(row, 2, y)
                row += 1
            self.my_tableWidget.setRowCount(row)            
        except OSError as e:
            print(e.message)



    def recInstall(self):
        for program in not_rec_list:
            cmd = ['sudo', 'apt-get', 'install', '-y', program]
            try:
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error installing {program}: {e}")
        self.recs()

    # ########################################
    #              Database Operations       #
    ##########################################
    def working_dir(self):
        self.working_dir_path = mkdtemp(prefix='wifern3')
        if not self.working_dir_path.endswith(os.sep):
            self.working_dir_path += os.sep
        os.chdir(self.working_dir_path)
        self.dBaseOpen()
        print("Working dir set to:", self.working_dir_path)


    def dBaseOpen(self):
        self.db.open()        
        if not self.db.open():
            msg = QMessageBox.critical(self, "Error", "Unable to establish a database connection.")
            msg.setDefaultButton(QMessageBox.Cancel)
            return False
        query = QSqlQuery(self.db)
        query.exec("CREATE TABLE IF NOT EXISTS reaver (bssid TEXT PRIMARY KEY, essid TEXT, channel INTEGER, power INTEGER, locked TEXT)")
        query.exec("CREATE TABLE IF NOT EXISTS victim (bssid TEXT PRIMARY KEY, firsttimeseen DATETIME, lasttimeseen DATETIME, channel INTEGER, speed TEXT, encryption TEXT, cipher INTEGER, authentication TEXT, power INTEGER, beacons INTEGER, data TEXT, lanip INTEGER, idlength INTEGER, essid TEXT, key TEXT)")
        query.exec("CREATE TABLE IF NOT EXISTS adapters (name varchar(8), bssid varchar(17), status varchar(7))")
        query.exec("CREATE TABLE IF NOT EXISTS monitors (name varchar(8), bssid varchar(17))")
        query.exec("CREATE TABLE IF NOT EXISTS recs (program_name varchar(20), available varchar(10), recommendation varchar(17))")
        query.exec("CREATE TABLE IF NOT EXISTS clients(bssid varchar(17), station varchar(17) references reaver (bssid), power int(3))")
        return True



##################### Wifi Operations#############################
##################################################################

    def start_wifi_scan(self):
            if self.access_pointScan_Button.text() == "Scan for Access Points":
                self.access_pointScan_Button.setText('Stop Scan')

                # Start airodump-ng scan in CSV format inside the temp folder
                self.start_airdump_ng()

            else:
                self.access_pointScan_Button.setText("Scan for Access Points")

                # Stop scan if it's running
                if self.process:
                    os.kill(self.process.processId(), SIGINT)
                    #self.process.terminate()  # Kill the airodump-ng process
                    print("Scan stopped.")
                # self.clear_wifi_table()  # Do not clear the table when stopping the scan

    def start_airdump_ng(self):
        # Query monitor interface from the database
        query = QtSql.QSqlQuery(self.db)
        query.prepare("SELECT name FROM monitors LIMIT 1")
        mon_iface = None

        if query.exec() and query.next():
            mon_iface = query.value(0)
        else:
            QtWidgets.QMessageBox.critical(self, "Error", "No monitor interface found in database.")
            return

        output_prefix = os.path.join(self.working_dir_path, "airodump_output")

        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.setProgram("sudo")
        self.process.setArguments([
            "airodump-ng",
            mon_iface,
            "--output-format", "csv",
            "--write", output_prefix,            
        ])
        self.process.readyReadStandardOutput.connect(self.process_output)
        self.process.start()

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_wifi_table)
        self.refresh_timer.start(5000)

        print(f"Scan started with airodump-ng on {mon_iface}, writing to: {output_prefix}")
################################################################################################################

    def process_output(self):
        """Handle and parse airodump-ng output for APs and clients."""
        output = self.process.readAllStandardOutput().data().decode()

        ap_lines = []
        client_lines = []
        in_client_section = False

        # Split into AP and Client sections
        for line in output.splitlines():
            if line.strip().startswith("Station MAC"):
                in_client_section = True
                continue
            if not line.strip():
                continue
            if in_client_section:
                client_lines.append(line)
            else:
                ap_lines.append(line)

        # === Process Access Points ===
        network_data = []
        for line in ap_lines:
            parts = re.split(r'\s{2,}', line.strip())
            if len(parts) >= 15:
                try:
                    network_data.append({
                        'bssid': parts[0].strip(),
                        'firsttimeseen': parts[1].strip(),
                        'lasttimeseen': parts[2].strip(),
                        'channel': parts[3].strip(),
                        'mb': parts[4].strip(),
                        'encryption': parts[5].strip(),
                        'cipher': parts[6].strip(),
                        'authentication': parts[7].strip(),
                        'power': parts[8].strip(),
                        'beacons': parts[9].strip(),
                        'data': parts[10].strip(),
                        'lanip':parts[11].strip(),
                        'idlength': parts[12].strip(),
                        'essid': parts[13].strip(),
                        'key' : parts[14].strip()
                    })
                except IndexError:
                    print(f"Skipping malformed AP line: {line}")

        self.setup_wifi_table()
        for network in network_data:
            self.add_network_to_table(**network)

        # === Process Clients ===
        self.Client_columnview.clear()  # Reset view
        for line in client_lines:
            parts = re.split(r'\s{2,}', line.strip())
            if len(parts) >= 6:
                client_mac = parts[0].strip()
                associated_bssid = parts[5].strip() if len(parts) > 5 else "UNKNOWN"
                display = f"{client_mac} → {associated_bssid}"
                self.Client_columnview.addItem(display)

        print(f"Added {len(network_data)} APs and {len(client_lines)} clients.")



################################################################################################################
    def refresh_wifi_table(self):
        """Read the CSV file and update the AP and client views."""
        output_file = "airodump_output-01.csv"
        if not os.path.exists(output_file):
            return

        with open(output_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        ap_section = []
        client_section = []
        in_client_section = False

        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith("Station MAC"):
                in_client_section = True
                continue

            if in_client_section:
                client_section.append(line)
            else:
                ap_section.append(line)

        # === Process APs ===
        self.setup_wifi_table()
        reader = csv.reader(ap_section)
        next(reader, None)  # Skip AP header row

        for row in reader:
            if len(row) < 15:
                continue            
            bssid, firsttimeseen, lasttimeseen, channel, speed, encryption, cipher, authentication, power, beacons, data, lanip, idlength, essid, key = row[:15]
            self.add_network_to_table(
                bssid.strip(), firsttimeseen.strip(), lasttimeseen.strip(), channel.strip(), speed.strip(), encryption.strip(), cipher.strip(), authentication.strip(),
                power.strip(), beacons.strip(), data.strip(), lanip.strip(), idlength.strip(), essid.strip(), key.strip()
            )

        # === Process Clients ===
        self.Client_columnview.clear()
        reader = csv.reader(client_section)
        next(reader, None)  # Skip client header row

        for row in reader:
            if len(row) < 6:
                continue
            client_mac = row[0].strip()
            bssid = row[5].strip() if len(row) > 5 else "UNKNOWN"
            self.Client_columnview.addItem(f"{client_mac} → {essid}")



    def add_network_to_table(self, bssid, firsttimeseen, lasttimeseen, channel, speed, encryption, cipher, authentication, power, beacons, data, lanip, idlength, essid, key):
        """Insert network details into the database."""

         # Check if the bssid or other required fields are valid (e.g., non-empty)
        if not bssid:
            print("Error: Missing essential data (bssid). Network not added.")
            QMessageBox.warning(self, "Invalid Data", "BSSID is missing. Network not added.")
            return

        # Prepare the SQL query
        query = QSqlQuery(self.db)
        query.prepare("""
            INSERT OR REPLACE INTO victim
            (bssid, firsttimeseen, lasttimeseen, channel, speed, encryption, cipher, authentication, power, beacons, data, lanip, idlength, essid, key)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """)

        # Bind the values to the query
        query.addBindValue(bssid)
        query.addBindValue(firsttimeseen)
        query.addBindValue(lasttimeseen)
        query.addBindValue(channel)
        query.addBindValue(speed)
        query.addBindValue(encryption)
        query.addBindValue(cipher)
        query.addBindValue(authentication)
        query.addBindValue(power)
        query.addBindValue(beacons)
        query.addBindValue(data)
        query.addBindValue(lanip)
        query.addBindValue(idlength)
        query.addBindValue(essid)
        query.addBindValue(key)

        # Execute the query and handle errors
        if query.exec():
            #print(f"Network {bssid} added to database.")
            #QMessageBox.information(self, "Network Added", f"Network with BSSID {bssid} added to the database.")
            pass
        else:
            # error_message = query.lastError().text()
            # print(f"Failed to insert network {bssid}: {error_message}")
            # QMessageBox.critical(self, "Database Error", f"Failed to add network {bssid}: {error_message}")
            pass


    def clear_wifi_table(self):
        """Clear the table view."""
        self.wifi_model.setQuery("SELECT * FROM victim", self.db)  # Refresh the table by requerying the database
        self.wifi_model.clear()  # Optionally clear the model data


    def setup_wifi_table(self):
        # Check if the database connection is open
        if not self.db.isOpen():
            print("Error: Database is not open.")
            QMessageBox.critical(self, "Database Error", "Database connection is not open.")
            return

        # Create a query model
        self.wifi_model = QSqlQueryModel(self)

        # Execute the query to fetch data from 'victim' table
        self.wifi_model.setQuery("SELECT * FROM victim", self.db)

        # Handle potential errors from the SQL query execution
        if self.wifi_model.lastError().isValid():
            print("SQL Error:", self.wifi_model.lastError().text())
            QMessageBox.critical(self, "Database Error", "Failed to load Wi-Fi data.")
            return

        # Define headers
        headers = [
            "BSSID", "firsttimeseen", "lasttimeseen", "channel", "speed", "encryption",
            "cipher", "authentication", "power", "beacons", "data", "lanip", "idlength", "essid", "key"
        ]

        # Set column headers for the model
        for idx, header in enumerate(headers):
            self.wifi_model.setHeaderData(idx, Qt.Orientation.Horizontal, header)

        # Set the model for the table view
        self.accessPointTable.setModel(self.wifi_model)

        # Adjust column sizes to fit content
        self.accessPointTable.resizeColumnsToContents()

        # Enable alternating row colors for better readability
        self.accessPointTable.setAlternatingRowColors(True)

        # Set selection behavior to select entire rows when clicked
        self.accessPointTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)

        # Disable editing of the table
        self.accessPointTable.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)

        # Optionally, log when the table is set up (for debugging)
        print("Wi-Fi table setup complete.")


    def wifi_window(self):
        try:
            if not self.mon_iface:
                raise AttributeError("Monitor interface not selected.")

            if self.access_pointScan_Button.text() == "Scan for Access Points":
                self.access_pointScan_Button.setText('Stop Scan')
                self.setup_wifi_table()

                self.file_Wifi = QFileSystemWatcher(self)
                self.file_Wifi.addPath('attack_session.db')
                self.file_Wifi.fileChanged.connect(self.wifirefresh)

                if self.wifi_model.lastError().isValid():
                    print("SQL Error:", self.wifi_model.lastError().text())
            else:
                self.access_pointScan_Button.setText("Scan for Access Points")
                with open('extra1.txt', 'r') as fw:
                    pid = int(fw.readline().strip())
                    os.kill(pid, signal.SIGINT)

        except AttributeError:
            QMessageBox.information(self, 'Monitor Interface', 'You must select a monitor interface', QMessageBox.StandardButton.Ok)
        except Exception as e:
            print("Unexpected error:", str(e))

    def wifirefresh(self):
        if not self.db.isOpen():
            if not self.db.open():
                QMessageBox.critical(self, "Database Error", "Unable to reopen the database.")
                return

        self.wifi_model.setQuery("SELECT * FROM victim", self.db)

        if self.wifi_model.lastError().isValid():
            print("Refresh SQL Error:", self.wifi_model.lastError().text())
            QMessageBox.warning(self, "Refresh Failed", "Could not refresh the Wi-Fi table.")
            return

        self.accessPointTable.resizeColumnsToContents()


##############################Interface Methods#################################

    def get_interface_mac(self, interface):
        """Helper to get MAC address for an interface, including 'unspec' format in monitor mode."""
        try:
            result = subprocess.run(
                f"ifconfig {interface}",
                capture_output=True, text=True, shell=True
            ).stdout

            # Match modern 'ether' or older 'HWaddr'
            mac_match = re.search(r'(ether|HWaddr)\s+([0-9a-fA-F:]{17})', result)
            if mac_match:
                return mac_match.group(2)

            # Match 'unspec' MAC (monitor mode, raw format)
            unspec_match = re.search(r'unspec\s+((?:[0-9A-Fa-f]{2}[-:]){5}[0-9A-Fa-f]{2})', result)
            if unspec_match:
                # Convert from dash-separated to colon-separated if needed
                return unspec_match.group(1).replace('-', ':')

            return "UNKNOWN"

        except Exception as e:
            print(f"Error fetching MAC for {interface}: {e}")
            return "UNKNOWN"


    def wireless_interface(self):
        global monitors, adapters
        query = QtSql.QSqlQuery(self.db)

        # Run iwconfig and capture output
        try:
            cmd = subprocess.run("iwconfig", capture_output=True, text=True, shell=True).stdout
        except Exception as e:
            print(f"iwconfig error: {e}")
            return

        adapters = re.findall(r"wlan\d+", cmd, re.IGNORECASE) if 'Mode:Managed' in cmd else []
        monitors = re.findall(r"wlan\d+mon", cmd, re.IGNORECASE) if 'Mode:Monitor' in cmd else []

        if not adapters and not monitors:
            self.adapters_comboBox.addItem("No Interface")
            return

        # --- Populate Adapters ---
        self.adapters_comboBox.clear()
        for adap in adapters:
            self.adapters_comboBox.addItem(adap)
            self.wlan0_monitor_Button.setVisible(True)

            mac = self.get_interface_mac(adap)
            query.prepare("INSERT INTO adapters(name, bssid, status) VALUES (?, ?, ?)")
            query.addBindValue(adap)
            query.addBindValue(mac)
            query.addBindValue("before")
            query.exec()

            if adap == self.adapters_comboBox.currentText():
                self.before_intface = (adap, mac)

        # --- Populate Monitors ---
        self.monitors_comboBox.clear()
        self.Monitor_select_comboBox.clear()
        for monit in monitors:
            self.monitors_comboBox.addItem(monit)
            self.Monitor_select_comboBox.addItem(monit)
            self.wlan1_monitor_button.setVisible(True)

            mac = self.get_interface_mac(monit)
            query.prepare("INSERT INTO monitors(name, bssid) VALUES (?, ?)")
            query.addBindValue(monit)
            query.addBindValue(mac)
            query.exec()

            if monit == self.monitors_comboBox.currentText():
                self.b_m_intface = (monit, mac)

        print("Adapters:", adapters)
        print("Monitors:", monitors)


    def monitor_mode_enable(self):
        """
        Enables monitor mode on the selected network interface.
        """
        query = QtSql.QSqlQuery(self.db)
        int_iface = str(self.adapters_comboBox.currentText())
        print(int_iface)
        # Retrieve BSSID from database for the selected adapter
        query.prepare("SELECT adapters.bssid FROM adapters WHERE adapters.name = ? AND adapters.status = ?")
        query.addBindValue(int_iface)
        query.addBindValue("before")
        query.exec()

        if not query.next():
            QMessageBox.warning(self, "Error", "No data found for selected adapter.")
            return

        Mon_bss = str(query.value(0)) #.toString())

        # Check if adapter is already in monitor mode
        if len(adapters) == len(monitors):
            QMessageBox.information(self, "Select Different Adapter",
                                          f"{int_iface} has already been put in monitor mode", QMessageBox.Ok)
            return

        # Check if there are too many monitor interfaces
        if len(monitors) > len(adapters):
            response = QMessageBox.information(self, 'Too Many Monitors',
                                                     'There are too many monitor interfaces up\nWould you like to reset them?',
                                                     QMessageBox.Yes | QMessageBox.No)
            if response == QMessageBox.Yes:
                self.reset_monitors()
            else:
                return

        # Check if the BSSID is already in monitors table
        query1 = QtSql.QSqlQuery()
        query1.prepare("SELECT monitors.name FROM monitors WHERE monitors.bssid = ?")
        query1.addBindValue(Mon_bss.upper())
        query1.exec()

        if query1.next():
            QMessageBox.information(self, "Select Different Adapter",
                                          f"{int_iface} has already been put in monitor mode", QMessageBox.Ok)
            return

        # Get the network interface's MAC address
        comm = subprocess.getoutput(f"ifconfig -a | awk '/HWaddr/ {{print $1 \" \" $NF}}'")        
        unspec_match = re.search(r'unspec\s+((?:[0-9A-Fa-f]{2}[-:]){5}[0-9A-Fa-f]{2})', comm)
        if unspec_match:
            # Convert from dash-separated to colon-separated if needed
            return unspec_match.group(1).replace('-', ':')

        for word in comm.splitlines():
            wor_essid = word[:-17]  # ESSID
            wor_mac = word[-17:]  # MAC address

            if wor_essid == int_iface:
                before_intface = wor_essid, wor_mac
                wor_mac_mon = self.stealth(str(wor_essid), str(wor_mac))

                # Update the database with the new MAC address in monitor mode
                query.prepare("INSERT INTO adapters(name, bssid, status) VALUES(?, ?, ?)")
                query.addBindValue(wor_essid)
                query.addBindValue(wor_mac_mon)
                query.addBindValue('after')
                query.exec()

        # Enable monitor mode on the selected interface
        print("the interface is ", int_iface)
        comm = subprocess.getoutput(f'sudo airmon-ng start {int_iface}')
        if 'monitor mode vif enabled ' in comm:
            # Extract the monitor interface name using regex
            reg = re.compile(r'wlan\d+mon', re.IGNORECASE)
            x_int = reg.findall(comm)

            for a, monitor in enumerate(x_int):
                mon_iface = monitor
                if mon_iface in monitors:
                    mon_iface = x_int[(a + 1) % len(x_int)]
                else:
                    monitors.append(mon_iface)

            if self.injection_working(mon_iface):
                self.update_monitor_combo_boxes()
            else:
                print('Injection NOT working')
        else:
            QMessageBox.warning(self, "Error", "Failed to enable monitor mode.")

    def injection_working(self, mon_iface_check: str) -> bool:
        try:
            process = subprocess.Popen(
                ['sudo', 'aireplay-ng', '-9', mon_iface_check],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True  # Automatically decode bytes to str
            )

            for line in iter(process.stdout.readline, ''):
                if 'Injection is working!' in line:
                    process.terminate()  # Graceful termination
                    process.wait(timeout=1)
                    QMessageBox.information(self, 'Injection',
                                            f'Injection on {mon_iface_check} is working!',
                                            QMessageBox.StandardButton.Ok)
                    return True

            process.terminate()
            process.wait(timeout=1)

            QMessageBox.information(self, 'Injection',
                                    f'Injection on {mon_iface_check} is NOT working!',
                                    QMessageBox.StandardButton.Ok)
            return False

        except subprocess.SubprocessError as e:
            QMessageBox.warning(self, 'Error',
                                f'Error checking injection: {str(e)}',
                                QMessageBox.StandardButton.Ok)
            return False



    def reset_monitors(self):
        """
        Resets monitor interfaces by stopping them and clearing related UI elements.
        """
        for monitor in monitors:
            subprocess.call(['airmon-ng', 'stop', monitor])

        monitors.clear()  # Clear the list of monitors

        # Clear the combo boxes related to monitors
        self.monitors_comboBox.clear()
        self.Monitor_select_comboBox.clear()

        # Reload the available interfaces
        self.wireless_interface()

    def update_monitor_combo_boxes(self):
        """
        Updates the combo boxes with the current monitor interfaces.
        """
        for monit in monitors:
            self.monitors_comboBox.addItem(monit)
            self.Monitor_select_comboBox.addItem(monit)

        self.wlan1_monitor_button.setVisible(True)


class victim:
    def __init__(self, bssid, power, beacons, data, channel, mb, encryption,
                 cipher, auth, essid, manufacturer):
        self.bssid = bssid
        self.power = power
        self.beacons = beacons
        self.data = data
        self.channel = channel
        self.mb = mb
        self.encryption = encryption
        self.cipher = cipher
        self.auth = auth
        self.essid = essid
        self.manufacturer = manufacturer




if __name__ == "__main__":
    app = QApplication(sys.argv)
    db = QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName('attack_session.db')
    if not db.open():
        print("Failed to open database")   
    query = QtSql.QSqlQuery(db)
    form = wifern3(db)
    form.show()
    sys.exit(app.exec())
