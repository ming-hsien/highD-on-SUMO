import time
import csv
from utils import check_sumo_env
import shutil

check_sumo_env()
import traci
from utils import start_sumo

time_block = 6
TOTAL_TIME = 22539 * time_block + 2600 * time_block

GUI = True
START_STEP = 0

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
                    'numLaneChanges': int(row['numLaneChanges'])
                }
                
    with open(tracks_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            current_frame = int(row['frame'])
            if current_frame not in frames_data:
                    frames_data[current_frame] = []
            if current_frame == tracks[int(row['id'])]['initialFrame']:
                frames_data[current_frame].append({
                    'first_appear': True,
                    'change_lane_duration' : 0,
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
                    # 'yVelocity' : abs(float(row['yVelocity'])),
                    # 'direction' : tracks[int(row['id'])]['direction'],
                    # 'laneId' : getlaneId(int(row['laneId']), tracks[int(row['id'])]['direction'])
                })

    return frames_data

def main():
    frames_data = read_trajectory_tracking_data("../data/29_tracksMeta.csv", "../data/29_tracks.csv")
    cfg_file = gene_config()
    start_sumo(cfg_file + "/freeway.sumo.cfg", False, gui=GUI)
    
    step, times = 0, 0
    
    while times < TOTAL_TIME:
        traci.simulationStep()
        if times > START_STEP and times % time_block == 0:
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
        time.sleep(0.00001)
        times+=1
    traci.close()

if __name__ == "__main__":
    main()
