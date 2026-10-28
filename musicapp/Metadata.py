def getmetadata(filename):
    import librosa
    import numpy as np

    y, sr = librosa.load(filename)

    # fetching tempo
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)
    tempo_val = float(tempo[0]) if hasattr(tempo, '__iter__') else float(tempo)

    # fetching beats
    y_harmonic, y_percussive = librosa.effects.hpss(y)
    tempo_track, beat_frames = librosa.beat.beat_track(y=y_percussive, sr=sr)

    # chroma_stft
    chroma_stft = librosa.feature.chroma_stft(y=y, sr=sr)

    # rmse
    rmse = librosa.feature.rms(y=y)

    # fetching spectral centroid
    spec_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]

    # spectral bandwidth
    spec_bw = librosa.feature.spectral_bandwidth(y=y, sr=sr)

    # fetching spectral rolloff
    spec_rolloff = librosa.feature.spectral_rolloff(y=y+0.01, sr=sr)[0]

    # zero crossing rate
    zero_crossing = librosa.feature.zero_crossing_rate(y)

    # mfcc
    mfcc = librosa.feature.mfcc(y=y, sr=sr)

    # metadata dictionary
    metadata_dict = {
        'tempo': tempo_val,
        'chroma_stft': float(np.mean(chroma_stft)),
        'rmse': float(np.mean(rmse)),
        'spectral_centroid': float(np.mean(spec_centroid)),
        'spectral_bandwidth': float(np.mean(spec_bw)),
        'rolloff': float(np.mean(spec_rolloff)),
        'zero_crossing_rates': float(np.mean(zero_crossing)),
    }

    for i in range(1, 21):
        metadata_dict['mfcc' + str(i)] = float(np.mean(mfcc[i - 1]))

    return list(metadata_dict.values())
