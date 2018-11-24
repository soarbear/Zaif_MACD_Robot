import os
import sys
import subprocess
from zaifdata.errors import ZaifDataError


def install_ta_lib():
    if sys.platform.startswith('linux'):
        # fixme
        cwd = os.path.dirname(__file__)
        subprocess.call(['tar', '-xzf', 'ta-lib-0.4.0-src.tar.gz'], cwd=cwd)
        talib_path = os.path.join(cwd, 'ta-lib')
        subprocess.call(['./configure', '--prefix=/usr'], cwd=talib_path, shell=True)
        subprocess.call(['make'], cwd=talib_path, shell=True)
        subprocess.call(['sudo', 'make', 'install'], cwd=talib_path)
        subprocess.call(['pip', 'install', 'TA-Lib'])
        return

    if sys.platform.startswith('darwin'):
        subprocess.call(["brew", "install", "ta-lib"])
        subprocess.call(['pip', 'install', 'TA-Lib'])
        return

    if sys.platform.startswith('win'):
        bits = '32' if sys.maxsize < 2 ** 31 else '64'
        py_version = str(sys.version_info.major) + str(sys.version_info.minor)
        __install_talib_for_windows(bits, py_version)
        return

    raise ZaifDataError('zaifdata does not support your platform')


def __install_talib_for_windows(bits, py_version):
    if bits == '32':
        file = os.path.join(os.path.dirname(__file__),
                            "TA_Lib-0.4.10-cp{v}-cp{v}m-win32.whl".format(v=py_version))
    else:
        file = os.path.join(os.path.dirname(__file__),
                            "TA_Lib-0.4.10-cp{v}-cp{v}m-win_amd64.whl".format(v=py_version))

    if os.path.isfile(file):
        subprocess.call(["pip", "install", file])
        return

    raise ZaifDataError('zaifdata does not support your platform')
