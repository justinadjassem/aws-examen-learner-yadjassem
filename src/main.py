import json
import os
import uuid
from datetime import datetime, timezone

import boto3


s3_client = boto3.client("s3")
dynamodb_client = boto3.resource("dynamodb")


def handler(event, context):
    s3_bucket = os.environ["S3_BUCKET"]
    dynamodb_table_name = os.environ["DYNAMODB_TABLE"]
    table = dynamodb_client.Table(dynamodb_table_name)

    # Parser le corps JSON de la requete
    body = json.loads(event.get("body", "{}"))
    readings = body["readings"]
    sensor_id = body["sensor_id"]

    # Generer un ID unique et un horodatage
    request_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    timestamp = now.isoformat()

    # Construire la cle S3 avec partitionnement temporel
    s3_key = (
        f"raw-zone/year={now.year}/month={now.month:02d}/"
        f"{sensor_id}_{request_id}.json"
    )

    # Sauvegarder le payload brut dans S3
    s3_client.put_object(
        Bucket=s3_bucket,
        Key=s3_key,
        Body=json.dumps(body),
        ContentType="application/json",
    )

    # Calculer les metriques a la volee
    temperatures = [r["temperature"] for r in readings]
    avg_temperature = round(sum(temperatures) / len(temperatures), 2)
    error_count = sum(1 for r in readings if r.get("status") == "ERROR")

    # Enregistrer le rapport dans DynamoDB
    table.put_item(
        Item={
            "request_id": request_id,
            "timestamp": timestamp,
            "sensor_id": sensor_id,
            "s3_path": f"s3://{s3_bucket}/{s3_key}",
            "avg_temperature": str(avg_temperature),
            "error_count": error_count,
            "total_readings": len(readings),
        }
    )

    return {
        "statusCode": 201,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "message": "Ingestion successful",
            "request_id": request_id,
            "sensor_id": sensor_id,
            "s3_path": f"s3://{s3_bucket}/{s3_key}",
            "avg_temperature": avg_temperature,
            "error_count": error_count,
            "total_readings": len(readings),
        }),
    }
