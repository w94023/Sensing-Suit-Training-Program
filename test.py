# # from lib.base import *
# # from lib.pyqt_base import *

# # from lib.scr.csv import *
# # from lib.scr.pyqt import *
# # from lib.scr.json import *

# # import random

# # import tensorflow as tf
# # import h5py

# # input_locations = []
# # for i in range(100):
# #     input_locations.append("Wireframe"+str(i+1))
    
# # output_locations = []
# # for i in range(10):
# #     output_locations.append("Marker"+str(i+1))
    
# # pre_training_epoch = 1000
# # pre_training_learning_rate = 0.001
# # full_training_epoch = 1000
# # full_training_learning_rate = 0.001

# # lambda1 = 0.2
# # lambda2 = 0.5
# # lambda3 = 0.8

# # execution_time = 10.123

# # embedded_vector_hist = []
# # time_hist = []

# # for i in range(2):
# #     time_hist.append(random.random())
# #     embedded_vector_hist.append(np.random.rand(1, 100))
    
# # if len(embedded_vector_hist) != len(time_hist):
# #     print("RETURN")

# # export_data_list = []
# # export_data_list.append(["", "Pre training epoch", pre_training_epoch, "Pre training learning rate", pre_training_learning_rate, "Full training epoch", full_training_epoch, "Full training learning rate", full_training_learning_rate])
# # export_data_list.append(["", "Lambda", lambda1, lambda2, lambda3])
# # export_data_list.append(["", "Execution time (s)", execution_time])
# # export_data_list.append([])
# # export_data_list.append(["", "Output locations"] + output_locations)
# # export_data_list.append([])
# # export_data_list.append(["Iteration", "Time (s)"] + input_locations)
# # for i in range(len(time_hist)):
# #     export_data_list.append([i+1, time_hist[i]] + embedded_vector_hist[i].tolist()[0])

# # df = pd.DataFrame(export_data_list).fillna("")

# # current_directory = os.path.dirname(os.path.abspath(__file__))
# # df.to_csv(Path(os.path.join(current_directory, "Test.csv")), header = False, index = False)

# # import numpy as np

# # a = np.array([
# #     [-0.5464, 0, 0],
# #     [0, -0.5464, 0.5464],
# #     [0, -0.3464, 0.2]
# # ])

# # b = np.array([
# #     [200, 0, 0],
# #     [0, 40, 0],
# #     [0, 0, 50]
# # ])

# # c = np.array([
# #     [-0.5464, 0, 0],
# #     [0, -0.5464, -0.3464],
# #     [0, 0.5464, 0.2]
# # ])

# # print(a)
# # print(b)
# # print(c)

# # d = a*b*c
# # print(d)

# ################################################################################

# # import serial
# # import struct
# # import time

# # def calculate_checksum(packet):
# #     """다이나믹셀 패킷의 체크섬 계산."""
# #     return ~sum(packet) & 0xFF

# # def print_hex_packet(packet):
# #     """패킷을 0xFF 형태로 출력."""
# #     hex_packet = " ".join(f"0x{byte:02X}" for byte in packet)
# #     print(hex_packet)

# # def read_position(serial_port, motor_id):
# #     """다이나믹셀 모터의 현재 위치 읽기."""
# #     # Read Position Instruction (Address: 36 (0x24), Length: 2 bytes)
# #     instruction_packet = [
# #         0xFF, 0xFF,              # Header
# #         motor_id,                # Motor ID
# #         4,                       # Length (Instruction + Parameters + Checksum)
# #         2,                       # Instruction: READ_DATA
# #         0x24,                    # Starting Address (36)
# #         2                        # Length of data to read
# #     ]
    
# #     # Add checksum
# #     checksum = calculate_checksum(instruction_packet[2:])
# #     instruction_packet.append(checksum)

# #     # Send packet
# #     serial_port.write(bytearray(instruction_packet))
# #     print_hex_packet(instruction_packet)
    
# #     # Wait for a response (allow time for the motor to reply)
# #     time.sleep(1)
    
# #     # Read response packet
# #     response = serial_port.read(serial_port.in_waiting or 20)
# #     print_hex_packet(response)
    
