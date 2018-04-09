
# SNOWBOY SET UP
import snowboydecoder
import sys
import signal

# Demo code for listening two hotwords at the same time

interrupted = False

class SnowBoy(object):

    def __init__(self):
        pass
    
    def signal_handler(self, signal, frame):
        global interrupted
        interrupted = True

    def interrupt_callback(self):
        global interrupted
        return interrupted

    """
    if len(sys.argv) < 6:
    print("Error: need to specify 5 model names")
    print("Usage: python demo.py 1st.model 2nd.model ... 5.model")
    sys.exit(-1)
    
    
    # Array of all files passed...
    models = sys.argv[1:]
    """
    def listener(self):

        
        #self.models = ["Houston.pmdl", "RL.pmdl", "GL.pmdl", "BL.pmdl", "EL.pmdl", "SD.pmdl"]
        self.models = ["Houston.pmdl"]
        self.models.append("RL.pmdl")
        self.models.append("GL.pmdl")
        self.models.append("BL.pmdl")
        self.models.append("EL.pmdl")
        self.models.append("SD.pmdl")
        
        print("\n\nMODELS: {}\n\n".format(self.models));
        # capture SIGINT signal, e.g., Ctrl+C
        signal.signal(signal.SIGINT, self.signal_handler)
        
        self.sensitivity = [.5]*len(self.models)
        self.detector = snowboydecoder.HotwordDetector(self.models, sensitivity=self.sensitivity)

        # Lambda = N files in Command Line                                      #Feedback audio
        self.callbacks = [lambda: snowboydecoder.play_audio_file(snowboydecoder.DETECT_DING), # Houston
                          lambda: snowboydecoder.play_audio_file(snowboydecoder.DETECT_DONG), # R
                          lambda: snowboydecoder.play_audio_file(snowboydecoder.DETECT_DING), # G
                          lambda: snowboydecoder.play_audio_file(snowboydecoder.DETECT_DONG), # B
                          lambda: snowboydecoder.play_audio_file(snowboydecoder.DETECT_DONG), # E.L.
                          lambda: snowboydecoder.play_audio_file(snowboydecoder.DETECT_DONG)] # S.D.
                        
        
        
        # main loop
        # make sure you have the same numbers of callbacks and models
        self.detector.start(detected_callback=self.callbacks,
                            interrupt_check=self.interrupt_callback,
                            sleep_time=0.03)
        
        self.detector.terminate()

        #Done
    #End of class
