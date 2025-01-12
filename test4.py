import serial
import time
import threading
import struct
import queue

def print_hex_packet(packet):
    """패킷을 0xFF 형태로 출력."""
    hex_packet = " ".join(f"0x{byte:02X}" for byte in packet)
    return hex_packet

# 서브리스트의 모든 시작 인덱스를 찾는 함수
def find_all_sublist_indices(lst, sub):
    indices = []
    for i in range(len(lst) - len(sub) + 1):
        if lst[i:i + len(sub)] == sub:
            indices.append(i)
    return indices

def two_bytes_to_int(lsb, msb, is_velocity):
    
    # 16비트 정수로 결합 (리틀 엔디안: LSB 먼저)
    combined = (msb << 8) | lsb  # MSB는 상위 바이트, LSB는 하위 바이트
    
    if not is_velocity:
        return combined
    
    if combined <= 0x03FF:
        # 양수 범위
        return combined
    else:
        # 음수 범위
        return -(combined - 0x0400) # 음수 변환 (부호를 반영)

class PacketManager():
    def __init__(self):
        self.buffer = []
        self.packet = bytearray(30)
        
    def on_data_received(self, data):
        for byte in data:
            str_byte = f"0x{byte:02X}"
            self.buffer.append(str_byte)
            
        self.analyze_buffer()
        
        msg = ""
        for i in range(15):
            if i == 1 or i == 2:
                msg += f"{two_bytes_to_int(self.packet[2*i], self.packet[2*i + 1], True):04}"
            else:
                msg += f"{two_bytes_to_int(self.packet[2*i], self.packet[2*i + 1], False):04}"
            msg += ","
        print(msg)
        
        # msg = print_hex_packet(self.packet)
        # print(msg)
        
        # print(self.packet)
        
    def extract_packets(self, start_sequence, packet_length):
        packets = []
        
        is_finished = False
        
        while not is_finished:
            start_index = -1
            if len(self.buffer) < packet_length:
                is_finished = True
                break
            
            for i in range(len(self.buffer) - 1):
                if self.buffer[i] == start_sequence and int(self.buffer[i+1], 16) > 240:
                    start_index = i
                    break
                
                if i == len(self.buffer) - 2:
                    is_finished = True
                    break 
                
            if (start_index + packet_length > len(self.buffer)):
                is_finished = True
                break
            
            packets.append(self.buffer[start_index:start_index + packet_length])
            del self.buffer[start_index:start_index + packet_length]
            
        return packets
    
    def calculate_checksum(self, data):
        """
        Calculate checksum by summing bytes 1 to 6 (1-based indexing),
        then inverting the lower 8 bits of the sum.

        Args:
            data (list of str): List of byte strings in the format "0xYY".

        Returns:
            int: The checksum value.
        """
        # 1번째부터 6번째 바이트 추출
        selected_bytes = data[1:7]  # Python의 0-based indexing

        # 문자열 바이트를 정수로 변환하고 합산
        total_sum = sum(int(byte, 16) for byte in selected_bytes)

        # 하위 8비트를 반전
        checksum = ~total_sum & 0xFF

        return checksum

    def analyze_buffer(self):
        if len(self.buffer) < 33:
            return
        
        packet = self.extract_packets("0xFF", 33)
        for i, token in enumerate(packet):
            if i < 2:
                continue
                
            self.packet[i-2] = int(token, 16)
        
        
        # for packet in packets:
        #     if len(packet) != 8:
        #         continue
            
        #     int_packet_token = []
        #     for token in packet:
        #         int_packet_token.append(int(token, 16))
                
        #     if int_packet_token[0] == 255:
        #         if int_packet_token[1] <= 254 and int_packet_token[1] >= 249:
        #             if int_packet_token[7] == self.calculate_checksum(packet):
                        
        #                 start_index = 255 - int(packet[1], 16) - 1
            
        #                 for i in range(2, len(packet)-1):
        #                     self.packet[5 * start_index + i-2] = int_packet_token[i]
        
        
packet_manager = PacketManager()

def packet_generation(count):
    instruction_packet = [
        0xFF,
        0xFF,
        0x01,
        count & 0xFF, 
        (count >> 8) & 0xFF,
        0x00,
        0x00,
    ]
    
    # instruction_packet = [
    #     0xFF,
    #     0xFF,
    #     0x01,
    #     0x04,
    #     0x02,
    #     0x24,
    #     0x06,
    #     0xCE,
    # ]
    
    # instruction_packet = [
    #     0xFF,
    #     0xFF,
    #     0x01,
    #     0x02
    # ]
    
    # Add checksum
    checksum = (~sum(instruction_packet[2:]) & 0xFF)  # Checksum 계산
    instruction_packet.append(checksum)

    return instruction_packet

def get_user_input(ser):
    count = 0
    direction = 1
    while True:
        if count >= 4096:
            if direction == 1:
                direction = -1
        if count <= 0:
            if direction == -1:
                direction = 1
        
        packet = packet_generation(count)
        # msg = print_hex_packet(packet)
        ser.write(bytearray(packet))
        # print(msg)
    
        # msg = print_hex_packet(packet_manager.packet)
        # print(msg)
        
        # msg = ""
        # for i in range(14):
        #     msg += f"{two_bytes_to_int(packet_manager.packet[2*i], packet_manager.packet[2*i + 1]):04}"
        #     msg += ","
        # print(msg)
            
        count += 10 * direction
        # print(count)
        
        time.sleep(0.001)

try:
    # COM4 포트, 115200 보드레이트로 시리얼 연결
    ser = serial.Serial('COM5', 115200, timeout=1)
    # ser = serial.Serial('COM3', 2000000, timeout=1)
    # ser = serial.Serial('COM5', 9600, timeout=1)
    print("Serial connection established. Listening for data...")
    
    # Start a thread for user input
    threading.Thread(target=get_user_input, args=(ser,), daemon=True).start()
    
    while True:
        # 시리얼 데이터 수신
        if ser.in_waiting > 0:  # 수신된 데이터가 있는 경우
            data = ser.read(ser.in_waiting)  # 모든 수신된 데이터 읽기 (바이너리)
            msg = print_hex_packet(data)
            print(msg)
            # packet_manager.on_data_received(data)
            # print(data)
        else:
            time.sleep(0.001)  # 데이터가 없으면 잠시 대기
        
except KeyboardInterrupt:
    print("\nCtrl+C detected. Exiting...")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Serial connection closed.")
        