# This Python file uses the following encoding: utf-8

def get_victim_list(self, csv_filename):
    # Credit for this method goes to the wifite dev team.
    if not os.path.exists(csv_filename):
        return [], []

    victims = []
    clients = []

    try:
        victim_clients = False
        with open(csv_filename, 'r') as csvfile:
            victimreader = csv.reader((line.replace('\0', '') for line in csvfile), delimiter=',')

            for row in victimreader:
                if len(row) < 2:
                    continue
                if not victim_clients:
                    if len(row) < 10:
                        continue
                    if row[0].strip() == 'Station MAC':
                        victim_clients = True
                    if row[0].strip() == 'BSSID' or row[0].strip() == 'Station Mac':
                        continue
                    enc = row[5].strip()
                    wps = False
                    if 'OPN' in enc:  # Fixed conditional check for 'OPN'
                        continue
                    if 'WPA' not in enc and 'WEP' not in enc:
                        continue
                    if enc == "WPA2WPA":
                        enc = "WPA2"
                        wps = True
                    power = int(row[8].strip())

                    essid = row[13].strip()
                    essidlen = int(row[12].strip())
                    essid = essid[:essidlen]
                    if power < 0:
                        power += 100

                    t = Victim(row[0].strip(), power, row[10].strip(), row[3].strip(), enc, essid)
                    t.wps = wps
                    t.model = Victim.get_manufacturer(row[0].strip())
                    victims.append(t)
                else:
                    if len(row) < 6:
                        continue
                    bssid = re.sub(r'[^a-zA-Z0-9:]', '', row[0].strip())
                    station = re.sub(r'[^a-zA-Z0-9:]', '', row[5].strip())
                    power = row[3].strip()
                    if station != 'notassociated':
                        c = Client(bssid, station, power)
                        clients.append(c)

    except IOError as e:
        print(f"I/O error: {e}")
        return [], []

    return victims, clients


def initscan(self, iface):
    try:
        if iface:
            cmd = ['airodump-ng', '--output-format', 'csv', '--ignore-negative-one', '-w', 'wifern-dump', iface]
            wifi_cmd = Popen(cmd, stdout=PIPE)
            wi = str(wifi_cmd.pid)
            with open('extra1.txt', 'w') as fw:
                fw.write(wi)
    except Exception as e:
        print(f"Error: {e}")  # Added basic exception handling

def wifi_sort(self):
    query = QtSql.QSqlQuery(db)
    query.prepare("insert into victims")
    victims, clients = self.get_victim_list('wifern-dump.csv')

    if len(victims) < 1:
        return  # Avoid infinite recursion

    for i, victim in enumerate(victims):  # Replaced while loop with proper for loop
        query.addBindValue(victim.bssid.lower())
        # More SQL operations here (e.g., query.exec_(), etc.)





        def MacGen(self):
            try:
                mac_count = int(self.mac_gen_lineEdit.text())
                file_path = os.path.join(os.path.expanduser('~'), 'wifern.txt')

                with open(file_path, 'w') as mac_file:  # text mode 'w' instead of binary 'wb'
                    for _ in range(mac_count):
                        x = self.randomMAC()
                        y = self.get_manufacturer(x)
                        print(x)
                        mac_file.write(f"{x},{y}\n")  # f-string for cleaner formatting

            except ValueError:
                QtWidgets.QMessageBox.information(
                    self, 'Wrong Value', 'Please enter a valid number', QtWidgets.QMessageBox.Ok
                )
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



#from dataclasses import dataclass, field
#from typing import List

@dataclass
class Client:
    """Contains information about the connected clients to the AP"""
    bssid: str
    station: str
    power: str
    essid: str
    encryption: str
    probes: List[str] = field(default_factory=list)


    def opendict(self):
        #################
        # Method works  #
        #################
        filename, _ = QFileDialog.getOpenFileName(
            self,
            'Select Dictionary',
            '',
            'Text files (*.txt);;List files (*.lst)'
        )

        if filename:
            self.dict_file_path.setText(filename)
            self.wordlist = os.path.basename(filename)
            self.wordlist_path = filename
            self.dict_file_path.setEnabled(False)
        else:
            QMessageBox.information(
                self,
                'Select File',
                'You must select a file',
                QMessageBox.StandardButton.Ok
            )



###################################################get victims method to json############################33


#########################Classes

######################Add a method to both classes:
class Victim:
    # existing fields...

    def to_dict(self):
        return {
            "bssid": self.bssid,
            "power": self.power,
            "channel": self.channel,
            "privacy": self.privacy,
            "encryption": self.encryption,
            "essid": self.essid,
            "wps": self.wps,
            "model": self.model
        }

class Client:
    # existing fields...

    def to_dict(self):
        return {
            "bssid": self.bssid,
            "station": self.station,
            "power": self.power,
            "essid": self.essid,
            "encryption": self.encryption
        }
##########################You can create a method or a wrapper around get_victim_list() like this:

    import json

    def export_victims_to_json(self, csv_filename, json_filename):
        victims, clients = self.get_victim_list(csv_filename)

        data = {
            "victims": [v.to_dict() for v in victims],
            "clients": [c.to_dict() for c in clients]
        }

        with open(json_filename, 'w') as json_file:
            json.dump(data, json_file, indent=4)


#############################3Usage example###########3
self.export_victims_to_json("wifern-dump.csv", "victims.json")
