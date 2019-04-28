project(minimal)

set(minimal_TYPESYSTEM
${CMAKE_CURRENT_SOURCE_DIR}/typesystem_minimal.xml
)

set(minimal_SRC
${CMAKE_CURRENT_BINARY_DIR}/minimal/minimal_module_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/minimal/obj_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/minimal/val_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/minimal/listuser_wrapper.cpp
${CMAKE_CURRENT_BINARY_DIR}/minimal/minbooluser_wrapper.cpp
)

configure_file("${CMAKE_CURRENT_SOURCE_DIR}/minimal-binding.txt.in"
               "${CMAKE_CURRENT_BINARY_DIR}/minimal-binding.txt" @ONLY)

add_custom_command(OUTPUT ${minimal_SRC}
COMMAND shiboken2 --project-file=${CMAKE_CURRENT_BINARY_DIR}/minimal-binding.txt ${GENERATOR_EXTRA_FLAGS}
DEPENDS ${minimal_TYPESYSTEM} ${CMAKE_CURRENT_SOURCE_DIR}/global.h shiboken2
WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
COMMENT "Running generator for 'minimal' test binding..."
)

include_directories(${CMAKE_CURRENT_SOURCE_DIR}
                    ${CMAKE_SOURCE_DIR}
                    ${SBK_PYTHON_INCLUDE_DIR}
                    ${libminimal_SOURCE_DIR}
                    ${libshiboken_SOURCE_DIR}
                    ${libshiboken_BINARY_DIR})
add_library(minimal MODULE ${minimal_SRC})
set_property(TARGET minimal PROPERTY PREFIX "")
set_property(TARGET minimal PROPERTY OUTPUT_NAME "minimal${PYTHON_EXTENSION_SUFFIX}")
if(WIN32)
    set_property(TARGET minimal PROPERTY SUFFIX ".pyd")
endif()
target_link_libraries(minimal
                      libminimal
                      ${SBK_PYTHON_LIBRARIES}
                      libshiboken)
