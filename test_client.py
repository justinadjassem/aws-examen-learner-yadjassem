"""
Script client de test pour le pipeline d'ingestion IoT.
Envoie un payload valide puis un payload corrompu vers l'URL CloudFront.

Usage:
    python test_client.py <CloudFrontIngestionURL>
    Exemple: python test_client.py https://d1234abcdef.cloudfront.net/ingest
"""

import json
import sys

import requests


def test_valid_payload(url):
    """Envoie un payload valide avec 4+ mesures structurees."""
    print("=" * 60)
    print("TEST 1 : Payload valide")
    print("=" * 60)

    payload = {
        "sensor_id": "sensor-01",
        "readings": [
            {"temperature": 22.5, "status": "OK"},
            {"temperature": 35.1, "status": "ERROR"},
            {"temperature": 19.8, "status": "OK"},
            {"temperature": 28.3, "status": "ERROR"},
            {"temperature": 21.0, "status": "OK"},
        ],
    }

    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("-" * 60)

    response = requests.post(url, json=payload)

    print(f"Status HTTP: {response.status_code}")
    print(f"Reponse: {json.dumps(response.json(), indent=2)}")
    print()


def test_corrupted_payload(url):
    """Envoie un payload corrompu pour provoquer une erreur Lambda."""
    print("=" * 60)
    print("TEST 2 : Payload corrompu (JSON mal forme)")
    print("=" * 60)

    corrupted_body = '{"sensor_id": "sensor-99", "readings": [{"status": "OK"}]}'
    # Manque la cle "temperature" dans les readings -> provoque une erreur

    print(f"URL: {url}")
    print(f"Payload: {corrupted_body}")
    print("-" * 60)

    response = requests.post(
        url,
        data=corrupted_body,
        headers={"Content-Type": "application/json"},
    )

    print(f"Status HTTP: {response.status_code}")
    try:
        print(f"Reponse: {json.dumps(response.json(), indent=2)}")
    except ValueError:
        print(f"Reponse brute: {response.text}")
    print()


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_client.py <CloudFrontIngestionURL>")
        print("Exemple: python test_client.py https://d1234abcdef.cloudfront.net/ingest")
        sys.exit(1)

    url = sys.argv[1]

    test_valid_payload(url)
    test_corrupted_payload(url)


if __name__ == "__main__":
    main()
