import time
import subprocess
def main():
    consumer1_process = subprocess.Popen(["python", r"C:\Users\ASUS\OneDrive\Desktop\code\serious_projects\Fraud_Detection_System\Consumer\consumer1.py"])
    time.sleep(5)
    print('consumer1_setup')
    consumer2_process = subprocess.Popen(["python", r"C:\Users\ASUS\OneDrive\Desktop\code\serious_projects\Fraud_Detection_System\Consumer\consumer2.py"])
    time.sleep(5)
    print('consumer2_setup')
    producer_process = subprocess.Popen(["python", r"C:\Users\ASUS\OneDrive\Desktop\code\serious_projects\Fraud_Detection_System\generator\data_generator.py"])
    print('producer_setup')
    try:
            consumer1_process.wait()
            consumer2_process.wait()
            producer_process.wait()
    except KeyboardInterrupt:
            print("\nStopping...")
            consumer1_process.terminate()
            consumer2_process.terminate()
            producer_process.terminate()

if __name__ == '__main__':
    main()