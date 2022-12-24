import os
import time
import datetime
import tempfile
from SrtFile import *
import moviepy.editor as mp
from threading import Thread
from pydub import AudioSegment
import speech_recognition as sr
from googletrans import Translator
from pydub.silence import split_on_silence, detect_nonsilent

lang_src_list = ["ja", "en", "ru", "de", "ar", "fr", "ko", "la", "es", "tr", "it", "hu", "id", "nl", "zh", "pt", "fil",
                 "hi"]
lang_des_list = ["en", "ar", "ja", "de", "fr", "ko", "la", "es", "tr", "it", "hu", "id", "nl", "zh", "pt", "fil", "hi"]


def get_smh(sec):
    return str(datetime.timedelta(seconds=sec))


def get_best_res(actual_result):
    if "confidence" in actual_result["alternative"]:
        # return alternative with highest confidence score
        best_hypothesis = max(actual_result["alternative"], key=lambda alternative: alternative["confidence"])
    else:
        # when there is no confidence available, we arbitrarily choose the first hypothesis.
        best_hypothesis = actual_result["alternative"][0]
    if "transcript" not in best_hypothesis:
        return ""
    return best_hypothesis["transcript"]


class VoiceRegTra(object):

    def __init__(self, path, lang_src="ja", lang_des="ja", logger=True, mode=1, base=15, base_2=5):
        self.start = 0
        self.path = path
        try:
            self.audio = mp.VideoFileClip(path).audio.copy()
        except Exception as e:
            if logger:
                print(e)
            self.audio = None
            return
        self.dur = self.audio.duration
        self.recognizer = sr.Recognizer()
        self.translator = Translator()
        self.tmppath = tempfile.gettempdirb().decode()
        self.lang_src = lang_src
        self.lang_des = lang_des
        self.switch = True
        self.base = base
        self.base_2 = base_2
        self.lastsec = 0
        self.lastsec_2 = 0
        self.thread_list = []
        self.thread_list_2 = []
        self.thread_pos = 0
        self.thread_pos_2 = 0
        self.splite_history = []
        self.splite_history_2 = []
        self.min_silence_len = 500
        self.silence_thresh = 10
        self.keep_silence = 500
        self.mode = mode
        self.srtfile = SrtFile(self.path)
        self.srtfile_2 = SrtFile(self.path)
        self.logger = logger

    def set_all_subs_2(self, i=0, dur=None):
        if not dur:
            dur = self.dur
        start = self.start
        len = self.base_2
        name = f"tmp_thread_2_{i}.wav"
        tmpname = f"{self.tmppath}\\{name}"
        thread_pos = self.thread_pos

        while self.thread_list[thread_pos].switch and start + len < dur:
            self.lastsec_2 = start
            if self.splite_audio_save_tmp(start, start + len, name=tmpname, mode=2):
                self.set_text_from_audio_2(tmpname, start)
            if start + len + 1 < dur:
                start += len
            else:
                self.thread_list[thread_pos].switch = False

    def set_text_from_audio_2(self, path, audiostart):
        try:
            chunk_filename = path
            with sr.AudioFile(chunk_filename) as source:
                audio_listened = self.recognizer.record(source)
                text = ""
                try:
                    text = self.recognizer.recognize_google(audio_listened, language=self.lang_src, show_all=True)
                    if len(text) > 0:
                        text = get_best_res(text)
                except sr.UnknownValueError as e:
                    pass
            if len(text) > 0:
                transleted = self.get_translated(text)
                self.srtfile_2.addsub(audiostart * 1000, audiostart * 1000 + self.base_2 * 1000, transleted, text)
                if self.logger:
                    print(get_smh(audiostart), text, transleted)

        except Exception as e:
            if self.logger:
                print(e, audiostart)

    def reset_translate(self):

        def reset_translate():
            print("Started Translating")
            if self.mode == 1:
                for sub in self.srtfile.allsubs:
                    sub.content = self.get_translated(sub.orgtext)
            else:
                for sub in self.srtfile_2.allsubs:
                    sub.content = self.get_translated(sub.orgtext)
            print("Ended Translating")

        Thread(target=reset_translate).start()

    def reset(self, start):
        self.splite_history.clear()
        self.splite_history_2.clear()
        self.srtfile_2.clear()
        self.srtfile.clear()
        self.startall(start)

    def setbase(self, base):
        self.base = base
        self.stopall()

    def setbase_2(self, base):
        self.base_2 = base
        self.stopall()

    def set_lang_src(self, lang_src):
        self.lang_src = lang_src

    def set_lang_des(self, lang_des):
        self.lang_des = lang_des

    def splite_audio_save_tmp(self, start, end, name="tmp.wav", mode=1):
        if start > end:
            return False
        tup = (start, end)
        if mode == 1:
            if tup in self.splite_history:
                return False
            else:
                self.splite_history.append(tup)
        elif mode == 2:
            if tup in self.splite_history_2:
                return False
            else:
                self.splite_history_2.append(tup)

        try:
            newau = self.audio.subclip(start, end)
            newau.write_audiofile(name, logger=None)
            return True
        except Exception as e:
            if self.logger:
                print("failed to splite", e, start, end, )
            return False

    def get_translated(self, text):
        try:
            transleted = self.translator.translate(text, src=self.lang_src, dest=self.lang_des).text
            return transleted
        except Exception as e:
            if self.logger:
                print(e, text)
            return text

    def myround(self, x, base=5):

        if round(x / base) != 0:
            return (base * round(x / base)) - base
        else:
            return (base * round(x / base))

    def set_text_from_audio(self, path, audiostart, thread_pos):
        try:
            sound = AudioSegment.from_wav(path)

            min_silence_len = self.min_silence_len
            silence_thresh = sound.dBFS - self.silence_thresh
            keep_silence = self.keep_silence
            chunks = split_on_silence(sound,
                                      # experiment with this value for your target audio file
                                      min_silence_len=min_silence_len,
                                      # adjust this per requirement
                                      silence_thresh=silence_thresh,
                                      # keep the silence for 1 second, adjustable as well
                                      keep_silence=keep_silence,
                                      )
            chunks_pos = detect_nonsilent(sound, min_silence_len=min_silence_len, silence_thresh=silence_thresh)

            folder_name = "audio-chunks_mode_2"
            folder_name = f"{self.tmppath}\\{folder_name}"
            # # create a directory to store the audio chunks
            if not os.path.isdir(folder_name):
                os.mkdir(folder_name)

            for i, audio_chunk in enumerate(chunks):
                if not self.thread_list[thread_pos].switch:
                    return 0
                realstart = chunks_pos[i][0] + audiostart * 1000
                realend = chunks_pos[i][1] + audiostart * 1000
                if realend - realstart < 400:
                    # print("skip",realend-realstart)
                    continue

                if chunks_pos[i][1] - chunks_pos[i][0] < 5000:
                    if chunks_pos[i][1] / 1000 == sound.duration_seconds:
                        return int(chunks_pos[-1][0] / 1000)

                chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
                audio_chunk.export(chunk_filename, format="wav")
                # recognize the chunk
                with sr.AudioFile(chunk_filename) as source:
                    audio_listened = self.recognizer.record(source)
                    # try converting it to text
                    try:
                        text = self.recognizer.recognize_google(audio_listened, language=self.lang_src, show_all=True)
                        if len(text) > 0:
                            text = get_best_res(text)
                            if text != "":
                                transleted = self.get_translated(text)
                                self.srtfile.addsub(realstart, realend, transleted, text)
                                if self.logger:
                                    print(get_smh(int(chunks_pos[i][0] / 1000) + audiostart), text, transleted)
                        else:
                            # print("not skiped", realend - realstart)
                            pass
                    except sr.UnknownValueError as e:
                        pass

            if len(chunks_pos) > 0:
                if chunks_pos[-1][1] - chunks_pos[-1][0] < 5000:
                    if chunks_pos[-1][1] / 1000 == sound.duration_seconds:
                        return int(chunks_pos[-1][0] / 1000)
            return 0
        except Exception as e:
            if self.logger:
                print(e, audiostart)
            return 0

    def set_all_subs(self, i=0, dur=None):
        if not dur:
            dur = self.dur
        len = self.base
        start = self.start
        end = start + len
        thread_pos = self.thread_pos
        name = f"tmp_thread_{i}.wav"
        tmpname = f"{self.tmppath}\\{name}"
        while self.thread_list[thread_pos].switch and self.switch and end <= dur:
            self.lastsec = start
            if self.splite_audio_save_tmp(start, end, name=tmpname):
                lastchunkpos = self.set_text_from_audio(tmpname, start, thread_pos)
                if lastchunkpos != 0:
                    end = end + len
                    start = start + lastchunkpos
                elif start + len + 1 < dur:
                    start = end
                    end = start + len
                    if end > dur:
                        end = dur
            elif start + len < dur:
                start = end
                end = start + len
                if end > dur:
                    end = dur
            else:
                self.thread_list[thread_pos].switch = False

    def get_sub(self, msec):
        if self.mode == 1:
            return self.srtfile.get_at(msec)
        elif self.mode == 2:
            return self.srtfile_2.get_at(msec)

    def get_srt_file(self):
        if self.mode == 1:
            new = self.srtfile
            return new
        elif self.mode == 2:
            new = self.srtfile_2
            return new

    def stopall(self):
        if len(self.thread_list) > 0:
            self.thread_list[self.thread_pos].switch = False

    def setmode(self, mode):

        if self.mode != mode:
            self.mode = mode

    def startall(self, start, i=0, dur=None):
        if len(self.thread_list) > 0:
            self.thread_list[self.thread_pos].switch = False
            self.thread_pos += 1

        if self.mode == 1:
            self.start = self.myround(start, self.base)
            thread = Thread(target=self.set_all_subs, args=(i, dur))

        else:
            self.start = self.myround(start, self.base_2)
            thread = Thread(target=self.set_all_subs_2, args=(i, dur))

        thread.switch = True
        self.thread_list.append(thread)
        thread.start()

    def getlastsec(self):
        if self.mode == 1:
            return self.lastsec
        if self.mode == 2:
            return self.lastsec_2

    def savesrt(self):
        if self.mode == 1:
            self.srtfile.save()
        else:
            self.srtfile_2.save()


