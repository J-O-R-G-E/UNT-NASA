
# SNOWBOY SET UP
import snowboydecoder
import sys
import signal

# Demo code for listening two hotwords at the same time

interrupted = False

def signal_handler(signal, frame):
    global interrupted
    interrupted = True

def interrupt_callback():
    global interrupted
    return interrupted

if len(sys.argv) < 6:
    print("Error: need to specify 5 model names")
    print("Usage: python demo.py 1st.model 2nd.model ... 5.model")
    sys.exit(-1)


# Array of all files passed...
models = sys.argv[1:]

# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

sensitivity = [.5]*len(models)
detector = snowboydecoder.HotwordDetector(models, sensitivity=sensitivity)

# Lambda = N files in Command Line
callbacks = [lambda: snowboydecoder.play_audio_file(snowboydecoder.DETECT_DING), # Houston
             lambda: snowboydecoder.play_audio_file(snowboydecoder.DETECT_DONG), # R
             lambda: snowboydecoder.play_audio_file(snowboydecoder.DETECT_DING), # G
             lambda: snowboydecoder.play_audio_file(snowboydecoder.DETECT_DONG), # B
             lambda: snowboydecoder.play_audio_file(snowboydecoder.DETECT_DONG), # E.L.
             lambda: snowboydecoder.play_audio_file(snowboydecoder.DETECT_DONG)] # S.D.

# main loop
# make sure you have the same numbers of callbacks and models
detector.start(detected_callback=callbacks,
               interrupt_check=interrupt_callback,
               sleep_time=0.03)

detector.terminate()
