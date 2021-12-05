import pvporcupine
from pvrecorder import PvRecorder
from datetime import datetime
from flask import Flask, request

# create the Flask app
app = Flask(__name__)

@app.route('/detect-word', methods=['GET'])
def detectWakeUpWord():
    access_key = "HcTsHA/u+gcelwsLYGu/+GuxyEMmKyptCtykh+7oxDCKmK6me8jIyg=="
    keywords = ['stop please']
    porcupine = None
    recorder = None
    answer = "false"
    try:
        porcupine = pvporcupine.create(
            access_key=access_key,
            keyword_paths=['/Users/pierbale/Documents/Github/WakeUpWordService/stop_please_mac_v2.0.0/stop-please_en_mac_v2_0_0.ppn'])

        recorder = PvRecorder(device_index=-1, frame_length=porcupine.frame_length)
        recorder.start()

        print('Listening {')

        t1 = datetime.now()
        while (datetime.now()-t1).seconds <= 2:
            pcm = recorder.read()
            result = porcupine.process(pcm)
            if result >= 0:
                answer = "true"
                print('[%s] Detected %s' % (str(datetime.now()), keywords[result]))
    except KeyboardInterrupt:
        print('Stopping ...')
    finally:
        if porcupine is not None:
            porcupine.delete()

        if recorder is not None:
            recorder.delete()

    return {'answer' : answer}

if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=True, port=5000)