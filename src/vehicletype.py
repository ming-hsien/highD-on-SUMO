import csv

import xml.etree.ElementTree as ET
import xml.dom.minidom

class Truck:
    def __init__(self, id, length):
        self.vid = "truck" + str(id)
        self.accel = "2.5"
        self.decel = "4.5"
        self.length = length
        self.maxSpeed = "80"
        self.vClass = "truck"
        self.carFollowModel = "EIDM"
        self.lcStrategic="1.0"
        self.lcKeepRight="0"
        self.lcOvertakeRight="1"
        self.lcCooperative="1"
        self.lcSpeedGain="1"
        self.lcLookaheadLeft="50"
            
    def make_data_frame(self):
        return {
            "id": self.vid,
            "accel": self.accel,
            "decel": self.decel,
            "length": self.length,
            "maxSpeed": self.maxSpeed,
            "vClass": self.vClass,
            "carFollowModel" : self.carFollowModel,
            "lcStrategic" : self.lcStrategic,
            "lcKeepRight" : self.lcKeepRight,
            "lcOvertakeRight" : self.lcOvertakeRight,
            "lcCooperative" : self.lcCooperative,
            "lcSpeedGain" : self.lcSpeedGain,
            "lcLookaheadLeft" : self.lcLookaheadLeft
        }

class Car:
    def __init__(self, id, length):
        self.vid = "car" + str(id)
        self.accel = "2.5"
        self.decel = "4.5"
        self.length = length
        self.maxSpeed = "80"
        self.vClass = "passenger"
        self.carFollowModel = "EIDM"
        self.lcStrategic="1.0"
        self.lcKeepRight="0"
        self.lcOvertakeRight="1"
        self.lcCooperative="1"
        self.lcSpeedGain="1"
        self.lcLookaheadLeft="50"
            
    def make_data_frame(self):
        return {
            "id": self.vid,
            "accel": self.accel,
            "decel": self.decel,
            "length": self.length,
            "maxSpeed": self.maxSpeed,
            "vClass": self.vClass,
            "carFollowModel" : self.carFollowModel,
            "lcStrategic" : self.lcStrategic,
            "lcKeepRight" : self.lcKeepRight,
            "lcOvertakeRight" : self.lcOvertakeRight,
            "lcCooperative" : self.lcCooperative,
            "lcSpeedGain" : self.lcSpeedGain,
            "lcLookaheadLeft" : self.lcLookaheadLeft
        }

class Vehicles:
    def __init__(self, tracksMeta_path, save_path):
        self.cars = []
        self.trucks = []
        self.tracksMeta_path = tracksMeta_path
        self.save_path = save_path
        
    def get_car_info(self):
        with open(self.tracksMeta_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row["class"] == "Car":
                    self.cars.append(Car(row["id"], row["width"]))
                elif row["class"] == "Truck":
                    self.trucks.append(Truck(row["id"], row["width"]))
        
    def create_vehicle_type_xml(self):
        root = ET.Element("additional")
        vTypeDist_car = ET.Element("vTypeDistribution", {"id": "car"})
        vTypeDist_truck = ET.Element("vTypeDistribution", {"id": "truck"})
        
        for vtype in self.cars:
            print(vtype.make_data_frame())
            ET.SubElement(vTypeDist_car, "vType", vtype.make_data_frame())
        root.append(vTypeDist_car)

        for vtype in self.trucks:
            ET.SubElement(vTypeDist_truck, "vType", vtype.make_data_frame())
        root.append(vTypeDist_truck)

        # tree = ET.ElementTree(root)
        xml_str = ET.tostring(root, 'utf-8')
        dom = xml.dom.minidom.parseString(xml_str)
        formatted_xml = dom.toprettyxml(indent="    ")
        with open(self.save_path, "w") as f:
            f.write(formatted_xml)

        print(f"{self.save_path} has been created.")


if __name__ == '__main__':
    vehicles_obj = Vehicles(tracksMeta_path = "../data/02_tracksMeta.csv", save_path = "../cfg/vehicletype.add.xml")
    vehicles_obj.get_car_info()
    vehicles_obj.create_vehicle_type_xml()

