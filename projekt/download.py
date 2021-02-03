import requests, re, os, csv, zipfile, pickle, gzip, sys
from bs4 import BeautifulSoup
from datetime import date
from io import StringIO
import numpy as np

class DataDownloader:
    def __init__(self, url="https://ehw.fit.vutbr.cz/izv/",folder="data", cache_filename="data_{}.pkl.gz"):
        """Initialize parametrs of DataDownloader."""
        self.url = url
        self.folder = folder
        self.cache_filename = cache_filename
        self.ListOfZipFiles = []
        self.saved_data = {}
        self.headers = ["region", "p1", "p36", "p37", "p2a", "weekday(p2a)", "p2b", "p6", "p7", "p8", "p9", "p10", "p11", "p12", "p13a", "p13b", "p13c", "p14", "p15", "p16", "p17", "p18", "p19", "p20", "p21", "p22", "p23", "p24", "p27", "p28", "p34", "p35", "p39", "p44", "p45a", "p47", "p48a", "p49", "p50a", "p50b", "p51", "p52", "p53","p55a","p57","p58","a","b","d","e","f","g","h","i","j","k","l","n","o","p","q","r","s","t","p5a"]
        self.duplicate_handling = []
        if not re.search("^.*{}.*$", self.cache_filename):
            self.cache_filename+="{}"


    def download_data(self):
        """Downloads the data and saves it to a zip file."""
        headers = {'User-Agent': 'Mozilla/5.0',}

        #Request for html data of url page
        r = requests.get(self.url, headers = headers, allow_redirects=True)
        soup = BeautifulSoup(r.text, "html.parser")

        #Checking if folder path exists, if not, creats it
        i=0
        while i<len(self.folder)-1:
            if self.folder[i] == '/':
                if not os.path.isdir(self.folder[:i]):
                    os.mkdir(self.folder[:i])
            i+=1
            if i==len(self.folder)-1:
                if not os.path.isdir(self.folder):
                    os.mkdir(self.folder)

        # if not os.path.isdir(self.folder):
        #     os.mkdir(self.folder)

        #Gets every href to zip file with data
        entries = []
        for link in soup.find_all('a'):
            if re.search("^data/.*.zip", link.get('href')):
                entries.append(link.get('href'))

        #Gets the newest dataset
        self.getCurrentData(entries)

        i=0
        #Saves each file in dataset
        for list in self.ListOfZipFiles:
            if not os.path.isfile(self.folder+list[4:]):
                r = requests.get(self.url+list)
                open(self.folder+list[4:], 'wb').write(r.content)
            #deletes prefix "data/"
            self.ListOfZipFiles[i] = list[4:]
            i+=1


    def getCurrentData(self, entries):
        """From all hrefs it gets the newest ones.

        Keyword arguments:
        entries - array of files
        """
        self.ListOfZipFiles.clear()
        #gets actual year
        year = date.today().year
        firstTimeFail = True
        #cycles until all years have been filtered
        while(1):
            firstTime = True
            zipFile = ""
            for entry in entries:
                index = 0
                if re.search("{}".format(year), entry):
                    if re.search(".*rok.*", entry):
                        zipFile = entry
                        break
                    else:
                        for char in entry:
                            if char.isdigit():
                                break
                            index+=1
                        if not entry[index:index+3].isdigit():
                            if firstTime:
                                zipFile = entry
                                firstTime = False
                            else:
                                if zipFile[index:index+2] < entry[index:index+2]:
                                    zipFile = entry
                        else:
                            zipFile = entry
                            break
            #if the new year don't have any data, tries to catch another one
            if zipFile=="":
                if firstTimeFail:
                    firstTimeFail = False
                else:
                    break
            else:
                #saves zip file name into list of filtered files
                self.ListOfZipFiles.append(zipFile)
            year-=1


    def getCsvFileByRegion(self, region):
        """Returns name of csv file of a region.

        Keyword arguments:
        entries - region name
        """
        result = ""
        if region == "PHA":
            result = "00.csv"
        elif region == "STC":
            result = "01.csv"
        elif region == "JHC":
            result = "02.csv"
        elif region == "PLK":
            result = "03.csv"
        elif region == "ULK":
            result = "04.csv"
        elif region == "HKK":
            result = "05.csv"
        elif region == "JHM":
            result = "06.csv"
        elif region == "MSK":
            result = "07.csv"
        elif region == "OLK":
            result = "14.csv"
        elif region == "ZLK":
            result = "15.csv"
        elif region == "VYS":
            result = "16.csv"
        elif region == "PAK":
            result = "17.csv"
        elif region == "LBK":
            result = "18.csv"
        elif region == "KVK":
            result = "19.csv"
        else:
            return None
        return result


    def parse_region_data(self, region):
        """From downloaded zip files, it extracts all data of region.

        Keyword arguments:
        region - region name

        Returns: tuple (list[str], list[np.ndarray])
        list[str] - column headers
        list[np.ndarray] - data of columns
        """

        #downloads newest data
        self.download_data()

        TmpList = [[] for i in range(65)]

        #goes through all the files and saves their data to the variable
        for zipName in self.ListOfZipFiles:
            with zipfile.ZipFile("./"+self.folder+"/"+zipName, 'r') as zf:
                if self.getCsvFileByRegion(region) == None:
                    print("ERROR: neznamy nazev kraje: " + region, file=sys.stderr)
                    return None
                #opens zip file for reading
                with zf.open(self.getCsvFileByRegion(region), "r") as f:
                    reader = f.read().decode("iso 8859-2")
                    reader = StringIO(reader)
                    reader = csv.reader(reader, delimiter = ";")
                    #saves every row of file
                    for row in reader:
                        TmpList[0].append(region)
                        i=1
                        #saves every column separated because of their types
                        for item in row:
                            if item != "":
                                if (i>0 and i<4) or (i>4 and i<6) or (i>6 and i<32) or (i>32 and i<35) or (i>35 and i<46) or i==61 or i==64:
                                    if not re.search("^[-]{0,1}[0-9]*$", item):
                                        item = None
                                    else:
                                        item=int(item)
                                elif i>45 and i<52:
                                    if not re.search("^[-]{0,1}[0-9]*[,.]{0,1}[0-9]+$", item):
                                        item = None
                                    else:
                                        item = item.replace(",", ".")
                                        if re.search("^[-]{1}.*$", item):
                                            item = item.replace("-", "")
                                            item = -(float(item))
                                        else:
                                            item = float(item)
                                elif i==6:
                                    if not re.search("^[-]{0,1}[0-9]*$", item):
                                        item = None
                                    else:
                                        if (len(item) == 4):
                                            #cas nijak neupravuji, jen rozdeluji minuty od hodin
                                            #policie uz nastavila hodnoty podle nich pozname nevalidni hodnotu
                                            #pro minuty tato hodnota je 60
                                            #pro hodiny tato hodnota je 25
                                            #dle meho nazoru mi prislo zbytecne na misto techto dvou hdonot davat nejakou jinou nevalidni hodnotu (napr. NaN, -1)
                                            #prepsal bych nevalidni vystup na jiny nevalidni vystup
                                            item = item[:2] + ":" + item[2:]
                                        else:
                                            item = None
                                TmpList[i].append(item)
                            else:
                                TmpList[i].append(None)
                            i+=1

        ListNpArrays = [[] for i in range(65)]

        #transforms into numpy.ndarray
        for x in range(0, 65):
            ListNpArrays[x] = np.array(TmpList[x], dtype=object)

        return (self.headers, ListNpArrays)


    def get_list(self, regions = None):
        """It extracts all data of regions.

        Keyword arguments:
        regions - names of regions

        Returns: tuple (list[str], list[np.ndarray])
        list[str] - column headers
        list[np.ndarray] - data of columns
        """

        dataInSavedData = False
        if regions == None:
            regions = ["PHA", "STC", "JHC", "PLK", "KVK", "ULK", "LBK", "HKK", "PAK", "OLK", "MSK", "JHM", "ZLK", "VYS"]

        FinalNpArrayList = [[] for i in range(65)]

        self.duplicate_handling = []

        #For every region:
        for region in regions:
            #gets duplicity of data and deletes them
            if region in self.duplicate_handling:
                print("ERROR: duplicitni predani kraje: " + region + ", data nebyla prevzata podruhe", file=sys.stderr)
                continue
            else:
                self.duplicate_handling.append(region)

            #Gets data of region from instance of class
            if self.saved_data:
                for key in self.saved_data:
                    if key == region:
                        for x in range(len(FinalNpArrayList)):
                            FinalNpArrayList[x] = np.concatenate((FinalNpArrayList[x],self.saved_data[region][1][x]), axis=None)
                        dataInSavedData = True
                        break

            #if instance of class do not have data of region,
            #check if file .pkl.gz of region exists and gets data from it,
            #if not, gets data from parse_region_data function,
            #creates file .pkl.gz of region and saves data into isntance of class:
            if not dataInSavedData:
                PickleExists = True
                try:
                    self.saved_data[region] = pickle.load(gzip.open(self.folder + "/" + self.cache_filename.format(region),'rb'))
                except FileNotFoundError:
                    PickleExists = False

                if not PickleExists:
                    data = self.parse_region_data(region)

                    if data == None:
                        continue

                    with gzip.open(self.folder + "/" + self.cache_filename.format(region),'wb') as f:
                        pickle.dump(data, f)
                    self.saved_data[region] = data
                    for x in range(len(FinalNpArrayList)):
                        FinalNpArrayList[x] = np.concatenate((FinalNpArrayList[x], self.saved_data[region][1][x]), axis=None)
                else:
                    for x in range(len(FinalNpArrayList)):
                        FinalNpArrayList[x] = np.concatenate((FinalNpArrayList[x], self.saved_data[region][1][x]), axis=None)

        return (self.headers, FinalNpArrayList)

#if script run as a main one,
#gets data from 3 regions
#and prints data on stdout
if __name__=="__main__":
    downloader = DataDownloader()
    regions = ["PHA", "KVK", "STC"]
    data = downloader.get_list(regions)
    if not len(data[1][0]):
        print("\n0 correct regions given")
    else:
        columns = ""
        first=True
        for item in data[0]:
            if first:
                columns+=item
                first = False
            else:
                columns+=(", " + item)
        print("Column types: " + columns)
        print("\nThe number of records: " + str(len(data[1][0])))
        StringOfRegs = ""
        first=True
        for item in regions:
            if first:
                StringOfRegs+=item
                first = False
            else:
                StringOfRegs+=(", " + item)
        print("\nRegions: " + StringOfRegs)
