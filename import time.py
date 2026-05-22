import time
import sys
import signal

running = True

spinner = ['|', '/', '-', '\\']

def signal_handler(sig, frame):
    global running
    running = False
    print('\nKalmar dali program. Tera kish!')

signal.signal(signal.SIGINT, signal_handler)

def main():
    print('Starting the program...')
    idx = 0
    while running:
        sys.stdout.write(f'\rLoading... {spinner[idx % len(spinner)]}')
        sys.stdout.flush()
        idx += 1
        time.sleep(0.1)
    print('\rLoading... silesia!           ')

if __name__ == '__main__':
    main()
        