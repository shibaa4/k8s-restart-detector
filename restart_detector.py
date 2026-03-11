import subprocess
import json
import requests
import os

THRESHOLD = 3


SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")


def send_slack_alert(namespace, pod_name, restart_count):

    message = {
        "text": f"🚨 Kubernetes Restart Alert\nNamespace: {namespace}\nPod: {pod_name}\nRestart Count: {restart_count}"
    }

    requests.post(SLACK_WEBHOOK, json=message)


def get_all_pods():

    output = subprocess.check_output(
        ["kubectl", "get", "pods", "-A", "-o", "json"],
        text=True
    )

    return json.loads(output)

def detect_restart_loops():

    pods_data = get_all_pods()
    print("Scanning cluster for restart loops...\n")

    for pod in pods_data["items"]:

        pod_name = pod["metadata"]["name"]
        namespace = pod["metadata"]["namespace"]
        container_statuses = pod["status"].get("containerStatuses", [])

        for container in container_statuses:

            restart_count = container.get("restartCount", 0)

            if restart_count >= THRESHOLD:

                print("🚨 RESTART ALERT")
                print("Namespace :", namespace)
                print("Pod Name  :", pod_name)
                print("Restart Count :", restart_count)

                send_slack_alert(namespace, pod_name, restart_count)

if __name__ == "__main__":
    detect_restart_loops()