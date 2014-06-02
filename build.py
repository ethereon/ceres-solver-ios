#!/usr/bin/env python

# Ceres iOS Build Script ~ Saumitro Dasgupta <saumitro@stanford.edu>

import os
import shutil
import subprocess as sp

# Source paths
BASE_PATH       = os.path.dirname(os.path.realpath(__file__))
P               = lambda x: os.path.join(BASE_PATH, x)
CERES_PATH      = P('ceres-solver')
EIGEN_PATH      = P('eigen-3.2.1')
BUILD_DIR       = P('build')
INSTALL_PATH    = P('dist')

# Toolchain paths
CMAKE_TC_PATH   = P('iOS-toolchain.cmake')
DEV_ROOT        = sp.check_output(['xcode-select' ,'--print-path']).strip()
XC_TC_ROOT      = os.path.join(DEV_ROOT, 'Toolchains/XcodeDefault.xctoolchain/')
DEV_PATH        = os.path.join(DEV_ROOT, 'Platforms/iPhoneOS.platform/Developer')
CC_PATH         = os.path.join(XC_TC_ROOT, 'usr/bin/clang')
CXX_PATH        = os.path.join(XC_TC_ROOT, 'usr/bin/clang++')
ARCHS           = ['armv7']
MIN_OS_VERSION  = '6.0'


def get_latest_sdk_path(platform):
    output = sp.check_output(['xcodebuild', '-showsdks'])
    sdks = [x for x in output.splitlines() if platform in x]
    latest = sdks[-1].split()[-1]
    return sp.check_output(['xcodebuild', '-version', '-sdk', latest, 'Path']).strip()

def setup_env_vars():
    os.environ['CC'] = CC_PATH
    os.environ['CXX'] = CXX_PATH
    flag_list = ['-miphoneos-version-min='+MIN_OS_VERSION]

    for an_arch in ARCHS:
        flag_list += ['-arch', an_arch]
    flag_list += ['-isysroot', get_latest_sdk_path(platform='iphoneos')]
    flags = ' '.join(flag_list)
    for k in ('CFLAGS', 'CXXFLAGS', 'LDFLAGS'):
        os.environ[k] = flags

def as_flag_defs(flag_map):
    return ['-D%s=%s'%(k,flag_map[k]) for k in flag_map]

def get_compiler_flags():
    return as_flag_defs({'EIGEN_INCLUDE_DIR': EIGEN_PATH
                        ,'MINIGLOG': 1
                        })

def get_cmake_flags():
    return as_flag_defs({'CMAKE_TOOLCHAIN_FILE':CMAKE_TC_PATH
                        ,'CMAKE_INSTALL_PREFIX':INSTALL_PATH
                        })

def setup_build_dir():
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)
    os.mkdir(BUILD_DIR)
    os.chdir(BUILD_DIR)

def build(src_path, install=True):

    # Configure
    setup_build_dir()
    compiler_flags = get_compiler_flags()
    cmake_flags = get_cmake_flags()

    # No longer necessary - taken care of in the toolchain file.
    # setup_env_vars

    # Start build
    try:
        cmd = ['cmake']+cmake_flags+compiler_flags+[src_path]
        sp.check_call(cmd)
        sp.check_call(['make'])
        if install:
            if not os.path.exists(INSTALL_PATH):
                os.mkdir(INSTALL_PATH)
            sp.check_call(['make', 'install'])
    except sp.CalledProcessError:
        print('Build failed.')

if __name__=='__main__':
    build(CERES_PATH)
