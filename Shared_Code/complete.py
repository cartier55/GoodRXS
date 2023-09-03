import simpleaudio as sa


def complete_sound():
    wave_obj = sa.WaveObject.from_wave_file("complete_sound.wav")
    play_obj = wave_obj.play()
    play_obj.wait_done()
