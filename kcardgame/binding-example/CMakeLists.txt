project(kcardgame)
cmake_minimum_required(VERSION 3.12)
cmake_policy(VERSION 3.12)

find_package(ECM 5 REQUIRED CONFIG)
find_package(Qt5 COMPONENTS Core REQUIRED)

get_target_property(QtCore_location Qt5::Core LOCATION)
get_filename_component(QtCore_libdir ${QtCore_location} DIRECTORY)

set(CMAKE_AUTOMOC ON)

project(Shiboken2-Qt-Example)

set(CMAKE_CXX_STANDARD 11)
set(sample_library "libexamplebinding")
set(bindings_library "Shiboken2QtExample")
set(wrapped_header ${CMAKE_SOURCE_DIR}/bindings.h)
set(typesystem_file ${CMAKE_SOURCE_DIR}/bindings.xml)
set(generated_sources
    ${CMAKE_CURRENT_BINARY_DIR}/${bindings_library}/qobjectwithenum_wrapper.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/${bindings_library}/shiboken2qtexample_module_wrapper.cpp)

find_package(Python3 REQUIRED COMPONENTS Interpreter Development)

if(NOT python_interpreter)
    find_program(python_interpreter "python33")
endif()

set(PYSIDE2_DIR ${Python3_SITELIB}/PySide2)

macro(pyside2_config option output_var)
    if(${ARGC} GREATER 2)
        set(is_list ${ARGV2})
    else()
        set(is_list "")
    endif()

    execute_process(
      COMMAND ${python_interpreter} "${PYSIDE2_DIR}/examples/utils/pyside2_config.py"
		${option}
      OUTPUT_VARIABLE ${output_var}
      OUTPUT_STRIP_TRAILING_WHITESPACE)

    if ("${${output_var}}" STREQUAL "")
        message(FATAL_ERROR "Error: Calling pyside2_config.py ${option} returned no output.")
    endif()
    if(is_list)
        string (REPLACE " " ";" ${output_var} "${${output_var}}")
    endif()
endmacro()

if ()
pyside2_config(--shiboken2-module-path shiboken2_module_path)
pyside2_config(--shiboken2-generator-path shiboken2_generator_path)
pyside2_config(--python-include-path python_include_dir)
pyside2_config(--shiboken2-generator-include-path shiboken_include_dir 1)
pyside2_config(--shiboken2-module-shared-libraries-cmake shiboken_shared_libraries 0)
pyside2_config(--pyside2-shared-libraries-cmake pyside2_link 0)
endif()
set(shiboken_path "/usr/bin/shiboken2${CMAKE_EXECUTABLE_SUFFIX}")
if(NOT EXISTS ${shiboken_path})
    message(FATAL_ERROR "Shiboken executable not found at path: ${shiboken_path}")
endif()

set(CMAKE_SKIP_BUILD_RPATH FALSE)
set(CMAKE_BUILD_WITH_INSTALL_RPATH TRUE)
set(CMAKE_INSTALL_RPATH ${shiboken2_module_path} ${CMAKE_CURRENT_SOURCE_DIR} ${QtCore_libdir})
set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)

set(${sample_library}_sources qobjectwithenum.cpp)
add_library(${sample_library} SHARED ${${sample_library}_sources})
target_link_libraries(${sample_library} Qt5::Core)
set_property(TARGET ${sample_library} PROPERTY PREFIX "")

get_target_property(qtcore_lib_includes Qt5::Core INTERFACE_INCLUDE_DIRECTORIES)
list(JOIN qtcore_lib_includes ";-I" lib_includes)
set(lib_includes "-I${lib_includes}")

target_compile_definitions(${sample_library} PRIVATE BINDINGS_BUILD)


set(shiboken_options --generator-set=shiboken --enable-parent-ctor-heuristic
    --enable-return-value-heuristic --use-isnull-as-nb_nonzero
    --avoid-protected-hack
    --enable-pyside-extensions
    ${lib_includes}
    -I${CMAKE_SOURCE_DIR}
    -T${CMAKE_SOURCE_DIR}
    -T${PYSIDE2_DIR}/typesystems/
    --output-directory=${CMAKE_CURRENT_BINARY_DIR}
    )

set(generated_sources_dependencies ${wrapped_header} ${typesystem_file})

add_custom_command(OUTPUT ${generated_sources}
                    COMMAND ${shiboken_path}
                    ${shiboken_options} ${wrapped_header} ${typesystem_file}
                    DEPENDS ${generated_sources_dependencies}
                    IMPLICIT_DEPENDS CXX ${wrapped_header}
                    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
                    COMMENT "Running generator for ${typesystem_file}.")

set(${bindings_library}_sources ${generated_sources})

add_library(${bindings_library} MODULE ${${bindings_library}_sources})

target_include_directories(${bindings_library} PRIVATE ${python_include_dir})
target_include_directories(${bindings_library} PRIVATE ${PYSIDE2_DIR}/include/)
target_include_directories(${bindings_library} PRIVATE ${PYSIDE2_DIR}/include/QtCore)
target_include_directories(${bindings_library} PRIVATE ${shiboken_include_dir})
target_include_directories(${bindings_library} PRIVATE ${CMAKE_SOURCE_DIR})

target_link_libraries(${bindings_library} PRIVATE ${shiboken_shared_libraries})
target_link_libraries(${bindings_library} PRIVATE ${sample_library})
target_link_libraries(${bindings_library} PRIVATE ${pyside2_link})

set_property(TARGET ${bindings_library} PROPERTY PREFIX "")
set_property(TARGET ${bindings_library} PROPERTY OUTPUT_NAME
             "${bindings_library}${PYTHON_EXTENSION_SUFFIX}")

install(TARGETS ${bindings_library} ${sample_library}
        LIBRARY DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}
        RUNTIME DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}
        )
