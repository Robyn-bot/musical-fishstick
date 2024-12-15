from math import *


class Transducer():
    def __init__(self, x, y, t_array):
        self.x = x #self just means this instance of the class; then the class method can be used multiple times
        self.y = y
        self.t_array = t_array
        self.signal = len(self.t_array) * [0]


class Receiver(Transducer):
    def __init__(self, x, y, t_array):
        super().__init__(x, y, t_array) #super(). gives access to methods and properties of a parent or sibling class


class Emitter(Transducer):
    def __init__(self, x, y, t_array):
        super().__init__(x, y, t_array)
        
    def generate_signal(self, f_c, n_cycles, amplitude):
        #time_difference is the time difference between consectuive time points in t_array
        time_difference = self.t_array[1] - self.t_array[0] #t_array is now a 1 dimensional list which contains discrete time points; calculating time step from the 2nd and 1st values of the list
        time_period = 1 / f_c #where f_c is the centre freq. of the sinusoid
        total_time = n_cycles * time_period
        #a sample is a discrete (amplitude) measurement of a signal at a specific point in time
        number_of_samples = int(total_time / time_difference)
        self.signal = [0] * len(self.t_array) #creates a list 'signal' that has as many 0s as there are time points in self.t_array; is now prepared to store the amplitudes of the generated sinusoid signal
        for i in range(number_of_samples):
            t = self.t_array[i] #allows the code to access an individual time point
             #in the form of a sine function, Asin(Bx+C)+D
            self.signal[i] = amplitude * sin(2 * pi* f_c * t)#f_c*t is the number of cycles that have occured up to that specific point in time; and *2π to convert freq. to radians; so the whole argument inside the sine function is the angle of how far along the sine wave you are a specific time t
        return self.signal
    

class SoundSimulator(): #not inheriting from Transducer class since this is managing emitters and receivers for sound simulation, not the transduction of the sound itself anymore
    def __init__(self, emitters, receivers, t_array, sos):
        self.emitters = emitters
        self.receivers = receivers
        self.t_array = t_array
        self.sos = sos
        self.signal = len(self.t_array) * [0] #needed to initialise signal attribute in this class as well
              
    def run(self):
        for receiver in self.receivers:
            receiver.signal = [0] * len(self.t_array) #creates a list that has as many 0s as time points defined by t_array: each element is now prepared to a receiver (which calculates the sound captured from the emitters)
            for emitter in self.emitters:
                distance = sqrt((receiver.x - emitter.x) ** 2 + (receiver.y - emitter.y) ** 2) #pythagoras of coordinates (x,y); distance between emitter and receiever
                time_delay = distance / self.sos #the delay caused by the sound having to travel a distance to reach the receiver
                for i in range(len(self.t_array)):
                    time_point = self.t_array[i] #iterating through the list of time points in t_array
                    if time_point >= time_delay: #checking if the current time in the loop is greater than or equal to the time delay it takes for the sound to reach, then will update the next time point that is greater
                        time_index = int((time_point - time_delay) / (self.t_array[1] - self.t_array[0])) #represents the point in time when the sound wave from the emitter arrives at the receiver
                        receiver.signal[i] += emitter.signal[time_index] / distance #updating receiver.signal list with the actual sound captured there; sound amplitude is decreasing with 1/distance relationship
        return self.receivers


class BeamFormer():
    def __init__(self, receivers, x_array, y_array, t_array, sos):
        self.receivers = receivers
        self.x_array = x_array
        self.y_array = y_array
        self.t_array = t_array
        self.sos = sos
        #field is a list within a list within a list, as this allows the 3 dimensions to communicate with each other
        self.field = [[[0.0 for t in range(len(self.t_array))] for x in range(len(self.x_array))] for y in range(len(self.y_array))] #each element within self.field[y][x][t] corresponds to the accoustic source strength q(r,t) at a specific spatial and temporal point

    def generate_field(self):
        N = len(self.receivers)                       
        for i in range(len(self.y_array)):
            for j in range(len(self.x_array)):
                for k in range(len(self.t_array)):
                    a_s_s = 0.0 #acoustic source strength has default value of 0.0
                    closest_receiver = min(self.receivers, key = lambda receiver: sqrt((receiver.y - self.y_array[i]) ** 2 + (receiver.x - self.x_array[j]) ** 2)) #min() returns the smallest element from the iterable self.receivers; using 'lambda' to create a small, inline function of using each receiver's distance, and receiver is the argument passed into this lambda function; 'key' allows the function to be performed on each element before the outside (sorting min()) function
                    minimum_distance = sqrt((closest_receiver.y - self.y_array[i]) ** 2 + (closest_receiver.x - self.x_array[j]) ** 2) #finding the distance from the closest receiver to the reconstructed acoustic source
                    minimum_time_delay = minimum_distance / self.sos
                    minimum_time_delay_index = minimum_time_delay / (self.t_array[1] - self.t_array[0]) #same as time delay below, but a time_delay_index only for the closest receiver
                    for receiver in self.receivers:
                        #r_i-r = distance between receiver and the acoustic source (which is specified by x_ and y_ array)
                        distance = sqrt((receiver.y - self.y_array[i]) ** 2 + (receiver.x - self.x_array[j]) ** 2) #self.x_ and y_array[i] is iterating through the list of spatial points like with time_point before
                        time_delay = distance / self.sos
                        time_delay_index = time_delay / (self.t_array[1] - self.t_array[0]) #relates the time delay to the discrete time steps in t_array: shows the position in t-array where the time delay occurs for a given receiver's distance from the source
                        relative_time_delay = int(time_delay_index - minimum_time_delay_index) #using the indexes instead of the delays themselves to specify where in t_array the relative time delay is calculating from
                        if k + relative_time_delay < len(receiver.signal): #ensuring that the list index is not out of range when reaching for the signals captured at each of the receivers
                            #implementing the accoustic source strength equation
                            a_s_s += distance * receiver.signal[k + relative_time_delay] #updating a_s_s list with the actual sound captured there
                        else: #for out of bound values of source strength
                            a_s_s += 0 #assume that signal amplitude is 0
                    self.field[i][j][k] = a_s_s * (1 / N) #assigning acoustic source strength to the field   