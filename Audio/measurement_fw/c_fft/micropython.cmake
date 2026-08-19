# CMake fragment for MicroPython USER_C_MODULES (rp2 / Pico2).
#
# Build from micropython tree:
#   make -C ports/rp2 BOARD=RPI_PICO2 \
#     USER_C_MODULES=/abs/path/to/measurement_fw/c_fft/micropython.cmake

add_library(usermod_fft_q15 INTERFACE)

target_sources(usermod_fft_q15 INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}/fft_q15.c
    ${CMAKE_CURRENT_LIST_DIR}/modfft_q15.c
)

target_include_directories(usermod_fft_q15 INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}
)

target_link_libraries(usermod INTERFACE usermod_fft_q15)
