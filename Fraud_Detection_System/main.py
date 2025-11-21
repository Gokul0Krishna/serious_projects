from Consumer.consumer import cmain
from generator.data_generator import gmain
import time
import subprocess
def main():
    consumer_process = subprocess.Popen(["python", r"C:\Users\ASUS\OneDrive\Desktop\code\serious_projects\Fraud_Detection_System\Consumer\consumer.py"])
    time.sleep(5)
    print('consumer_setup')
    producer_process = subprocess.Popen(["python", r"C:\Users\ASUS\OneDrive\Desktop\code\serious_projects\Fraud_Detection_System\generator\data_generator.py"])
    print('producer_setup')
    try:
            consumer_process.wait()
            producer_process.wait()
    except KeyboardInterrupt:
            print("\nStopping...")
            consumer_process.terminate()
            producer_process.terminate()

if __name__ == '__main__':
    main()