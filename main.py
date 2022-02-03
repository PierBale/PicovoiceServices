import pvporcupine
import pvrhino
import time
from datetime import datetime
from pvrecorder import PvRecorder
from flask import Flask

# create the Flask app
app = Flask(__name__)

@app.route('/detect-word', methods=['GET'])
def detectWakeUpWord():
    access_key = "ATTy/mq5rE0mATss7Zs6CMoxWVr1qHHZckyBtnjLORzPYqd3obccCA=="
    keywords = ['hey stop']
    porcupine = None
    recorder = None
    answer = "false"
    try:
        porcupine = pvporcupine.create(
            access_key=access_key,
            keyword_paths=['/Users/pierbale/Documents/Github/WakeUpWordService/hey_stop_mac_v2.1.0/hey-stop_en_mac_v2_1_0.ppn'])

        recorder = PvRecorder(device_index=0, frame_length=porcupine.frame_length)
        recorder.start()

        print('Listening {')

        while True:
            if answer == "false":
                pcm = recorder.read()
                result = porcupine.process(pcm)
                if result >= 0:
                    answer = "true"
                    print('[%s] Detected %s' % (str(datetime.now()), keywords[result]))
            else:
                break
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
    access_key = "ATTy/mq5rE0mATss7Zs6CMoxWVr1qHHZckyBtnjLORzPYqd3obccCA=="

    rhino = None
    recorder = None
    answer_intent = ''
    answer_slot = ''

    try:
        rhino = pvrhino.create(
            access_key=access_key,
            context_path='/Users/pierbale/Documents/Github/WakeUpWordService/detection_command/detection_command_easy-ibm-smart-2/Detection-Command_en_mac_v2_1_0.rhn')

        recorder = PvRecorder(device_index=-1, frame_length=rhino.frame_length)
        recorder.start()

        print(f"Using device: {recorder.selected_device}")
        print("Listening...")
        print()

        t_end = time.time() + 50
        while time.time() < t_end:
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
    # run app in debug mode on port 5002
    app.run(debug=True, port=5002)