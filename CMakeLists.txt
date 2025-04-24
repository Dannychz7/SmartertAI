cmake_minimum_required(VERSION 3.10)
project(VoiceListener)

set(CMAKE_CXX_STANDARD 17)

include_directories(${CMAKE_SOURCE_DIR}/vosk)
include_directories(/opt/homebrew/include) # adjust for PortAudio
link_directories(/opt/homebrew/lib)

add_executable(VoiceListener main.cpp)

target_link_libraries(VoiceListener 
    ${CMAKE_SOURCE_DIR}/vosk/libvosk.dylib 
    portaudio
)
