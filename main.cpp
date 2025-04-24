#include <vosk_api.h>
#include <portaudio.h>
#include <iostream>
#include <string>
#include <cstring>

#define SAMPLE_RATE 16000
#define FRAMES_PER_BUFFER 512

VoskRecognizer *recognizer;

static int audio_callback(const void *inputBuffer, void *, unsigned long framesPerBuffer,
                          const PaStreamCallbackTimeInfo*, PaStreamCallbackFlags, void*) {
    if (recognizer && inputBuffer) {
        if (vosk_recognizer_accept_waveform(recognizer, inputBuffer, framesPerBuffer * sizeof(short))) {
            const char *result = vosk_recognizer_result(recognizer);
            std::string res(result);
            std::cout << "[RESULT]: " << res << std::endl;
            if (res.find("atlas") != std::string::npos || res.find("nova") != std::string::npos) {
                std::cout << "Wake word detected!" << std::endl;
            }
        } else {
            const char *partial = vosk_recognizer_partial_result(recognizer);
            std::string p(partial);
            std::cout << "[PARTIAL]: " << p << "\r";
        }
    }
    return paContinue;
}

int main() {
    const char *model_path = "model"; // Unzip vosk-model-small-en-us-0.15 to this directory
    Model *model = vosk_model_new(model_path);
    recognizer = vosk_recognizer_new(model, SAMPLE_RATE);

    Pa_Initialize();
    PaStream *stream;
    Pa_OpenDefaultStream(&stream, 1, 0, paInt16, SAMPLE_RATE,
                         FRAMES_PER_BUFFER, audio_callback, nullptr);
    Pa_StartStream(stream);

    std::cout << "Listening for 'atlas' or 'nova'..." << std::endl;
    std::cin.get();  // Wait for user to press Enter to exit

    Pa_StopStream(stream);
    Pa_CloseStream(stream);
    Pa_Terminate();

    vosk_recognizer_free(recognizer);
    vosk_model_free(model);
    return 0;
}
