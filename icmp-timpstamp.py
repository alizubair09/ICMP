import socket
import struct
import time

def icmp_timestamp_request(target_host):
    # Create a raw socket
    icmp = socket.getprotobyname("icmp")
    raw_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    
    # Construct the ICMP packet (Type 13 for Timestamp Request)
    packet = struct.pack("!BBHHH", 13, 0, 0, 12345, 0)
    checksum = checksum(packet)
    packet = struct.pack("!BBHHH", 13, 0, checksum, 12345, 0)
    
    # Send the packet to the target host
    raw_socket.sendto(packet, (target_host, 0))
    
    # Wait for a response
    raw_socket.settimeout(3)  # Set timeout to 3 seconds
    try:
        response, addr = raw_socket.recvfrom(1024)
        remote_timestamp = struct.unpack("!LL", response[20:28])[0]
        return remote_timestamp
    except socket.timeout:
        return None

def calculate_time_difference(remote_timestamp):
    if remote_timestamp:
        local_timestamp = int(time.time())
        time_difference = abs(local_timestamp - remote_timestamp)
        return time_difference
    else:
        return None

def checksum(data):
    checksum = 0
    for i in range(0, len(data), 2):
        checksum += (data[i] << 8) + data[i+1]
    checksum = (checksum >> 16) + (checksum & 0xffff)
    checksum += checksum >> 16
    return ~checksum & 0xffff

def main():
    target_host = input("Enter the target host IP address: ")
    remote_timestamp = icmp_timestamp_request(target_host)
    
    if remote_timestamp:
        time_difference = calculate_time_difference(remote_timestamp)
        if time_difference is not None:
            print(f"The difference between the local and remote clocks is {time_difference} seconds.")
        else:
            print("Failed to calculate time difference.")
    else:
        print("No response received from the target host.")

if __name__ == "__main__":
    main()
