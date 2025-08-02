import subprocess

def call_nok(self):
        phone_number = '01064602147'
        self.make_call(phone_number)

def call_112(self):
        phone_number = '12'
        self.make_call(phone_number)

def call_119(self):
        phone_number = '19'
        self.make_call(phone_number)

def hang_up(self): #안됨젠장
        adb_command = 'adb shell input keyevent 6'  # KEYCODE_ENDCALL
        try:
            subprocess.run(adb_command, shell=True, check=True)
            print("Call ended.")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while hanging up: {e}")

def make_call(self, phone_number):
        adb_command = f'adb shell am start -a android.intent.action.CALL -d tel:{phone_number}'
        try:
            subprocess.run(adb_command, shell=True, check=True)
            print(f"Calling {phone_number}...")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred: {e}")
