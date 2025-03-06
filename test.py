import tobii_research as tr

found_eyetrackers = tr.find_all_eyetrackers()
if found_eyetrackers:
    for eyetracker in found_eyetrackers:
        print(f"Found eyetracker with serial number: {eyetracker.serial_number}")
else:
    print("Tobiiデバイスが見つかりませんでした")
