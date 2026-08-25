# Application source files
target_sources(${CMAKE_PROJECT_NAME} PRIVATE

    # Libraries
    ${CMAKE_SOURCE_DIR}/App/Libraries/cli/src/FreeRTOS_CLI.c

    # Modules
    # ${CMAKE_SOURCE_DIR}/App/Modules/foo/src/foo.c
)

# Application include directories
target_include_directories(${CMAKE_PROJECT_NAME} PRIVATE

    # Libraries
    ${CMAKE_SOURCE_DIR}/App/Libraries/cli/include

    # Modules
    # ${CMAKE_SOURCE_DIR}/App/Modules/foo/include
)