import time
import ryRecog06_eng as ry
import numpy as np
from queue import Queue
import matplotlib.pyplot as pl
import sounddevice as sd

CHANNEL         = 1
sampleRate      = 16000 # SamplePerSec
SamplePerFrame  = 1000

BufferSize      = 160   # 16000 / 1000 * 10 s
Buffer          = (1e-10) * np.random.random((BufferSize, SamplePerFrame, CHANNEL))
Frame_index     = 0

recogQ      = Queue(100)

def sdStream():
    aStream= sd.Stream(callback   = input_to_buffer, 
                       channels   = CHANNEL,       
                       samplerate = sampleRate,  
                       blocksize  = SamplePerFrame #1000 sample/frame
                       )
    return aStream

def input_to_buffer(input_data, output_data, frames, time, status):
    global Frame_index, Buffer

    if status:
        print(status)
        
    Buffer[Frame_index % BufferSize] = input_data       
    Frame_index += 1
    
def Get1secSpeech():
    global Buffer, BufferSize, Frame_index
    
    x  = Buffer
    t1 = (Frame_index % BufferSize)
    x  = np.vstack((x[t1:], x[0:t1]))
    x  = x.flatten()    
    x  = x.astype(np.float32) 
    x  = x[-16000:]    
    print('.', end='', flush=True)
    
    return x

def recogQ_Get(q):
    return [q.get() for i in range(q.qsize())]


