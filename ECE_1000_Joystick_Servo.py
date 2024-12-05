# Import/Declare necessary libraries
from machine import PWM, ADC, Pin
import math
import utime

# The x-direction and y-direction of the joystick connected to pins 26 and 27 respectively.
adc_x_joystick = ADC(Pin(26))
adc_y_joystick = ADC(Pin(27))

# The switch pin is set to pin 16, PULL_UP means that the pin is normally at 1 and when pressed will be at 0
sw_joystick = Pin(16, Pin.IN, Pin.PULL_UP)

# Initializing the Pulse Width Modulation pins that will be used to control the position of the servo motor
servo_x = PWM(Pin(0), freq=50) #Servo for X-direction
servo_y = PWM(Pin(2), freq=50) #Servo for Y-direction
servo_switch = PWM(Pin(1), freq = 50) #Servo for switch

# This function will map the ADC value for the joystick to a value between -100 and 100 for ease of viewing (creating a slope between two points (m) and then creating a line y = mx + b)
# joystick_position = value from ADC (VRx)
# joystick_min = Move the joystick and see what the value is all the way left
# joystick_max = Move the joystick and see what the value is all the way right
# desired_min = -100 or 100 (depending on which direction of the joystick you want to be top or bottom)
# desired_max = 100 or -100 (^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^)
def get_joystick_value(joystick_position, joystick_min, joystick_max, desired_min, desired_max):
    m = ((desired_min - desired_max)/(joystick_min - joystick_max))
    return int((m*joystick_position) - (m*joystick_max) + desired_max)

# This function will take the value from the joystick (between -100 and 100) and then convert it to a duty cycle to be used to control the servo motor (for my servos: 0.5 ms = 0 degrees,  2.5 ms = 180 degrees, and the period of the wave is normally 20 ms [1/freq = 1/50 = 0.02 sec])
def get_servo_duty_cycle(joystick_value, min_angle_ms, max_angle_ms, period_ms, desired_min, desired_max):
    point_1_x = desired_min
    point_1_y = (min_angle_ms/period_ms)*65536
    point_2_x = desired_max
    point_2_y = (max_angle_ms/period_ms)*65535
    m = (point_2_y - point_1_y) / (point_2_x - point_1_x)
    return int((m*joystick_value) - (m*desired_min) + point_1_y)
    
# In this while loop, we will continually read the status (position) of the x direction and switch, the value shown for x will be between 0 and 65535, as the 65535 is the maximum number that can be represented with an unsigned 16 bit integer
# however, we will be representing this number in terms of -100 to 100 in order to read the value more clearly, -100 will represent the servo -90 degrees and 100 will represent the servo +90 degrees
while True:
    # Read X and Y joystick positions as well as whether switch is pressed.
    x_position = adc_x_joystick.read_u16()
    y_position = adc_y_joystick.read_u16()
    sw_status = sw_joystick.value()        
    
    # This will map the position of the joystick's X and Y directions from -100 to 100
    x_value = get_joystick_value(x_position, 416, 65535, -100, 100)
    y_value = get_joystick_value(y_position, 416, 65535, -100, 100
                                 )
    # This portion will find the maximum length of values (from -100 to 100) and then if we are close to 0 (meaning the joystick is in the middle), the values will be set to 0 to remove any jittering or noise
    range_of_values=math.sqrt(x_value**2)
    range_of_values=math.sqrt(y_value**2)
    # Increase or decrease from 8 to get the joystick to read 0 at the middle position
    if range_of_values<=8:
        x_value=0
        
    # This will take the function from above and use it
    x_duty = get_servo_duty_cycle(x_value, 0.5, 2.5, 20, -100, 100)
    y_duty = get_servo_duty_cycle(y_value, 0.5, 2.5, 20, -100, 100)
    # This portion will get the value from the switch and will set it to the max value if the switch is pressed in (think of the claw opening if the switch is pressed) ... for this we just need to use the maximum angle for the servo (180) but represented in terms of ms (2.5 ms for my servo) and the period of the wave is 20 ms
    if sw_status == 0:
        sw_duty = int((2.5*65535)/20)
    else:
        sw_duty = int((0.5*65535)/20)
    
    # Now, update the servo motors
    servo_x.duty_u16(x_duty)
    servo_y.duty_u16(y_duty)
    servo_switch.duty_u16(sw_duty)
    
    # Finally, we print out the values so we can check what is happening as the code runs
    print(f"x_value is: {x_value},  x_duty is: {x_duty}, y_value is: {y_value}, y_duty is: {y_duty}, sw_status is: {sw_status}, sw_duty is: {sw_duty}")
    
    utime.sleep(0.1)