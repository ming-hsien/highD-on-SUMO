from math import sqrt
import random
import os
import sys
import time
import re
import csv
from utils import check_sumo_env
import shutil

check_sumo_env()
import traci
from traci import StepListener, constants as tc, vehicle
from plexe import (
    Plexe,
    ACC,
    CACC,
    GEAR,
    RPM,
    CONSENSUS,
    PLOEG,
    ENGINE_MODEL_REALISTIC,
    FAKED_CACC,
)
from utils import (
    start_sumo,
    running,
    add_platooning_vehicle,
    add_vehicle,
    communicate,
    get_distance,
)


TOTAL_TIME = 22539*8+2600*8

END_EDGE_ID = "E7"

GUI = True

# inter-vehicle distance

START_STEP = 0
# lane_number latoon insert
CHECK_ALL = 0b01111  # SpeedMode
LAN_CHANGE_MODE = 0b011001011000
#                   0123456789
ptype_list = []

# def init_csv_file(path):
#     f = open(path, "w")
#     writer = csv.writer(f)
#     writer.writerow(
#         [
#             "id",
#             "frame",
#             "idv_type",
#             "v",
#             "acc",
#             "x",
#             "lane_index",
#             "vehicle_sum",
#             "p_vehicle_sum",
#         ]
#     )
#     return f, writer


def gene_config():
    copy_cfg = (
    "simulated")
    shutil.copytree("../cfg", copy_cfg, dirs_exist_ok=True)
    return copy_cfg

def getlaneId(laneId, directions):
    if directions == 1:
        return str(laneId - 1)
    elif directions == 2:
        return str(laneId - 4) 
    
# def build_vehicletype(tp, id, length):
#     traci.vehicletype.add(
#         typeID = str(tp) + str(id),
#         accel = 1.0,
#         decel = 2.0,
#         length = length,
#         maxSpeed = 80.0,
#         vClass = tp
#     )

def read_trajectory_tracking_data(tracksMeta_path, tracks_path):
    frames_data = {}
    tracks = {}
    with open(tracksMeta_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            current_id = int(row['id'])
            if current_id not in tracks:
                tracks[current_id] = {
                    'carid': str(row['class']).lower() + str(current_id),
                    'initialFrame': int(row['initialFrame']),
                    'finalFrame' : int(row['finalFrame']),
                    'direction': int(row['drivingDirection']), # 1 is right to left, 2 is left to right
                }
                # build_vehicletype(str(row['class']), str(current_id), float(row['height']))
                
    with open(tracks_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            current_frame = int(row['frame'])
            # if tracks[int(row['id'])]['direction'] == 2:
            #     print(getlaneId(int(row['laneId']), tracks[int(row['id'])]['direction']))
            #     continue
            if current_frame not in frames_data:
                    frames_data[current_frame] = []
            if current_frame == tracks[int(row['id'])]['initialFrame']:
                frames_data[current_frame].append({
                    'first_appear': True,
                    'x': float(row['x']),
                    'carid': tracks[int(row['id'])]['carid'],
                    'xVelocity' : abs(float(row['xVelocity'])),
                    'yVelocity' : abs(float(row['yVelocity'])),
                    'direction' : int(tracks[int(row['id'])]['direction']),
                    'laneId' : getlaneId(int(row['laneId']), tracks[int(row['id'])]['direction'])
                })
            else:
                frames_data[current_frame].append({
                    'first_appear': False,
                    'carid': tracks[int(row['id'])]['carid'],
                    'xVelocity' : abs(float(row['xVelocity'])),
                    'yVelocity' : abs(float(row['yVelocity'])),
                    'direction' : tracks[int(row['id'])]['direction'],
                    'laneId' : getlaneId(int(row['laneId']), tracks[int(row['id'])]['direction'])
                })

    return frames_data



# def has_vehicle_entered(step, vehicles_to_enter):
#     return vehicles_to_enter.get(step) is not None

# def aggregate_vehicles(tracks_meta):
#     vehicles_to_enter = {}
#     for vid, data in tracks_meta.items():
#         if data.get('found'):
#             data['id'] = vid
#             frame = data['initialFrame']
#             if frame in vehicles_to_enter:
#                 vehicles_to_enter[frame].append(data)
#             else:
#                 vehicles_to_enter[frame] = [data]
#     return vehicles_to_enter


def main():
    frames_data = read_trajectory_tracking_data("../data/02_tracksMeta.csv", "../data/02_tracks.csv")
    cfg_file = gene_config()
    start_sumo(cfg_file + "/freeway.sumo.cfg", False, gui=GUI)
    
    step, times = 0, 0
    
    while times < TOTAL_TIME:
        traci.simulationStep()
        
        if times > START_STEP and times % 8 ==0:
            if step in frames_data:
                for data in frames_data[step]:
                    try:
                        if data['first_appear']:
                            if int(data['direction']) == 2:
                                traci.vehicle.add(
                                    vehID=str(data['carid']),
                                    routeID="left_to_right",
                                    typeID=str(data['carid']),
                                    departSpeed=data['xVelocity'],
                                    departPos=str(float(data['x'] - 450)),
                                    departLane=data['laneId']
                                )
                            else:
                                traci.vehicle.add(
                                    vehID=str(data['carid']),
                                    routeID="right_to_left",
                                    typeID=str(data['carid']),
                                    departSpeed=data['xVelocity'],
                                    departPos=str(450 - float(data['x'])),
                                    departLane=data['laneId']
                                )
                        else:
                            if str(data['carid']) in traci.vehicle.getIDList():
                                traci.vehicle.setSpeed(str(data['carid']), data['xVelocity'])
                    except Exception as e:
                        pass
            step += 1
        time.sleep(0.005)
        times+=1
    traci.close()

if __name__ == "__main__":
    main()
