# Automatically execute each sample in specified directory and extract Xposed logs.
# An Android device (real device or emulator) with adb debugging privileges should be connected in advance.
import os
import re
import time

APK_DIR = '~/DroidHook-Host/samples/'

# For device with EdXposed
XPOSED_LOG_FILE = '/data/user_de/0/org.meowcat.edxposed.manager/log/all.log'
# For device with original Xposed
# XPOSED_LOG_FILE = '/data/data/de.robv.android.xposed.installer/log/error.log'

LOG_DIR = '~/DroidHook-Host/log/'
RUN_TIME = 60


if __name__ == "__main__":
    apk_list = os.listdir(APK_DIR)
    count = 0
    os.system('adb root')
    for apk in apk_list:
        count += 1
        if (apk + '.log') in os.listdir(LOG_DIR):
            print('%d: %s has already been analysed.' % (count, apk))
            continue

        # Get the apk file's package name
        pkg_name_raw = os.popen('aapt dump badging %s | grep package' % (APK_DIR + apk)).read()
        l = re.search("name=\'[a-zA-Z0-9._]*\'", pkg_name_raw).span()
        pkg_name = pkg_name_raw[l[0] + 6 : l[1] - 1]

        # Set the PackageName file on /sdcard
        os.system('adb shell rm /sdcard/PackageName')
        os.system('adb shell "echo ' + pkg_name + ' > /sdcard/PackageName"')

        # Reboot the device
        os.system('adb shell reboot now')
        while True:
            result = os.popen('adb shell getprop sys.boot_completed').read()
            if result == '1\n':
                break
            else:
                time.sleep(3)
        time.sleep(5)
        os.system('adb shell settings put global airplane_mode_on 0')
        os.system('adb shell svc wifi enable')

        # Install the apk to device
        result = os.popen('adb install ' + APK_DIR + apk)
        result_str = result.read()
        result_int = result_str.find('Failure')
        if result_int > 0:
            with open(LOG_DIR + 'failure_apk.log', 'a') as f:
                f.write(pkg_name + ': ' + result_str[result_int:])
            continue
        time.sleep(5)

        # Grant Priviledges
        pkg_perm_raw = os.popen('aapt dump badging %s | grep android.permission' % (APK_DIR + apk)).read()
        pkg_perm = re.finditer(r"android.permission.[A-Z_]+", pkg_perm_raw)
        for perm in pkg_perm:
            os.system('adb shell pm grant %s %s' % (pkg_name, perm.group()))
        time.sleep(3)

        # Start Monitor
        start_time = time.time()
        while True:
            os.system('adb shell monkey -p ' + pkg_name + ' --throttle 300 --ignore-crashes --ignore-timeouts --monitor-native-crashes 100')
            if RUN_TIME < (time.time() - start_time):
                break

        # Stop the app
        os.system('adb shell am force-stop ' + pkg_name)

        # Remove the app
        os.system('adb uninstall ' + pkg_name)

        # Get xposed log
        os.system('adb pull ' + XPOSED_LOG_FILE + ' ' + LOG_DIR + apk + '.log')

        # Remove old xposed log
        os.system('adb shell rm ' + XPOSED_LOG_FILE)

        # End
        print(str(count) + ': File ' + apk + ' finished.')
