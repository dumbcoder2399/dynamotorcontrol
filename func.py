import os

import sys,tty,termios
from dynamixel_sdk import *   


fd = sys.stdin.fileno()
old_settings = termios.tcgetattr(fd)
def getch():
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

class Dynamix(object):
    
    def __init__(self,DXL_ID,DXL_MINIMUM_POSITION_VALUE,DXL_MAXIMUM_POSITION_VALUE):
        
        self.DXL_ID                      = DXL_ID 
        self.DXL_MINIMUM_POSITION_VALUE  = DXL_MINIMUM_POSITION_VALUE          # Dynamixel will rotate between this value
        self.DXL_MAXIMUM_POSITION_VALUE  = DXL_MAXIMUM_POSITION_VALUE
        # Control table address
        self.ADDR_MX_TORQUE_ENABLE      = 24               # Control table address is different in Dynamixel model
        self.ADDR_MX_GOAL_POSITION      = 30
        self.ADDR_MX_PRESENT_POSITION   = 36

        # Protocol version
        self.PROTOCOL_VERSION            = 1            # See which protocol version is used in the Dynamixel

        # Default setting
        self.BAUDRATE                    = 1000000             # Dynamixel default baudrate : 57600
        self.DEVICENAME                  = '/dev/ttyUSB3'    # Check which port is being used on your controller
                                                        # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"

        self.TORQUE_ENABLE               = 1                 # Value for enabling the torque
        self.TORQUE_DISABLE              = 0                 # Value for disabling the torque
        self.DXL_MOVING_STATUS_THRESHOLD = 20                # Dynamixel moving status threshold       
    
    def body(self):
        

        # Write goal position
        self.dxl_comm_result, self.dxl_error = self.packetHandler.write4ByteTxRx(self.portHandler, self.DXL_ID, self.ADDR_MX_GOAL_POSITION, self.dxl_goal_position[self.index])
        if self.dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(self.dxl_comm_result))
        elif self.dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(self.dxl_error))

        while 1:
            # Read present position
            self.dxl_present_position, self.dxl_comm_result, self.dxl_error = self.packetHandler.read4ByteTxRx(self.portHandler, self.DXL_ID, self.ADDR_MX_PRESENT_POSITION)
            if self.dxl_comm_result != COMM_SUCCESS:
                print("%s" % self.packetHandler.getTxRxResult(self.dxl_comm_result))
            elif self.dxl_error != 0:
                print("%s" % self.packetHandler.getRxPacketError(self.dxl_error))

            print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (self.DXL_ID, self.dxl_goal_position[self.index],self.dxl_present_position))

            if not abs(self.dxl_goal_position[self.index] - self.dxl_present_position) > self.DXL_MOVING_STATUS_THRESHOLD:
                break

        # Change goal position
        if self.index == 0:
            self.index = 1
        else:
            self.index = 0

    def disabletorque(self):
        # Disable Dynamixel Torque
        self.dxl_comm_result, self.dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, self.DXL_ID, self.ADDR_MX_TORQUE_ENABLE, self.TORQUE_DISABLE)
        if self.dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(self.dxl_comm_result))
        elif self.dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(self.dxl_error))

        # Close port
        self.portHandler.closePort()

    def move(self):
              
            
        
        self.index = 0
        self.dxl_goal_position = [self.DXL_MINIMUM_POSITION_VALUE, self.DXL_MAXIMUM_POSITION_VALUE]         # Goal position


        self.portHandler = PortHandler(self.DEVICENAME)

        self.packetHandler = PacketHandler(self.PROTOCOL_VERSION)

        # Open port
        if self.portHandler.openPort():
            print("Succeeded to open the port")
        else:
            print("Failed to open the port")
            print("Press any key to terminate...")
            getch()
            quit()

        self.dxl_comm_result, self.dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, self.DXL_ID, self.ADDR_MX_TORQUE_ENABLE, self.TORQUE_ENABLE)
        if self.dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(self.dxl_comm_result))
        elif self.dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(self.dxl_error))
        else:
            print("Dynamixel has been successfully connected")

        while True:
            print("Press any key to continue! (or press ESC to quit!)")
    
            if getch() == chr(0x1b):
                break
            self.body()
            
        self.disabletorque 









