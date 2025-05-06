import pyaudio
import soxr
import threading
import numpy as np


'''Test to write and read from audio 
with different threads, and handle rate-mismatch!'''


p = pyaudio.PyAudio()

output_stream = p.open(
            input_device_index=1,
            output=True,input=False,
            rate=44100,
            channels=2,
            frames_per_buffer = 1024,
            format=pyaudio.paInt16)

input_stream = p.open(
            input_device_index=0,
            output=False,input=True,
            rate=16000,
            channels=1,
            frames_per_buffer = 1024,
            format=pyaudio.paInt16)
duration = 5

# n seconds = (frame_rate / chunk) * n
def convert_channels(c_in,c_out,np_array):
    if c_in == c_out:
        return np_array
    else:
        if c_in == 2 and c_out == 1:
            n = len(np_array)
            data = np.reshape(np_array,[n//4,2,2])
            return data.mean(1) # get right axis!
        
        elif c_out == 2 and c_in == 1:
            # mono to stereo
            # N, --> (N,2), then formatted byte-wise!
            return np.stack([np_array,np_array],axis=-1)
def read_audio():
    for i in range(int((16000/1024)*5)):
        # convert to ints, reconvert to bytes
        data = input_stream.read(1024)
        data = np.frombuffer(data,dtype=np.int16)
        data_write = soxr.resample(data,16000,44100)
        data_write = convert_channels(1,2,data_write)
        output_stream.write(data_write.tobytes())
    return 0


# converting mono--> stereo, vice-versa


succ = read_audio()






################################################
# testing...
# import wave

# new_obj = wave.open("pyaudio_test.wav",'wb')

# with wave.open('rtp_Audio/audio/test_record.wav','wb') as wf:
#     wf.setnchannels(1)
#     wf.setsampwidth(2)
#     wf.setframerate(16000)
#     wf.setnframes(16000*5)

#     wf.writeframes(frames)

# output_stream.stop_stream()
# output_stream.close()
# input_stream.stop_stream()
# input_stream.close()
# p.terminate()