import requests
import subprocess
import time

PROMETHEUS_URL = "http://10.24.200.57:9090/api/v1/query?query=100%20-%20(avg%20by%20(instance)%20(irate(node_cpu_seconds_total{mode='idle'}[5m]))%20*%20100)" # CPU usage query
THRESHOLD = 75.0
GCP_INSTANCE_GROUP = "flask-group"
GCP_ZONE = "us-central1-a"

def get_cpu_usage():
    try:
        response = requests.get(PROMETHEUS_URL)
        response.raise_for_status()  # Raise HTTPError for bad responses
        data = response.json()
        cpu_usage = float(data['data']['result'][0]['value'][1])
        return cpu_usage
    except requests.exceptions.RequestException as e:
        print(f"Error querying Prometheus: {e}")
        return None
    except (KeyError, IndexError, ValueError) as e:
        print(f"Error parsing Prometheus response: {e}")
        return None

def scale_gcp_instances(num_instances):
    try:
        subprocess.run(
            ["gcloud", "compute", "instance-groups", "managed", "resize", GCP_INSTANCE_GROUP,
             f"--size={num_instances}", f"--zone={GCP_ZONE}"], check=True
        )
        print(f"Scaled GCP instances to {num_instances}.")
    except subprocess.CalledProcessError as e:
        print(f"Error scaling GCP instances: {e}")

def main():
    while True:
        cpu_usage = get_cpu_usage()
        if cpu_usage is not None:
            print(f"CPU Usage: {cpu_usage:.2f}%")
            if cpu_usage > THRESHOLD:
                print("CPU usage exceeds threshold. Scaling GCP instances.")
                scale_gcp_instances(3)  # Scale to 3 instances
            else:
                scale_gcp_instances(1)  # Scale back to 1 instance
        time.sleep(60)  # Check every 60 seconds

if __name__ == "__main__":
    main()
