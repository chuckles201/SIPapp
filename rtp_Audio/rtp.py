# Audio file
# .mp3 compressed audio
# .flac compressed unloss
# .wav uncompressed (raw)


# wave module built-in
import wave
import matplotlib.pyplot as plt
import numpy as np

'''
Num channels: audio from diff directions
Sample width: bytes per sample
Framerate/freq: samples per sec
num frames: total num frames (samples)
frame values

'''
obj = wave.open("rtp_Audio/audio/char.wav",'rb')


print("Number channels: ",obj.getnchannels())
print("Sample-Width :", obj.getsampwidth() )
print("Frame Rate: ", obj.getframerate())
print("Length: ", obj.getnframes()/obj.getframerate())
print("Num frames: ",obj.getnframes())
print("*Parameters: ",obj.getparams())


# Getting raw-frames!
# 2bytes for left channel, 2 for right...
frames = obj.readframes(-1)

def bytes_to_int(byte_string):
    # for 2-byte sample-width
    # skip every other byte to plot
    return [int.from_bytes(byte_string[i:i+2],"little",signed=True) for i in range(0,len(byte_string),2)]

print("Raw-bytes:")
print("\n\n\n",len(frames),frames[0:4])

obj.close()

# now plot these
t_record = obj.getnframes()/obj.getframerate()
t = np.linspace(0,t_record,obj.getnframes())
fr = np.frombuffer(frames,np.int16)
plt.plot(t,bytes_to_int(frames))
plt.show()

# allows us to write to a new object!
obj_new = wave.open("rtp_Audio/audio/char_new.wav",'wb')

obj_new.setnchannels(1)
obj_new.setsampwidth(2)
obj_new.setframerate(44100)
obj_new.setnframes(288000)

obj_new.writeframes(frames)

obj_new.close()