# #     # Validate response
# #     if len(response) < 6 or response[0:2] != b'\xFF\xFF':
# #         print(response)
# #         raise Exception("Invalid response received")
    
# #     # Extract data
# #     response_id = response[2]
# #     error = response[4]
# #     if error != 0:
# #         raise Exception(f"Error from motor: {error}")

# #     # Position value (2 bytes: Low byte + High byte)
# #     position = struct.unpack("<H", response[5:7])[0]
# #     return position

# # def main():
# #     # 시리얼 포트 설정 (사용 중인 환경에 맞게 수정)
# #     port_name = "COM5"  # Windows의 경우 포트 이름 예: COM3
# #     baud_rate = 57600  # 다이나믹셀 기본 통신 속도

# #     # 모터 ID 설정
# #     motor_id = 0xFE  # 읽으려는 다이나믹셀 모터의 ID

# #     try:
# #         # 시리얼 포트 열기
# #         with serial.Serial(port_name, baudrate=baud_rate, timeout=1) as serial_port:
# #             # 모터 현재 위치 읽기
# #             position = read_position(serial_port, motor_id)
# #             print(f"Motor ID {motor_id} Current Position: {position}")

# #     except Exception as e:
# #         print(f"Error: {e}")

# # if __name__ == "__main__":
# #     main()
    
# ################################################################################

# import serial
# import time
# import threading
# import struct
# import queue

# def print_hex_packet(packet):
#     """패킷을 0xFF 형태로 출력."""
#     hex_packet = " ".join(f"0x{byte:02X}" for byte in packet)
#     return hex_packet

# def create_goal_position_packet(motor_id, goal_position):
#     """
#     다이나믹셀 목표 위치 설정 패킷 생성 메서드.

#     Args:
#         motor_id (int): 모터 ID (1~253).
#         goal_position (int): 목표 위치 (0~4095, 모델에 따라 범위 다름).

#     Returns:
#         list: 생성된 패킷 리스트.
#     """
    
#     # 목표 위치를 2바이트로 분할 (Little Endian)
#     position_low = goal_position & 0xFF       # 하위 바이트
#     position_high = (goal_position >> 8) & 0xFF  # 상위 바이트
    
#     # Instruction Packet 구성
#     instruction_packet = [
#         0xFF, 0xFF,       # Header
#         0xFE,         # Motor ID
#         0x05,         # Length: Instruction(1) + Data Length(2) + Checksum(1)
#         0x03,             # Instruction: WRITE_DATA
#         0x1E,          # Starting Address
#         position_low,     # Goal Position Low Byte
#         position_high     # Goal Position High Byte
#     ]
    
#     # Checksum 계산 및 추가
#     checksum = (~sum(instruction_packet[2:]) & 0xFF)  # Checksum 계산
#     instruction_packet.append(checksum)
    
#     return instruction_packet

# def read_position():
#     """다이나믹셀 모터의 현재 위치 읽기."""
#     # Read Position Instruction (Address: 36 (0x24), Length: 2 bytes)
#     # instruction_packet = [
#     #     0xFF, 0xFF,              # Header
#     #     0x01,                # Motor ID
#     #     4,                       # Length (Instruction + Parameters + Checksum)
#     #     2,                       # Instruction: READ_DATA
#     #     0x24,                    # Starting Address (36)
#     #     6,                        # Length of data to read
#     # ]
    
#     # instruction_packet = [
#     # 0xFF, 0xFF,              # Header
#     # 0x01,                # Motor ID
#     # 8,                       # Length (Instruction + Parameters + Checksum)
#     # 0,                       # Instruction: READ_DATA
#     # 0xE8,
#     # 0x03,
#     # 0x0A,
#     # 0x00,
#     # 0x20,
#     # 0x00, 
#     # ]
    
#     instruction_packet = [
#     0xFF,
#     0xFF,
#     0x01,
#     0x1E,
#     0x00,
#     0x00,
#     0x00,
#     0x00,
#     ]
    
#     # # Add checksum
#     # checksum = (~sum(instruction_packet[2:]) & 0xFF)  # Checksum 계산
#     # instruction_packet.append(checksum)
    