def multithread_translate(path, lang_src="en", lang_des="ar", mode=1, files=[], switch=[], num=10, base=30, base_2=5,
                          silence_thresh=8, min_silence_len=500):
    def inthread():
        start_time = time.time()
        wholedur = 0
        print(f"Multithread Translate {mode}: Started", " lang_src : ", lang_src, " lang_des : ", lang_des)
        for i in range(num):
            if switch[0]:
                voic = VoiceRegTra(path, lang_src=lang_src, lang_des=lang_des, logger=False, mode=mode, base=base,
                                     base_2=base_2)
                wholedur = voic.dur
                start = int(i * wholedur / num)
                end = int((i + 1) * wholedur / num)
                voic.dur = end
                voic.start = start
                voic.silence_thresh = silence_thresh
                voic.min_silence_len = min_silence_len
                voic.startall(start, i, end)
                files.append(voic)
        while True and switch[0]:
            cheecker = False
            lastsec = 0
            for file in files:
                cheecker = cheecker or file.thread_list[-1].is_alive()
                lastsec = (file.getlastsec() - file.start) + lastsec
            if not cheecker:
                break
            procent_new = round((lastsec / wholedur) * 100, 2)
            log = f"{(procent_new if procent_new < 100 else 100)} % / {get_smh(round(time.time() - start_time))} Sec"
            print(log, end="\r", flush=True)
            time.sleep(1)

        if switch[0]:
            srtfile = SrtFile(path)
            for file in files:
                srtfile.allsubs += file.get_srt_file().allsubs
            srtfile.save()
            switch[0] = False
            print(f"Multithread Translate {mode}: Finished")
        else:
            for file in files:
                file.stopall()
                file.srtfile.clear()
            files.clear()
            print(f"Multithread Translate {mode}: Stopped")

    thread = Thread(target=inthread)
    thread.start()
