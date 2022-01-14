import pvporcupine, pvrhino
from pvrecorder import PvRecorder
from datetime import datetime
from flask import Flask

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
        while (datetime.now()-t1).seconds <= 1:
            if answer == "false":
                pcm = recorder.read()
                result = porcupine.process(pcm)
                if result >= 0:
                    answer = "true"
                    print('[%s] Detected %s' % (str(datetime.now()), keywords[result]))
            else:
                break
        print((datetime.now()-t1).seconds)
    except KeyboardInterrupt:
        print('Stopping ...')
    finally:
        if porcupine is not None:
            porcupine.delete()

        if recorder is not None:
            recorder.delete()

    return {'answer' : answer}

@app.route('/detect-command', methods=['GET'])
def detectCommand():
    access_key = "HcTsHA/u+gcelwsLYGu/+GuxyEMmKyptCtykh+7oxDCKmK6me8jIyg=="

    rhino = None
    recorder = None
    answer_intent = ''
    answer_slot = ''

    try:
        rhino = pvrhino.create(
            access_key= access_key,
            context_path='/Users/pierbale/Documents/Github/WakeUpWordService/dectectioncommand_mac_v2.0.0/DectectionCommand_en_mac_v2_0_0.rhn')

        recorder = PvRecorder(device_index=-1, frame_length=rhino.frame_length)
        recorder.start()

        print(f"Using device: {recorder.selected_device}")
        print("Listening...")
        print()

        t1 = datetime.now()
        while True:
            pcm = recorder.read()

            is_finalized = rhino.process(pcm)
            if is_finalized:
                inference = rhino.get_inference()
                if inference.is_understood:
                    answer_intent = inference.intent
                    for slot, value in inference.slots.items():
                        answer_slot = answer_slot + " " + value
                    break

    except KeyboardInterrupt:
        print('Stopping ...')

    finally:
        if recorder is not None:
            recorder.delete()

        if rhino is not None:
            rhino.delete()

    return {'answer_intent':answer_intent, 'answer-slot':answer_slot}

if __name__ == '__main__':
    # run app in debug mode on port 5001
    app.run(debug=True, port=5002)