#     return instruction_packet

# # Queue to handle user input in a separate thread
# input_queue = queue.Queue()

# def find_packets(data, start_sequence, packet_length):
#     packets = []
#     index = 0
#     while index < len(data):
#         # Find the start sequence
#         index = data.find(start_sequence, index)
#         if index == -1:  # No more occurrences
#             break
#         # Extract the packet
#         packets.append(data[index:index + packet_length])
#         index += len(start_sequence)  # Move index forward
#     return packets

# def two_bytes_to_int(lsb, msb):
#     # Little-Endian 순서의 바이트
    
#     # Little-Endian 바이트로부터 int16 변환
#     byte_data = bytes([lsb, msb])
#     int16_value = struct.unpack('<h', byte_data)[0]  # '<h': Little-Endian, signed short
    
#     return int16_value

# def get_user_input(ser):
#     while True:
#         # user_input = input()
#         # input_queue.put(user_input)
#         packet = read_position()
#         str_packet = print_hex_packet(packet)  # 송신 데이터 출력
#         print(f"sent packet {str_packet}")
        
#         ser.write(bytearray(packet))
        
#         time.sleep(1)

# def read_serial_data():
#     try:
#         # COM4 포트, 115200 보드레이트로 시리얼 연결
#         ser = serial.Serial('COM3', 115200, timeout=1)
#         print("Serial connection established. Listening for data...")
        
#         # Start a thread for user input
#         threading.Thread(target=get_user_input, args=(ser,), daemon=True).start()
        
#         while True:
#             # Check for user input
#             # if not input_queue.empty():
#             #     user_input = input_queue.get()
#             #     if user_input == "\x04":  # Ctrl+D
#             #         # packet = create_goal_position_packet(0xFE, 1000)
#             #         packet = read_position()
#             #         str_packet = print_hex_packet(packet)  # 송신 데이터 출력
#             #         print(f"sent packet {str_packet}")
                    
#             #         ser.write(bytearray(packet))

#             # 시리얼 데이터 수신
#             if ser.in_waiting > 0:  # 수신된 데이터가 있는 경우
#                 data = ser.read(ser.in_waiting)  # 모든 수신된 데이터 읽기 (바이너리)
            
#                 str_data = print_hex_packet(data)
#                 print(f"received packet {str_data}")
                
                
#                 # # Validate response
#                 # if len(data) < 6 or data[0:2] != b'\xFF\xFF':
#                 #     raise Exception("Invalid response received")
                
#                 # # Extract data
#                 # response_id = data[2]
#                 # error = data[4]
#                 # if error != 0:
#                 #     raise Exception(f"Error from motor: {error}")

#                 # # Position value (2 bytes: Low byte + High byte)
#                 # position = struct.unpack("<H", data[5:7])[0]
#                 # print("position")
#                 # print(position)
                
#                 # speed = struct.unpack("<H", data[7:9])[0]
#                 # print("speed")
#                 # print(speed)
                
#                 # load = struct.unpack("<H", data[9:11])[0]
#                 # print("load")
#                 # print(load)
                
#                 # # 각 메시지 출력
#                 # for i, message in enumerate(messages, 1):
#                 #     hex_message = " ".join(f"{byte:02X}" for byte in message)
#                 #     print(f"Message {i}: {hex_message}")
#             else:
#                 time.sleep(0.001)  # 데이터가 없으면 잠시 대기
            
#     except KeyboardInterrupt:
#         print("\nCtrl+C detected. Exiting...")
#     except Exception as e:
#         print(f"An error occurred: {e}")
#     finally:
#         if 'ser' in locals() and ser.is_open:
#             ser.close()
#             print("Serial connection closed.")

# if __name__ == "__main__":
#     read_serial_data()

a = 0x02+0x00+0x00+0x00+0x00+0x00+0x8F+0x06+0xC7+0x07+0x67+0x08+0x79+0x07+0x41+0x08+0x6A+0x07+0x28+0x08+0xA8+0x07+0x6B+0x0A+0xB3+0x03+0x7C+0x00+0x62+0x02
print(a)